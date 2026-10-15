# ADR-001: Authentication Provider - NextAuth vs Clerk

## Status
Accepted

## Context
The blockchain snapshots service requires a robust authentication system that supports:
- Traditional email/password authentication
- Cosmos wallet authentication (Keplr)
- User tier management (free/premium)
- Future integration with the main BryanLabs website
- Cost-effective scaling to thousands of users

We evaluated two primary authentication solutions:
1. **NextAuth.js v5** - Open source authentication library
2. **Clerk** - Managed authentication service

## Decision
We chose **NextAuth.js v5** as our authentication provider.

## Rationale

### Cost Analysis
- **NextAuth**: $0 (open source)
- **Clerk**: $25/month base + $0.02 per monthly active user
  - For 5,000 MAU: ~$125/month ($1,500/year)
  - For 10,000 MAU: ~$225/month ($2,700/year)

### Technical Requirements

#### Cosmos Wallet Authentication
- **NextAuth**: Full control to implement custom Cosmos wallet provider
  ```typescript
  // Our current implementation works perfectly
  CredentialsProvider({
    id: "wallet",
    name: "Cosmos Wallet",
    async authorize(credentials) {
      // Custom signature verification
    }
  })
  ```
- **Clerk**: Would require webhooks and custom flows, adding complexity

#### Data Sovereignty
- **NextAuth**: All user data stored in our database (Prisma + SQLite/PostgreSQL)
- **Clerk**: User data stored on Clerk's servers, potential compliance issues for blockchain users

#### Future Integration
- **NextAuth**: Easy to share authentication between snapshots.bryanlabs.net and bryanlabs.dev
- **Clerk**: Would require separate Clerk organization or complex multi-domain setup

### Feature Comparison

| Feature | NextAuth | Clerk |
|---------|----------|-------|
| Email/Password Auth | ✅ Built | ✅ Built |
| Custom Auth (Wallet) | ✅ Easy | ⚠️ Workarounds |
| MFA/2FA | ⚠️ Manual | ✅ Built-in |
| User Management UI | ❌ Build yourself | ✅ Included |
| Session Management | ✅ JWT/Database | ✅ Managed |
| Rate Limiting | ⚠️ Add yourself | ✅ Built-in |
| Audit Logs | ⚠️ Add yourself | ✅ Built-in |
| Cost at Scale | ✅ Free | ❌ Expensive |
| Vendor Lock-in | ✅ None | ❌ High |

### Security Considerations
- **NextAuth**: We manage security updates but have full control
- **Clerk**: Managed security but introduces external dependency

## Consequences

### Positive
- Zero authentication costs regardless of user count
- Full control over authentication flow and user data
- Seamless Cosmos wallet integration
- Easier future integration with main website
- No vendor lock-in
- Already implemented and working well

### Negative
- We must handle security updates ourselves
- Need to build user management UI (already done)
- Manual implementation of advanced features if needed (MFA, audit logs)

### Mitigation Strategies
To address NextAuth limitations:
1. Implement rate limiting using Redis
2. Add audit logging for security events
3. Consider adding MFA support using libraries like `speakeasy`
4. Regular security audits of authentication code

## Future Considerations
If requirements change significantly, we could reconsider Clerk for:
- Enterprise B2B features (SAML, SSO)
- Compliance certifications (SOC2, HIPAA)
- Dedicated security team requirements

However, for a community-focused blockchain service, NextAuth remains the optimal choice.

## References
- [NextAuth.js Documentation](https://authjs.dev/)
- [Clerk Pricing](https://clerk.com/pricing)
- [Our Implementation](../authentication.md)
- Implementation files:
  - `/auth.ts` - Main auth configuration
  - `/auth.config.ts` - Auth middleware config
  - `/app/api/auth/[...nextauth]/route.ts` - Auth API routes

## Decision Date
2025-01-26

## Decision Makers
- Dan Bryan (Lead Developer)
- Based on snapshot service requirements and cost analysis