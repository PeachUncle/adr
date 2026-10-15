# ADR-003: Authentication Mechanism

**Status**: Accepted
**Date**: 2025-10-22
**Decision Makers**: System Architecture Designer
**Context**: Secure user authentication and authorization for competitive ranking system

## Context and Problem Statement

Love Rank Pulse requires secure authentication to:
- Protect player accounts and personal data
- Ensure match results are submitted by authorized users
- Prevent unauthorized leaderboard manipulation
- Support both web and future mobile clients
- Provide scalable session management

## Decision Drivers

- **Security**: Industry-standard authentication practices
- **Scalability**: Stateless authentication for horizontal scaling
- **User Experience**: Seamless login/logout flow
- **Cross-Platform**: Support web and future mobile apps
- **Performance**: Minimal latency for auth checks
- **Compliance**: GDPR and data protection requirements

## Considered Options

### Option 1: JWT (JSON Web Tokens) ✅ SELECTED

**Architecture:**
```
Client Request → API Gateway → JWT Verification → Protected Route
                      ↓
                 JWT Secret (env)
```

**Implementation:**
- Access Tokens: Short-lived (15 minutes), no refresh
- Password Hashing: bcrypt with 12 rounds
- Token Storage: httpOnly cookies (web), secure storage (mobile)
- Token Rotation: Re-issue on refresh

**Pros:**
- Stateless authentication (no server-side session storage)
- Horizontal scaling without session synchronization
- Standard format (RFC 7519) with wide library support
- Cross-domain support for microservices
- Small payload size (~200-500 bytes)
- Self-contained claims reduce database lookups

**Cons:**
- Cannot revoke tokens before expiration (mitigation: short TTL)
- Slightly larger payload than session IDs
- Requires secure secret management

### Option 2: Session-Based Authentication

**Architecture:**
```
Client Request → API Gateway → Session Lookup (Redis) → Protected Route
```

**Pros:**
- Easy to revoke sessions server-side
- Smaller client-side storage (session ID only)
- Familiar implementation pattern

**Cons:**
- Requires centralized session store (Redis/database)
- Single point of failure without replication
- Higher latency for session lookups
- Complex horizontal scaling
- Increased infrastructure cost

### Option 3: OAuth 2.0 + Third-Party Providers

**Providers**: Auth0, Firebase Auth, Supabase Auth

**Pros:**
- Offload authentication complexity
- Social login support
- Built-in security features

**Cons:**
- External dependency (service outage risk)
- Monthly costs scale with active users
- Vendor lock-in
- Less control over auth flow

## Decision Outcome

**Chosen Option**: JWT (JSON Web Tokens)

### Justification

JWT provides the optimal balance of security, scalability, and developer control:

1. **Stateless Design**: No session storage eliminates scaling bottlenecks
2. **Industry Standard**: Well-vetted security model with extensive tooling
3. **Performance**: Fast verification without database lookups
4. **Cost Efficiency**: No third-party service fees
5. **Flexibility**: Full control over claims and expiration policies

### Implementation Details

**Token Structure:**
```typescript
interface JWTPayload {
  userId: string;       // Player ID from database
  username: string;     // Display name
  email: string;        // User email
  iat: number;          // Issued at timestamp
  exp: number;          // Expiration timestamp
}
```

**Security Configuration:**
```typescript
// /src/lib/auth.ts
const JWT_SECRET = process.env.JWT_SECRET; // 256-bit secret
const JWT_EXPIRES_IN = '15m';              // Access token TTL
const BCRYPT_ROUNDS = 12;                  // Password hashing rounds

export class AuthUtils {
  static generateToken(payload: JWTPayload): string {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
  }

  static verifyToken(token: string): JWTPayload {
    return jwt.verify(token, JWT_SECRET) as JWTPayload;
  }

  static async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, BCRYPT_ROUNDS);
  }
}
```

**Authentication Flow:**

