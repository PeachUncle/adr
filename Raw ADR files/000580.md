# ADR-003: JWT Authentication

## Status

**Accepted** - January 2024

## Context

We need a secure and scalable authentication mechanism for the JobPilot AI Platform that:

- Works across multiple services (microservices architecture)
- Supports web, mobile, and browser extension clients
- Enables stateless authentication
- Provides reasonable security
- Scales horizontally
- Supports token refresh without re-authentication
- Works with OAuth providers

Authentication options considered:
1. Session-based authentication
2. JWT (JSON Web Tokens)
3. OAuth 2.0 only
4. API Keys

## Decision

We will use **JWT (JSON Web Tokens)** for authentication with the following design:

### Token Structure

**Access Token**:
- Short-lived (15 minutes)
- Contains user ID, email, role
- Used for API authentication
- Stored in memory (not localStorage)

**Refresh Token**:
- Long-lived (7 days)
- Opaque token stored in Redis
- Used to obtain new access tokens
- Stored in httpOnly cookie or secure storage

### Implementation Details

```typescript
// Access Token Payload
{
  userId: 'uuid',
  email: 'user@example.com',
  role: 'user' | 'premium' | 'admin',
  iat: timestamp,
  exp: timestamp
}

// Refresh Token
{
  tokenId: 'uuid',
  userId: 'uuid',
  iat: timestamp,
  exp: timestamp
}
```

### Token Lifecycle

1. **Login**: User provides credentials
2. **Token Generation**: Both access and refresh tokens generated
3. **Access Token Usage**: Included in Authorization header
4. **Token Refresh**: Use refresh token to get new access token
5. **Logout**: Invalidate refresh token in Redis

### Security Measures

1. **Short-lived access tokens** - Limit exposure window
2. **Refresh token rotation** - New refresh token on each refresh
3. **Token blacklisting** - Store invalidated tokens in Redis
4. **Secure token storage** - httpOnly cookies for web, secure storage for mobile
5. **HTTPS only** - All token transmission over HTTPS
6. **Token signing** - HS256 algorithm with strong secret

## Consequences

### Positive

1. **Stateless**: No server-side session storage needed
   - Services can scale horizontally easily
   - No session synchronization across instances

2. **Microservices Friendly**: Token verified independently by each service
   - No central session store dependency
   - Services remain decoupled

3. **Multi-Client Support**: Works across web, mobile, extension
   - Same authentication mechanism
   - Consistent user experience

4. **Performance**: Fast token verification
   - No database lookup on each request
   - Cryptographic verification only

5. **Self-Contained**: Token contains user information
   - Reduces database queries
   - User context available immediately

6. **Standard**: Industry-standard approach
   - Well-documented
   - Extensive library support
   - Security best practices established

### Negative

1. **Token Size**: JWTs are larger than session IDs
   - Every request includes ~200-500 bytes
   - Bandwidth overhead

2. **Token Revocation**: Difficult to invalidate access tokens
   - Mitigation: Short expiration time (15 min)
   - Maintain token blacklist in Redis

3. **Secret Management**: JWT secret must be secured
   - Compromise of secret = all tokens compromised
   - Must use strong secrets
   - Rotate secrets periodically

4. **Token Theft**: If stolen, valid until expiration
   - Mitigation: Short expiration + HTTPS only
   - Implement refresh token rotation

5. **Payload Size Limits**: Can't store too much data
   - Keep payload minimal
   - Store extended data in database

## Alternatives Considered

### 1. Session-Based Authentication

**Pros**:
- Simple to implement
- Easy to revoke sessions
- Smaller cookie size
- Server controls session lifetime

**Cons**:
- Requires centralized session store
- Difficult to scale horizontally
- Session synchronization across instances
- Not microservices-friendly
- Sticky sessions or session replication needed

**Why Rejected**: Doesn't scale well with microservices architecture.

### 2. OAuth 2.0 Only

**Pros**:
- Industry standard
- Delegates authentication to providers
- Good for social login
- No password management

**Cons**:
- Requires users to have OAuth provider accounts
- Dependency on external services
- More complex for simple email/password auth
- Vendor lock-in potential

**Why Rejected**: We need email/password auth in addition to OAuth. JWT can work with both.

### 3. API Keys

**Pros**:
- Simple to implement
- Good for service-to-service auth
- Easy to rotate
- No expiration needed

