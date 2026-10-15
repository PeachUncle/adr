# ADR: Security & Validation — helmet, cors, express-validator, express-rate-limit

- Status: Accepted
- Date: 2025-11-11
- Owners: Security/Platform Team <security@example.com>
- Links: Issue: TBD, express-validator docs, express-rate-limit docs

## Context

The backend exposes public APIs and must protect against common web threats, input tampering, and abusive traffic. The codebase already includes `helmet`, `cors`, `express-validator`, and `express-rate-limit` in dependencies.

## Decision

We will adopt the following baseline security posture for the Express backend:

- `helmet` — set secure HTTP headers
- `cors` — configure strict origins for production and permissive for local dev
- `express-validator` — validate and sanitize incoming request data per-route
- `express-rate-limit` — protect sensitive endpoints with per-IP limits; use Redis-backed store when running multiple instances

Rationale: These libraries are widely used, documented, and already present in the repository.

## Alternatives Considered

- Custom validation middleware: increases maintenance cost; not recommended
- Use API gateway rate limiting only: good but defense-in-depth requires app-level limits too

## Consequences

- Positive: Reduces XSS/CSRF surface, prevents abusive traffic, enforces input hygiene.
- Negative: Possible false positives (rate-limit) and additional infra if Redis-backed store is required for rate-limiter.

## Implementation Plan

- [ ] Add `helmet()` with recommended options in `server.ts`
- [ ] Configure `cors()` with `origin` list controlled by env var `CORS_ORIGINS`
- [ ] Apply `express-validator` chains to all public POST/PUT endpoints; centralize error formatter
- [ ] Apply `express-rate-limit` globally with tighter rules for auth endpoints; switch to Redis store in clustered deployments
- [ ] Add tests that attempt typical injection patterns and confirm sanitized/blocked responses

## Test Cases

- [ ] Verify headers set by `helmet` (X-Content-Type-Options, X-Frame-Options)
- [ ] Try malicious payloads and ensure `express-validator` triggers 400 responses
- [ ] Rate-limit test: exceed requests and ensure 429 responses

## Traceability

| RF ID | RF Description | RNF | Component(s) Impacted |
|-------|----------------|-----|-----------------------|
| RF-SEC-001 | Public APIs | Security | backend, infra |

## Effort Estimate

Dev:
- Middleware wiring and per-route validation: 4h
- Tests and integration: 3h

Ops:
- Configure Redis for rate-limiter (if needed): 2h
