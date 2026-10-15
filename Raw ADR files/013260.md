# ADR 0015: Backend Custom Error Design

## Status

Accepted

## Context

In ADR 0007 (Backend Architecture - Onion Architecture), we defined that each layer should have its own `error/` package for custom error types. However, the specific design and implementation rules for these custom errors were not clearly defined. This has led to:

* Inconsistent error handling across different layers and contexts.
* Difficulty in debugging due to lack of structured error information.
* Challenges in mapping errors to appropriate HTTP status codes at the API layer.
* Missing context when errors propagate through multiple layers.
* Unclear responsibilities regarding where to log errors and at what level.

To ensure maintainability, testability, and consistent error handling throughout the application, we need to establish comprehensive guidelines for custom error design across all architectural layers.

## Decision

We will adopt the following custom error design strategy for the backend application:

### 1. Error Type Design Principles

#### 1.1 Error Structure

* Use `struct` types that implement the `error` interface.
* All custom error types must implement the `Error() string` method.
* Leverage Go 1.13+ error wrapping features (`errors.Is`, `errors.As`, `Unwrap()`).
* Include structured information (error code, context fields, wrapped errors) in custom error types.

#### 1.2 Error Wrapping Strategy

* Use `fmt.Errorf("context: %w", err)` to wrap errors when adding context.
* Implement `Unwrap() error` method for custom errors that wrap other errors.
* Implement `Is(target error) bool` for sentinel error comparison.
* Implement `As(target interface{}) bool` for type assertion when needed.

**Base Error Structure Example:**

```go
// BaseError provides common fields for all custom errors
type BaseError struct {
    Code    string                 // Error code (e.g., "DOMAIN_001")
    Message string                 // Human-readable message
    Cause   error                  // Wrapped underlying error
    Context map[string]interface{} // Additional context information
}

func (e *BaseError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("[%s] %s: %v", e.Code, e.Message, e.Cause)
    }
    return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func (e *BaseError) Unwrap() error {
    return e.Cause
}
```

### 2. Layer-Specific Error Responsibilities

#### 2.1 Domain Layer Errors (`internal/<context>/domain/error/`)

**Responsibility:** Business rule violations, invariant violations, domain validation failures.

**Characteristics:**

* Independent of infrastructure or presentation concerns.
* Focus on domain-specific business rules.
* Should be named to reflect domain concepts.
* No HTTP status codes or technical error details.

**Examples:**

```go
package error

import (
    "errors"
    "fmt"
)

// Sentinel errors for common domain violations
// These are used for error comparison with errors.Is() across layer boundaries
var (
    ErrInvalidEntity      = errors.New("invalid entity")
    ErrInvariantViolation = errors.New("invariant violation")
)

// ValidationError represents a domain validation failure
type ValidationError struct {
    Field   string
    Value   interface{}
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed for field '%s': %s", e.Field, e.Message)
}

// Is enables errors.Is() comparison with sentinel error
func (e *ValidationError) Is(target error) bool {
    return target == ErrInvalidEntity
}

// BusinessRuleViolationError represents a business rule violation
type BusinessRuleViolationError struct {
    Rule    string
    Entity  string
    Message string
}

func (e *BusinessRuleViolationError) Error() string {
    return fmt.Sprintf("business rule '%s' violated for %s: %s", e.Rule, e.Entity, e.Message)
}

func (e *BusinessRuleViolationError) Is(target error) bool {
    return target == ErrInvariantViolation
}

// InvalidStateTransitionError represents an invalid state transition
type InvalidStateTransitionError struct {
    Entity      string
    FromState   string
    ToState     string
    Reason      string
}

func (e *InvalidStateTransitionError) Error() string {
    return fmt.Sprintf("invalid state transition for %s from '%s' to '%s': %s",
        e.Entity, e.FromState, e.ToState, e.Reason)
}
```

**Usage in Domain Layer:**

```go
// In entity factory function
func NewRepository(id RepositoryID, url string) (*Repository, error) {
    if url == "" {
        return nil, &error.ValidationError{
            Field:   "url",
            Value:   url,
            Message: "repository URL cannot be empty",
        }
    }
    // ... create entity
    return &Repository{id: id, url: url}, nil
}
```

**How Sentinel Errors are Used:**

The sentinel errors (`ErrInvalidEntity`, `ErrInvariantViolation`) serve as category markers that enable layer-agnostic error checking. They are primarily used in upper layers (Application, Interfaces) to determine error categories without depending on specific error types:

