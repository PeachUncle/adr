# ADR-004: Error Handling and Exception Patterns

## Status

**Accepted** - 2026-01-07

## Context

Luminote interacts with multiple external systems (web pages, AI provider APIs)
and must handle various failure modes gracefully. Users need clear, actionable
error messages without exposing sensitive information or overwhelming them with
technical details.

Key challenges:

- External APIs have different error formats
- Network failures can occur at any step
- Rate limits must be communicated clearly
- Invalid user input needs validation
- Debugging requires detailed logs, but users need simple messages
- Errors during streaming require special handling

We need an error handling strategy that:

- Provides consistent error structure across the application
- Maps errors to appropriate HTTP status codes
- Gives users actionable guidance
- Logs sufficient detail for debugging
- Works well with FastAPI and SvelteKit
- Is easy for GitHub Copilot to follow and extend

## Decision

We will implement a **layered error handling system** with custom exceptions,
centralized error handling, and user-friendly error messages.

### Error Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│  (Toast notifications, error modals, inline warnings)      │
├─────────────────────────────────────────────────────────────┤
│                  Frontend Error Handler                     │
│  (Catches API errors, maps to user messages)               │
├─────────────────────────────────────────────────────────────┤
│                        API Layer                            │
│  (Returns structured error responses)                       │
├─────────────────────────────────────────────────────────────┤
│                Backend Exception Handler                    │
│  (Catches exceptions, logs, converts to HTTP responses)    │
├─────────────────────────────────────────────────────────────┤
│                   Business Logic Layer                      │
│  (Raises custom exceptions with context)                   │
├─────────────────────────────────────────────────────────────┤
│                  External Services                          │
│  (Web scraping, AI APIs)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Backend Exception Hierarchy

```python
# backend/app/core/errors.py

class LuminoteException(Exception):
    """Base exception for all Luminote errors"""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: dict | None = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

# Client errors (4xx)
class ClientError(LuminoteException):
    """Base class for client errors"""
    def __init__(self, message: str, code: str, details: dict | None = None):
        super().__init__(message, code, status_code=400, details=details)

class InvalidURLError(ClientError):
    """Invalid URL format"""
    def __init__(self, url: str):
        super().__init__(
            message=f"Invalid URL format: {url}",
            code="INVALID_URL",
            details={"url": url}
        )

class ValidationError(ClientError):
    """Request validation failed"""
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            code="VALIDATION_ERROR",
            details={"field": field, "reason": reason}
        )

class AuthenticationError(LuminoteException):
    """Authentication/authorization failed"""
    def __init__(self, provider: str, reason: str = ""):
        super().__init__(
            message=f"Authentication failed for {provider}: {reason}",
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details={"provider": provider}
        )

# Server errors (5xx)
class ServiceError(LuminoteException):
    """Base class for service errors"""
    def __init__(self, message: str, code: str, details: dict | None = None):
        super().__init__(message, code, status_code=500, details=details)

class ExternalServiceError(ServiceError):
    """External service (AI API, website) failed"""
    def __init__(self, service: str, reason: str):
        super().__init__(
            message=f"External service '{service}' failed: {reason}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "reason": reason}
        )

class ExtractionError(LuminoteException):
    """Content extraction failed"""
    def __init__(self, url: str, reason: str):
        super().__init__(
            message=f"Failed to extract content from {url}: {reason}",
            code="EXTRACTION_ERROR",
            status_code=422,
            details={"url": url, "reason": reason}
        )

# Rate limiting (429)
class RateLimitError(LuminoteException):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int, provider: str | None = None):
        message = f"Rate limit exceeded. Retry after {retry_after} seconds."
        if provider:
            message += f" (Provider: {provider})"
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after, "provider": provider}
        )

# Specific errors
class TranslationError(ServiceError):
    """Translation failed"""
    def __init__(self, provider: str, model: str, reason: str):
        super().__init__(
            message=f"Translation failed using {provider}/{model}: {reason}",
            code="TRANSLATION_ERROR",
            details={"provider": provider, "model": model, "reason": reason}
        )

class ContentTooLargeError(ClientError):
    """Content exceeds size limit"""
    def __init__(self, size: int, max_size: int):
        super().__init__(
            message=f"Content size ({size} bytes) exceeds limit ({max_size} bytes)",
            code="CONTENT_TOO_LARGE",
            details={"size": size, "max_size": max_size}
        )

class QuotaExceededError(AuthenticationError):
    """API quota exceeded"""
    def __init__(self, provider: str):
        super().__init__(
            provider=provider,
            reason="API quota exhausted"
        )
        self.code = "QUOTA_EXCEEDED"
```

### Exception Handler Middleware