**Cons**:
- Not suitable for user authentication
- Requires secure storage
- Manual rotation process
- No built-in expiration

**Why Rejected**: Not appropriate for user-facing authentication.

### 4. Opaque Tokens

**Pros**:
- Can be revoked immediately
- No information disclosure
- Smaller token size

**Cons**:
- Requires database lookup on every request
- Centralized token store needed
- Performance impact
- Not stateless

**Why Rejected**: Doesn't meet our stateless requirement.

## Implementation Guidelines

### Token Generation

```typescript
import * as jwt from 'jsonwebtoken';

// Generate access token
const accessToken = jwt.sign(
  {
    userId: user.id,
    email: user.email,
    role: user.role,
  },
  process.env.JWT_SECRET,
  { expiresIn: '15m' }
);

// Generate refresh token
const refreshToken = jwt.sign(
  {
    tokenId: uuid(),
    userId: user.id,
  },
  process.env.JWT_REFRESH_SECRET,
  { expiresIn: '7d' }
);

// Store refresh token in Redis
await redis.set(
  `refresh_token:${refreshToken.tokenId}`,
  user.id,
  'EX',
  7 * 24 * 60 * 60
);
```

### Token Verification

```typescript
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: process.env.JWT_SECRET,
      ignoreExpiration: false,
    });
  }

  async validate(payload: any) {
    return {
      userId: payload.userId,
      email: payload.email,
      role: payload.role,
    };
  }
}
```

### Token Refresh

```typescript
async refreshTokens(refreshToken: string) {
  // Verify refresh token
  const payload = jwt.verify(
    refreshToken,
    process.env.JWT_REFRESH_SECRET
  );

  // Check if token exists in Redis
  const userId = await redis.get(`refresh_token:${payload.tokenId}`);
  if (!userId) {
    throw new UnauthorizedException('Invalid refresh token');
  }

  // Delete old refresh token
  await redis.del(`refresh_token:${payload.tokenId}`);

  // Generate new tokens
  const user = await this.userService.findById(userId);
  return this.generateTokens(user);
}
```

### Token Storage (Client-Side)

**Web Application**:
```typescript
// Store refresh token in httpOnly cookie
res.cookie('refreshToken', refreshToken, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 7 * 24 * 60 * 60 * 1000
});

// Store access token in memory (Redux/Context)
// Do NOT store in localStorage (XSS vulnerability)
```

**Mobile Application**:
```typescript
// Use secure storage
import * as SecureStore from 'expo-secure-store';

await SecureStore.setItemAsync('accessToken', accessToken);
await SecureStore.setItemAsync('refreshToken', refreshToken);
```

## Security Best Practices

1. **Strong Secrets**: Use 256-bit random secrets
   ```bash
   openssl rand -hex 32
   ```

2. **HTTPS Only**: Never transmit tokens over HTTP

3. **Token Rotation**: Rotate refresh tokens on each use

4. **Token Blacklist**: Maintain blacklist for logout
   ```typescript
   await redis.set(
     `blacklist:${tokenId}`,
     '1',
     'EX',
     tokenExpirationTime
   );
   ```

5. **Rate Limiting**: Limit login and refresh attempts
   ```typescript
   @UseGuards(ThrottlerGuard)
   @Throttle(5, 60) // 5 requests per minute
   async login() {}
   ```

6. **Validation**: Validate all token fields
   ```typescript
   if (!payload.userId || !payload.email) {
     throw new UnauthorizedException('Invalid token payload');
   }
   ```

## Migration Strategy

N/A - Greenfield project

## Testing Strategy

1. **Unit Tests**: Token generation and verification
2. **Integration Tests**: Full authentication flow
3. **Security Tests**: Token manipulation attempts
4. **Load Tests**: Token verification performance

## Monitoring

Track these metrics:
- Token generation rate
- Token verification failures
- Refresh token usage
- Invalid token attempts
- Token expiration events

## References

- [JWT.io](https://jwt.io/)
- [RFC 7519 - JSON Web Token](https://tools.ietf.org/html/rfc7519)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [Auth0 JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

## Related ADRs

- [ADR-001: Microservices Architecture](001-microservices-architecture.md)
- [ADR-008: Redis for Caching](008-redis-caching.md)

## Changelog

- 2024-01-15: Initial version - Accepted
- 2024-01-20: Added refresh token rotation
