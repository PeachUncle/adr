# ADR-004: Error Handling Strategy

**Status:** Accepted  
**Date:** 2025-01-27  
**Deciders:** Architecture Team

## Context

AIDevelo.ai needed a comprehensive error handling strategy that:
- Provides consistent error responses
- Enables effective debugging
- Prevents information leakage in production
- Supports error tracking and monitoring
- Handles both operational and unexpected errors

## Decision

We implemented a **multi-layered error handling strategy**:

1. **Error Classes Hierarchy** - Custom error classes for different error types
2. **Error Middleware** - Centralized error handling with RFC 7807 format
3. **Structured Logging** - JSON-formatted logs with context
4. **Error Tracking** - Sentry integration for production monitoring
5. **Debug Mode** - Gated debug information for troubleshooting

## Rationale

### Error Classes

**Custom Error Classes** (`server/src/utils/errors.ts`):
- `AppError` - Base class for operational errors
- `ValidationError` - Input validation failures (422)
- `BadRequestError` - Invalid requests (400)
- `UnauthorizedError` - Authentication failures (401)
- `ForbiddenError` - Authorization failures (403)
- `NotFoundError` - Resource not found (404)
- `InternalServerError` - Unexpected errors (500)

**Benefits:**
- Type-safe error handling
- Consistent error structure
- Easy to extend with new error types

### Error Middleware Pattern

**Pattern:** All controllers use `next(error)` instead of direct responses

```typescript
// ✅ Good
try {
  // ... logic
  if (!resource) {
    return next(new NotFoundError('Resource not found'));
  }
  res.json({ success: true, data: resource });
} catch (error) {
  next(error instanceof Error ? error : new InternalServerError(String(error)));
}

// ❌ Bad
return res.status(404).json({ error: 'Not found' });
```

**Benefits:**
- Centralized error formatting
- Consistent error responses
- Easy to add error tracking/logging

### Structured Logging

**StructuredLoggingService** provides:
- JSON-formatted logs
- Request correlation (requestId)
- User context (userId, orgId)
- Error stack traces (truncated)

**Benefits:**
- Machine-readable logs
- Easy log aggregation
- Better debugging with context

### Error Tracking (Sentry)

**Integration:**
- Automatic error capture
- Performance monitoring
- Release tracking
- Error grouping and fingerprinting

**Benefits:**
- Real-time error alerts
- Error trends and patterns
- Production error visibility

### Debug Mode

**Gated Debug Information:**
- Header-based: `x-aidevelo-debug` with shared secret
- Environment-based: `DEBUG_ERRORS=true`
- Includes stack traces, error details, validation errors

**Benefits:**
- Safe debugging in production
- No information leakage to unauthorized users
- Flexible debugging options

## Alternatives Considered

1. **Simple Try-Catch with Direct Responses**
   - Inconsistent error formats
   - Hard to track and monitor
   - No centralized error handling

2. **Error Codes Only**
   - Lacks context
   - Hard to debug
   - Poor developer experience

3. **Always Show Stack Traces**
   - Security risk in production
   - Information leakage
   - Not suitable for production

## Consequences

- **Positive:**
  - Consistent error handling across codebase
  - Better debugging capabilities
  - Production-safe error responses
  - Error tracking and monitoring
  - Easy to extend

- **Negative:**
  - Requires discipline to use `next(error)` pattern
  - Slightly more verbose than direct responses
  - Need to migrate existing code to new pattern

## Implementation Status

- ✅ Error classes defined
- ✅ Error middleware implemented (RFC 7807)
- ✅ Structured logging service
- ✅ Sentry integration
- ✅ Debug mode support
- ⚠️ Some controllers still need migration to `next(error)` pattern

## Best Practices

1. **Always use `next(error)` in controllers**
2. **Use appropriate error class** (NotFoundError, ValidationError, etc.)
3. **Include context in errors** (step, requestId)
4. **Log errors with StructuredLoggingService**
5. **Never log sensitive data** (passwords, tokens, PII)

## References

- [Error Handling Guide](docs/ERROR_HANDLING_GUIDE.md)
- [Error Analysis](docs/ERROR_ANALYSIS.md)
- [Error Handler Implementation](server/src/middleware/errorHandler.ts)
