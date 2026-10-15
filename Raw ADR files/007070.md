# ADR 003: JWT Token Authentication

**Status:** Accepted

**Date:** 2024-11-12

**Deciders:** Piotr Świderski

**Technical Story:** Need secure, stateless authentication that works with Laravel backend and supports future mobile apps.

---

## Context

BuildFlow requires authentication for:
- Web application (React SPA)
- Future mobile apps (iOS, Android)
- API access (Business tier)
- Multiple backend implementations

### Current Situation
- RESTful API architecture
- Single Page Application frontend
- Multiple backend implementations
- Future mobile app support needed
- No sessions (stateless preferred)

### Requirements
- Stateless authentication (no server-side sessions)
- Framework-agnostic approach (primarily Laravel, but portable)
- Secure token storage
- Token refresh capability
- Revocation support
- Mobile-friendly
- Industry standard

---

## Decision

**We will use JWT (JSON Web Tokens) for authentication with access tokens and refresh tokens.**

### Implementation Details

1. **Token Structure**
   - **Access Token**: Short-lived (15 minutes), used for API requests
   - **Refresh Token**: Long-lived (7 days), used to get new access tokens
   - Both signed with HS256 (HMAC with SHA-256)

2. **Authentication Flow**
   ```
   1. User submits credentials (email + password)
   2. Server validates credentials
   3. Server generates access token + refresh token
   4. Client stores tokens (localStorage for web, secure storage for mobile)
   5. Client includes access token in Authorization header
   6. Server validates token on each request
   7. When access token expires, use refresh token to get new one
   ```

3. **Token Payload**
   ```json
   {
     "sub": "user_id",
     "org_id": "organization_id",
     "role": "owner|manager|field_worker",
     "iat": 1234567890,
     "exp": 1234567890
   }
   ```

4. **API Endpoints**
   - `POST /auth/register` - Create account
   - `POST /auth/login` - Get tokens
   - `POST /auth/refresh` - Refresh access token
   - `POST /auth/logout` - Revoke tokens (blacklist refresh token)
   - `GET /auth/me` - Get current user

5. **Security Measures**
   - HTTPS only in production
   - Tokens signed with secret key (env variable)
   - Refresh tokens stored in database (revocable)
   - Rate limiting on auth endpoints
   - Password hashing with bcrypt/Argon2
   - CORS configured properly

6. **Multi-Tenancy Integration**
   - Token includes `org_id`
   - All API requests scoped to user's organization
   - Prevents cross-organization data access

---

## Consequences

### Positive
- ✅ **Stateless**: No server-side session storage
- ✅ **Scalable**: Easy to add more servers
- ✅ **Mobile-Friendly**: Works well with native apps
- ✅ **Cross-Implementation**: Works with all backends
- ✅ **Industry Standard**: Well-understood and documented
- ✅ **Flexible**: Can include custom claims
- ✅ **Performance**: No database lookup on each request
- ✅ **API-Friendly**: Simple Bearer token header

### Negative
- ⚠️ **Token Size**: Larger than session IDs
- ⚠️ **Storage**: XSS risk if stored in localStorage
- ⚠️ **Revocation**: Harder than session invalidation
- ⚠️ **Secret Management**: Must protect signing keys
- ⚠️ **Clock Skew**: Servers must have synchronized time

### Risks & Mitigation
- **Risk**: XSS attack steals token from localStorage
  - **Mitigation**: Content Security Policy, sanitize inputs, short token lifetime
  
- **Risk**: Token stolen in transit
  - **Mitigation**: HTTPS only, secure flag on cookies
  
- **Risk**: Cannot immediately revoke access token
  - **Mitigation**: Short lifetime (15 min), refresh token blacklist
  
- **Risk**: Secret key compromised
  - **Mitigation**: Rotate keys, use strong secrets, env variables

---

## Alternatives Considered

### Alternative 1: Session-Based Authentication
**Description:** Traditional server-side sessions with session cookies

**Pros:**
- Easier to revoke immediately
- Smaller cookie size
- Well-understood
- Built into most frameworks

**Cons:**
- Requires shared session storage (Redis)
- Not stateless
- Harder to scale horizontally
- CSRF protection needed
- Not ideal for mobile apps
- Less portable if adding future implementations

**Why rejected:** Need stateless solution for horizontal scaling and mobile support. Session-based auth would require shared Redis for any future implementations.

### Alternative 2: OAuth 2.0 with External Provider
**Description:** Use Google, Facebook, GitHub for authentication

**Pros:**
- No password management
- Better security (delegated)
- Social login convenience
- 2FA handled by provider

**Cons:**
- Dependency on external service
- Privacy concerns for users
- Requires internet connectivity
- More complex integration
- Users may not have accounts
- Not suitable for all business types

**Why rejected:** Construction businesses need simple email/password. Can add social login later as optional.

### Alternative 3: API Keys
**Description:** Simple API keys for authentication

**Pros:**
- Very simple
- No expiration needed
- Easy to implement

**Cons:**
- No user context
- Hard to manage permissions
- No automatic expiration
- Not suitable for web apps
- Security risk if leaked

**Why rejected:** Too simple for web application. Better for API-only access (can add later for Business tier).

### Alternative 4: Opaque Tokens
**Description:** Random strings stored in database

**Pros:**
- Easy to revoke
- Can't be decoded
- Simple to implement

**Cons:**
- Database lookup on every request
- Not stateless
- Doesn't scale as well
- No information in token

**Why rejected:** Want stateless solution for better scalability. JWT allows no database lookup.

---

## Related Decisions

- [ADR-004](004-multi-tenancy-row-level.md) - Token includes org_id for tenancy
- [ADR-009](009-feature-flags-for-tiers.md) - Role in token enables feature checks

---

## References

- [JWT.io - Introduction to JWT](https://jwt.io/introduction)
- [RFC 7519 - JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [Auth0 - JWT vs Sessions](https://auth0.com/blog/stateless-auth-for-stateful-minds/)
- [Tymon JWT Auth (Laravel)](https://github.com/tymondesigns/jwt-auth)
- [LexikJWTAuthenticationBundle (Symfony)](https://github.com/lexik/LexikJWTAuthenticationBundle)

---

## Notes

### Token Lifetime Rationale
- **15 minutes access token**: Balance between security and UX. Long enough for normal session, short enough to limit damage if stolen.
- **7 days refresh token**: Long enough to avoid frequent re-login, short enough to require periodic re-authentication.

### Future Enhancements
- 2FA support (TOTP)
- Remember me (longer refresh token)
- Multiple devices management
- Suspicious activity detection
- IP-based restrictions (optional)

### Implementation Notes
- **Laravel**: Use `tymon/jwt-auth` package
- **Symfony**: Use `lexik/jwt-authentication-bundle`
- **Next.js**: Use `jsonwebtoken` library

All implementations must use the same token structure and validation logic to ensure cross-compatibility.

---

**Last Updated:** 2024-11-12
