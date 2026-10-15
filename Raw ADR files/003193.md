# ADR: Authentication — Supabase Auth + JWT for Backend APIs

- Status: Accepted
- Date: 2025-11-11
- Owners: Security Team <security@example.com>
- Links: Issue: TBD, Supabase Auth docs, backend auth controller

## Context

The repository uses Supabase on the frontend and includes `jsonwebtoken` and `bcryptjs` on the backend. We need a secure, interoperable authentication approach that allows frontend auth via Supabase and backend API authorization for server-side routes and services.

## Decision

Primary authentication will use Supabase Auth for end-user flows (sign in/up, OAuth). For server-to-server and API protections, we will use JWTs signed and validated in backend endpoints using `jsonwebtoken`. Password hashing (if we store or verify passwords on backend) will use `bcryptjs`.

Flow:
- Frontend uses Supabase Auth (OAuth or email/password) and keeps session on client.
- For some backend-only flows, a service role key (server) will be used with caution.
- Backend will verify incoming requests using Authorization: Bearer <access_token> where token is a Supabase JWT or an internal JWT issued by backend when necessary.

## Alternatives Considered

- Use only Supabase Auth for all auth and let Supabase Edge Functions run protected logic (simpler but changes service boundaries).
- Use third-party auth service (Auth0) — adds cost and integration friction.

## Consequences

- Positive: Leverage Supabase Auth features (magic links, OAuth), consistent user model between frontend and backend.
- Negative: Need to carefully manage token verification and ensure token expiry/rotation is handled. Avoid storing sensitive keys in frontend.

## Implementation Plan

- [ ] Standardize token verification middleware in `backend/middleware/auth.ts` using `jsonwebtoken` and Supabase token validation as needed
- [ ] If backend issues internal JWTs, sign with a secure key and store in CI/CD secrets
- [ ] Use `bcryptjs` for any server-side password hashing (if required)
- [ ] Add tests for auth middleware (valid token, expired token, missing token)

## Test Cases

- [ ] Verify Supabase session token accepted by protected API endpoints
- [ ] Verify expired tokens are rejected and proper 401 returned
- [ ] Verify password hashing and comparison with bcryptjs

## Traceability

| RF ID | RF Description | RNF | Component(s) Impacted |
|-------|----------------|-----|-----------------------|
| RF-AUTH-001 | User Sign-in | Security | frontend, backend, supabase |

## Effort Estimate

Dev:
- Auth middleware & tests: 4h
- Integrate Supabase session handling: 3h

Ops:
- Rotate keys and add to CI/CD secrets: 1h
