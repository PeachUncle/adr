# ADR-00005: Backend Architecture and API Design

## Status
**Accepted** - 2024-09-28

## Context
The AGoat Publisher system needs a robust, scalable backend that supports both content management and business-specific functionality (Thorne health products). The backend must handle authentication, data management, and provide a clean API for the frontend while maintaining security and performance.

## Decision
Implement a Go-based backend using:
- **Go 1.24.2** for high performance and concurrency
- **Gorilla Mux** for HTTP routing and middleware
- **Gorilla Sessions** for secure session management
- **PostgreSQL driver (lib/pq)** for database connectivity
- **Google UUID** for unique identifier generation
- **Structured logging** with JSON format
- **RESTful API** design with clear resource endpoints
- **Middleware-based** architecture for cross-cutting concerns

## Rationale
1. **Performance**: Go provides excellent performance and low memory footprint
2. **Concurrency**: Native goroutines handle concurrent requests efficiently
3. **Reliability**: Strong typing and error handling reduce runtime errors
4. **Ecosystem**: Rich ecosystem with mature libraries for web development
5. **Deployment**: Single binary deployment simplifies operations
6. **Maintainability**: Simple, readable code with clear patterns
7. **Security**: Built-in security features and secure session management

## Consequences

### Positive
- **Performance**: High throughput and low latency
- **Scalability**: Efficient handling of concurrent requests
- **Reliability**: Strong typing and error handling
- **Maintainability**: Simple, readable codebase
- **Deployment**: Single binary deployment
- **Security**: Built-in security features
- **Monitoring**: Structured logging for observability

### Negative
- **Learning Curve**: Team needs Go expertise
- **Ecosystem**: Smaller ecosystem compared to Node.js/Python
- **Development Speed**: May be slower for rapid prototyping
- **Dependencies**: Fewer third-party libraries available

## Implementation Details

### Technology Stack
```go
// go.mod
module agoat.io/agoat-publisher

go 1.24.2

require (
    github.com/google/uuid v1.6.0
    github.com/gorilla/mux v1.8.1
    github.com/gorilla/sessions v1.4.0
    github.com/lib/pq v1.10.9
)
```

### Architecture Patterns
1. **Layered Architecture**: Clear separation of concerns
2. **Middleware Pattern**: Cross-cutting concerns handled by middleware
3. **Repository Pattern**: Data access abstraction
4. **Service Layer**: Business logic encapsulation
5. **Handler Pattern**: HTTP request/response handling

### API Design
```go
// RESTful endpoints
/api/status                    // System health check
/api/login                     // Authentication
/api/sites                     // Site management
/api/sites/{id}                // Individual site operations
/api/sites/{siteId}/posts      // Post management
/api/sites/{siteId}/posts/{id} // Individual post operations
/api/auth/azure-user           // Azure AD integration
/api/auth/cognito/*            // Cognito integration
/api/thorne/*                  // Thorne business domain
```

### Key Features
1. **Structured Logging**: JSON-formatted logs with unique IDs
2. **Error Handling**: Comprehensive error types and responses
3. **Session Management**: Secure session handling with Gorilla Sessions
4. **Database Integration**: Efficient PostgreSQL connectivity
5. **Authentication**: OIDC-compliant authentication handlers
6. **CORS Support**: Cross-origin resource sharing configuration
7. **Health Checks**: System monitoring and health endpoints

### Security Measures
- Secure session management with encrypted cookies
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- CORS configuration for cross-origin requests
- Authentication middleware for protected endpoints
- Audit logging for security events

### Performance Optimizations
- Connection pooling for database connections
- Efficient HTTP routing with Gorilla Mux
- Structured logging for performance monitoring
- Concurrent request handling with goroutines
- Memory-efficient data structures

### Development Workflow
1. **Hot Reload**: Air tool for automatic code reloading
2. **Testing**: Built-in testing framework with table-driven tests
3. **Linting**: gofmt and golint for code quality
4. **Documentation**: Godoc for API documentation
5. **Build**: Single binary compilation for deployment

## References
- [Go Documentation](https://golang.org/doc/)
- [Gorilla Mux Documentation](https://github.com/gorilla/mux)
- [Gorilla Sessions Documentation](https://github.com/gorilla/sessions)
- [PostgreSQL Driver Documentation](https://github.com/lib/pq)
- [API Documentation](../../docs/api/restful-url-structure.md)
- [Backend Requirements](../../requirements-and-user-stories/final-functional/authentication-requirements.md)
- [Performance Requirements](../../requirements-and-user-stories/final-nonfunctional/performance-requirements.md)