```go
// In Application Layer (Usecase)
func (uc *UserUsecase) CreateUser(ctx context.Context, req *dto.CreateUserRequest) (*dto.UserResponse, error) {
    user, err := entity.NewUser(userID, req.Name)
    if err != nil {
        // Check if it's a domain validation error using sentinel
        if errors.Is(err, domainerror.ErrInvalidEntity) {
            // Convert to application-level validation error
            return nil, &apperror.ValidationFailedError{
                Errors: []apperror.FieldError{
                    {Field: "user", Message: err.Error()},
                },
            }
        }
        
        // Check if it's a business rule violation using sentinel
        if errors.Is(err, domainerror.ErrInvariantViolation) {
            // Convert to application-level conflict error
            return nil, &apperror.ConflictError{
                ResourceType: "User",
                Reason:       err.Error(),
                Cause:        err,
            }
        }
        
        // Unexpected domain error
        return nil, fmt.Errorf("unexpected domain error: %w", err)
    }
    // ... continue processing
}
```

```go
// In Interfaces Layer (Handler)
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.usecase.CreateUser(r.Context(), req)
    if err != nil {
        // The error mapping can also check sentinel errors if needed
        // but typically works with application layer errors
        if errors.Is(err, apperror.ErrBadRequest) {
            // This includes wrapped domain validation errors
            httpErr := interror.BadRequest(err.Error())
            httpErr.WriteJSON(w)
            return
        }
        // ... other error handling
    }
    // ... success response
}
```

**Benefits of Sentinel Errors:**

* **Layer Independence:** Upper layers can categorize errors without importing specific error types from lower layers.
* **Error Grouping:** Multiple specific error types can be grouped under one sentinel (e.g., different validation errors all match `ErrInvalidEntity`).
* **Flexible Handling:** Allows for both specific error type checking (`errors.As`) and category checking (`errors.Is`).

#### 2.2 Application Layer Errors (`internal/<context>/application/error/`)

**Responsibility:** Use case execution errors, resource not found, authorization failures, application-level validation.

**Characteristics:**

* Orchestrates domain errors and adds application context.
* Wraps domain and infrastructure errors.
* Defines application-level error categories (NotFound, Unauthorized, etc.).
* Can reference resources by ID or type.

**Examples:**

```go
package error

import (
    "errors"
    "fmt"
)

// Sentinel errors for common application failures
var (
    ErrNotFound      = errors.New("resource not found")
    ErrUnauthorized  = errors.New("unauthorized")
    ErrForbidden     = errors.New("forbidden")
    ErrConflict      = errors.New("resource conflict")
    ErrBadRequest    = errors.New("bad request")
)

// NotFoundError represents a resource not found error
type NotFoundError struct {
    ResourceType string
    ResourceID   string
    Cause        error
}

func (e *NotFoundError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("%s not found (ID: %s): %v", e.ResourceType, e.ResourceID, e.Cause)
    }
    return fmt.Sprintf("%s not found (ID: %s)", e.ResourceType, e.ResourceID)
}

func (e *NotFoundError) Is(target error) bool {
    return target == ErrNotFound
}

func (e *NotFoundError) Unwrap() error {
    return e.Cause
}

// UnauthorizedError represents an authentication failure
type UnauthorizedError struct {
    Reason string
    Cause  error
}

func (e *UnauthorizedError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("unauthorized: %s: %v", e.Reason, e.Cause)
    }
    return fmt.Sprintf("unauthorized: %s", e.Reason)
}

func (e *UnauthorizedError) Is(target error) bool {
    return target == ErrUnauthorized
}

func (e *UnauthorizedError) Unwrap() error {
    return e.Cause
}

// ForbiddenError represents an authorization failure
type ForbiddenError struct {
    Resource string
    Action   string
    UserID   string
}

func (e *ForbiddenError) Error() string {
    return fmt.Sprintf("user %s is forbidden to %s on resource %s", e.UserID, e.Action, e.Resource)
}

func (e *ForbiddenError) Is(target error) bool {
    return target == ErrForbidden
}

// ConflictError represents a resource conflict (e.g., duplicate key)
type ConflictError struct {
    ResourceType string
    Identifier   string
    Reason       string
    Cause        error
}

func (e *ConflictError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("conflict: %s with identifier '%s' already exists: %s: %v",
            e.ResourceType, e.Identifier, e.Reason, e.Cause)
    }
    return fmt.Sprintf("conflict: %s with identifier '%s' already exists: %s",
        e.ResourceType, e.Identifier, e.Reason)
}

func (e *ConflictError) Is(target error) bool {
    return target == ErrConflict
}

func (e *ConflictError) Unwrap() error {
    return e.Cause
}

// ValidationFailedError represents application-level validation failure
type ValidationFailedError struct {
    Errors []FieldError
}

type FieldError struct {
    Field   string
    Message string
}

func (e *ValidationFailedError) Error() string {
    return fmt.Sprintf("validation failed: %d error(s)", len(e.Errors))
}

func (e *ValidationFailedError) Is(target error) bool {
    return target == ErrBadRequest
}
```

