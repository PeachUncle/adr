# ADR-0001: Global Exception Handling with Middleware

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Development Team

## Context

Previously, each controller method contained try-catch blocks for exception handling, leading to:
- Code duplication across controllers
- Inconsistent error responses
- Generic exception types without context
- Difficulty in maintaining error handling logic

## Decision

Implement a centralized exception handling strategy using:
1. **Global Exception Handling Middleware** for HTTP response mapping
2. **Domain-specific exceptions** with rich context information
3. **Exception-free controllers** that rely on middleware
4. **Consistent error response format** across all endpoints

## Consequences

### Positive
- ✅ **Cleaner controllers**: No more try-catch blocks
- ✅ **Consistent errors**: Same format across all endpoints
- ✅ **Better debugging**: Specific exceptions with context
- ✅ **Easier maintenance**: Centralized error handling logic
- ✅ **Better testing**: Clear exception expectations

### Negative
- ⚠️ **Breaking change**: API response format changed
- ⚠️ **Learning curve**: Team needs to understand new exception types
- ⚠️ **Initial effort**: Required updating all services and tests

### Neutral
- 🔄 **Different pattern**: Services throw exceptions instead of returning null
- 🔄 **More classes**: Exception hierarchy requires more files

## Implementation

```csharp
// Before
public async Task<ActionResult<ActivityDto>> GetById(int id)
{
    try {
        var activity = await _service.GetActivityByIdAsync(id);
        if (activity == null) return NotFound();
        return Ok(activity);
    } catch (Exception ex) {
        return StatusCode(500, ex.Message);
    }
}

// After
public async Task<ActionResult<ActivityDto>> GetById(int id)
{
    var activity = await _service.GetActivityByIdAsync(id);
    return Ok(activity);
}
```

## Alternatives Considered

1. **Keep current approach**: Too much duplication
2. **Base controller with error handling**: Still requires inheritance
3. **Result pattern**: Added complexity without clear benefits

## References

- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [ASP.NET Core Error Handling](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/error-handling)