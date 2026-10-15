# 5. Error Handling Conventions

## Status

Accepted

Date: 2025-06-30

## Context

Go's approach to error handling is distinct from many other programming languages, relying on explicit error values 
rather than exceptions. As our services grow in complexity, establishing clear error handling conventions becomes 
essential to ensure:

- Consistent error creation, propagation, and handling across all services
- Preservation of error context and stack traces for effective debugging
- Clear mapping between internal errors and API responses
- Integration with our logging system

Inconsistent error handling approaches lead to several challenges:

- Difficulty tracing the root cause of errors across service boundaries
- Loss of error context during propagation
- Debugging complexity in production environments
- Lack of clarity about which errors should be logged at which levels

## Decision

We will adopt the following error handling conventions for all Go services in our platform:

### 1. Error Types

#### 1.1 Domain-Specific Sentinel Errors

Define package-level sentinel errors for expected error conditions in each domain:

```go
var (
    // ErrCustomerAlreadyExists indicates the customer with the given email already exists
    ErrCustomerAlreadyExists = errors.New("customer already exists")
    // ErrInvalidCredentials indicates the provided credentials are invalid
    ErrInvalidCredentials = errors.New("invalid credentials")
    // ErrInvalidRefreshToken indicates the refresh token is invalid or expired
    ErrInvalidRefreshToken = errors.New("invalid or expired refresh token")
    // ErrTokenMismatch indicates a mismatch between the provided token and expected value
    ErrTokenMismatch = errors.New("token mismatch")
)
```

#### 1.2 Rich Error Types

For errors that need to carry additional context, define custom error types:

```go
// ValidationError represents a validation error with field-specific details
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}
```

### 2. Error Creation and Wrapping

#### 2.1 Creating New Errors

- Use `errors.New()` for simple sentinel errors
- Use `fmt.Errorf()` with `%w` for wrapped errors to preserve the error chain

```go
// Creating new errors
errors.New("simple error message")

// Wrapping errors with context
fmt.Errorf("failed to create customer: %w", err)
```

#### 2.2 Error Wrapping Guidelines

- Always wrap errors when crossing package boundaries
- Add context that explains what operation failed
- Avoid wrapping errors multiple times within the same function
- Preserve the original error type for error checks

```go
// Good: Wrap with context
return fmt.Errorf("fetching customer with ID %s: %w", id, err)

// Avoid: Too many wrappings
// if err := validateInput(input); err != nil {
//   return fmt.Errorf("input validation failed: %w", 
//     fmt.Errorf("customer creation failed: %w", err))
// }
```

### 3. Error Checking and Handling

#### 3.1 Error Type Checks

- Use `errors.Is()` to check against sentinel errors
- Use `errors.As()` to check and extract custom error types

```go
// Checking against sentinel errors
if errors.Is(err, ErrCustomerAlreadyExists) {
    // Handle specific error case
}

// Extracting rich error types
var validationErr *ValidationError
if errors.As(err, &validationErr) {
    // Access validationErr.Field and validationErr.Message
}
```

#### 3.2 Error Handling in Different Layers

- **Repository Layer**: Return domain errors or wrap technical errors
- **Service Layer**: Add business context to errors, perform error translation
- **Handler/API Layer**: Map domain errors to HTTP status codes and API error responses

### 4. Error Logging

#### 4.1 Log Level Guidelines

- Log client errors (400-level) at WARN level
- Log server errors (500-level) at ERROR level
- Include contextual information with logs

```go
if errors.Is(err, ErrCustomerAlreadyExists) {
    logger.Warn("Customer already exists", log.Field{Key: "email", Value: req.Email})
    c.JSON(http.StatusConflict, newErrorResponse(CodeCustomerAlreadyExists, MsgCustomerAlreadyExists))
    return
}
logger.Error("Failed to register customer", err)
```

#### 4.2 Error Context

- Always log the original error object to preserve stack traces
- Include relevant request IDs and parameters (sanitized)
- Never log sensitive information (passwords, tokens, etc.)

### 5. Performance Considerations

- Avoid creating errors in hot paths
- Reuse sentinel errors when appropriate
- Be mindful of string concatenation in error messages
- Consider using error pools for high-throughput services

## Consequences

### Positive

- Consistent error handling and reporting across all services
- Improved error context for more effective debugging
- Clear distinction between expected and unexpected errors
- Better developer experience through standardized patterns
- Simplified error handling in handlers through pattern reuse
- Enhanced integration with our logging system

### Negative

- Potential verbosity in error handling code
- Need for discipline in the following conventions
- Small overhead from error wrapping and context enrichment

### Neutral

- May need periodic updates as Go error handling evolves
- Occasional refactoring of error handling code to maintain consistency

## Implementation Notes

### Example: Complete Error Handling Flow

Below is an example of a complete error handling flow from repository to API response:

```go
// Repository layer
func (r *customerRepository) FindByEmail(ctx context.Context, email string) (*Customer, error) {
    customer, err := r.db.GetCustomerByEmail(ctx, email)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, nil // Not found is not an error in this context
        }
        return nil, fmt.Errorf("finding customer by email %s: %w", email, err)
    }
    return customer, nil
}

// Service layer
func (s *customerService) RegisterCustomer(ctx context.Context, input RegisterCustomerInput) (RegisterCustomerOutput, error) {
    // Check if customer exists
    existing, err := s.repo.FindByEmail(ctx, input.Email)
    if err != nil {
        return RegisterCustomerOutput{}, fmt.Errorf("checking existing customer: %w", err)
    }
    if existing != nil {
        return RegisterCustomerOutput{}, ErrCustomerAlreadyExists
    }

    // Create customer logic...
}

// Handler layer
func (h *Handler) RegisterCustomer(c *gin.Context) {
    ctx := c.Request.Context()
    logger := h.logger.WithContext(ctx)

    // Request binding...

    output, err := h.service.RegisterCustomer(ctx, input)
    if err != nil {
        if errors.Is(err, ErrCustomerAlreadyExists) {
            logger.Warn("Customer already exists", log.Field{Key: "email", Value: req.Email})
            c.JSON(http.StatusConflict, newErrorResponse(CodeCustomerAlreadyExists, MsgCustomerAlreadyExists))
            return
        }
        logger.Error("Failed to register customer", err)
        c.JSON(http.StatusInternalServerError, newErrorResponse(CodeInternalError, MsgInternalError))
        return
    }

    // Success response...
}
```

## Related Documents

- [Logging Conventions](./0004-logging-conventions.md)
- [Interface Design Principles](./0002-interface-design-principles.md)
- [Go Error Handling Best Practices](https://go.dev/blog/go1.13-errors)

## Contributors

- Àlex Grau Roca