**Usage in Application Layer:**

```go
// In use case
func (uc *RepositoryUsecase) GetRepository(ctx context.Context, id string) (*dto.RepositoryResponse, error) {
    repoID, err := entity.NewRepositoryID(id)
    if err != nil {
        // Wrap domain error with application context
        return nil, &apperror.ValidationFailedError{
            Errors: []apperror.FieldError{
                {Field: "id", Message: "invalid repository ID format"},
            },
        }
    }

    repo, err := uc.repoRepository.FindByID(ctx, repoID)
    if err != nil {
        // Wrap infrastructure error
        return nil, fmt.Errorf("failed to retrieve repository: %w", err)
    }
    if repo == nil {
        return nil, &apperror.NotFoundError{
            ResourceType: "Repository",
            ResourceID:   id,
        }
    }

    return uc.toDTO(repo), nil
}
```

#### 2.3 Infrastructure Layer Errors (`internal/<context>/infrastructure/error/`)

**Responsibility:** Technical failures (database, external APIs, file I/O), connection issues.

**Characteristics:**

* Wrap third-party library errors (GORM, HTTP clients, etc.).
* Distinguish between transient (retryable) and permanent errors.
* Include technical details useful for debugging.
* Convert external errors to domain-appropriate errors.

**Examples:**

```go
package error

import (
    "errors"
    "fmt"
)

// Sentinel errors for infrastructure failures
var (
    ErrDatabase       = errors.New("database error")
    ErrExternalAPI    = errors.New("external API error")
    ErrConnection     = errors.New("connection error")
    ErrTimeout        = errors.New("timeout error")
    ErrRetryable      = errors.New("retryable error")
)

// DatabaseError represents a database operation failure
type DatabaseError struct {
    Operation string // "FindByID", "Save", "Delete", etc.
    Table     string
    Cause     error
    Retryable bool
}

func (e *DatabaseError) Error() string {
    return fmt.Sprintf("database error during %s on table %s: %v", e.Operation, e.Table, e.Cause)
}

func (e *DatabaseError) Is(target error) bool {
    if target == ErrDatabase {
        return true
    }
    if target == ErrRetryable && e.Retryable {
        return true
    }
    return false
}

func (e *DatabaseError) Unwrap() error {
    return e.Cause
}

// ExternalAPIError represents an external API call failure
type ExternalAPIError struct {
    Service    string // "GitHub", "GitLab", etc.
    Endpoint   string
    StatusCode int
    Cause      error
    Retryable  bool
}

func (e *ExternalAPIError) Error() string {
    return fmt.Sprintf("external API error calling %s at %s (status %d): %v",
        e.Service, e.Endpoint, e.StatusCode, e.Cause)
}

func (e *ExternalAPIError) Is(target error) bool {
    if target == ErrExternalAPI {
        return true
    }
    if target == ErrRetryable && e.Retryable {
        return true
    }
    return false
}

func (e *ExternalAPIError) Unwrap() error {
    return e.Cause
}

// ConnectionError represents a connection failure
type ConnectionError struct {
    Target string // "database", "redis", "external API", etc.
    Cause  error
}

func (e *ConnectionError) Error() string {
    return fmt.Sprintf("connection error to %s: %v", e.Target, e.Cause)
}

func (e *ConnectionError) Is(target error) bool {
    return target == ErrConnection
}

func (e *ConnectionError) Unwrap() error {
    return e.Cause
}

// StorageError represents a storage operation failure
type StorageError struct {
    Operation string // "Upload", "Download", "Delete"
    Path      string
    Cause     error
}

func (e *StorageError) Error() string {
    return fmt.Sprintf("storage error during %s at path %s: %v", e.Operation, e.Path, e.Cause)
}

func (e *StorageError) Unwrap() error {
    return e.Cause
}
```

**Usage in Infrastructure Layer:**

```go
// In repository implementation
func (r *PostgresRepositoryImpl) FindByID(ctx context.Context, id entity.RepositoryID) (*entity.Repository, error) {
    var model GormRepositoryModel
    err := r.db.WithContext(ctx).First(&model, "repository_id = ?", id.String()).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, nil // Return nil, nil for not found (application layer handles this)
        }
        // Wrap GORM error with infrastructure error
        return nil, &infraerror.DatabaseError{
            Operation: "FindByID",
            Table:     "repositories",
            Cause:     err,
            Retryable: isRetryableDBError(err), // Helper function to detect transient errors
        }
    }
    return toDomainEntity(&model)
}
```

#### 2.4 Interfaces Layer Errors (`internal/<context>/interfaces/error/`)

**Responsibility:** HTTP status code mapping, client-friendly error responses, API error formatting.

**Characteristics:**

