# ADR-0003: Sidecar Authentication Architecture

> **Scope**: Document the decision to implement authentication as a separate service (sidecar pattern) rather than integrating it directly into the main backend.

- **Status:** Accepted
- **Date:** 2025-12-16
- **Feature:** 004-better-auth-service
- **Context:** The project requires authentication for the Physical AI & Humanoid Robotics textbook platform, but needed to balance security, scalability, and separation of concerns. The decision was made to implement authentication as a separate Node.js service using Better Auth, while keeping the FastAPI backend focused on RAG functionality.

## Decision

Implement authentication using a sidecar architecture with:
- **Auth Server**: Node.js + Hono + Better Auth running on port 4000
- **Backend**: FastAPI RAG service on port 8000 (stateless token verification)
- **Database**: Shared Neon Postgres for users and JWKS keys
- **Frontend**: Docusaurus consuming auth endpoints and passing JWTs to backend

## Consequences

### Positive

- **Separation of Concerns**: Auth logic completely separated from RAG business logic
- **Scalability**: Auth and RAG services can scale independently
- **Security**: Stateless token verification in FastAPI (no DB queries for auth)
- **Flexibility**: Different auth providers can be swapped without affecting backend
- **Maintainability**: Clear boundaries between authentication and business logic

### Negative

- **Complexity**: Additional service to deploy and maintain
- **Latency**: Extra network hop for token verification (though cached JWKS minimizes impact)
- **Operations**: More services to monitor and keep running

## Alternatives Considered

Alternative A: Integrated auth in FastAPI - Rejected because it would mix auth concerns with RAG business logic
Alternative B: Third-party auth service (Auth0, Firebase) - Rejected because it would create vendor lock-in and reduce control over user data
Alternative C: Simple JWT with hardcoded secrets - Rejected because it lacks proper key rotation and security practices

## References

- Feature Spec: specs/004-better-auth-service/spec.md
- Implementation Plan: specs/004-better-auth-service/plan.md
- Related ADRs: history/adr/0001-package-management-with-pnpm.md, history/adr/0002-typescript-migration-strategy.md
- Evaluator Evidence: history/prompts/general/1765774920-architecture-overview-documentation.general.prompt.md