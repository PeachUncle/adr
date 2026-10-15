# 4. Logging Conventions

## Status

Accepted

Date: 2025-06-25

## Context

As we build domain services in Go, we need consistent logging practices that:

- Provide structured, machine-parseable logs
- Include appropriate context for troubleshooting
- Support different log levels for various environments
- Correlate logs across service boundaries
- Balance verbosity with performance considerations
- Follow industry best practices for observability

Inconsistent logging approaches lead to several challenges:

- Difficulty tracing requests across service boundaries
- Inconsistent log levels and formats
- Missing critical context in production issues
- Performance overhead from excessive logging
- Difficulty filtering logs for specific events or errors

## Decision

We will adopt zap (go.uber.org/zap) as our standard logging library with a custom Logger interface that abstracts 
implementation details, providing the following benefits:

### 1. Structured Logging

- Use structured, JSON-formatted logs in production
- Include contextual fields with all log messages
- Use consistent field naming across services

```go
logger.Info("Customer created successfully", 
    log.Field{Key: "customer_id", Value: customer.ID},
    log.Field{Key: "email", Value: customer.Email})
```

### 2. Log Levels

- **Debug**: Detailed information for debugging (disabled in production)
- **Info**: Normal application behavior, key lifecycle events
- **Warn**: Potential issues that don't prevent operation
- **Error**: Errors that affect a specific operation but allow the service to continue
- **Fatal**: Critical errors that prevent the service from continuing

### 3. Request Context Propagation

- Include request ID in all logs related to a request
- Pass logger with request context through the call chain
- Use the WithContext method to enrich logs with request information

```go
// Logger enriched with request information from context
logger.WithContext(ctx).Error("Failed to find customer", err)
```

### 4. Standard Log Fields

| Field Name | Description | Example |
|------------|-------------|--------|
| request.request_id | Unique request identifier | "7f3ed891-c6f1-4b74-a589-103e41f1d5b0" |
| request.host | Hostname from the request | "api.example.com" |
| request.real_ip | Client's IP address | "192.168.1.1" |
| request.user_agent | User agent string | "Mozilla/5.0..." |
| timestamp | ISO 8601 timestamp | "2025-06-25T14:35:05Z" |
| level | Log level | "info", "error" |
| message | Human-readable message | "Customer created successfully" |
| error | Error details | {"message":"document not found"} |
| caller | Source file and line | "service.go:42" |
| stack_trace | Stack trace (for errors) | "goroutine 1..." |

### 5. Error Logging

- Error and Fatal methods accept error as a second parameter
- Add context about the operation that failed using fields
- Include relevant IDs and parameters (sanitized of sensitive data)

```go
// Direct error logging (minimal approach)
logger.Error("Failed to create customer", err)

// Error logging with additional context
logger.WithContext(ctx).Error("Failed to create customer", err)

// With additional context fields
logger.Info("Operation attempted", 
    log.Field{Key: "operation", Value: "CreateCustomer"},
    log.Field{Key: "email", Value: email})
logger.Error("Operation failed", err)
```

### 6. Sensitive Data Handling

- Never log passwords, tokens, or credentials

### 7. Logger Initialization

- Initialize a single root logger in the application entry point
- Pass logger instances to components via constructors

```go
// In main.go
logger, err := log.NewProduction()
if err != nil {
    log.Fatalf("can't initialize logger: %v", err)
}
defer logger.Sync()

// For testing
logger, _ := log.NewTest()
```

## Consequences

### Positive

- Consistent, structured logs across all services
- Improved troubleshooting with detailed context
- Better correlation of events across service boundaries
- Efficient log searching and filtering
- Reduced time to identify and resolve issues

### Negative

- Small performance overhead from structured logging
- Learning curve for proper logging practices
- Need for discipline in the following conventions

### Neutral

- Regular review of logging patterns for effectiveness

## Implementation Notes

### Logger Interface

We've implemented a standardized logger interface that abstracts the underlying implementation:

```go
// Logger provides methods for structured and leveled logging within the application.
type Logger interface {
	Sync() error
	WithContext(ctx context.Context) Logger
	Debug(msg string, fields ...Field)
	Info(msg string, fields ...Field)
	Warn(msg string, fields ...Field)
	Error(msg string, err error)
	Fatal(msg string, err error)
}

type Field struct {
	Key   string
	Value any
}
```

### Middleware for Request Context

We've implemented middleware to add request information to the context:

```go
// RequestInfoMiddleware is a middleware that attaches request-specific information to the context.
func RequestInfoMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = uuid.New().String()
		}

		realIP := c.GetHeader("X-Real-IP")
		if realIP == "" {
			realIP = c.ClientIP()
		}

		// log is the internal log package
		info := log.RequestInfo{
			RequestID: requestID,
			Host:      c.Request.Host,
			RealIP:    realIP,
			UserAgent: c.Request.UserAgent(),
		}

		ctx := log.WithRequestInfo(c.Request.Context(), info)
		c.Request = c.Request.WithContext(ctx)
		c.Next()
	}
}
```

### Context Utilities

We've implemented a package for storing and retrieving request context:

```go
// RequestInfo represents metadata about a request
type RequestInfo struct {
	RequestID string
	Host      string
	RealIP    string
	UserAgent string
}

// WithRequestInfo adds request-specific information to the provided context
func WithRequestInfo(ctx context.Context, info RequestInfo) context.Context {
	ctx = context.WithValue(ctx, requestIDKey, info.RequestID)
	ctx = context.WithValue(ctx, hostKey, info.Host)
	ctx = context.WithValue(ctx, realIPKey, info.RealIP)
	ctx = context.WithValue(ctx, userAgentKey, info.UserAgent)
	return ctx
}

// LoggerWithRequestInfo enriches the provided logger with request metadata
func LoggerWithRequestInfo(ctx context.Context, logger *zap.Logger) *zap.Logger {
	reqInfo := RequestInfo{
		RequestID: RequestIDFromContext(ctx),
		Host:      HostFromContext(ctx),
		RealIP:    RealIPFromContext(ctx),
		UserAgent: UserAgentFromContext(ctx),
	}

	return logger.With(zap.Object("request", reqInfo))
}
```

## Related Documents

- [Interface Design Principles](./0002-interface-design-principles.md)
- [Dependency Injection](./0003-dependency-injection-and-service-initialization.md)

## Contributors

- Àlex Grau Roca