* Maps application/domain/infrastructure errors to HTTP status codes.
* Provides structured JSON error responses.
* Sanitizes error messages for external clients.
* Includes request ID for tracing.

**Examples:**

```go
package error

import (
    "encoding/json"
    "net/http"
)

// HTTPError represents an HTTP error response
type HTTPError struct {
    StatusCode int                    `json:"-"`
    Code       string                 `json:"code"`
    Message    string                 `json:"message"`
    Details    map[string]interface{} `json:"details,omitempty"`
    RequestID  string                 `json:"request_id,omitempty"`
}

func (e *HTTPError) Error() string {
    return e.Message
}

// WriteJSON writes the error as JSON response
func (e *HTTPError) WriteJSON(w http.ResponseWriter) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(e.StatusCode)
    json.NewEncoder(w).Encode(e)
}

// NewHTTPError creates a new HTTPError
func NewHTTPError(statusCode int, code, message string) *HTTPError {
    return &HTTPError{
        StatusCode: statusCode,
        Code:       code,
        Message:    message,
        Details:    make(map[string]interface{}),
    }
}

// WithDetails adds details to the error
func (e *HTTPError) WithDetails(details map[string]interface{}) *HTTPError {
    e.Details = details
    return e
}

// WithRequestID adds request ID to the error
func (e *HTTPError) WithRequestID(requestID string) *HTTPError {
    e.RequestID = requestID
    return e
}

// Predefined HTTP errors
func BadRequest(message string) *HTTPError {
    return NewHTTPError(http.StatusBadRequest, "BAD_REQUEST", message)
}

func Unauthorized(message string) *HTTPError {
    return NewHTTPError(http.StatusUnauthorized, "UNAUTHORIZED", message)
}

func Forbidden(message string) *HTTPError {
    return NewHTTPError(http.StatusForbidden, "FORBIDDEN", message)
}

func NotFound(message string) *HTTPError {
    return NewHTTPError(http.StatusNotFound, "NOT_FOUND", message)
}

func Conflict(message string) *HTTPError {
    return NewHTTPError(http.StatusConflict, "CONFLICT", message)
}

func InternalServerError(message string) *HTTPError {
    return NewHTTPError(http.StatusInternalServerError, "INTERNAL_SERVER_ERROR", message)
}

func ServiceUnavailable(message string) *HTTPError {
    return NewHTTPError(http.StatusServiceUnavailable, "SERVICE_UNAVAILABLE", message)
}
```

**Error Mapping Helper:**

```go
package error

import (
    "errors"
    apperror "YOUR_PROJECT/internal/<context>/application/error"
    infraerror "YOUR_PROJECT/internal/<context>/infrastructure/error"
)

// MapToHTTPError maps application/domain/infrastructure errors to HTTP errors
func MapToHTTPError(err error, requestID string) *HTTPError {
    var httpErr *HTTPError

    switch {
    // Application layer errors
    case errors.Is(err, apperror.ErrNotFound):
        httpErr = NotFound("Resource not found")
    case errors.Is(err, apperror.ErrUnauthorized):
        httpErr = Unauthorized("Authentication required")
    case errors.Is(err, apperror.ErrForbidden):
        httpErr = Forbidden("Access denied")
    case errors.Is(err, apperror.ErrConflict):
        httpErr = Conflict("Resource already exists")
    case errors.Is(err, apperror.ErrBadRequest):
        httpErr = BadRequest("Invalid request")

    // Infrastructure layer errors
    case errors.Is(err, infraerror.ErrConnection):
        httpErr = ServiceUnavailable("Service temporarily unavailable")
    case errors.Is(err, infraerror.ErrTimeout):
        httpErr = ServiceUnavailable("Request timeout")
    case errors.Is(err, infraerror.ErrRetryable):
        httpErr = ServiceUnavailable("Temporary error, please retry")

    // Default to internal server error
    default:
        httpErr = InternalServerError("An unexpected error occurred")
    }

    return httpErr.WithRequestID(requestID)
}
```

**Usage in Handler:**

```go
package handlers

import (
    "net/http"
    "YOUR_PROJECT/internal/<context>/application/usecase"
    "YOUR_PROJECT/internal/<context>/interfaces/error"
    "YOUR_PROJECT/internal/shared/infrastructure/middleware"
)

type RepositoryHandler struct {
    usecase *usecase.RepositoryUsecase
}

func (h *RepositoryHandler) GetRepository(w http.ResponseWriter, r *http.Request) {
    // Extract request ID from context
    requestID, _ := r.Context().Value(middleware.RequestIDKey).(string)

    id := r.URL.Query().Get("id")
    repo, err := h.usecase.GetRepository(r.Context(), id)
    if err != nil {
        // Map error to HTTP error and write response
        httpErr := error.MapToHTTPError(err, requestID)
        httpErr.WriteJSON(w)
        return
    }

    // Success response
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(repo)
}
```

