# ADR-0006: API Response Format

Date: 2025-01-29

## Status

Accepted

## Context

Our API currently returns raw DTOs directly from controllers without a standardized response wrapper. This approach has several limitations:

1. Inconsistent response structures between success and error cases
2. No standard way to include metadata or pagination information
3. Difficult to add cross-cutting concerns like response versioning or debugging information
4. Error responses don't follow a consistent format across all endpoints

Microsoft's official guidelines recommend:
- Using ProblemDetails (RFC 7807) for error responses
- Supporting content negotiation with JSON as the default format
- Returning appropriate HTTP status codes
- Providing consistent response structures

## Decision

We will implement the following API response standards:

### 1. Use ActionResult<T> for All Controller Actions

Controllers should return `ActionResult<T>` to support both successful responses and error responses with proper HTTP status codes.

### 2. Success Responses

For successful responses, we will return the data directly without a wrapper envelope. This follows Microsoft's recommendation and RESTful principles:

```json
// GET /api/v1/users/123
{
  "id": "123",
  "email": "user@example.com",
  "displayName": "John Doe"
}
```

For collections:
```json
// GET /api/v1/users
[
  {
    "id": "123",
    "email": "user@example.com",
    "displayName": "John Doe"
  }
]
```

### 3. Error Responses Using ProblemDetails

All error responses will use the ProblemDetails format (RFC 7807) which is the Microsoft-recommended standard:

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "traceId": "00-trace-id-00",
  "errors": {
    "Email": ["The Email field is required."],
    "DisplayName": ["Display name must be between 1 and 100 characters."]
  }
}
```

### 4. Standard HTTP Status Codes

- **200 OK**: Successful GET, PUT operations
- **201 Created**: Successful POST creating a new resource
- **204 No Content**: Successful DELETE or operations with no response body
- **400 Bad Request**: Validation errors or malformed requests
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Conflict with current state (e.g., duplicate key)
- **500 Internal Server Error**: Unhandled server errors

### 5. Content Negotiation

- Support JSON as the default and primary format
- Use `[Produces("application/json")]` attribute on controllers
- Honor Accept headers when additional formats are supported

### 6. Response Headers

- Include `Location` header for 201 Created responses
- Support `ETag` headers for caching when appropriate
- Include API version in response headers

## Implementation

### Update GlobalExceptionHandlingMiddleware

Convert our current error response to use ProblemDetails:

```csharp
private async Task HandleExceptionAsync(HttpContext context, Exception exception)
{
    ProblemDetails problemDetails = new()
    {
        Instance = context.Request.Path,
        Detail = exception.Message
    };

    switch (exception)
    {
        case ValidationException validationException:
            problemDetails.Status = StatusCodes.Status400BadRequest;
            problemDetails.Title = "One or more validation errors occurred.";
            problemDetails.Type = "https://tools.ietf.org/html/rfc7231#section-6.5.1";
            problemDetails.Extensions["errors"] = validationException.Errors;
            break;
        // ... other cases
    }
    
    context.Response.StatusCode = problemDetails.Status.Value;
    await context.Response.WriteAsJsonAsync(problemDetails);
}
```

### Update ApiControllerBase

Ensure all controllers inherit from our base controller that provides consistent response handling.

### Configure API Behavior Options

Update the InvalidModelStateResponseFactory to return ProblemDetails format.

## Consequences

### Positive

- Consistent error response format following industry standards (RFC 7807)
- Better integration with client libraries that understand ProblemDetails
- Easier to add metadata to responses in the future if needed
- Aligns with Microsoft's official recommendations
- Supports proper content negotiation

### Negative

- Need to update all existing error handling code
- Client applications need to be updated to handle ProblemDetails format
- Slightly more complex error handling setup

## References

- [Microsoft API Design Best Practices](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)
- [RFC 7807 - Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
- [ASP.NET Core Web API Formatting](https://learn.microsoft.com/en-us/aspnet/core/web-api/advanced/formatting)
- [ASP.NET Core Error Handling](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling)