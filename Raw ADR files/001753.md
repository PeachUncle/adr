# ADR-002 — Authentication & Session Strategy (JWT RS256 with Refresh Rotation)

> **File:** docs/adr/ADR-002-authentication-token-strategy.md  
> **Purpose:** Decide the application-wide authentication and session strategy for FitVibe.

---

id: ADR-002
title: "Authentication & Session Strategy — JWT (RS256) with Refresh Token Rotation and Sliding Sessions"
status: "Accepted"
date: "2025-10-13"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
supersedes: []
links:

- PRD: "docs/1. Product Requirements Document.md#security--privacy"
- TDD: "docs/2. Technical Design Document v2.md#authentication-authorization"
- QA: "docs/3. Testing and Quality Assurance Plan.md#security-tests-and-slos"
- ADR-001: "docs/adr/ADR-001-api-versioning-policy.md"

---

## Context

FitVibe’s web SPA and future native clients require an authentication mechanism that is:

- **Secure by default** (privacy-by-design, GDPR-aligned)
- **Browser-friendly** (protect against XSS/CSRF)
- **Stateless for scale** (horizontal scaling across instances)
- **Revocable** (account/device compromise response)
- **Observable** (auditing, anomaly detection, SLOs)

We considered cookie-based server sessions (opaque IDs, Redis), opaque tokens, and JWT-based access + refresh flows. The platform will run behind a reverse proxy with TLS termination and expects multiple clients (SPA now; mobile in Phase 2).

## Decision

Adopt **JWT access tokens (RS256)** with **rotating refresh tokens** and **sliding session expiration**, using **HttpOnly, Secure cookies** for browser clients and **Authorization headers** for non-browser clients.

### Token Model

- **Access Token (AT)**: JWT (RS256), **short-lived** (10–15 min).  
  Claims: `iss`, `aud`, `sub`, `exp`, `iat`, `nbf`, `jti`, `sid`, `scope`, `roles`, `locale`.  
  Header includes `kid` for key rotation.
- **Refresh Token (RT)**: Opaque, **one-time-use rotating token** with **reuse detection**. Stored **hashed** in DB. Lifetime **up to 30 days** (configurable) subject to **max_session_age**.
- **Session**: Identified by `sid` stored with device metadata (UA, IP hash, platform, createdAt, lastUsedAt, revokedAt).

### Storage & Transport

- **Browser**:
  - `AT` in **HttpOnly, Secure, SameSite=Lax** cookie `at`, path `/`, domain app scope.
  - `RT` in **HttpOnly, Secure, SameSite=Strict** cookie `rt`, path `/auth/refresh`.
  - CSRF protection via **double-submit token** (header `X-CSRF-Token` matching a non-HttpOnly cookie) for **state-changing** requests.
- **Mobile/API clients**: Bearer `Authorization` header for `AT`; `RT` exchanged via refresh endpoint using client-auth or signed body.

### Rotation & Reuse Detection

- On each refresh:
  1. Validate existing RT against DB **hash** and **session state**.
  2. Invalidate the used RT (rotate) and issue a **new RT** and **new AT**.
  3. If a **reused** or invalid RT is presented, **revoke entire session** (`sid`) and require re-login.
- **Sliding session**: Extend session `expiresAt` on legitimate refreshes, capped by `max_session_age` (e.g., 30 days).

### Key Management

- **Asymmetric keys (RS256)** with `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY`.
- Use `kid` header and maintain a **JWKS** endpoint for current/previous public keys.
- **Key rotation**: Planned **quarterly** or on incident; keep previous key active for overlap window.

### Authorization

- **RBAC** baked into tokens (`roles`, `scope`).
- Enforce **least privilege** at route/method level.
- Admin endpoints require elevated scopes and stricter rate limits.

### Security Controls

- **Rate limiting** on `/auth/*` and login by IP + account.
- **Device/session management UI**: List & revoke sessions per device.
- **Anomaly detection**: Alert on RT reuse, impossible travel, excessive refreshes.
- **TLS everywhere**; cookies always `Secure`.
- **Content Security Policy** and **no AT in JS-accessible storage** (avoid XSS exfiltration risk).

## Consequences

**Positive**

- Strong revocation and compromise response via RT rotation & reuse detection.
- Scales horizontally; JWT verification is stateless.
- Works for SPA and future mobile/partner clients.

**Trade-offs**

- Added complexity (session store, RT rotation logic, reuse detection).
- More moving parts (JWKS, key rotation ops).
- Requires rigorous implementation and tests.

## Alternatives Considered

1. **Opaque server sessions (Redis) only**  
   _Pros_: Simple revocation, familiar pattern.  
   _Cons_: Sticky sessions or shared store; less suitable for third-party APIs; harder for zero-downtime deploys across regions.

2. **JWT only without refresh**  
   _Pros_: Simpler.  
   _Cons_: Either very short AT (poor UX) or long AT (security risk); no sliding sessions; weak revocation.

3. **LocalStorage tokens**  
   _Pros_: Simple implementation.  
   _Cons_: High XSS exfiltration risk; not acceptable for security posture.

## Implementation Notes

- **DB**: `auth.sessions` (sid PK), `auth.refresh_tokens` (hash, sid FK, revoked, expiresAt, createdAt, lastUsedAt, ipHash, ua).
- **Endpoints**: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/sessions`, `/auth/revoke/:sid`.
- **Cookies**: `at` (Lax), `rt` (Strict), `csrf` (non-HttpOnly).
- **Headers**: `Authorization: Bearer <AT>`, `X-CSRF-Token` for mutations.
- **Middleware**: JWT verify with `kid` → fetch public key; scope/role guards; CSRF for state-changing methods.
- **Observability**: Emit audit logs for login, refresh, logout, revoke, RT reuse; metrics: `auth_login_success_total`, `auth_rt_reuse_total`, `auth_refresh_latency_ms` (p95).

## QA & Acceptance

- Contract tests for token issuance/refresh/reuse/revocation.
- Playwright E2E ensures cookies are HttpOnly/SameSite and CSRF blocks forged requests.
- Security tests: RT reuse triggers session revocation; key rotation keeps logins working.
- Performance: p95 login/refresh < 300 ms; error rate < 0.5% under load.

## Backout Plan

If critical issues arise (e.g., widespread RT reuse false-positives), **fallback to opaque server sessions** (Redis-backed) with `sid` cookie while investigating. Keep JWT verification for API auth but disable RT rotation temporarily by feature flag. Maintain a migration to clean stale RTs and close sessions on rollback.

## Change Log

- **1.0 (2025-10-13):** Initial acceptance.
