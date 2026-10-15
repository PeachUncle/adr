# ADR: JWT-Based Authorization with Module Roles

Status
- Accepted

Context
- The evaluations module is designed as an embeddable component for contact center solutions
- Customers need to integrate the module with their existing identity providers and authorization systems
- The module requires user identification and role-based access control for three distinct roles: FormDesigner, Supervisor, and Operator
- The solution must be flexible enough to work with various identity providers (Azure AD, Keycloak, IdentityServer, etc.)
- The module validates JWT tokens (signature, issuer, audience, lifetime) but does not issue tokens or verify passwords
- User metadata (ID, name, email) needs to be accessible within the application layer

Decision
- Use JWT Bearer tokens as the authentication mechanism
- Implement claims-based authorization using a custom `module_role` claim
- Define three module roles as an enum: `FormDesigner`, `Supervisor`, `Operator`
- Extract user information from standard JWT claims (`sub`, `name`, `given_name`, `family_name`, `email`)
- Create domain interface `IModuleUser` for accessing current user context
- Implement stateless authorization - no session state stored in the module
- Configure authorization policies for each module role using claims-based assertions

Scope
- Applies to all layers: Domain (interfaces), Infrastructure (implementation), Host (configuration)
- Authorization is enforced at the endpoint level using ASP.NET Core authorization policies
- Does not include user management, authentication, or token generation - these remain the customer's responsibility

Rationale
- **Industry Standard**: JWT is the de facto standard for API authorization and is supported by all modern identity providers
- **Stateless Design**: The module doesn't maintain session state, making it scalable and cloud-ready
- **Flexible Integration**: Customers can use any OAuth2/OpenID Connect compliant identity provider
- **Claims-Based Model**: Extracting user metadata from token claims eliminates additional database lookups
- **Separation of Concerns**: Authentication is delegated to customer's infrastructure; module only handles authorization
- **Role-Based Security**: Three distinct roles align with business domain (form design, supervision, evaluation)

Consequences
- Customers must configure their identity provider to issue JWT tokens with the `module_role` claim
- Token validation requires HTTPS in production (configurable for development)
- Module depends on `Microsoft.AspNetCore.Authentication.JwtBearer` package
- Integration complexity is minimal - customers only need to configure Authority and Audience
- Adding new roles requires updating the `ModuleRole` enum and authorization policies
- The module trusts claims in validated JWT tokens without additional verification
- **Security Model**: The module validates JWT signature, issuer, audience, and expiration. It does NOT issue tokens or handle password authentication - this remains the customer's Identity Provider responsibility

Architecture Components

## Domain Layer
```csharp
// Value Objects
public readonly record struct UserId(string Value);
public sealed record ModuleUserInfo(UserId Id, Option<string> Name, Option<string> Email);

// Enumerations
public enum ModuleRole { FormDesigner, Operator, Supervisor }

// Interfaces
public interface IModuleUser
{
    bool IsInRole(ModuleRole role);
    void Print(IMedia media);
}
```

## Infrastructure Layer
```csharp
internal sealed class HttpContextModuleUser : IModuleUser
{
    // Extracts user information from HttpContext.User claims
    // Implements role checking via module_role claim
}
```

## Host Layer
```csharp
// JWT Bearer authentication configuration
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => { /* Authority, Audience */ });

// Authorization policies
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("FormDesigner", policy =>
        policy.RequireAuthenticatedUser()
              .RequireAssertion(context =>
                  context.User.HasClaim("module_role", ModuleRole.FormDesigner.ToString())));
    // ... other policies
});
```

## Endpoint Protection
```csharp
group.MapGet("/", ListFormsEndpoint)
    .RequireAuthorization("FormDesigner")
    .ProducesProblem(StatusCodes.Status401Unauthorized)
    .ProducesProblem(StatusCodes.Status403Forbidden);
```

Role Definitions

