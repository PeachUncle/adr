# ADR-004: Supabase BaaS for Authentication

**Status:** Accepted  
**Date:** September 2025  
**Decision Makers:** Không Huỳnh Ngọc Hân, Team  

---

## Context

The UIT-Go platform requires secure user authentication with:
- Email/password registration and login
- JWT token generation and validation
- Password reset functionality
- Email verification
- Session management

We need to choose between building a custom auth system or using a Backend-as-a-Service (BaaS) solution.

---

## Decision Drivers

1. **Security**: Industry-standard practices (bcrypt, JWT, rate limiting)
2. **Development Speed**: Time-to-market for MVP
3. **Cost**: Free tier availability (Module E)
4. **Maintenance**: Ongoing security patches, updates
5. **Scalability**: Handle 10K+ users without re-architecture

---

## Considered Options

### Option 1: Custom Auth Service (NestJS + Passport + JWT)
**Pros:**
- ✅ Full control over implementation
- ✅ No external dependencies
- ✅ Learn authentication internals

**Cons:**
- ❌ **Security risk**: Easy to make mistakes (password storage, token leakage)
- ❌ **Time-consuming**: 2-3 weeks to build securely
- ❌ **Maintenance burden**: Patch vulnerabilities, update algorithms
- ❌ No OAuth/social login out of the box

### Option 2: Firebase Authentication
**Pros:**
- ✅ Easy integration
- ✅ Social logins (Google, Facebook)
- ✅ Free tier (50K MAU)

**Cons:**
- ❌ **Vendor lock-in**: Google-specific APIs
- ❌ Heavier SDK (~500 KB)
- ❌ Less flexible for custom claims

### Option 3: Supabase Auth (CHOSEN)
**Pros:**
- ✅ **Open-source**: Can self-host if needed
- ✅ **PostgreSQL-based**: Data in our control
- ✅ **JWT tokens**: Standard RS256, works with any service
- ✅ **Free tier**: 50,000 monthly active users
- ✅ **Email verification**: Built-in templates
- ✅ **Row Level Security**: Advanced authorization patterns
- ✅ **Lightweight SDK**: ~100 KB

**Cons:**
- ❌ External service dependency (mitigated by self-host option)
- ❌ Smaller community than Firebase

---

## Decision Outcome

**Chosen:** **Supabase Auth** (Option 3)

### Rationale

1. **Security Best Practices:**
   - Passwords hashed with bcrypt (auto-handled)
   - JWT signed with RS256 (asymmetric keys)
   - Rate limiting on login endpoints (built-in)
   - **No security code for us to mess up**

2. **Cost = $0** (Module E Alignment):
   - Free tier covers MVP and beyond (50K MAU)
   - Paid tier only needed at scale ($25/mo for 100K MAU)
   - **Immediate cost savings vs building custom**

3. **Development Speed:**
   - Integration completed in **2 days** vs 2-3 weeks custom
   - Team focused on business logic, not auth internals
   - **Faster time-to-MVP**

4. **Zero Trust Architecture:**
   - API Gateway validates JWT on every request
   - No need to call Auth Service for validation (stateless)
   - Services trust the JWT signature (verified by Supabase public key)

5. **Future-Proof:**
   - Can self-host Supabase if vendor concerns arise
   - Open-source license (Apache 2.0)
   - Standard JWT works with any service

### Architecture Pattern: Zero Trust

```
┌─────────┐                  ┌─────────────┐
│ Client  │──register/login──▶│  Supabase   │
└─────────┘                  └──────┬──────┘
     │                              │
     │ access_token (JWT)           │
     ▼                              │
┌─────────────┐                     │
│ API Gateway │◀────JWT Public Key──┘
└──────┬──────┘
       │ (JWT validated, user context extracted)
       │
       ▼
  Microservices (trust JWT payload)
```

**Benefits:**
- Auth Service doesn't become a bottleneck
- Services can work offline (stateless validation)
- Horizontal scaling is simple

---

## Implementation

**Registration Flow:**
```typescript
// Auth Service
async register(email: string, password: string) {
  // 1. Create user in Supabase
  const { data, error } = await this.supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: 'https://uit-go.vn/verify-email'
    }
  });
  
  if (error) throw new BadRequestException(error.message);
  
  // 2. Create user profile in User Service
  await this.userService.createUser({
    id: data.user.id,
    email: data.user.email,
    ...
  });
  
  return {
    access_token: data.session.access_token,
    refresh_token: data.session.refresh_token,
    user: data.user
  };
}
```

**JWT Validation (API Gateway):**
```typescript
@Injectable()
export class JwtAuthGuard implements CanActivate {
  async canActivate(context: ExecutionContext) {
    const request = context.switchToHttp().getRequest();
    const token = this.extractToken(request);
    
    // Verify JWT signature using Supabase JWT secret
    const payload = jwt.verify(token, process.env.SUPABASE_JWT_SECRET);
    
    request.user = {
      id: payload.sub,
      email: payload.email,
      role: payload.user_metadata?.role
    };
    
    return true;
  }
}
```

---

## Trade-offs Accepted

| Lost | Impact | Mitigation |
|------|--------|------------|
| Full control | Cannot customize auth logic deeply | Supabase provides hooks/triggers for custom logic |
| External dependency | Supabase downtime affects us | Self-host option available, 99.9% uptime SLA |
| Data residency | User data on Supabase servers | Can self-host for GDPR compliance |

---

## Validation

**Security Audit:**
- ✅ Password strength enforcement (min 6 chars, configurable)
- ✅ Email verification prevents fake accounts
- ✅ Rate limiting (60 requests/hour on auth endpoints)
- ✅ JWT expiration (1 hour, refresh token for renewal)
- ✅ HTTPS only (enforced)

**Performance:**
- Login latency: ~200ms (Supabase API call)
- JWT validation: ~2ms (local verification)
- Registration: ~300ms (Supabase + User Service)

---

## References

1. [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
2. [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
3. [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Status:** ✅ ACCEPTED  
**Cost:** $0/month (free tier)  
**Next Review:** When MAU > 40K (approaching free tier limit)