### 3. Error Handling Strategy

#### 3.1 Error Propagation Rules

* **Domain Layer:** Create and return domain-specific errors. Never log errors.
* **Application Layer:** Wrap domain/infrastructure errors with application context. Log errors at `ERROR` level only for unexpected failures.
* **Infrastructure Layer:** Convert third-party errors to custom infrastructure errors. Log errors at `ERROR` level.
* **Interfaces Layer:** Map errors to HTTP responses. Log all errors with appropriate level. Never expose internal error details to clients.

#### 3.2 Error Wrapping Guidelines

```go
// Good: Add context while preserving error chain
return fmt.Errorf("failed to create user: %w", err)

// Good: Wrap with custom error
return &apperror.NotFoundError{
    ResourceType: "User",
    ResourceID:   id,
    Cause:        err,
}

// Bad: Lose error chain
return fmt.Errorf("failed to create user: %v", err) // Use %w, not %v

// Bad: Swallow error details
return errors.New("operation failed") // Without wrapping original error
```

#### 3.3 Logging Strategy (Integration with ADR 0008)

* **Domain Layer:** No logging (pure business logic).
* **Application Layer:**
  * Log `ERROR` for unexpected failures.
  * Log `WARN` for expected but noteworthy conditions.
  * Include `error` field in structured log.
* **Infrastructure Layer:**
  * Log `ERROR` for all failures with full context.
  * Include operation details, connection info, etc.
* **Interfaces Layer:**
  * Log all errors with appropriate level.
  * `ERROR`: 5xx errors.
  * `WARN`: 4xx errors (client errors).
  * Always include `request_id`.

**Example Logging with Errors:**

```go
// In Application Layer
func (uc *UserUsecase) CreateUser(ctx context.Context, req *dto.CreateUserRequest) (*dto.UserResponse, error) {
    logger := ctx.Value(middleware.LoggerKey).(*slog.Logger)

    user, err := entity.NewUser(/* ... */)
    if err != nil {
        // Domain validation error - log at WARN level
        logger.WarnContext(ctx, "User creation failed due to validation error",
            slog.Any("error", err),
            slog.String("username", req.Username))
        return nil, err
    }

    if err := uc.userRepo.Save(ctx, user); err != nil {
        // Infrastructure error - log at ERROR level
        logger.ErrorContext(ctx, "Failed to save user to database",
            slog.Any("error", err),
            slog.String("user_id", user.ID().String()))
        return nil, fmt.Errorf("failed to save user: %w", err)
    }

    return uc.toDTO(user), nil
}
```

### 4. Error Message Design

#### 4.1 Error Code System

Use a compact hierarchical error code format: `<CONTEXT><LAYER><NUMBER>`

**Format Specification:**
- **CONTEXT**: 2 characters - Context identifier
- **LAYER**: 1 character - Layer identifier
- **NUMBER**: 4 digits - Sequential error number

**Context Identifiers (2 characters):**

Context identifiers prevent error code collisions across different bounded contexts:

* `GR`: git_repository context
* `US`: user management context
* `PR`: project management context
* (Add more as contexts are added)

**Layer Identifiers (1 character):**

* `D`: Domain Layer
* `A`: Application Layer
* `I`: Infrastructure Layer
* `P`: Presentation/Interfaces Layer

**Examples:**

* `GRD0001`: git_repository domain error #1 (validation)
* `GRD0007`: git_repository domain error #7 (business rule violation)
* `GRA0001`: git_repository application error #1 (resource not found)
* `GRA0003`: git_repository application error #3 (unauthorized access)
* `GRI0001`: git_repository infrastructure error #1 (database connection)
* `GRI0005`: git_repository infrastructure error #5 (external API error)
* `USA0001`: user context application error #1 (resource not found)

**Error Code Management:**

To enable developers to quickly identify where errors occur, implement centralized error code management:

```go
// internal/<context>/domain/error/codes.go
package error

// ErrorCode represents a unique error identifier
// Format: <CONTEXT><LAYER><NUMBER>
// - CONTEXT: 2 characters (e.g., GR for git_repository)
// - LAYER: 1 character (D for domain, A for application, I for infrastructure)
// - NUMBER: 4 digits (e.g., 0001)
// Example: GRD0001
type ErrorCode string

const (
    // Validation errors
    CodeInvalidEntityField     ErrorCode = "GRD0001"
    CodeRequiredFieldMissing   ErrorCode = "GRD0002"
    CodeInvalidFieldFormat     ErrorCode = "GRD0003"
    CodeFieldValueOutOfRange   ErrorCode = "GRD0004"
    
    // Business rule violations
    CodeBusinessRuleViolation  ErrorCode = "GRD0007"
    CodeInvalidStateTransition ErrorCode = "GRD0008"
    CodeInvariantViolation     ErrorCode = "GRD0009"
)

// String returns the string representation of the error code
func (c ErrorCode) String() string {
    return string(c)
}
```