| Role | Description | Permissions |
|------|-------------|-------------|
| **FormDesigner** | Creates, edits, and manages evaluation forms | View forms list, create forms, edit forms, delete forms |
| **Supervisor** | Evaluates operator performance using forms | View forms, submit evaluations, view evaluation results |
| **Operator** | Contact center agent being evaluated | View own evaluation results (future) |

JWT Token Requirements

Customers must configure their identity provider to include these claims:

### Required Claims
- `sub` (or `NameIdentifier`): User unique identifier
- `module_role`: One of: `FormDesigner`, `Supervisor`, `Operator`

### Optional Claims
- `preferred_username` or `username`: Username/login identifier
- `name`: Full display name
- `given_name`: First name
- `family_name`: Last name
- `email`: Email address

Example JWT Payload:
```json
{
  "sub": "user-12345",
  "module_role": "FormDesigner",
  "preferred_username": "ipetrov",
  "name": "Иван Петров",
  "given_name": "Иван",
  "family_name": "Петров",
  "email": "ivan.petrov@company.com",
  "aud": "evaluations-module",
  "iss": "https://identity-provider.com",
  "exp": 1697654321
}
```

Configuration

### appsettings.json
```json
{
  "JwtBearer": {
    "Authority": "https://your-identity-provider.com",
    "Audience": "evaluations-module"
  }
}
```

JWT Signature Validation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Identity Provider (Keycloak/Azure AD/IdentityServer)           │
│                                                                 │
│  1. User authenticates (username/password/SSO)                 │
│  2. Signs JWT with PRIVATE KEY                                 │
│  3. Returns JWT to client                                      │
│                                                                 │
│  Publishes public keys:                                        │
│  GET /.well-known/openid-configuration                         │
│  GET /.well-known/jwks.json                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ JWT Token (signed)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Client Application (Browser/Mobile/Desktop)                    │
│  Stores token and includes in API requests                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Request
                         │ Authorization: Bearer eyJhbG...
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Evaluations Module (ASP.NET Core)                              │
│                                                                 │
│  [Startup - One Time]                                          │
│  1. Read Authority from config                                 │
│  2. Download JWKS (public keys) from Identity Provider         │
│  3. Cache keys in memory                                       │
│                                                                 │
│  [Every Request]                                               │
│  4. Extract JWT from Authorization header                      │
│  5. Parse JWT header to get 'kid' (key ID)                     │
│  6. Find matching public key in cache                          │
│  7. VALIDATE SIGNATURE using public key                        │
│  8. Verify issuer, audience, expiration                        │
│  9. Extract claims (sub, module_role, name, email)             │
│  10. Allow/Deny request based on authorization policy          │
└─────────────────────────────────────────────────────────────────┘

Security Guarantees:
✓ Token cannot be forged (requires private key held by Identity Provider)
✓ Token cannot be tampered (signature validation fails)
✓ Module never handles user passwords or credentials
✓ Stateless - no session storage required
```

Validation
- Integration tests verify 401 Unauthorized for missing tokens
- Integration tests verify 403 Forbidden for incorrect roles
- Integration tests verify 200 OK for valid tokens with correct roles
- Unit tests verify HttpContextModuleUser correctly extracts claims
- Unit tests verify ModuleUserInfo.Print() serializes user data

Alternatives Considered
- **API Keys**: Rejected - not suitable for user-level authorization, lacks standard support
- **OAuth2 Client Credentials**: Rejected - service-to-service auth, doesn't identify individual users
- **Basic Authentication**: Rejected - requires storing credentials, not stateless
- **Cookie-Based Sessions**: Rejected - stateful, difficult to integrate with external systems
- **Custom Token Format**: Rejected - reinventing the wheel, poor ecosystem support

References
- RFC 7519: JSON Web Token (JWT)
- OAuth 2.0 Authorization Framework (RFC 6749)
- OpenID Connect Core 1.0
- Microsoft Docs: JWT Bearer Authentication in ASP.NET Core
- Integration guide: `docs/integration/jwt-authentication.md`
