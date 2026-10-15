# 2. Rest API Error Response Format

## Status

Accepted

Date: 2025-06-19

## Context

As our service architecture grows, we need a consistent error handling strategy across all APIs to:

- Provide clear, actionable error information to API consumers
- Enable efficient debugging and troubleshooting
- Support both human and machine readability of errors
- Standardize error responses across services
- Reduce the cognitive load for developers consuming our APIs
- Align with industry best practices for API design

## Decision

We will adopt an error response format based on RFC 7807 (Problem Details for HTTP APIs) with adaptations to fit 
our specific needs. The standard format will be:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": ["Optional array of specific error details"]
}
```

Where:

1. **code** (required): A machine-readable identifier for the error type. This should be:
   - Uppercase with underscores (e.g., `VALIDATION_ERROR`)
   - Specific to the error scenario
   - Consistent across similar errors in different services

2. **message** (required): A human-readable explanation of the error that:
   - Is concise and clear
   - Does not expose sensitive information
   - Uses consistent language across the platform

3. **details** (optional): An array of strings that provides additional context:
   - For validation errors, lists the specific fields with problems
   - For complex errors, provides more granular information
   - Helps guide API consumers toward resolution

## Consequences

### Positive

- Consistent error format improves developer experience
- Machine-readable error codes enable automated handling by clients
- Detailed error messages facilitate easier debugging
- Standardization reduces onboarding time for new developers
- Aligns with modern API design practices
- Clear mapping between HTTP status codes and error types

### Negative

- Needs documentation maintenance to keep error codes standardized
- May increase response size slightly compared to minimal error responses
- Teams need to coordinate on shared error code definitions

### Neutral

- Shifts some error handling complexity from clients to the API
- Requires consideration for internationalization of error messages
- Different clients may use the error structure in different ways

## Implementation Notes

### HTTP Status Codes

Status codes should align with the semantics of the error:

- `400 Bad Request`: Client errors (validation, malformed requests)
- `401 Unauthorized`: Authentication failures
- `403 Forbidden`: Authorization failures
- `404 Not Found`: Resource not found
- `409 Conflict`: Business rule violations (e.g., duplicate resources)
- `422 Unprocessable Entity`: Semantic validation errors
- `500 Internal Server Error`: Unexpected server errors

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid JSON or request format |
| `VALIDATION_ERROR` | 400 | Request failed validation rules |
| `INVALID_CREDENTIALS` | 401 | Authentication failed |
| `UNAUTHORIZED` | 403 | Not authorized to perform action |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `RESOURCE_ALREADY_EXISTS` | 409 | Resource already exists (conflict) |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Related Documents

- [RFC 7807: Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807)
- [OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3)

## Contributors

- Àlex Grau Roca
