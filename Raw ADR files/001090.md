# ADR-0003: Authentication Strategy

**Date:** 2025-11-27  
**Status:** Active  
**Deciders:** Core Team, Security Lead

---

## Context

Chef's Mind AI requires secure authentication and authorization for:

- **User Access:** Restaurant owners, chefs, managers
- **Role-Based Access:** Different permissions for different user types
- **OAuth Integration:** Seamless login via Google for better UX
- **API Security:** Protect backend routes from unauthorized access
- **Session Management:** Maintain user state across requests

### Requirements

1. **Easy Onboarding:** Users should be able to sign in with Google OAuth
2. **Role-Based Access Control (RBAC):** Different users have different permissions
   - `admin`: Full access to all features
   - `chef`: Menu creation, recipes, ordering
   - `accountant`: Cost analysis, reports, financial data
   - `viewer`: Read-only access
3. **Stateless API:** JWT tokens for API authentication
4. **Security:** Industry-standard OAuth 2.0 + JWT with proper validation

---

## Decision

**We will implement a hybrid authentication strategy:**

### Components

1. **Google OAuth 2.0** (`server/auth/google.ts`)
   - Primary authentication method for end users
   - Uses Passport.js Google Strategy
   - Callback handling and token exchange

2. **JWT Tokens** (`server/middleware/jwtAuth.ts`)
   - After successful OAuth, issue JWT tokens
   - Tokens contain: `userId`, `email`, `role`, `exp`
   - Short-lived access tokens (15min–1h)
   - Optional refresh tokens for extended sessions

3. **Session Management** (`server/session.ts`)
   - Express session for frontend-enhanced
   - Cookie-based sessions with secure flags
   - Session store (in-memory for dev, Redis for production)

4. **RBAC Middleware** (`server/middleware/rbac.ts`)
   - Protect routes based on user roles
   - Example: `/api/admin/*` requires `admin` role
   - Granular permissions per endpoint

### Authentication Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Redirected to Google OAuth consent screen
   ↓
3. Google redirects back with authorization code
   ↓
4. Backend exchanges code for Google tokens
   ↓
5. Backend creates user in DB (if new) or fetches existing
   ↓
6. Backend issues JWT token
   ↓
7. Frontend stores JWT in localStorage/cookie
   ↓
8. Every API request includes JWT in Authorization header
   ↓
9. Middleware validates JWT and extracts user info
   ↓
10. RBAC middleware checks role permissions
```

---

## Consequences

### Advantages

✅ **User Experience:** One-click Google sign-in, no password management  
✅ **Security:** OAuth 2.0 is industry-standard, JWT is stateless and scalable  
✅ **Flexibility:** RBAC allows fine-grained access control  
✅ **Multi-Frontend Support:** JWT works with both Vite client and Next.js enhanced  
✅ **Audit Trail:** JWTs contain user info for logging and tracing  

### Disadvantages

⚠️ **Complexity:** OAuth + JWT + RBAC increases setup complexity  
⚠️ **Token Management:** Refresh token rotation adds implementation overhead  
⚠️ **Revocation Challenges:** JWTs cannot be easily revoked (need blacklist or short expiry)  
⚠️ **Configuration Overhead:** Google OAuth requires app registration, redirect URLs, credentials  

### Risks

🔴 **Token Leakage:** If JWT is exposed (XSS, MITM), attacker gains access until expiry  
🔴 **OAuth Misconfiguration:** Incorrect redirect URIs can break authentication  
🟡 **Session vs JWT Confusion:** Two auth mechanisms (session for Next.js, JWT for API) may cause confusion  

---

## Alternatives Considered

### Alternative 1: Session-Only (No JWT)

- ✅ Simpler, no token management
- ❌ Doesn't work well with stateless APIs or mobile apps
- ❌ Requires sticky sessions in load-balanced environments

### Alternative 2: Firebase Auth

- ✅ Managed service, handles OAuth, JWT, RBAC
- ❌ Vendor lock-in
- ❌ Additional cost and external dependency

### Alternative 3: GitHub OAuth Only

- ✅ Simple for developer-focused apps
- ❌ Not suitable for restaurant/chef users (non-developers)

### Alternative 4: Username/Password Only

- ✅ Full control, no external dependencies
- ❌ Poor UX (password fatigue)
- ❌ Higher security risk (password breaches)

---

## Status

**Active** — Google OAuth + JWT + RBAC is implemented and in use.

### Implementation Details

**Configuration:**

- Google OAuth credentials stored in `.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- JWT secret stored in `.env`: `JWT_SECRET`
- Redirect URIs configured in Google Cloud Console

**Roles:**

- Default role: `viewer`
- Admin role assigned manually in database
- Role stored in `users` table, included in JWT claims

**Security Measures:**

- `httpOnly` cookies for session (prevents XSS)
- CORS configured to allow only trusted origins
- JWT expiry set to 1 hour
- Rate limiting on auth endpoints

### Documentation Needed

📌 **TODO:** Document Google OAuth setup process for new developers  
📌 **TODO:** Create RBAC permission matrix (which roles can access which endpoints)  
📌 **TODO:** Document JWT refresh token flow (if implemented)  

### Next Review

- **When:** After implementing refresh tokens or adding more OAuth providers
- **Trigger:** Security audit or compliance requirements
- **Action:** Review token expiry policies, add OAuth providers (GitHub, Microsoft)
