# ADR-004: JWT Authentication

**Status:** Accepted

**Date:** 2025-01-15

**Decision Makers:** JumpStart Core Team

## Context

JumpStart applications often require two separate deployment architectures:

1. **Blazor Server Application** - Cookie-based authentication for interactive UI
2. **Separate Web API** - Token-based authentication for:
   - Blazor Server calling API endpoints
   - Mobile applications
   - Third-party integrations
   - Microservices communication
   - JavaScript SPAs

When the Blazor Server application needs to call the separate Web API, we faced several challenges:

- **Different Authentication Mechanisms** - Cookies work for browser, not API calls
- **Cross-Service Identity** - Need to pass user identity from Blazor to API
- **Secure Token Transmission** - Tokens must be securely stored and transmitted
- **Token Expiration** - Handle token refresh without disrupting user experience
- **Unauthorized Access** - Detect and handle authentication failures gracefully
- **Standards Compliance** - Use industry-standard authentication protocols

We needed a solution that enables secure, stateless authentication for API calls while integrating seamlessly with Blazor Server's cookie authentication.

## Decision

We will implement **JWT (JSON Web Token) authentication** with the following components:

### 1. JWT Token Service

Service for generating secure tokens with configurable claims:

```csharp
public interface IJwtTokenService
{
    string GenerateToken(int userId, string username, Dictionary<string, string>? additionalClaims = null);
}

public class JwtTokenService : IJwtTokenService
{
    private readonly IConfiguration _configuration;

    public string GenerateToken(int userId, string username, Dictionary<string, string>? additionalClaims = null)
    {
        var secretKey = _configuration["JwtSettings:SecretKey"];
        var issuer = _configuration["JwtSettings:Issuer"];
        var audience = _configuration["JwtSettings:Audience"];
        var expirationMinutes = int.Parse(_configuration["JwtSettings:ExpirationMinutes"] ?? "60");

        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
            new Claim(ClaimTypes.Name, username),
            new Claim(JwtRegisteredClaimNames.Sub, username),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
        };

        if (additionalClaims != null)
        {
            foreach (var claim in additionalClaims)
            {
                claims.Add(new Claim(claim.Key, claim.Value));
            }
        }

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: issuer,
            audience: audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(expirationMinutes),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

### 2. Token Store

In-memory storage for tokens per user session:

```csharp
public interface ITokenStore
{
    string? GetToken(string userId);
    void SetToken(string userId, string token);
    void RemoveToken(string userId);
}

public class TokenStore : ITokenStore
{
    private readonly ConcurrentDictionary<string, string> _tokens = new();

    public string? GetToken(string userId) => 
        _tokens.TryGetValue(userId, out var token) ? token : null;

    public void SetToken(string userId, string token) => 
        _tokens[userId] = token;

    public void RemoveToken(string userId) => 
        _tokens.TryRemove(userId, out _);
}
```

### 3. JWT Authentication Handler

HTTP message handler that automatically attaches JWT tokens to API requests:

```csharp
public class JwtAuthenticationHandler : DelegatingHandler
{
    private readonly ITokenStore _tokenStore;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public JwtAuthenticationHandler(ITokenStore tokenStore, IHttpContextAccessor httpContextAccessor)
    {
        _tokenStore = tokenStore;
        _httpContextAccessor = httpContextAccessor;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, 
        CancellationToken cancellationToken)
    {
        var userId = _httpContextAccessor.HttpContext?.User
            .FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (userId != null)
        {
            var token = _tokenStore.GetToken(userId);
            if (!string.IsNullOrEmpty(token))
            {
                request.Headers.Authorization = 
                    new AuthenticationHeaderValue("Bearer", token);
            }
        }

        return await base.SendAsync(request, cancellationToken);
    }
}
```

### 4. API Configuration

Web API configured to validate JWT tokens:

```csharp
// appsettings.json
{
  "JwtSettings": {
    "SecretKey": "YourSuperSecretKeyThatIsAtLeast32CharactersLong!",
    "Issuer": "JumpStartBlazorServer",
    "Audience": "JumpStartApi",
    "ExpirationMinutes": 60
  }
}

