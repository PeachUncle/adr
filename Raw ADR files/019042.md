# ADR-0004: Frontend Authentication Architecture

- **Status:** Accepted
- **Date:** 2026-01-03
- **Feature:** 006-frontend-integration
- **Context:** Phase 2.4 frontend must authenticate users and communicate with the secured Phase 2.3 backend API. The backend expects JWT tokens with HS256 signatures containing `sub` (user_id) and `email` claims. We need to decide how to handle user authentication, session management, and JWT token generation on the frontend.

## Decision

We will use the following integrated authentication architecture:

- **Authentication Library**: Better Auth (installed dependency)
- **Auth State Management**: React Context + custom `useAuth` hook
- **JWT Generation**: Client-side HS256 token generation using `jose` library
- **Token Storage**: LocalStorage with auth context synchronization
- **Session Persistence**: Automatic restore on page load from stored token/user
- **Protected Routes**: Client-side redirect in dashboard page (middleware for future enhancement)

**Critical Integration**: The JWT secret (`BETTER_AUTH_SECRET`) MUST match the backend's `JWT_SECRET` to ensure token verification succeeds.

## Consequences

### Positive

- **Backend Compatible**: HS256 JWT with `sub` and `email` claims matches backend expectations exactly
- **Session Persistence**: Users remain logged in across browser refreshes
- **Unified Context**: Single source of truth for auth state throughout app
- **Simple Token Management**: Custom hook provides clean API for components
- **No Backend Changes**: All auth logic is frontend-side; backend JWT verification unchanged
- **Flexible**: Can extend to support token refresh, multi-tab sync in future

### Negative

- **Secret in Frontend**: JWT secret must be available to frontend (acceptable for demo/hackathon scope)
- **Client-Side Token Generation**: Less secure than server-issued tokens (production would use backend-issued JWTs)
- **LocalStorage Vulnerability**: XSS attacks could access stored tokens (mitigated by React's auto-escaping)
- **No Automatic Refresh**: Tokens expire after 24 hours; user must re-authenticate
- **Better Auth Underutilized**: Using Better Auth mainly for UI flows, not its full JWT plugin

## Alternatives Considered

**Alternative A: Better Auth JWT Plugin with JWKS**
- Pros: Standard asymmetric key verification, more secure
- Rejected: Backend expects HS256 with shared secret; would require backend changes (out of scope)

**Alternative B: NextAuth.js (Auth.js)**
- Pros: Mature library, extensive provider support, server-side sessions
- Rejected: More complex setup; Better Auth already installed; would add dependency

**Alternative C: Custom Auth without Library**
- Pros: Full control, no dependency
- Rejected: More boilerplate; Better Auth provides useful UI components and flows

**Alternative D: Backend-Issued JWTs Only**
- Pros: More secure; tokens never generated client-side
- Rejected: Would require new backend endpoint for token issuance (backend changes out of scope)

**Alternative E: Cookie-Based Sessions**
- Pros: Automatic CSRF protection, httpOnly cookies
- Rejected: Backend API expects Bearer tokens; would require backend auth flow changes

## References

- Feature Spec: [specs/006-frontend-integration/spec.md](../../specs/006-frontend-integration/spec.md)
- Implementation Plan: [specs/006-frontend-integration/plan.md](../../specs/006-frontend-integration/plan.md)
- Phase 2.3 Auth Spec: [specs/005-auth-integration/spec.md](../../specs/005-auth-integration/spec.md)
- Related ADRs: [ADR-0003](./0003-frontend-technology-stack.md)
- Research: [specs/006-frontend-integration/research.md](../../specs/006-frontend-integration/research.md)
