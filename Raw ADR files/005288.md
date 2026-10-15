# ADR-004: Use JWT with Refresh Tokens for Authentication

## Status

✅ **Accepted**

**Date:** 27. Oktober 2025

## Context

Die AI-Freelancer-Plattform braucht Authentication für:

- User Login/Logout (Freelancer, Firmen, Admin)
- Session Management (7 Tage "Remember Me")
- API Authorization (Protected Endpoints)
- Security (DSGVO, Password Security)

**Requirements:**

- Secure (bcrypt Password Hashing, Token Expiration)
- Stateless (Horizontal Scaling möglich)
- Long-lived Sessions (7 Tage)
- Token Refresh (ohne Re-Login)

## Decision

Ich verwende **JWT (JSON Web Tokens) mit Refresh Tokens** via **NextAuth.js v5**.

### Authentication Flow

```
1. User submits email + password
   ↓
2. Server validates credentials (bcrypt.compare)
   ↓
3. Server generates:
   - Access Token (JWT, 15 min) → Stored in Memory
   - Refresh Token (JWT, 7 days) → Stored in HTTP-only Cookie
   ↓
4. Client sends Access Token in requests: Authorization: Bearer <token>
   ↓
5. Access Token expired? → Use Refresh Token to get new Access Token
   ↓
6. Refresh Token expired? → User must re-login
```

## Rationale

### Why JWT?

**Stateless:**

- ✅ No server-side session storage
- ✅ Horizontal scaling easy (no session-stickiness)
- ✅ Works with serverless (AWS ECS, Lambda)

**Self-contained:**

- ✅ Token contains user info (userId, role)
- ✅ No DB lookup on every request (fast)

**Standard:**

- ✅ Well-established (RFC 7519)
- ✅ Libraries available (jsonwebtoken, jose)

### Why Refresh Tokens?

**Short-lived Access Tokens (15 min):**

- ✅ Security: Stolen token is useless after 15 min
- ✅ Revocation: Refresh Token can be revoked

**Long-lived Refresh Tokens (7 days):**

- ✅ UX: User doesn't have to re-login every 15 min
- ✅ Security: Stored in HTTP-only Cookie (XSS-protected)

### Why NextAuth.js?

**Pros:**

- ✅ Next.js-native (built for App Router)
- ✅ Handles JWT automatically
- ✅ Providers support (Email/Password, Google, GitHub, etc.)
- ✅ Session management built-in
- ✅ CSRF protection

**Cons:**

- ❌ Abstraction (weniger Kontrolle)
- ❌ V5 ist noch Beta (aber stable genug)

**Alternatives:**

- Custom JWT implementation (mehr Arbeit)
- Lucia (neue Library, kleineres Ecosystem)

## Implementation

### NextAuth.js Configuration

```typescript
// src/lib/auth.ts
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { prisma } from './db';
import bcrypt from 'bcryptjs';
import { z } from 'zod';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    CredentialsProvider({
      credentials: {
        email: { type: 'email' },
        password: { type: 'password' },
      },
      async authorize(credentials) {
        // Validate input
        const parsed = z
          .object({
            email: z.string().email(),
            password: z.string().min(8),
          })
          .safeParse(credentials);

        if (!parsed.success) return null;

        // Find user
        const user = await prisma.user.findUnique({
          where: { email: parsed.data.email },
          include: {
            freelancerProfile: true,
            companyProfile: true,
          },
        });

        if (!user) return null;

        // Check email verification
        if (!user.emailVerified) return null;

        // Verify password
        const valid = await bcrypt.compare(parsed.data.password, user.passwordHash);

        if (!valid) return null;

        // Update last login
        await prisma.user.update({
          where: { id: user.id },
          data: { lastLogin: new Date() },
        });

        return {
          id: user.id,
          email: user.email,
          role: user.role,
          profileId: user.freelancerProfile?.id || user.companyProfile?.id,
        };
      },
    }),
  ],
  session: {
    strategy: 'jwt',
    maxAge: 7 * 24 * 60 * 60, // 7 days
  },
  jwt: {
    maxAge: 15 * 60, // 15 minutes (access token)
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.userId = user.id;
        token.role = user.role;
        token.profileId = user.profileId;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.userId;
      session.user.role = token.role;
      session.user.profileId = token.profileId;
      return session;
    },
  },
  pages: {
    signIn: '/login',
    signOut: '/logout',
    error: '/error',
  },
});
```

### Password Hashing

```typescript
// Registration
import bcrypt from 'bcryptjs';

const passwordHash = await bcrypt.hash(password, 12); // Cost factor 12

await prisma.user.create({
  data: {
    email,
    passwordHash,
    role: 'FREELANCER',
  },
});
```

### Token Structure

```typescript
// Access Token (JWT)
{
  "userId": "uuid-here",
  "email": "user@example.com",
  "role": "FREELANCER",
  "profileId": "uuid-here",
  "iat": 1234567890,
  "exp": 1234568790 // 15 minutes later
}

// Refresh Token (stored in HTTP-only cookie)
// Managed automatically by NextAuth.js
```

### Protected API (tRPC)

```typescript
// src/server/trpc.ts
export const protectedProcedure = publicProcedure.use(async ({ ctx, next }) => {
  const session = await auth(); // NextAuth helper

  if (!session || !session.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }

  return next({
    ctx: {
      session: session,
    },
  });
});
```

## Consequences

### Positive

1. **Secure**
   - bcrypt (cost 12) → Brute-force-resistent
   - Short-lived Access Tokens → Stolen token useless after 15min
   - HTTP-only Cookies → XSS-protected Refresh Tokens

2. **Scalable**
   - Stateless (no session storage)
   - Horizontal scaling works

3. **Good UX**
   - 7-day sessions ("Remember Me")
   - Silent token refresh (no re-login)

### Negative

1. **Token Revocation Complex**
   - JWT kann nicht direkt revoked werden
   - **Mitigation:** Blacklist in DB (später) oder Short-lived Tokens

2. **Token Size**
   - JWT ist größer als Session-ID (300-500 bytes)
   - **Mitigation:** Akzeptabel für Produktivität

## Security Measures

✅ **Password Security:**

- bcrypt (cost 12)
- Min. 8 chars, 1 number, 1 special char
- Rate limiting: 5 login attempts / 15 min

✅ **Token Security:**

- HTTPS only
- HTTP-only Cookies (Refresh Token)
- SameSite=Strict (CSRF protection)
- Token expiration (15 min / 7 days)

✅ **DSGVO:**

- Password reset flow (1h token expiration)
- User can delete account (delete tokens)

## Follow-up Actions

- [x] NextAuth.js installieren
- [x] Auth Config erstellen
- [ ] Email Verification Flow implementieren
- [ ] Password Reset Flow implementieren
- [ ] Rate Limiting auf Login-Route

## References

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [bcrypt](https://github.com/kelektiv/node.bcrypt.js)

---

**Author:** Max Mustermann
**Date:** 27. Oktober 2025
**Status:** Accepted
