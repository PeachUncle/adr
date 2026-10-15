# ADR-001: Authentication & Security Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-14
- **Feature:** Phase 2 Part 2 - User Authentication
- **Context:** The Todo API requires user authentication to enable multi-user support and task ownership. We need to select an authentication mechanism, password hashing algorithm, authorization pattern, and rate limiting strategy that work together as an integrated security solution.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes - affects all protected endpoints
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes - JWT vs sessions, Argon2 vs bcrypt
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes - impacts routes, services, middleware
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We adopt a stateless JWT-based authentication stack with defense-in-depth security:

| Component | Technology | Configuration |
|-----------|------------|---------------|
| **Authentication** | JWT (stateless) | HS256, 30-min expiry, `python-jose` |
| **Password Hashing** | Argon2id | `argon2-cffi` with secure defaults (64MB memory, 3 iterations) |
| **Authorization** | Service-layer filtering | User ID injected via FastAPI dependency injection |
| **Rate Limiting** | slowapi | 5/min register, 10/min login, per-IP |

### Token Structure
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "exp": 1734200000,
  "iat": 1734198200
}
```

### Authorization Pattern
- `get_current_user` dependency extracts and validates JWT
- Services receive `user_id` parameter for all data access
- Tasks filtered at query level: `WHERE user_id = :current_user_id`

## Consequences

### Positive

- **Stateless scaling**: No session store required; API instances can scale horizontally
- **Modern security**: Argon2id is the current OWASP recommendation, resistant to GPU/ASIC attacks
- **Testable authorization**: Service-layer filtering is explicit, auditable, and easy to unit test
- **API-first design**: JWT works seamlessly with mobile apps, SPAs, and third-party integrations
- **Brute-force protection**: Rate limiting on auth endpoints prevents credential stuffing

### Negative

- **Token revocation**: Cannot invalidate tokens before expiry (mitigated by 30-min TTL)
- **Token size**: JWT larger than session cookie (~300 bytes vs ~32 bytes)
- **Client responsibility**: Clients must securely store tokens (no httpOnly cookie protection)
- **Memory overhead**: Argon2id uses 64MB per hash operation (acceptable for auth-only usage)
- **No refresh tokens**: Users must re-authenticate after 30 minutes (acceptable for MVP; add in Part 3)

## Alternatives Considered

### Alternative A: Session-Based Authentication
- **Components**: Server-side sessions with Redis store, session cookies
- **Pros**: Revocable, smaller cookie size, httpOnly protection
- **Cons**: Requires Redis infrastructure, stateful (scaling complexity), not ideal for API-first
- **Why rejected**: Adds operational complexity; JWT better fits our stateless API architecture

### Alternative B: bcrypt for Password Hashing
- **Components**: `passlib[bcrypt]` with work factor 12
- **Pros**: Battle-tested, widely deployed, no memory constraints
- **Cons**: GPU-vulnerable, no memory-hardness, slower to increase difficulty
- **Why rejected**: Argon2id is the modern standard; bcrypt is legacy (still acceptable fallback)

### Alternative C: Middleware-Only Authorization
- **Components**: FastAPI middleware that validates ownership before route execution
- **Pros**: Centralized, declarative
- **Cons**: Less flexible, harder to test in isolation, route coupling
- **Why rejected**: Service-layer filtering is more explicit and testable

## References

- Feature Spec: `specs/phase2/part2-authentication/spec.md`
- Implementation Plan: `specs/phase2/part2-authentication/plan.md` (pending)
- Related ADRs: None (first ADR in this project)
- Evaluator Evidence: `history/prompts/phase2-authentication/001-auth-spec-creation.spec.prompt.md`
