# ADR 004: JWT-based Authentication

**Date**: 2026-01-13  
**Status**: Accepted

## Context

The application needs user authentication. Options:

1. **JWT (JSON Web Tokens)** - Stateless tokens
2. **Session-based** - Server-side sessions with cookies
3. **OAuth2 only** - Delegate to external providers

## Decision

**Use JWT tokens for API authentication with email/password login.**

Architecture:
```
┌────────┐  POST /login   ┌─────────┐
│Frontend│ ─────────────► │ Backend │
└────────┘                └─────────┘
    │                          │
    │    { token: "eyJ..." }   │
    │ ◄──────────────────────  │
    │                          │
    │  Authorization: Bearer   │
    │ ─────────────────────►   │
    │                          │
```

## Token Structure

```json
{
  "sub": "123",           // User ID
  "email": "user@example.com",
  "role": "USER",         // USER or ADMIN
  "emailVerified": true,
  "iat": 1704067200,      // Issued at
  "exp": 1704153600       // Expires (24h)
}
```

## Consequences

### Pros
- **Stateless**: No session storage needed on server
- **Scalable**: Works with multiple backend instances
- **Mobile-friendly**: Easy to use in mobile apps
- **Self-contained**: Token carries user info (no DB lookup per request)

### Cons
- **Token size**: Larger than session ID (~500 bytes)
- **No revocation**: Can't invalidate individual tokens (until expiry)
- **Secret management**: Must secure JWT secret

### Security Measures

1. **HTTPS only**: Tokens never sent over HTTP
2. **Short expiry**: 24 hours (configurable)
3. **Secure secret**: Min 32 characters, from environment variable
4. **HttpOnly consideration**: Token in localStorage (SPA pattern)

## Implementation

```java
// JwtUtil.java - Token generation
public String generateToken(User user) {
    return Jwts.builder()
        .subject(user.getId().toString())
        .claim("email", user.getEmail())
        .claim("role", user.getRole().name())
        .claim("emailVerified", user.isEmailVerified())
        .issuedAt(Date.from(now))
        .expiration(Date.from(now.plusMillis(expirationMs)))
        .signWith(secretKey)
        .compact();
}
```

```typescript
// Frontend - Token storage
localStorage.setItem('token', response.token);

// API calls
headers: {
  'Authorization': `Bearer ${token}`
}
```

## Security Flow

```
Registration → Email Verification → Login → JWT → Access Protected Routes
                     │
                     ▼
              Password Reset (if needed)
```

## Future Considerations

- **Refresh tokens**: For longer sessions without re-login
- **OAuth2 integration**: Google/GitHub login
- **2FA**: TOTP-based two-factor authentication
- **Token blacklist**: Redis-based revocation for logout

## References

- [JWT.io](https://jwt.io/)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)