1. **Registration:**
   ```
   Client → POST /api/auth/register
   Server → Hash password (bcrypt)
   Server → Create player record
   Server → Generate JWT
   Server → Return { token, user }
   ```

2. **Login:**
   ```
   Client → POST /api/auth/login { email, password }
   Server → Lookup player by email
   Server → Verify password (bcrypt.compare)
   Server → Generate JWT with player claims
   Server → Return { token, user }
   ```

3. **Protected Requests:**
   ```
   Client → GET /api/players/:id
            Authorization: Bearer <JWT>
   Server → Extract token from header
   Server → Verify JWT signature
   Server → Check expiration
   Server → Attach user to request
   Server → Process request
   ```

**Middleware Implementation:**
```typescript
// /src/api-gateway/middleware/authMiddleware.ts
export const authenticateJWT = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const token = AuthUtils.extractTokenFromHeader(req.headers.authorization);

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const payload = AuthUtils.verifyToken(token);
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
};
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## Consequences

### Positive
- **Scalability**: No shared session state enables horizontal scaling
- **Performance**: Fast auth verification without database lookups
- **Security**: Industry-standard JWT + bcrypt combination
- **Developer Experience**: Simple integration with existing tooling
- **Cost**: No third-party service fees

### Negative
- **Token Revocation**: Cannot invalidate tokens before expiration
  - **Mitigation**: Short TTL (15 minutes) limits exposure window
- **Secret Management**: JWT secret must be secured
  - **Mitigation**: Environment variables, never committed to repo
- **Token Theft**: Stolen tokens are valid until expiration
  - **Mitigation**: httpOnly cookies, HTTPS only, short TTL

### Security Measures

1. **Token Security:**
   - HTTPS-only transmission
   - httpOnly cookies prevent XSS theft
   - Short expiration (15 min)
   - Secure secret (256-bit minimum)

2. **Password Security:**
   - bcrypt with 12 rounds (computationally expensive)
   - No plaintext password storage
   - Password strength validation
   - Rate limiting on login attempts (5/15min)

3. **API Security:**
   - Rate limiting on auth endpoints
   - CORS whitelisting
   - Helmet.js security headers
   - Input validation and sanitization

### Risks and Mitigation

**Risk**: JWT secret compromise
**Mitigation**:
- Store in environment variables
- Rotate secret periodically
- Use key management service in production

**Risk**: Token theft via XSS
**Mitigation**:
- httpOnly cookies
- Content Security Policy headers
- Input sanitization

**Risk**: Brute force password attacks
**Mitigation**:
- bcrypt computational cost
- Rate limiting (5 attempts/15min)
- Account lockout after failed attempts

## Performance Considerations

**Token Verification Time:**
- JWT verification: ~1-2ms (cryptographic operation)
- No database lookup required
- Scales linearly with request volume

**Password Hashing Time:**
- bcrypt (12 rounds): ~200-300ms
- Acceptable for infrequent operations (login/register)
- Prevents brute force attacks

## Migration Path

**Future Enhancements:**
1. Refresh token support (7-day TTL)
2. Multi-factor authentication (TOTP)
3. Social login integration (Google, GitHub)
4. Email verification workflow
5. Password reset flow

## Testing Strategy

**Security Testing:**
- Token tampering detection
- Expired token rejection
- Invalid signature rejection
- Password hashing verification
- Rate limiting enforcement

**Integration Testing:**
- Registration flow
- Login flow
- Protected route access
- Token refresh
- Logout cleanup

## Related Decisions
- ADR-001: Database Selection (stores user credentials)
- ADR-002: ORM Selection (Prisma for user queries)
- ADR-004: Deployment Strategy (secret management)

## References
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [bcrypt Documentation](https://github.com/kelektiv/node.bcrypt.js)
- Implementation: `/workspaces/love-rank-pulse/src/lib/auth.ts`
- Middleware: `/workspaces/love-rank-pulse/src/api-gateway/middleware/authMiddleware.ts`
