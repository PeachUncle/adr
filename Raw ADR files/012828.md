# ADR-006: Authentication Strategy

## Status

Accepted

## Context

We need an authentication mechanism for the Ohana Booking System with:

- Three user roles: Admin, Coordinator, Performer
- Separate frontend (Vue SPA) and backend (NestJS API)
- Phase 1: Admin/Coordinator only
- Phase 1.5: Add Performer logins

Requirements:

- Secure authentication
- Role-based authorization
- Works well with SPA + API architecture
- Reasonable token expiry
- Good DX (not overly complex)

## Decision Drivers

- **Architecture fit**: Frontend and backend on different domains/ports
- **Scalability**: Stateless auth scales horizontally
- **Security**: Industry-standard practices
- **Developer experience**: Reasonable complexity
- **NestJS ecosystem**: Well-supported patterns
- **Mobile-ready**: JWT works for future mobile apps

## Options Considered

### Option A: JWT with Refresh Tokens

**Flow:**

1. User logs in → receives access token (15min) + refresh token (7 days)
2. Access token sent with each API request
3. When access token expires, use refresh token to get new access token
4. Refresh token stored in httpOnly cookie (XSS protection)

**Pros:**

- ✅ **Stateless** - API doesn't need to store sessions
- ✅ **Scales horizontally** - no session store needed
- ✅ **Works across domains** - SPA and API can be on different origins
- ✅ **Industry standard** - well-understood pattern
- ✅ **Mobile-ready** - JWT works for future mobile apps
- ✅ **Refresh tokens** - balance security (short access tokens) with UX (don't re-login)
- ✅ **NestJS support** - `@nestjs/jwt` and `@nestjs/passport` built-in

**Cons:**

- ⚠️ **Token invalidation** - can't revoke tokens server-side (but short expiry mitigates)
- ⚠️ **Refresh token management** - need secure storage strategy

**Implementation:**

```tsx
// Access token payload
{
  sub: userId,
  email: '[user@example.com](mailto:user@example.com)',
  role: 'admin',
  iat: 1234567890,
  exp: 1234568790  // 15 minutes
}

// Refresh token stored in httpOnly cookie
// Access token stored in memory (Vue app state)
```

### Option B: Session-based (Cookies)

**Pros:**

- ✅ **Simpler** - traditional, well-understood
- ✅ **Revocable** - can invalidate sessions server-side
- ✅ **Built into NestJS** - `@nestjs/session`

**Cons:**

- ❌ **Stateful** - requires session store (Redis)
- ❌ **CORS complexity** - credentials across domains is tricky
- ❌ **Scaling** - sticky sessions or shared session store needed
- ❌ **Not mobile-friendly** - cookies don't work well in native apps

### Option C: OAuth2 (Auth0, Clerk, Supabase Auth)

**Pros:**

- ✅ **Managed service** - don't build auth yourself
- ✅ **Social logins** - Google, Facebook, etc.
- ✅ **Compliance** - handles security best practices

**Cons:**

- ❌ **Overkill** - only need email/password for internal tool
- ❌ **Cost** - paid service for something simple
- ❌ **Dependency** - reliant on third-party
- ❌ **Complexity** - OAuth flow is more complex for simple use case

## Decision

**We will use JWT with refresh tokens (Option A).**

### Implementation Details

**Backend (NestJS):**

```tsx
// Auth flow
POST /api/auth/login
  → Returns: { accessToken, user }
  → Sets httpOnly cookie: refreshToken

POST /api/auth/refresh
  → Reads refreshToken from cookie
  → Returns: { accessToken }

POST /api/auth/logout
  → Clears refreshToken cookie
```

**Frontend (Vue):**

```tsx
// Store access token in memory (Pinia)
const authStore = useAuthStore();
authStore.accessToken = [response.data](http://response.data).accessToken;

// Axios interceptor for automatic refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      await refreshAccessToken();
      return axios(error.config);
    }
    return Promise.reject(error);
  }
);
```

**Token Expiry:**

- Access token: **15 minutes** (security)
- Refresh token: **7 days** (UX balance)

**Security Measures:**

- Refresh token in httpOnly cookie (XSS protection)
- Access token in memory only (not localStorage - XSS risk)
- HTTPS required in production
- Refresh token rotation (issue new refresh token with each refresh)

### Rationale

1. **Architecture fit**: Perfect for separate SPA + API
2. **Scalability**: Stateless API can scale horizontally
3. **Security**: Short-lived access tokens + httpOnly refresh tokens
4. **Mobile-ready**: JWT works for future native apps
5. **NestJS native**: Built-in support via Passport + JWT

## Consequences

### Positive

- Stateless API - easy to scale, no session store needed
- Works across domains - frontend/backend can be on different origins
- Mobile-ready - same auth flow works for future mobile apps
- Security best practices - short access tokens, httpOnly refresh tokens
- Good UX - users stay logged in for 7 days
- Standard pattern - many examples and libraries

### Negative

- Cannot revoke access tokens server-side (but 15min expiry limits risk)
- Refresh token management adds complexity
- Need to handle token refresh in frontend

### Risks

- **Token theft**: If access token stolen, valid for 15 minutes
  - _Mitigation_: Short expiry, HTTPS only, don't store in localStorage
- **Refresh token theft**: If stolen from cookie, can generate access tokens
  - _Mitigation_: httpOnly cookie, token rotation, HTTPS, can blacklist refresh tokens
- **Logout doesn't immediately invalidate**: Access tokens valid until expiry
  - _Mitigation_: 15min expiry acceptable; can add token blacklist if needed

## Follow-up Actions

- [ ] Install NestJS packages: `@nestjs/jwt @nestjs/passport passport passport-jwt`
- [ ] Create `AuthModule` with JWT strategy
- [ ] Implement login endpoint (returns access + refresh tokens)
- [ ] Implement refresh endpoint
- [ ] Create `@UseGuards(JwtAuthGuard)` decorator for protected routes
- [ ] Create `@Roles()` decorator for role-based access
- [ ] Implement frontend auth store (Pinia)
- [ ] Create axios interceptor for automatic token refresh
- [ ] Add logout flow (clear refresh token cookie)
