# ADR-0003: Authentication Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Authentication Architecture" includes library, token strategy, middleware pattern).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 001-phase-2-web-app
- **Context:** Phase 2 requires secure multi-user authentication that works across Next.js frontend and FastAPI backend. Users must be able to sign up, log in, and maintain authenticated sessions. The backend must validate user identity for every API request and enforce user data isolation (users can only access their own tasks). Authentication must follow modern security practices (JWT tokens, bcrypt password hashing, HTTPS-only cookies) and support auto-refresh without manual user intervention.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Security-critical, affects all protected endpoints
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - NextAuth, Auth0, custom JWT evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Touches frontend, backend, database, and session management
-->

## Decision

We will adopt the following integrated authentication architecture:

- **Library:** Better Auth (framework-agnostic auth library)
- **Token Strategy:** JWT (JSON Web Tokens)
- **Frontend Auth:** Better Auth client with JWT plugin
- **Frontend Storage:** Zustand store with persist middleware (localStorage)
- **Backend Validation:** PyJWT middleware (FastAPI dependency injection)
- **Password Hashing:** Bcrypt (via Better Auth)
- **Session Management:** JWT auto-refresh when <1 day remains
- **User Isolation:** User ID extracted from validated JWT, used in all database queries
- **Middleware Pattern:** FastAPI dependency injection (`Depends(get_current_user)`)

### Authentication Flow

1. **Signup/Login:** User submits credentials to Better Auth API (`/api/auth/[...all]`)
2. **Token Issuance:** Better Auth validates credentials, returns JWT token + user data
3. **Frontend Storage:** Zustand store persists token + user to localStorage
4. **API Requests:** Axios interceptor injects `Authorization: Bearer <token>` header
5. **Backend Validation:** FastAPI middleware validates JWT, extracts user_id, injects into request
6. **Data Isolation:** All database queries filter by `user_id` from validated token
7. **Token Refresh:** Frontend auto-refreshes token when expiry <1 day (silent refresh)
8. **Logout:** Frontend clears Zustand store + redirects to login page

### Rationale

Better Auth is framework-agnostic, allowing it to bridge Next.js frontend and FastAPI backend. JWT tokens are stateless, reducing database lookups for every request. Better Auth handles password hashing, token signing, and user management, while PyJWT provides validation on the backend. Zustand persist ensures tokens survive page refreshes. This architecture enforces the "Authentication & Authorization First" constitutional principle by validating users at the middleware level before any business logic executes.

## Consequences

### Positive

- **Framework Agnostic:** Better Auth works with Next.js + FastAPI, unlike NextAuth (Next.js only)
- **Stateless Tokens:** JWTs don't require database lookups for validation, improving performance
- **Built-in Security:** Better Auth handles bcrypt hashing, CSRF protection, and token signing
- **TypeScript Support:** Better Auth client is fully typed, preventing auth-related bugs
- **Middleware Enforcement:** FastAPI dependency injection ensures no endpoint can bypass auth
- **Auto-Refresh:** Silent token refresh prevents session expiration during active use
- **User Isolation:** User ID embedded in JWT, enforced in all database queries
- **Testability:** Dependency injection makes testing authenticated endpoints straightforward
- **Session Persistence:** Zustand persist ensures users stay logged in across browser sessions
- **Global Error Handling:** Axios interceptor handles 401 (unauthorized) globally, logging out users automatically

### Negative

- **Token Revocation Complexity:** JWTs can't be invalidated before expiry (logout only clears client-side token)
  - *Mitigation:* Short token expiry (7 days) with refresh strategy
- **Token Size:** JWTs add ~200-500 bytes to every request header (acceptable overhead)
- **Better Auth Maturity:** Relatively new library (but actively maintained by reputable developer)
- **Refresh Race Conditions:** Concurrent requests during refresh could cause token mismatch
  - *Mitigation:* Axios request queue ensures only one refresh happens at a time
- **localStorage Security:** XSS attacks could steal tokens from localStorage
  - *Mitigation:* httpOnly cookies preferred but require server-side rendering; Phase 2 accepts localStorage risk with HTTPS enforcement
- **Middleware Performance:** JWT validation adds ~10-20ms per request (acceptable for <500ms p95 target)

## Alternatives Considered

### Alternative A: NextAuth.js
- **Pros:** Tight Next.js integration, built-in providers (Google, GitHub), session management
- **Cons:** Tightly coupled to Next.js, harder to integrate with FastAPI backend, requires adapter for database
- **Why Rejected:** NextAuth is Next.js-specific; our FastAPI backend would need to re-implement auth validation independently, leading to fragmented auth logic. Better Auth's framework-agnostic design allows unified auth strategy.

### Alternative B: Auth0 (Third-Party Service)
- **Pros:** Enterprise-grade security, hosted solution, supports OAuth providers
- **Cons:** Third-party dependency, costs money in production ($25/month after free tier), network dependency
- **Why Rejected:** Violates "deploy to free-tier services" constraint; introduces external dependency that could fail or require payment; Better Auth gives us full control.

### Alternative C: Custom JWT Implementation
- **Pros:** Full control, no dependencies, lightweight
- **Cons:** Security risks (implementing crypto correctly is hard), requires building signup/login/refresh logic, no password reset, no email verification
- **Why Rejected:** Security-critical code should use battle-tested libraries; building custom auth violates "don't reinvent the wheel" principle and increases attack surface.

### Token Storage Alternative: httpOnly Cookies
- **Pros:** Immune to XSS attacks (JavaScript can't access), more secure than localStorage
- **Cons:** Requires server-side rendering for initial auth check, complicates API deployment (CORS issues), harder to implement with Vercel edge functions
- **Why Rejected:** Phase 2 prioritizes rapid development; httpOnly cookies add deployment complexity. localStorage + HTTPS + short token expiry is acceptable risk for hackathon timeline.

## References

- Feature Spec: [specs/001-phase-2-web-app/spec.md](../../specs/001-phase-2-web-app/spec.md)
- Implementation Plan: [specs/001-phase-2-web-app/plan.md](../../specs/001-phase-2-web-app/plan.md)
- Research Notes: [specs/001-phase-2-web-app/research.md](../../specs/001-phase-2-web-app/research.md)
- Related ADRs: ADR-0001 (Frontend Stack - Zustand storage), ADR-0002 (Backend Stack - PyJWT validation)
- Context7 Research: Better Auth (/better-auth/better-auth)
- Constitution Principle: "Authentication & Authorization First" (constitution-prompt-phase-2.md)
