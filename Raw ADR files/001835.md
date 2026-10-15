# ADR-002: JWT Authentication with Header-Based Tokens

## Status

Accepted

## Date

2025-10-01 (Pre-M1 Planning)

## Context

Need authentication system that works for:

- Web application (browser)
- Future mobile applications (iOS/Android)
- API security requirements

Requirements:

- Secure password storage
- Stateless authentication (no server-side sessions)
- Support for access token expiry (short-lived)
- Refresh token mechanism (longer-lived)
- Mobile compatibility

## Decision

Use **JWT (JSON Web Tokens)** with:

- **Access tokens**: Short-lived (15 min), sent in `Authorization` header
- **Refresh tokens**: Long-lived (7 days), stored client-side in secure storage
- **Password hashing**: bcrypt with 12 rounds
- **Token storage**: Client-side (localStorage for web, secure storage for mobile)

**Flow:**

1. Login → Server returns access token + refresh token
2. Client stores both tokens securely
3. Client sends access token in header: `Authorization: Bearer <token>`
4. When access token expires → Use refresh token to get new access token
5. Refresh token rotation on each refresh (invalidates old refresh token)

## Alternatives Considered

### Alternative 1: Session-Based Authentication (Cookie + Redis)

- **Pros**:
  - More secure (token never exposed to JavaScript)
  - Server can revoke sessions instantly
  - Industry standard for web apps
- **Cons**:
  - Requires server state (Redis/database)
  - Doesn't work well with mobile apps
  - CORS complexity with cookies
  - Horizontal scaling requires session sharing
- **Why rejected**: Mobile incompatibility is a dealbreaker. Cookie-based auth doesn't work naturally in React Native.

### Alternative 2: JWT with HTTP-Only Cookies

- **Pros**:
  - XSS protection (JavaScript can't access token)
  - Automatic cookie sending
  - More secure for web
- **Cons**:
  - **Doesn't work on mobile** (React Native doesn't have HTTP-only cookies)
  - CSRF vulnerabilities (need CSRF tokens)
  - CORS configuration complexity
  - Can't use with native mobile apps
- **Why rejected**: Planning mobile apps from the start. Can't use a web-only solution.

### Alternative 3: OAuth 2.0 / OpenID Connect

- **Pros**:
  - Industry standard
  - Supports social login (Google, GitHub)
  - Battle-tested security
- **Cons**:
  - Overkill for simple email/password auth
  - Requires external provider or complex setup
  - More moving parts (authorization server)
- **Why rejected**: Too complex for MVP. Can add later if social login needed.

### Alternative 4: API Keys

- **Pros**:
  - Simple to implement
  - Long-lived, no refresh needed
- **Cons**:
  - No expiration (security risk)
  - Can't identify user actions within session
  - No way to revoke without database lookup
- **Why rejected**: Insufficient security for user-facing app

## Consequences

### Positive

- ✅ **Mobile compatible**: Works identically on web and mobile
- ✅ **Stateless**: No Redis/session store needed (simpler architecture)
- ✅ **Scalable**: No session sharing between servers
- ✅ **Standard**: JWT is widely understood, libraries exist everywhere
- ✅ **Flexible**: Can add claims (user role, plan, etc.) to token
- ✅ **Testable**: Easy to mock tokens in tests

### Negative

- ❌ **XSS vulnerability**: If site has XSS, attacker can steal token from localStorage
- ❌ **Can't revoke instantly**: Need to wait for token expiry (mitigated by short 15min access tokens)
- ❌ **Token size**: JWT is larger than session ID (not significant in practice)
- ❌ **Client storage**: Need to handle token storage securely on client

### Neutral

- ℹ️ **Refresh token rotation**: Adds complexity but improves security
- ℹ️ **Token blacklist**: May need to implement for critical security (logout, password change)

## Implementation Notes

**Token Structure:**

```typescript
// Access Token Payload
{
  userId: string;
  email: string;
  plan?: 'free' | 'pro';
  iat: number;        // Issued at
  exp: number;        // Expires (15 min from iat)
}

// Refresh Token Payload
{
  userId: string;
  sessionId: string;  // To track and rotate
  iat: number;
  exp: number;        // Expires (7 days from iat)
}
```

**Security Measures:**

1. **bcrypt**: 12 rounds (industry standard, ~250ms to hash)
2. **Short access token expiry**: 15 minutes reduces stolen token window
3. **Refresh token rotation**: Old refresh token invalidated when used
4. **Token blacklist**: For logout/password change (store in MongoDB with TTL)
5. **Rate limiting**: Prevent brute force on login endpoint

**Client Storage:**

- **Web**: localStorage (or sessionStorage for more security)
- **Mobile**: react-native-keychain (encrypted storage)

**Endpoints:**

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/password-reset-request`
- `POST /api/v1/auth/password-reset`

## Interview Talking Points

1. **"Why JWT over sessions?"**
   - Answer: Planning mobile apps from the start. Sessions with cookies don't work naturally in React Native. JWT works identically on web and mobile - same API, same token format, same security model. Also, JWT is stateless, so I don't need Redis for session storage, which simplifies deployment.

2. **"What about XSS attacks?"**
   - Answer: JWT in localStorage is vulnerable to XSS. I'm mitigating this with:
     - Short 15-minute access token expiry (limits damage window)
     - Content Security Policy headers
     - Input sanitization (Zod validation)
     - React's built-in XSS protection
   - HTTP-only cookies would be more secure for web, but they don't work on mobile. This is a conscious trade-off prioritizing mobile compatibility.

3. **"How do you handle token expiry?"**
   - Answer: Two-token strategy. Access token is short-lived (15 min), sent with every request. When it expires, client uses long-lived refresh token (7 days) to get a new access token. This balances security (short access token) with UX (don't make users re-login every 15 minutes). I also rotate refresh tokens on each use to detect if one is stolen.

4. **"Can you revoke a token?"**
   - Answer: JWT is stateless, so can't revoke directly. For critical cases (logout, password change), I implement a token blacklist in MongoDB with TTL indexes. When user logs out, I add their access token to blacklist (with 15-min expiry). Middleware checks blacklist before accepting token. This is rare enough that database lookup is acceptable.

5. **"Why 15 minutes for access token?"**
   - Answer: Balance between security and UX. Shorter is more secure (less time for attacker if stolen) but more refresh requests. 15 minutes means user rarely notices refreshing. For comparison, Google uses 1 hour, GitHub uses 15 minutes. I chose 15 as a security-conscious default that's still user-friendly.

6. **"What about CSRF?"**
   - Answer: Not vulnerable because I'm using Authorization headers, not cookies. CSRF exploits automatic cookie-sending by browsers. Since I'm manually adding tokens to headers, attacker's site can't make authenticated requests. This is one benefit of header-based auth over cookie-based.

7. **Demonstrates:**
   - Security awareness (XSS, CSRF, brute force)
   - Mobile-first thinking
   - Understanding of authentication fundamentals
   - Trade-off analysis (security vs UX vs mobile compatibility)
   - Knowledge of token rotation and blacklisting patterns

## References

- [JWT.io](https://jwt.io/)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [RFC 7519 - JWT Specification](https://tools.ietf.org/html/rfc7519)
- [Auth0 Refresh Token Rotation](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)
