# ADR-002: Authentication via API Endpoints Pattern

## Status
Accepted

## Context
When implementing authentication in our pure Blazor Server application, we encountered a critical issue:

### The Problem
- Using `SignInManager` directly in Blazor components caused "Headers are read-only, response has already started" errors
- This error occurs because Blazor Server components execute within the SignalR circuit context
- HTTP response headers (including authentication cookies) cannot be modified after the response has started
- Multiple developers spent hours trying different approaches that all failed

### Failed Approaches
1. **Direct SignInManager Usage**: Injecting and using SignInManager in Blazor components
2. **Custom Cookie Handling**: Attempting to manually set authentication cookies
3. **Hybrid Solutions**: Mixing Razor Pages for auth with Blazor for everything else
4. **JavaScript Interop**: Trying to set cookies via JavaScript

## Decision
Implement authentication operations through dedicated API endpoints that execute outside the Blazor rendering context.

### Implementation Pattern
```
Blazor Component → HTTP Request → API Endpoint → SignInManager → Set Cookies → Response
```

### Implementation Details
1. Created `/auth/login`, `/auth/logout`, `/auth/register` API endpoints
2. These endpoints handle all SignInManager operations
3. `IdentityAuthService` calls these endpoints via HttpClient
4. HttpClient configured to use internal container port (8080)
5. Authentication cookies are properly set in the HTTP response

## Consequences

### Positive
1. **Microsoft Approved**: This is the official pattern for Blazor Server authentication
2. **Reliable**: Works consistently without header modification errors
3. **Separation of Concerns**: Authentication logic isolated in API endpoints
4. **Testable**: API endpoints can be tested independently
5. **Reusable**: Same endpoints can be used by other clients if needed

### Negative
1. **Additional Complexity**: Requires API endpoints instead of direct service calls
2. **Network Overhead**: Authentication operations require HTTP calls
3. **Debugging Complexity**: Authentication flow spans multiple layers

### Mitigation
- Comprehensive documentation of the authentication flow
- Clear error messages when authentication fails
- Logging at each step of the authentication process
- Helper methods to simplify common authentication tasks

## Technical Details

### AuthEndpoints.cs
```csharp
app.MapPost("/auth/login", async (LoginRequest request, SignInManager<WitchCityRopeUser> signInManager) =>
{
    var result = await signInManager.PasswordSignInAsync(
        request.Email, 
        request.Password, 
        request.RememberMe, 
        lockoutOnFailure: false);
    
    return result.Succeeded ? Results.Ok() : Results.BadRequest();
});
```

### IdentityAuthService.cs
```csharp
public async Task<bool> LoginAsync(string email, string password, bool rememberMe)
{
    var response = await _httpClient.PostAsJsonAsync("/auth/login", new
    {
        email,
        password,
        rememberMe
    });
    
    return response.IsSuccessStatusCode;
}
```

## Why This Is Required
Microsoft's official guidance states that SignInManager operations MUST happen outside Blazor's rendering context. This is a fundamental limitation of how Blazor Server works with SignalR circuits.

## Related Documentation
- [JWT Service-to-Service Authentication](/docs/functional-areas/authentication/jwt-service-to-service-auth.md) - Complete implementation of Web→API authentication flow
- [Authentication API Pattern](/docs/standards-processes/development-standards/authentication-patterns.md) - Development patterns and standards

## References
- [Microsoft Blazor Server Authentication Documentation](https://docs.microsoft.com/aspnet/core/blazor/security/server)
- [SignInManager and Blazor Server Issues](https://github.com/dotnet/aspnetcore/issues)
- Internal investigation documented in `/docs/AUTHORIZATION_MIGRATION.md`