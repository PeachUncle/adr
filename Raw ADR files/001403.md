# ADR: Authentication Model Alignment (Bearer vs httpOnly Cookies)

- Status: Accepted
- Date: 2025-08-18
- Owners: khalil

## Context

The current client stores JWTs in `localStorage` (`client/src/api/axios.ts`), which is susceptible to XSS. The server (`server/src/app.ts`) already integrates CSRF protection via `csurf` and is well-positioned to support cookie-based auth with proper SameSite and Secure attributes. To meet our security goals (CSP tightened, secrets management, CSRF), we should align our auth model end-to-end.

## Options

- Option A: Bearer tokens in Authorization header
  - Pros: Simple to reason about; widely used in APIs; no CSRF concern if cookies are not used for auth.
  - Cons: Storing tokens in `localStorage` is vulnerable to XSS; rotating and revoking is typically client-managed; more leak-prone in browser contexts.

- Option B: httpOnly, Secure cookies + CSRF token
  - Pros: Tokens are not accessible to JS (httpOnly); aligns with existing `csurf` middleware; reduces XSS exfiltration risk; simplifies client code (no manual header management for auth token).
  - Cons: Requires CSRF token endpoint and client header (`x-csrf-token`); must configure CORS and SameSite appropriately for local dev and production.

## Decision

Choose Option B: httpOnly, Secure cookies for access/refresh tokens, coupled with CSRF tokens for state-changing requests.

## Consequences / Implementation Plan

Server (Express):
- Issue `access_token` (short-lived) and `refresh_token` (longer-lived) as httpOnly, Secure cookies.
- Set cookie attributes:
  - access: `httpOnly`, `secure` (prod), `sameSite=strict` (prod) or `lax` (dev), `path=/`.
  - refresh: same as above, possibly `path=/auth/refresh`.
- Add `/auth/csrf` endpoint to return `{ csrfToken }` from `csurf` for client usage.
- Add `/auth/refresh` route implementing refresh token rotation and revocation list.
- Update auth middleware to read tokens from cookies instead of `Authorization` header (preserve backwards compatibility temporarily behind a flag/env).
- Update CORS to allow credentials and ensure allowed origins are explicitly configured (already set to `credentials: true`).

Client (React):
- Remove storing JWT in `localStorage`.
- Configure Axios instance to `withCredentials: true`.
- On app start (and before mutating requests), fetch CSRF token from `/auth/csrf` and set header `x-csrf-token` via Axios interceptor.
- Adjust login/logout flows to rely on cookies being set/cleared by the server; stop attaching Bearer token manually.

Data Model & Security:
- Implement refresh token rotation: issue new refresh token on each refresh; store token hash server-side; maintain a revoke list; invalidate on reuse detection.
- Consider RS256 only in production (keys via env or secrets manager) and enforce.

Migration Strategy:
- Phase 1 (compat): Support both Bearer and cookie auth based on env flag `AUTH_MODE` (default cookie in prod).
- Phase 2: Remove Bearer path from the client and disable in server for prod.

Testing & Ops:
- Add integration tests covering login, CSRF token retrieval, refresh workflow, logout, and revocation.
- Update CI to run the new tests; ensure CORS + cookies behave in dev (localhost) and prod.

## Alternatives Considered
- Double Submit Cookie for CSRF without `csurf` – viable but `csurf` is already integrated and sufficient.
- Same-origin SPA + backend to avoid CORS altogether – possible in future, but current architecture uses separate dev hosts.

## References
- `server/src/app.ts` (CSRF and CORS)
- `server/src/middleware/auth.ts` (Auth handling)
- `client/src/api/axios.ts` (Token storage and interceptors)