// Program.cs (Web API)
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        var jwtSettings = builder.Configuration.GetSection("JwtSettings");
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtSettings["Issuer"],
            ValidAudience = jwtSettings["Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(jwtSettings["SecretKey"])),
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization();
```

### 5. Blazor Server Integration

```csharp
// Program.cs (Blazor Server)
builder.Services.AddScoped<IJwtTokenService, JwtTokenService>();
builder.Services.AddScoped<ITokenStore, TokenStore>();
builder.Services.AddTransient<JwtAuthenticationHandler>();

// Register Refit clients with JWT handler
builder.Services.AddSimpleApiClient<IProductApiClient>($"{apiBaseUrl}/api/products")
    .AddHttpMessageHandler<JwtAuthenticationHandler>();
```

### 6. Token Generation on Login

```csharp
public class LoginService
{
    private readonly IJwtTokenService _tokenService;
    private readonly ITokenStore _tokenStore;

    public async Task<string> LoginAsync(string username, string password)
    {
        // Authenticate user (ASP.NET Core Identity, custom, etc.)
        var user = await AuthenticateUserAsync(username, password);
        
        if (user != null)
        {
            // Generate JWT token
            var token = _tokenService.GenerateToken(
                user.Id, 
                user.UserName, 
                additionalClaims: new Dictionary<string, string>
                {
                    ["email"] = user.Email,
                    ["role"] = user.Role
                });
            
            // Store token for this user's session
            _tokenStore.SetToken(user.Id.ToString(), token);
            
            return token;
        }
        
        throw new UnauthorizedAccessException("Invalid credentials");
    }
}
```

## Consequences

### Positive Consequences

- **Stateless Authentication** - API doesn't need to maintain session state
- **Scalability** - API can scale horizontally without session affinity
- **Standard Protocol** - JWT is industry-standard (RFC 7519)
- **Cross-Platform** - Works with any client (Blazor, mobile, JavaScript, etc.)
- **Self-Contained** - Token contains all necessary user information
- **Secure** - HMAC SHA-256 signing prevents tampering
- **Flexible Claims** - Can include any user information needed by API
- **Automatic Attachment** - Handler transparently adds tokens to requests
- **Separation of Concerns** - Blazor auth and API auth are independent
- **Easy Testing** - Can generate test tokens for automated tests

### Negative Consequences

- **Token Storage** - In-memory dictionary is not distributed (single server only)
- **No Automatic Refresh** - Tokens expire, user must re-authenticate
- **Token Size** - Larger than opaque tokens, included in every request
- **Revocation Complexity** - Cannot easily revoke tokens before expiration
- **Secret Key Management** - Must securely store and rotate secret keys
- **Clock Skew Issues** - Time synchronization required (mitigated with ClockSkew = 0)

### Neutral Consequences

- **Token Lifetime** - Must balance security (short lifetime) vs UX (long lifetime)
- **HTTPS Required** - Tokens must be transmitted over HTTPS in production
- **Memory Usage** - TokenStore keeps tokens in memory per user

## Alternatives Considered

### 1. Cookie-Based Authentication Only

Use cookies for both Blazor Server and API calls.

**Pros:**
- Single authentication mechanism
- Automatic cookie handling
- Session management built-in

**Cons:**
- CSRF protection required
- Doesn't work for mobile apps or third-party integrations
- Requires session affinity for load balancing
- Not suitable for microservices

**Why Rejected:** Not flexible enough for separate API deployment.

### 2. API Key Authentication

Use long-lived API keys instead of JWT tokens.

**Pros:**
- Simple to implement
- No expiration handling

**Cons:**
- User context not embedded in key
- Difficult to rotate
- Not standard protocol
- Cannot pass user-specific claims

**Why Rejected:** JWT provides better user context and standards compliance.

### 3. OAuth 2.0 / OpenID Connect

Use full OAuth 2.0 flow with external identity provider.

**Pros:**
- Industry standard
- Supports refresh tokens
- Centralized identity management
- Token revocation support

**Cons:**
- Complex to implement
- Requires external identity server
- Overkill for simple scenarios
- More moving parts

**Why Rejected:** Too complex for typical JumpStart applications; can be adopted later if needed.

### 4. Reference Tokens (Opaque)

Use random tokens that API looks up in database.

**Pros:**
- Smaller token size
- Easy revocation (remove from database)
- Can store more data server-side

**Cons:**
- Requires database lookup on every request
- Not stateless
- Scalability issues
- Not self-contained

**Why Rejected:** Violates stateless API design principle.

### 5. Certificate-Based Authentication

Use client certificates for mutual TLS.

**Pros:**
- Very secure
- No token management

**Cons:**
- Complex certificate management
- Difficult for browser-based clients
- Not suitable for user authentication

**Why Rejected:** Too complex for typical web applications.

## Security Considerations

### Secret Key Requirements

- **Minimum 32 characters** (256 bits for HMAC SHA-256)
- **Cryptographically random** - Use secure random generator
- **Never commit to source control** - Store in configuration or secrets manager
- **Rotate regularly** - Change periodically and on suspected compromise

### Token Validation

The API validates:
- ? **Signature** - Token hasn't been tampered with
- ? **Issuer** - Token came from expected source
- ? **Audience** - Token intended for this API
- ? **Expiration** - Token is still valid
- ? **Clock Skew** - Zero tolerance (must have synchronized clocks)

### HTTPS Requirement

?? **Always use HTTPS in production** to prevent token interception.

### Token Lifetime

Balance security vs user experience:
- **Short (15-60 minutes)** - More secure, requires frequent re-auth
- **Long (hours/days)** - Better UX, more risk if compromised

### Claims to Include

? **Always include:**
- User ID (NameIdentifier)
- Username (Name)
- JWT ID (Jti) for unique token identification

? **Consider including:**
- Email
- Roles
- Permissions
- Organization ID
- Custom claims needed by API

? **Never include:**
- Passwords
- Sensitive personal information (SSN, etc.)
- Credit card information

## Future Enhancements

### 1. Distributed Token Store

Replace in-memory dictionary with Redis or distributed cache:

```csharp
public class RedisTokenStore : ITokenStore
{
    private readonly IDistributedCache _cache;
    
    public string? GetToken(string userId) =>
        _cache.GetString($"jwt:{userId}");
    
    public void SetToken(string userId, string token) =>
        _cache.SetString($"jwt:{userId}", token, new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(60)
        });
}
```

### 2. Refresh Token Support

Add refresh tokens for automatic token renewal:

```csharp
public interface IJwtTokenService
{
    TokenResponse GenerateToken(int userId, string username);
    TokenResponse RefreshToken(string refreshToken);
}

public class TokenResponse
{
    public string AccessToken { get; set; }
    public string RefreshToken { get; set; }
    public DateTimeOffset Expires { get; set; }
}
```

### 3. Token Revocation

Implement token blacklist for early revocation:

```csharp
public interface ITokenBlacklist
{
    Task AddAsync(string jti, DateTimeOffset expiration);
    Task<bool> IsBlacklistedAsync(string jti);
}
```

## References

- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [Microsoft JWT Bearer Authentication](https://docs.microsoft.com/en-us/aspnet/core/security/authentication/jwt)
- [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [ADR-005: Refit for API Clients](005-refit-api-clients.md)

## Related Documentation

- [How-To: Secure Endpoints](../../how-to/secure-endpoints.md)
- [How-To: Configure JWT](../../how-to/configure-jwt.md)
- [API Reference: IJwtTokenService](../../api/services/ijwttokenservice.md)