```python
# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.errors import LuminoteException
from app.core.logging import logger
import uuid

app = FastAPI()

@app.exception_handler(LuminoteException)
async def luminote_exception_handler(
    request: Request,
    exc: LuminoteException
) -> JSONResponse:
    """Handle all Luminote exceptions"""

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log error with context
    logger.error(
        f"Error handling request {request_id}",
        extra={
            "request_id": request_id,
            "error_code": exc.code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )

    # Return user-friendly response
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details,
            "request_id": request_id,
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    logger.exception(
        f"Unhandled exception in request {request_id}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        }
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
            "details": {},
            "request_id": request_id,
        }
    )
```

### Frontend Error Handling

```typescript
// src/lib/utils/error-handler.ts

export interface APIError {
  error: string;
  code: string;
  details: Record<string, any>;
  request_id?: string;
}

export interface UserFriendlyError {
  title: string;
  message: string;
  action?: {
    label: string;
    handler: () => void;
  };
  canRetry: boolean;
  severity: 'error' | 'warning' | 'info';
}

const ERROR_MESSAGES: Record<string, UserFriendlyError> = {
  INVALID_URL: {
    title: 'Invalid URL',
    message: 'The URL format is not recognized. Please check and try again.',
    canRetry: true,
    severity: 'error',
  },
  EXTRACTION_ERROR: {
    title: 'Cannot Extract Content',
    message: 'Unable to extract readable content from this page. Try copying and pasting the text instead.',
    action: {
      label: 'Use Paste Mode',
      handler: () => navigateToPasteMode(),
    },
    canRetry: false,
    severity: 'warning',
  },
  AUTHENTICATION_ERROR: {
    title: 'API Key Invalid',
    message: 'Your API key is invalid or has expired. Please check your configuration.',
    action: {
      label: 'Update Settings',
      handler: () => openSettings(),
    },
    canRetry: false,
    severity: 'error',
  },
  RATE_LIMIT_EXCEEDED: {
    title: 'Rate Limit Reached',
    message: 'Too many requests. Please wait a moment before trying again.',
    canRetry: true,
    severity: 'warning',
  },
  QUOTA_EXCEEDED: {
    title: 'API Quota Exhausted',
    message: 'Your API quota has been exhausted. Please upgrade your account or wait for reset.',
    action: {
      label: 'Check Provider',
      handler: () => openProviderAccount(),
    },
    canRetry: false,
    severity: 'error',
  },
  TRANSLATION_ERROR: {
    title: 'Translation Failed',
    message: 'Failed to translate content. This may be a temporary issue with the AI provider.',
    canRetry: true,
    severity: 'error',
  },
  CONTENT_TOO_LARGE: {
    title: 'Content Too Large',
    message: 'The content is too large to process. Try translating a smaller section.',
    canRetry: false,
    severity: 'warning',
  },
};

export class ErrorHandler {
  static handleAPIError(error: APIError): UserFriendlyError {
    const userError = ERROR_MESSAGES[error.code];

    if (!userError) {
      return {
        title: 'Error',
        message: error.error || 'An unexpected error occurred',
        canRetry: true,
        severity: 'error',
      };
    }

    // Add details to message if available
    if (error.details.retry_after) {
      userError.message += ` Please wait ${error.details.retry_after} seconds.`;
    }

    return userError;
  }

  static async handleStreamError(
    error: Error,
    onRetry?: () => Promise<void>
  ): Promise<void> {
    const userError = this.handleAPIError(error as APIError);

    // Show toast notification
    await showErrorToast(userError);

    // Log for debugging
    console.error('Stream error:', error);

    // Offer retry if applicable
    if (userError.canRetry && onRetry) {
      await onRetry();
    }
  }
}

// Error toast component
export async function showErrorToast(error: UserFriendlyError): Promise<void> {
  // Implementation depends on UI library
  toast.error(error.message, {
    title: error.title,
    action: error.action,
  });
}
```

### Error Response Format

**Standard Error Response:**