```go
// internal/<context>/application/error/codes.go
package error

type ErrorCode string

const (
    // Resource errors
    CodeResourceNotFound    ErrorCode = "GRA0001"
    CodeResourceConflict    ErrorCode = "GRA0002"
    
    // Authentication/Authorization
    CodeUnauthorized        ErrorCode = "GRA0003"
    CodeForbidden           ErrorCode = "GRA0004"
    CodeInvalidCredentials  ErrorCode = "GRA0005"
    
    // Validation errors
    CodeValidationFailed    ErrorCode = "GRA0006"
    CodeInvalidRequest      ErrorCode = "GRA0007"
)
```

**Enhanced Error Types with Codes:**

```go
// Domain Layer with error codes
type ValidationError struct {
    Code    ErrorCode
    Field   string
    Value   interface{}
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("[%s] validation failed for field '%s': %s", e.Code, e.Field, e.Message)
}

func (e *ValidationError) ErrorCode() ErrorCode {
    return e.Code
}

// Factory functions to prevent manual error struct/code pairing errors
func NewURLValidationError(field string, value interface{}, message string, isSchemeError bool) *ValidationError {
    code := CodeInvalidURL  // GRD0005
    if isSchemeError {
        code = CodeUnsupportedURLScheme  // GRD0006
    }
    
    return &ValidationError{
        Code:    code,
        Field:   field,
        Value:   value,
        Message: message,
    }
}

// Usage in domain
func validateRepositoryURL(repoURL string) error {
    parsedURL, err := url.ParseRequestURI(repoURL)
    if err != nil {
        return domainerror.NewURLValidationError("url", repoURL, "invalid repository URL format", false)
    }
    
    if parsedURL.Scheme != "https" {
        return domainerror.NewURLValidationError("url", repoURL, "unsupported repository URL scheme: only https is supported", true)
    }
    
    return nil
}
```

**Benefits of Factory Functions:**

* **Type Safety**: The compiler ensures the correct error code is always used
* **Reduced Bugs**: Eliminates manual pairing of error struct and error code
* **Better API**: Clear function signatures document required error context
* **Consistency**: All errors of the same type are created the same way

**Error Code Registry:**

Maintain a centralized registry for documentation and monitoring:

```go
// internal/shared/error/registry.go
package error

// ErrorCodeInfo provides metadata about an error code
type ErrorCodeInfo struct {
    Code        string
    Context     string // Context/Bounded Context (e.g., "git_repository", "user")
    Layer       string
    Category    string
    Description string
    Severity    string // "LOW", "MEDIUM", "HIGH", "CRITICAL"
    Retryable   bool
}

// Global error code registry
var ErrorCodeRegistry = map[string]ErrorCodeInfo{
    "GRD0001": {
        Code:        "GRD0001",
        Context:     "git_repository",
        Layer:       "Domain",
        Category:    "Validation",
        Description: "Invalid entity field value",
        Severity:    "MEDIUM",
        Retryable:   false,
    },
    "GRD0002": {
        Code:        "GRD0002",
        Context:     "git_repository",
        Layer:       "Domain",
        Category:    "Validation",
        Description: "Required field is missing",
        Severity:    "MEDIUM",
        Retryable:   false,
    },
    "GRA0001": {
        Code:        "GRA0001",
        Context:     "git_repository",
        Layer:       "Application",
        Category:    "Resource",
        Description: "Requested resource not found",
        Severity:    "LOW",
        Retryable:   false,
    },
    "GRI0001": {
        Code:        "GRI0001",
        Context:     "git_repository",
        Layer:       "Infrastructure",
        Category:    "Database",
        Description: "Database connection error",
        Severity:    "CRITICAL",
        Retryable:   true,
    },
    // ... more entries
}

// GetErrorCodeInfo retrieves metadata for an error code
func GetErrorCodeInfo(code string) (ErrorCodeInfo, bool) {
    info, exists := ErrorCodeRegistry[code]
    return info, exists
}
```

**Logging with Error Codes:**

Error codes enable quick identification in logs:

