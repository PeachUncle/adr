# ADR-0005: Error Handling Pattern

**Status**: ✅ Accepted  
**Date**: 2025-11-10  
**Deciders**: Backend Team  
**Tags**: error-handling, middleware, express, monitoring

---

## Context and Problem Statement

We need a consistent error handling pattern across the backend API that provides meaningful error messages to clients, logs errors for debugging, integrates with monitoring services, and doesn't expose sensitive information.

## Decision Drivers

- **Consistency**: Uniform error response format
- **Security**: Don't expose stack traces in production
- **Logging**: Capture errors for debugging
- **Monitoring**: Integration with Sentry
- **User Experience**: Meaningful error messages
- **Developer Experience**: Easy to use pattern

## Considered Options

### Option 1: Centralized Error Handler Middleware ✅ SELECTED
**Pros**:
- ✅ Single source of truth for errors
- ✅ Consistent response format
- ✅ Easy logging integration
- ✅ Security: Filter sensitive data

**Cons**:
- ⚠️ Must use next(error) in routes

---

### Option 2: Try-Catch in Every Route
**Pros**:
- ✅ Explicit error handling
- ✅ Route-specific logic

**Cons**:
- ❌ Code duplication
- ❌ Inconsistent formats
- ❌ Easy to forget

---

### Option 3: Error Classes with Inheritance
**Pros**:
- ✅ Type-safe errors
- ✅ Custom error types

**Cons**:
- ⚠️ More boilerplate
- ⚠️ Requires custom class per error

---

## Decision Outcome

**Chosen Option**: Centralized Error Handler Middleware (Option 1)

### Rationale

1. **Single Handler**: All errors flow through one middleware
2. **Consistent Format**: Uniform JSON response structure
3. **Security**: Filter stack traces in production
4. **Logging**: Automatic error logging with context
5. **Monitoring**: Automatic Sentry integration
6. **Simplicity**: Easy for team to use (just throw/next)

### Implementation

**Error Handler Middleware**:
```typescript
// src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';
import { logger } from '../config/logger';
import * as Sentry from '@sentry/node';

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Log error with context
  logger.error({
    err,
    req: {
      method: req.method,
      url: req.url,
      body: req.body,
      userId: req.session?.user?.id,
    },
  }, 'Request error');
  
  // Send to Sentry
  Sentry.captureException(err, {
    user: { id: req.session?.user?.id },
    extra: { url: req.url, method: req.method },
  });
  
  // Determine status code
  const statusCode = (err as any).statusCode || 500;
  
  // Security: Don't expose stack trace in production
  const errorResponse = {
    success: false,
    error: err.message || 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  };
  
  res.status(statusCode).json(errorResponse);
};
```

**Usage in Routes**:
```typescript
// Async/await with try-catch
router.get('/notes', requireAuth, async (req, res, next) => {
  try {
    const notes = await prisma.note.findMany({
      where: { userId: req.session.user!.id },
    });
    res.json({ success: true, data: notes });
  } catch (error) {
    next(error); // Pass to error handler
  }
});

// Or use express-async-errors (auto-catch)
import 'express-async-errors';

router.get('/notes', requireAuth, async (req, res) => {
  // No try-catch needed - errors auto-caught
  const notes = await prisma.note.findMany({
    where: { userId: req.session.user!.id },
  });
  res.json({ success: true, data: notes });
});
```

**Custom Error Classes** (Optional):
```typescript
// src/utils/errors.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = 'Resource not found') {
    super(message, 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401);
  }
}

export class ValidationError extends AppError {
  constructor(message: string = 'Validation failed') {
    super(message, 400);
  }
}

// Usage
throw new NotFoundError('Note not found');
throw new ValidationError('Invalid email format');
```

## Error Response Format

### Standard Format

```json
{
  "success": false,
  "error": "Note not found"
}
```

### Development (with stack trace)

```json
{
  "success": false,
  "error": "Note not found",
  "stack": "Error: Note not found\n    at ..."
}
```

### Validation Errors

```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "email": "Invalid email format",
    "password": "Password too short"
  }
}
```

## Consequences

### Positive

✅ **Consistent responses** - All errors same format  
✅ **Automatic logging** - All errors logged with context  
✅ **Security** - Stack traces hidden in production  
✅ **Monitoring** - Automatic Sentry integration  
✅ **Maintainability** - Single place to update error handling  
✅ **Developer experience** - Just throw/next(error)  

### Negative

⚠️ **Must remember next()** - Easy to forget in async routes  
⚠️ **Generic errors** - May need custom error classes for specificity  

## Validation

✅ **All errors logged**  
✅ **All errors sent to Sentry**  
✅ **No stack traces in production responses**  
✅ **Consistent error format across endpoints**  
✅ **Status codes correct (400, 401, 404, 500)**  

## Best Practices

### 1. Use Specific Status Codes

```typescript
// 400: Bad Request (client error)
res.status(400).json({ success: false, error: 'Invalid input' });

// 401: Unauthorized (not authenticated)
res.status(401).json({ success: false, error: 'Authentication required' });

// 403: Forbidden (authenticated but not authorized)
res.status(403).json({ success: false, error: 'Access denied' });

// 404: Not Found
res.status(404).json({ success: false, error: 'Note not found' });

// 500: Internal Server Error (server error)
res.status(500).json({ success: false, error: 'Server error' });
```

### 2. Don't Expose Sensitive Info

```typescript
// ❌ Bad: Exposes database structure
throw new Error('Duplicate key violation on users.email_unique');

// ✅ Good: Generic user-friendly message
throw new Error('Email already registered');
```

### 3. Include Context in Logs

```typescript
logger.error({
  err,
  userId: req.session.user?.id,
  noteId: req.params.id,
  action: 'delete_note',
}, 'Failed to delete note');
```

### 4. Validation Errors

```typescript
// Use Zod for validation
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

try {
  const data = schema.parse(req.body);
} catch (error) {
  if (error instanceof z.ZodError) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: error.errors,
    });
  }
  throw error;
}
```

## Monitoring

### Sentry Integration

```typescript
// Automatically captures unhandled errors
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
});

// Errors in errorHandler auto-sent to Sentry
```

### Error Metrics

Track in monitoring dashboard:
- Total errors per hour
- Errors by endpoint
- Errors by user
- Error rate (%)
- Most common errors

## References

- [Express Error Handling](https://expressjs.com/en/guide/error-handling.html)
- [Sentry Node.js](https://docs.sentry.io/platforms/node/)
- Internal: `src/middleware/errorHandler.ts`, `src/utils/errors.ts`

## Related ADRs

- [ADR-0001: Express Choice](./0001-express-choice.md) - Error middleware
- [ADR-0004: Logging Framework](./0004-logging-framework.md) - Error logging

---

**Last Updated**: December 13, 2025  
**Review Date**: June 2026