```json
{
  "error": "Failed to extract content from https://example.com: Host unreachable",
  "code": "EXTRACTION_ERROR",
  "details": {
    "url": "https://example.com",
    "reason": "Host unreachable"
  },
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Validation Error:**

```json
{
  "error": "Validation failed for field 'target_language': Must be ISO 639-1 code",
  "code": "VALIDATION_ERROR",
  "details": {
    "field": "target_language",
    "reason": "Must be ISO 639-1 code"
  },
  "request_id": "..."
}
```

**Rate Limit Error:**

```json
{
  "error": "Rate limit exceeded. Retry after 60 seconds. (Provider: openai)",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "retry_after": 60,
    "provider": "openai"
  },
  "request_id": "..."
}
```

## Consequences

### Positive

- **Consistency**: All errors follow the same structure
- **User-Friendly**: Clear messages with actionable guidance
- **Debuggable**: Request IDs link frontend errors to backend logs
- **Type-Safe**: Custom exceptions carry structured data
- **Extensible**: Easy to add new error types
- **Copilot-Friendly**: Clear patterns for raising and handling errors

### Negative

- **Verbosity**: Custom exception classes add boilerplate
- **Maintenance**: Error messages need to be kept up-to-date
- **Localization**: Error messages hardcoded in English (can be addressed later)

### Trade-offs

- Chose custom exceptions over error codes for better type safety
- Chose centralized handler over per-route handling for consistency
- Chose detailed logging over minimal logs for better debugging
- Chose user-friendly messages over technical accuracy for better UX

## Alternatives Considered

### 1. HTTP Status Codes Only

**Pros:**

- Simple
- Standard
- Less code

**Cons:**

- Not enough granularity
- Can't provide actionable guidance
- Hard to distinguish error types

**Verdict:** Rejected - Insufficient detail for good UX

### 2. Error Codes as Strings

```python
return {"error": "INVALID_URL", "message": "..."}
```

**Pros:**

- Simple
- Easy to match in frontend

**Cons:**

- No type safety
- No exception hierarchy
- Harder to carry context

**Verdict:** Rejected - Less type-safe than custom exceptions

### 3. Problem Details (RFC 7807)

```json
{
  "type": "https://luminote.app/errors/invalid-url",
  "title": "Invalid URL",
  "status": 400,
  "detail": "...",
  "instance": "/api/v1/extract"
}
```

**Pros:**

- Standard format
- Extensible
- Machine-readable

**Cons:**

- More complex
- Requires type registry
- Overkill for our use case

**Verdict:** Rejected - Too complex for our needs

### 4. GraphQL-Style Errors

```json
{
  "data": null,
  "errors": [
    {
      "message": "...",
      "extensions": { "code": "..." }
    }
  ]
}
```

**Pros:**

- Handles partial failures
- Rich error structure

**Cons:**

- Designed for GraphQL
- Doesn't match REST semantics
- More complex parsing

**Verdict:** Rejected - We're using REST, not GraphQL

## Implementation Notes

### For GitHub Copilot

When implementing error handling:

1. **Always raise specific exceptions:**

```python
# Good
raise InvalidURLError(url)

# Bad
raise Exception("Invalid URL")
```

1. **Catch specific exceptions first:**

```python
try:
    extract_content(url)
except InvalidURLError as e:
    # Handle invalid URL
except ExtractionError as e:
    # Handle extraction failure
except LuminoteException as e:
    # Handle other Luminote errors
except Exception as e:
    # Handle unexpected errors
```

1. **Include context in exceptions:**

```python
try:
    translate(text)
except requests.HTTPError as e:
    if e.response.status_code == 429:
        retry_after = int(e.response.headers.get('Retry-After', 60))
        raise RateLimitError(retry_after, provider="openai")
```

1. **Log before raising (if needed):**

```python
try:
    result = external_api_call()
except Exception as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise ExternalServiceError("openai", str(e))
```

### Validation Pattern

```python
from pydantic import BaseModel, validator

class TranslationRequest(BaseModel):
    url: str
    target_language: str

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @validator('target_language')
    def validate_language(cls, v):
        if len(v) != 2:
            raise ValueError('Must be ISO 639-1 code (2 letters)')
        return v.lower()
```

### Testing Error Handling

```python
# tests/api/test_errors.py

def test_invalid_url_error(client):
    response = client.post(
        "/api/v1/extract",
        json={"url": "not-a-url"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_URL"
    assert "request_id" in data

def test_rate_limit_error(client, mocker):
    # Mock rate limit
    mocker.patch(
        'app.services.translation_service.translate',
        side_effect=RateLimitError(60, "openai")
    )

    response = client.post("/api/v1/translate", json={...})
    assert response.status_code == 429
    assert response.json()["details"]["retry_after"] == 60
```

### Frontend Error Display

```svelte
<!-- ErrorToast.svelte -->
<script lang="ts">
  import type { UserFriendlyError } from '$lib/utils/error-handler';
  export let error: UserFriendlyError;
</script>

<div class="toast toast-{error.severity}">
  <h4>{error.title}</h4>
  <p>{error.message}</p>
  {#if error.action}
    <button on:click={error.action.handler}>
      {error.action.label}
    </button>
  {/if}
</div>
```

## Error Monitoring

For production, consider adding:

```python
# backend/app/core/monitoring.py

import sentry_sdk

def init_monitoring():
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=0.1,
            before_send=filter_sensitive_data,
        )

def filter_sensitive_data(event, hint):
    # Remove API keys from error reports
    if 'request' in event:
        headers = event['request'].get('headers', {})
        if 'Authorization' in headers:
            headers['Authorization'] = '[FILTERED]'
    return event
```

## References

- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [RFC 7807 - Problem Details](https://tools.ietf.org/html/rfc7807)
- [Feature Specifications - Error Handling](../feature-specifications.md#4-clear-error-handling-for-fetch-failures-invalid-keys-and-rate-limits)

## Changelog

- 2026-01-07: Initial version accepted