```go
func (uc *UserUsecase) CreateUser(ctx context.Context, req *dto.CreateUserRequest) (*dto.UserResponse, error) {
    logger := ctx.Value(middleware.LoggerKey).(*slog.Logger)

    user, err := entity.NewUser(userID, req.Name)
    if err != nil {
        // Extract error code if available
        var codeErr interface{ ErrorCode() ErrorCode }
        var errorCode string
        if errors.As(err, &codeErr) {
            errorCode = codeErr.ErrorCode().String()
        }
        
        logger.WarnContext(ctx, "User creation failed",
            slog.Any("error", err),
            slog.String("error_code", errorCode),  // ← Log error code
            slog.String("username", req.Username))
        
        return nil, &apperror.ValidationFailedError{
            Code: apperror.CodeValidationFailed,
            Errors: []apperror.FieldError{
                {Field: "user", Message: err.Error(), Code: errorCode},
            },
        }
    }
    // ...
}
```

**HTTP Response with Error Codes:**

```go
package error

import (
    "time"
)

type HTTPError struct {
    StatusCode int                    `json:"-"`
    Code       string                 `json:"code"`          // e.g., "APP_RES_001"
    Message    string                 `json:"message"`
    Details    map[string]interface{} `json:"details,omitempty"`
    RequestID  string                 `json:"request_id,omitempty"`
    Timestamp  time.Time              `json:"timestamp"`     // For tracking
}

// Example JSON response:
// {
//   "code": "APP_RES_001",
//   "message": "Repository not found",
//   "request_id": "550e8400-e29b-41d4-a716-446655440000",
//   "timestamp": "2025-11-05T10:30:00Z",
//   "details": {
//     "resource_type": "Repository",
//     "resource_id": "invalid-id"
//   }
// }
```

**Error Code Documentation Generation:**

Generate documentation from the registry:

```go
// cmd/tools/generate_error_docs.go
func main() {
    f, _ := os.Create("docs/error-codes.md")
    defer f.Close()
    
    fmt.Fprintln(f, "# Error Code Reference")
    fmt.Fprintln(f, "")
    fmt.Fprintln(f, "## Error Codes")
    fmt.Fprintln(f, "")
    fmt.Fprintln(f, "| Code | Layer | Category | Description | Severity | Retryable |")
    fmt.Fprintln(f, "|------|-------|----------|-------------|----------|-----------|")
    
    for _, info := range error.ErrorCodeRegistry {
        fmt.Fprintf(f, "| %s | %s | %s | %s | %s | %v |\n",
            info.Code, info.Layer, info.Category, info.Description, info.Severity, info.Retryable)
    }
}
```

**Benefits:**

* **Quick Identification:** Error code in logs immediately tells you the layer and category
* **Monitoring:** Error codes can be aggregated and monitored (e.g., alert on high frequency of `INF_DB_001`)
* **Documentation:** Centralized registry serves as error documentation
* **Client Integration:** API clients can handle specific error codes programmatically
* **Debugging:** Searching logs by error code finds all occurrences of that specific error type

#### 4.2 Message Internationalization (Future Consideration)

For now, use English messages. Structure code to support future i18n:

```go
type ErrorCode string

const (
    ErrCodeInvalidInput ErrorCode = "DOM_VAL_001"
    // ... more codes
)

// Future: Load from resource bundle
func (code ErrorCode) Message(locale string) string {
    // Load from i18n resource
    return "Invalid input" // Default English
}
```

#### 4.3 User vs Developer Messages

* **User Messages:** Simple, non-technical, actionable.
* **Developer Messages:** Include technical details, stack traces, error codes.

```go
type DetailedError struct {
    UserMessage      string // "The repository URL is invalid"
    DeveloperMessage string // "Repository URL validation failed: scheme must be https"
    ErrorCode        string // "DOM_VAL_001"
    Details          map[string]interface{}
}
```

### 5. Testing Strategy (Integration with ADR 0009)

#### 5.1 Unit Testing Custom Errors

```go
func TestValidationError_Error(t *testing.T) {
    err := &error.ValidationError{
        Field:   "email",
        Value:   "invalid-email",
        Message: "must be a valid email address",
    }

    expected := "validation failed for field 'email': must be a valid email address"
    assert.Equal(t, expected, err.Error())
}

func TestValidationError_Is(t *testing.T) {
    err := &error.ValidationError{Field: "name", Message: "required"}
    assert.ErrorIs(t, err, error.ErrInvalidEntity)
}
```

#### 5.2 Testing Error Handling

```go
func TestUserUsecase_CreateUser_ValidationError(t *testing.T) {
    mockRepo := new(MockUserRepository)
    usecase := NewUserUsecase(mockRepo)

    // Test with invalid input
    _, err := usecase.CreateUser(context.Background(), &dto.CreateUserRequest{
        Username: "", // Invalid: empty username
    })

    // Assert error type
    var validationErr *apperror.ValidationFailedError
    assert.ErrorAs(t, err, &validationErr)
    assert.Len(t, validationErr.Errors, 1)
    assert.Equal(t, "username", validationErr.Errors[0].Field)
}
```

#### 5.3 Testing Error Propagation

