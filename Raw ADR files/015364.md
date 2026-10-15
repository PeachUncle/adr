# User Service Authentication Strategy

* Status: superseded by [ADR-011 Spring Authorization Server](011_spring_authorization_server.md)
* Deciders: Platform Team, Security Team
* Date: 2025-12-05

## Context and Problem Statement

The platform currently implements OAuth2 Resource Server pattern per `006_AUTHN_AUTHZ.md`, where services validate JWTs issued by an **external OAuth provider** (Auth0, Okta, Azure AD). The proposed User Service (`016_USER_SERVICE.md`) introduces a new model where the **User Service itself issues JWTs** for three user types: SERVICE_ACCOUNT (self-checkout), CUSTOMER (B2C online), and EMPLOYEE (in-store assisted selling).

This creates architectural tension: Should the User Service act as an internal Identity Provider (IdP), or should it integrate with the existing external IdP model? How do custom permissions (read, write, admin, customer_search) and user types map to the existing OAuth scope-based authorization?

## Decision Drivers

1. **Multi-channel support**: Three distinct user types require different permission models and authentication flows
2. **Customer search restriction**: Only EMPLOYEE users with `customer_search` permission can search customer records - a business-critical security requirement
3. **Existing investment**: Platform already has OAuth2 Resource Server implementation in `libs/platform/platform-security/`
4. **Operational simplicity**: Minimize the number of token validation configurations across services
5. **Security boundary**: User credentials (password hashes) should be managed in a controlled, auditable service
6. **Token trust chain**: Services must trust tokens consistently across the platform

## Considered Options

1. **Hybrid IdP Model** - User Service as internal IdP alongside external IdP (chosen)
2. **External IdP Only** - Delegate all authentication to external IdP, User Service as profile store
3. **User Service as Sole IdP** - Replace external IdP entirely with User Service

## Decision Outcome

Chosen option: **Hybrid IdP Model**

The User Service acts as an **internal Identity Provider** for platform-managed users (service accounts, customers, employees), while the existing external IdP model remains available for federated/SSO scenarios. Services validate tokens from **both issuers** using a multi-issuer JWT validation configuration.

This approach provides:
- Direct control over user lifecycle and permissions for platform users
- Flexibility to support external IdP integration for enterprise customers
- Clear mapping between User Service permissions and OAuth scopes
- Single source of truth for user-to-permission relationships

### Positive Consequences

- Full control over token claims, including `user_type` and custom permissions
- Direct username/password authentication without external IdP dependency
- Employee `customer_search` permission enforced at token issuance
- Existing `platform-security` library reusable with minor extensions
- Services can validate tokens from User Service or external IdP using same pattern

### Negative Consequences

- Two token issuers increases validation complexity
- Must maintain RSA key pair for User Service token signing
- Token revocation more complex with internal issuer (no central introspection)
- Potential for token format divergence between issuers

## Pros and Cons of the Options

### 1. Hybrid IdP Model (chosen)

**Good**
- Full control over user authentication and token claims
- Custom `user_type` and `permissions` claims map directly to business requirements
- Employee-only `customer_search` enforced at token issuance time
- Existing OAuth2 Resource Server pattern extends naturally to multi-issuer
- No external IdP dependency for core platform users
- Can add external IdP later for B2B/enterprise SSO scenarios

**Bad**
- Must securely manage RSA signing keys
- Two issuers means two JWK endpoints to configure
- Token revocation requires custom solution (refresh token revocation table in User Service)
- Additional operational burden for key rotation

### 2. External IdP Only

**Good**
- Single token issuer simplifies validation
- Enterprise-grade security (Auth0, Okta expertise)
- Built-in MFA, passwordless, social login
- Centralized token revocation

**Bad**
- Custom `user_type` and `permissions` claims require IdP customization (rules, actions)
- User Service becomes a profile store only, splitting user management across systems
- External IdP latency for every authentication
- Cost scales with user count
- Less control over token structure

### 3. User Service as Sole IdP

**Good**
- Single internal source of truth for all authentication
- Maximum control and customization
- No external dependencies

**Bad**
- Loses ability to integrate with enterprise SSO
- Must implement all IdP features (MFA, social login, passwordless)
- Security expertise required for IdP implementation
- No standards compliance (OIDC Discovery, etc.) without significant effort

## Implementation Notes and Next Steps

### Token Claim Mapping

User Service tokens will include both custom claims and standard OAuth scopes:

```json
{
  "iss": "https://user-service.example.com",
  "sub": "user-uuid",
  "aud": ["reactive-platform"],
  "user_type": "EMPLOYEE",
  "permissions": ["read", "write", "admin", "customer_search"],
  "scope": "read write admin customer_search",
  "store_number": 1234,
  "exp": 1234567890
}
```

The `scope` claim mirrors `permissions` for compatibility with existing `JwtAuthenticationConverter`:
- `permissions` array: Application-level use
- `scope` space-delimited: Spring Security authority extraction

### Multi-Issuer Configuration

Extend `JwtValidatorConfig` to accept multiple issuers:

```yaml
app:
  security:
    allowed-issuers:
      - https://user-service.example.com  # User Service (internal)
      - https://auth.example.com          # External IdP
    jwk-set-uris:
      https://user-service.example.com: http://user-service:8084/.well-known/jwks.json
      https://auth.example.com: https://auth.example.com/.well-known/jwks.json
```

### Permission-to-Scope Mapping

| User Type       | Permissions                           | OAuth Scopes                           |
|-----------------|---------------------------------------|----------------------------------------|
| SERVICE_ACCOUNT | read                                  | read                                   |
| CUSTOMER        | read, write                           | read write                             |
| EMPLOYEE        | read, write, admin, customer_search   | read write admin customer_search       |

### Next Steps

1. **Extend platform-security**: Add multi-issuer JWT decoder support in `JwtValidatorConfig`
2. **Implement User Service**: Follow `016_USER_SERVICE.md` phases 1-4
3. **Add JWK endpoint**: User Service exposes `/.well-known/jwks.json` for public key
4. **Update service configs**: Add User Service issuer to `allowed-issuers` list
5. **Integration tests**: Verify tokens from both issuers validate correctly

## References

- `libs/platform/platform-security/src/main/java/org/example/platform/security/JwtAuthenticationConverter.java` - Current scope extraction
- `libs/platform/platform-security/src/main/java/org/example/platform/security/JwtValidatorConfig.java` - Current issuer validation
- `apps/product-service/src/main/java/org/example/product/security/SecurityConfig.java` - OAuth2 Resource Server config
- `docs/archive/006_AUTHN_AUTHZ.md` - Original OAuth2 implementation plan
- `016_USER_SERVICE.md` - User Service implementation plan
- `docs/standards/security.md` - Security standards and patterns
