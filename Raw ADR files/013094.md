# ADR-010: HTTP Error Handling Standard

## Status
Proposed

## Context
The system needs a consistent, standards-based approach to HTTP error handling that provides clear, actionable information to API clients while maintaining security and usability. After evaluating various industry standards, we choose to adopt RFC 7807 - Problem Details for HTTP APIs as our error response format.

## Decision

### 1. Error Response Format
We will implement RFC 7807 using the following structure:

```json
{
  "type": "https://openk.dev/errors/{category}",
  "title": "Human-readable summary",
  "status": 400,
  "detail": "Detailed human-readable explanation",
  "instance": "/api/v1/resource/identifier",
  "extensions": {}  // Optional additional context
}
```

### 2. Core Fields
| Field | Purpose | Example |
|-------|---------|---------|
| type | URI identifying error category | "https://openk.dev/errors/validation" |
| title | Short, human-readable summary | "Invalid Username Format" |
| status | HTTP status code | 400 |
| detail | Specific error explanation | "Username contains invalid characters" |
| instance | URI of error occurrence | "/api/v1/derivation/params" |

### 3. Error Categories and Types
Base URI: https://openk.dev/errors/

| Category | URI Suffix | Usage |
|----------|------------|-------|
| validation | /validation | Input validation errors |
| auth | /auth | Authentication/authorization errors |
| notfound | /not-found | Resource not found |
| internal | /internal | Server errors |
| conflict | /conflict | Resource conflicts |

### 4. HTTP Status Code Mapping
| Scenario | Status | Type Suffix | Example Title |
|----------|--------|-------------|---------------|
| Validation Error | 400 | validation | "Invalid Request Format" |
| Not Found | 404 | not-found | "Resource Not Found" |
| Server Error | 500 | internal | "Internal Server Error" |
| Conflict | 409 | conflict | "Resource Already Exists" |

### 5. Extensions
Each error category may include additional context in the extensions field:

#### Validation Errors
```json
{
  "type": "https://openk.dev/errors/validation",
  "title": "Invalid Username Format",
  "status": 400,
  "detail": "Username contains invalid characters",
  "instance": "/api/v1/derivation/params",
  "validationErrors": [{
    "field": "username",
    "constraint": "alphanumeric",
    "value": "test@user"
  }]
}
```

#### Not Found Errors
```json
{
  "type": "https://openk.dev/errors/not-found",
  "title": "Derivation Parameters Not Found",
  "status": 404,
  "detail": "No derivation parameters found for username 'testuser'",
  "instance": "/api/v1/derivation/params/testuser",
  "resource": {
    "type": "derivation_params",
    "identifier": "testuser"
  }
}
```

#### Server Errors
```json
{
  "type": "https://openk.dev/errors/internal",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "The server encountered an error while processing the request",
  "instance": "/api/v1/derivation/params",
  "traceId": "abcdef123456"
}
```

### 6. Security Considerations
- Internal error details must never be exposed in responses
- Stack traces must never be included
- Sensitive data must be sanitized from error responses
- Validation errors may include submitted values only if they don't contain sensitive data
- TraceIDs should be provided for internal errors to aid debugging while maintaining security

## Consequences

### Positive
- Standards-based approach using RFC 7807
- Consistent error format across all endpoints
- Machine-readable for automated handling
- Human-readable for debugging
- Extensible for specific error types
- Clear security boundaries

### Negative
- More verbose than simple error messages
- Requires careful handling of sensitive data
- Need to maintain error type documentation

## Implementation Notes
1. Create centralized error handling package
2. Implement middleware for consistent error formatting
3. Define strongly typed error structures
4. Create error response helpers
5. Add error handling tests

## References
- RFC 7807 - Problem Details for HTTP APIs (https://tools.ietf.org/html/rfc7807)
