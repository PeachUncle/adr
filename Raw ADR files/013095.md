# ADR-012: Logging Architecture

## Status
Revised (supersedes previous version)

## Context
OpenK needs a consistent logging approach that prioritizes efficiency and maintains clear usage patterns across different parts of the system. We need to define where and how to use logging most effectively.

## Decision

### 1. Core Architecture
- Use Go's slog as the standard logging interface
- Use LogAttrs pattern exclusively for maximum efficiency
- Maintain consistent context propagation
- Configure logging at server initialization

### 2. Logging Patterns

#### 2.1 Server Components
Server components with logger instance use:
```go
// With context (when context exists)
s.logger.LogAttrs(ctx, slog.LevelInfo, "handling request",
    slog.String("path", r.URL.Path),
    slog.Duration("duration", duration),
)

// Without context (when no context available)
s.logger.LogAttrs(nil, slog.LevelInfo, "server starting",
    slog.String("address", s.server.Addr),
    slog.Duration("timeout", s.config.Timeout),
)
```

#### 2.2 Independent Packages
Independent packages use slog directly:
```go
// With context (when context exists)
slog.Default().LogAttrs(ctx, slog.LevelInfo, "rotating key",
    slog.String("key_id", keyID),
    slog.Time("rotation_time", time.Now()),
)

// Without context (when no context available)
slog.Default().LogAttrs(nil, slog.LevelInfo, "initializing crypto",
    slog.String("provider", "aes-gcm"),
)
```

### 3. Context Usage Guidelines

#### 3.1 When to Include Context Parameter
Functions should take context when they:
- Make network calls
- Access databases or external storage
- Perform long-running operations
- Need cancellation/timeout support
- Propagate request-scoped data

Example:
```go
// Should take context - involves storage
func (k *KeyManager) Rotate(ctx context.Context, keyID string) error

// Should not take context - pure computation
func (k *KeyManager) ValidateKeyFormat(keyID string) error
```

#### 3.2 Context in Logging
- Pass context to LogAttrs when available from function parameters
- Use nil context when logging from functions without context
- Never create new contexts just for logging

### 4. Logger Usage Boundaries

#### 4.1 Server Logger (s.logger)
Use for:
- HTTP handlers and middleware
- Server startup/shutdown
- Request processing
- Server-specific operations

#### 4.2 Direct slog Usage
Use for:
- Independent packages (crypto, kms)
- Utility functions
- Library code
- Any code that shouldn't depend on server

### 5. Implementation Requirements

#### 5.1 Configuration
```go
type Config struct {
    Level       slog.Level
    Format      string // "json" or "text"
    AddSource   bool
    TimeFormat  string
}
```

#### 5.2 Initialization
- Configure at server startup
- Set default logger for independent packages
- Configure handler options appropriately
- Enable JSON output in production

### 6. Best Practices
- Always use LogAttrs for consistency and efficiency
- Include relevant context when available
- Use structured logging with proper attribute types
- Follow consistent attribute naming
- Clear log levels based on operational importance

## Consequences

### Positive
- Consistent, efficient logging across codebase
- Clear context usage guidelines
- Type-safe attribute logging
- Performance optimized by default
- Clear boundaries between server and package logging

### Negative
- More verbose than key-value logging
- Requires discipline to maintain consistency
- Need to properly propagate context

## Implementation Notes
1. Update all existing logging to use LogAttrs
2. Implement proper context propagation
3. Configure appropriate log levels
4. Document usage patterns

## References
- slog documentation
- ADR-004 Service Architecture
- ADR-010 HTTP Error Handling