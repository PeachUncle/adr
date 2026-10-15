# ADR-0005: JWT Authentication

**Status:** Accepted  
**Date:** 2026-01-XX  
**Context:** Backend POC-2 - Authentication Strategy  
**Decision Makers:** Backend Team

---

## Context

We need to choose an authentication strategy for our backend API. The authentication mechanism must work with our microservices architecture, support stateless authentication, and integrate seamlessly with the frontend. This decision affects scalability, security, and developer experience.

**Requirements:**

- Stateless authentication (works with microservices)
- Scalable (no server-side session storage)
- Secure (industry-standard)
- Works with frontend (JWT tokens)
- Refresh token support
- Role-based access control (RBAC)

---

## Decision

We will use **JWT (JSON Web Tokens) with refresh tokens** for authentication.

**Rationale:**

- **Stateless** - No server-side session storage, works with microservices
- **Scalable** - No session storage overhead, works across service instances
- **Industry standard** - Widely used, battle-tested
- **Secure** - When properly implemented (short-lived access tokens, refresh tokens)
- **Works with frontend** - Frontend can store tokens, send in Authorization header
- **RBAC support** - Can include role in JWT payload

**Token Structure:**

- **Access Token:** Short-lived (15 minutes), includes user info and role
- **Refresh Token:** Long-lived (7 days), stored in database, used to refresh access token

---

## Alternatives Considered

### 1. Session-Based Authentication

**Pros:**
- Simple to implement
- Server-side session control
- Easy to revoke sessions
- Familiar pattern

**Cons:**
- Requires session storage (Redis/database)
- Not stateless (doesn't work well with microservices)
- Session storage overhead
- Harder to scale across service instances
- Doesn't work well with microservices architecture

**Decision:** Not chosen - Doesn't work well with microservices architecture. Stateless JWT is better.

---

### 2. OAuth 2.0 / OpenID Connect

**Pros:**
- Industry standard
- Supports third-party authentication
- Secure
- Works with microservices

**Cons:**
- More complex than JWT
- Requires OAuth server
- May be overkill for POC-2
- Steeper learning curve

**Decision:** Not chosen for POC-2 - Too complex for POC-2. Can add OAuth later if needed.

---

### 3. API Keys

**Pros:**
- Simple to implement
- Easy to revoke
- Works with microservices

**Cons:**
- Less secure than JWT
- No expiration (unless manually managed)
- Not suitable for user authentication
- More suitable for service-to-service auth

**Decision:** Not chosen - Not suitable for user authentication. May use for service-to-service auth later.

---

### 4. JWT with Refresh Tokens (Chosen)

**Pros:**
- Stateless (works with microservices)
- Scalable (no session storage)
- Industry standard
- Secure (when properly implemented)
- Works with frontend
- RBAC support

**Cons:**
- Harder to revoke (but refresh tokens can be revoked)
- Token size (but acceptable)
- Need to handle token expiration

**Decision:** Chosen - Best balance of simplicity, security, and scalability for POC-2.

---

## Trade-offs

### Pros

- ✅ **Stateless** - No server-side session storage
- ✅ **Scalable** - Works across service instances
- ✅ **Industry Standard** - Widely used, battle-tested
- ✅ **Secure** - When properly implemented
- ✅ **Works with Frontend** - Frontend can store tokens
- ✅ **RBAC Support** - Can include role in JWT payload

### Cons

- ⚠️ **Token Revocation** - Harder to revoke (but refresh tokens can be revoked)
- ⚠️ **Token Size** - JWT tokens can be large (but acceptable)
- ⚠️ **Token Expiration** - Need to handle token expiration and refresh

---

## Consequences

### Positive

- ✅ **Scalability** - No session storage, works across service instances
- ✅ **Microservices-Friendly** - Stateless, works with microservices
- ✅ **Security** - Industry-standard authentication
- ✅ **Developer Experience** - Simple to implement and use
- ✅ **Frontend Integration** - Works seamlessly with frontend

### Negative

- ⚠️ **Token Revocation** - Harder to revoke access tokens (but refresh tokens can be revoked)
- ⚠️ **Token Management** - Need to handle token expiration and refresh

### Neutral

- 🔄 **Security** - JWT is secure when properly implemented (short-lived tokens, refresh tokens)
- 🔄 **Performance** - JWT validation is fast (no database lookup for access tokens)

---

## Implementation Notes

- Use `jsonwebtoken` library (9.x)
- Access token: 15 minutes expiration
- Refresh token: 7 days expiration, stored in database
- Include user ID, email, and role in JWT payload
- Use secure secret for signing
- Implement token refresh endpoint
- Revoke refresh tokens on logout

**Token Structure:**

```typescript
interface JWTPayload {
  userId: string;
  email: string;
  role: 'ADMIN' | 'CUSTOMER' | 'VENDOR';
  iat: number;
  exp: number;
}
```

**Implementation:**

```typescript
import jwt from 'jsonwebtoken';

// Generate access token
const accessToken = jwt.sign(
  { userId: user.id, email: user.email, role: user.role },
  process.env.JWT_SECRET!,
  { expiresIn: '15m' }
);

// Generate refresh token
const refreshToken = jwt.sign(
  { userId: user.id },
  process.env.JWT_REFRESH_SECRET!,
  { expiresIn: '7d' }
);

// Verify token
const decoded = jwt.verify(token, process.env.JWT_SECRET!);
```

---

## Security Considerations

- ✅ **Short-lived access tokens** - 15 minutes expiration
- ✅ **Refresh tokens** - Stored in database, can be revoked
- ✅ **Secure secrets** - Use strong, random secrets
- ✅ **HTTPS** - Use HTTPS in production (POC-3)
- ✅ **Token storage** - Frontend stores tokens securely
- ✅ **Token validation** - Validate tokens on every request

**Reference:** See `docs/security-strategy-banking.md` for comprehensive security strategy.

---

## Migration Path

### POC-2 → POC-3

- Continue with JWT
- Add HTTPS (POC-3)
- Enhance token security

### POC-3 → MVP

- Continue with JWT
- Add OAuth 2.0 if needed for third-party authentication
- Enhance token management

---

## Related Decisions

- **ADR-0001: Use Express Framework** - JWT middleware for Express
- Frontend authentication (independent but related)
- Security strategy (comprehensive security approach)

---

## References

- [JWT.io](https://jwt.io/) - JWT documentation
- [jsonwebtoken npm package](https://www.npmjs.com/package/jsonwebtoken)
- `docs/security-strategy-banking.md` - Comprehensive security strategy
- `docs/backend-poc2-architecture.md` - Architecture documentation
- `docs/backend-poc2-tech-stack.md` - Tech stack documentation

---

**Last Updated:** 2026-01-XX

