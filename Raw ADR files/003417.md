# ADR-002: API Design Decisions (RFC 7807 Problem Details)

**Status:** Accepted  
**Date:** 2025-01-27  
**Deciders:** Architecture Team

## Context

AIDevelo.ai API needed a standardized error response format that:
- Provides consistent error structure across all endpoints
- Includes sufficient context for debugging
- Follows industry standards
- Supports both production and debug modes

## Decision

We adopted **RFC 7807 Problem Details for HTTP APIs** as the standard error response format.

## Rationale

### Advantages

1. **Industry Standard**
   - RFC 7807 is a recognized standard for HTTP API error responses
   - Well-documented and understood by API consumers
   - Tooling support available

2. **Structured Error Information**
   - `type`: URI identifying the error type
   - `title`: Human-readable summary
   - `status`: HTTP status code
   - `detail`: Detailed error message
   - `instance`: URI of the specific occurrence

3. **Extensibility**
   - Can add custom fields (e.g., `code`, `validation-errors`, `debug`)
   - Supports different error types (validation, authentication, etc.)

4. **Debug Mode Support**
   - Can include stack traces and detailed debugging info in debug mode
   - Sanitized responses in production

### Implementation

**Error Handler:** `server/src/middleware/errorHandler.ts`

```typescript
interface ProblemDetails {
  type?: string; // URI reference
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  [key: string]: unknown; // Extension members
}
```

**Content-Type:** `application/problem+json`

**Error Types:**
- `/errors/validation` - Validation errors (422)
- `/errors/unauthorized` - Authentication errors (401)
- `/errors/forbidden` - Authorization errors (403)
- `/errors/not-found` - Resource not found (404)
- `/errors/internal-server-error` - Server errors (500)

## Alternatives Considered

1. **Custom Error Format**
   - `{ success: false, error: {...} }`
   - Not standardized
   - Would require custom client handling

2. **Simple HTTP Status + Message**
   - Too minimal
   - Lacks context and structure
   - Hard to debug

## Consequences

- **Positive:**
  - Consistent error format across all endpoints
  - Better developer experience
  - Easier error tracking and monitoring
  - Standard compliance

- **Negative:**
  - Slightly more verbose than simple error messages
  - Requires error handler middleware
  - All endpoints must use error middleware pattern

## Implementation Status

- ✅ Error handler implements RFC 7807
- ✅ All endpoints use error middleware
- ✅ Debug mode support implemented
- ✅ Request ID correlation for error tracking

## References

- [RFC 7807 Specification](https://tools.ietf.org/html/rfc7807)
- [Error Handler Implementation](server/src/middleware/errorHandler.ts)