```go
func TestRepositoryHandler_GetRepository_NotFound(t *testing.T) {
    mockUsecase := new(MockRepositoryUsecase)
    handler := NewRepositoryHandler(mockUsecase)

    // Setup mock to return NotFoundError
    mockUsecase.On("GetRepository", mock.Anything, "non-existent-id").
        Return(nil, &apperror.NotFoundError{
            ResourceType: "Repository",
            ResourceID:   "non-existent-id",
        })

    // Create test request
    req := httptest.NewRequest(http.MethodGet, "/repositories?id=non-existent-id", nil)
    w := httptest.NewRecorder()

    // Execute handler
    handler.GetRepository(w, req)

    // Assert HTTP response
    assert.Equal(t, http.StatusNotFound, w.Code)

    var httpErr error.HTTPError
    json.NewDecoder(w.Body).Decode(&httpErr)
    assert.Equal(t, "NOT_FOUND", httpErr.Code)
}
```

### 6. Implementation Guidelines

#### 6.1 Creating New Custom Errors

1. Identify the appropriate layer for the error.
2. Define the error struct with relevant fields.
3. Implement `Error() string` method.
4. Implement `Is()` or `As()` if needed for sentinel comparison.
5. Implement `Unwrap()` if wrapping another error.
6. Add error code constant.
7. Write unit tests for the error type.

#### 6.2 Error Conversion at Layer Boundaries

```go
// Infrastructure -> Application
func (r *PostgresUserRepository) FindByID(ctx context.Context, id entity.UserID) (*entity.User, error) {
    // ... GORM query ...
    if errors.Is(err, gorm.ErrRecordNotFound) {
        // Convert to nil (application layer interprets as not found)
        return nil, nil
    }
    if err != nil {
        // Wrap as infrastructure error
        return nil, &infraerror.DatabaseError{
            Operation: "FindByID",
            Table:     "users",
            Cause:     err,
        }
    }
    // ...
}

// Application -> Interfaces
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.usecase.GetUser(r.Context(), userID)
    if err != nil {
        // Map to HTTP error
        httpErr := interror.MapToHTTPError(err, requestID)
        httpErr.WriteJSON(w)
        return
    }
    // ...
}
```

### 7. Migration Strategy

#### 7.1 Phase 1: Create Error Packages

* Create `error/` package in each layer of each context.
* Define common error types (NotFound, Validation, etc.).
* Implement error mapping utilities.

#### 7.2 Phase 2: Update New Code

* All new code must use custom errors.
* New handlers must use error mapping.

#### 7.3 Phase 3: Refactor Existing Code

* Gradually replace generic errors with custom errors.
* Update tests to assert on custom error types.
* Prioritize critical paths and frequently failing scenarios.

## Consequences

### Pros

* **Improved Debugging:** Structured error information with error codes and context makes debugging faster and more efficient.
* **Consistent Error Handling:** Unified error handling strategy across all layers reduces cognitive load and improves maintainability.
* **Better API Design:** Clean error responses with appropriate HTTP status codes improve API usability.
* **Enhanced Observability:** Structured errors integrate well with logging (ADR 0008) and monitoring systems.
* **Type Safety:** Using custom error types enables type-safe error handling with `errors.Is` and `errors.As`.
* **Testability:** Well-defined error types make it easier to test error scenarios and error propagation.
* **Separation of Concerns:** Layer-specific errors maintain clean architecture boundaries.

### Cons

* **Initial Development Overhead:** Creating custom error types for each scenario requires additional development time.
* **Learning Curve:** Team members need to understand the error hierarchy and when to use which error type.
* **Boilerplate Code:** More code is needed for error definition and mapping compared to simple string errors.
* **Maintenance Burden:** Error types and codes need to be maintained and documented as the system evolves.
* **Over-Engineering Risk:** For simple applications, this approach might be unnecessarily complex.

### Mitigation Strategies

* Provide code templates and generators for common error types.
* Create comprehensive documentation with examples.
* Establish code review guidelines for error handling.
* Use shared base error types to reduce boilerplate.
* Start with essential error types and expand as needed.

## Related ADRs

* **ADR 0007:** Backend Architecture - Onion Architecture (defines layer structure)
* **ADR 0008:** Backend Logging Strategy (error logging integration)
* **ADR 0009:** Backend Testing Strategy (error testing approaches)

## References

* [Go Blog: Error handling and Go](https://go.dev/blog/error-handling-and-go)
* [Go Blog: Working with Errors in Go 1.13](https://go.dev/blog/go1.13-errors)
* [Effective Go: Errors](https://go.dev/doc/effective_go#errors)
* [Dave Cheney: Don't just check errors, handle them gracefully](https://dave.cheney.net/2016/04/27/dont-just-check-errors-handle-them-gracefully)
