## Context
The repository currently has a single backend project (`backend/MiLyst.Api`) that hosts minimal API endpoints and development reverse proxy behavior (YARP + Vite dev server). The project context calls for a Clean Architecture approach and for EF Core + PostgreSQL, but these are not yet implemented in code.

Multi-tenancy is a first-class concern for the application:
- Tenant identification is resolved from an HTTP header.
- Tenant isolation is via a single database with a `TenantId` column on tenant-scoped data.

## Goals / Non-Goals
- Goals:
  - Establish a clear layered backend structure that follows the dependency rule.
  - Add EF Core + PostgreSQL as the persistence mechanism.
  - Keep minimal APIs as the presentation style.
  - Preserve a simple developer experience (`task dev` remains the happy path).
  - Provide a path to enforce tenant isolation consistently across queries.
- Non-Goals:
  - Implement all product features (boards/tasks/projects) in this change.
  - Finalize the authorization/roles model.
  - Add sharding or hard isolation; keep a single shared DB approach for now.

## Decisions
- Decision: Split backend into multiple projects
  - `MiLyst.Domain`: entities, value objects, domain rules (no EF Core, no ASP.NET dependencies)
  - `MiLyst.Application`: use cases, orchestration, DTOs, validation; defines interfaces needed from persistence and other services
  - `MiLyst.Infrastructure`: EF Core DbContext, migrations, persistence implementations, and external integrations
  - `MiLyst.Api`: minimal API endpoints and composition root (DI setup, middleware, auth wiring)

- Decision: Keep persistence abstractions small and explicit
  - Prefer an application-level abstraction such as `IApplicationDbContext` (or narrowly-scoped repositories) over a generic repository pattern.
  - Use query shaping best practices (DTO projections, pagination, `AsNoTracking()` on read paths).

- Decision: Tenant enforcement at the data access boundary
  - Provide an `ITenantContext` (or equivalent) resolved per request.
  - Enforce tenant scoping via EF Core global query filters for tenant-owned entities.
  - Validate that write operations always set `TenantId` based on server-side tenant context.

- Decision: Development workflow for Postgres
  - Prefer a local Postgres instance via container tooling for a predictable dev experience.
  - Add Taskfile tasks (or docs) to start/stop Postgres for local development.

## Risks / Trade-offs
- Risk: Large refactor churn
  - Mitigation: Move incrementally; keep `MiLyst.Api` running throughout by introducing the new projects first, then migrating endpoints and logic.

- Risk: Multi-tenancy enforcement mistakes (data leakage)
  - Mitigation: Centralize tenant resolution and enforce tenant filters in one place (query filters + integration tests).

- Risk: EF Core performance pitfalls at scale
  - Mitigation: Establish conventions early (pagination, projections, no lazy loading, use `AsNoTracking()` for reads).

## Migration Plan
1. Create the new projects (Domain/Application/Infrastructure) and wire up references to satisfy the dependency rule.
2. Introduce Infrastructure EF Core DbContext + Npgsql provider; add migrations and local dev configuration.
3. Move API endpoints to call Application use cases rather than inline logic.
4. Add tenant resolution middleware/services and tenant enforcement patterns in Infrastructure.
5. Add automated tests (unit + integration) to validate boundaries and tenant isolation.

## Open Questions
- Should tenant identification be via a fixed header name (e.g., `X-Tenant-Id`) or configurable?
- Should we apply migrations automatically on startup in Development only, or require an explicit task/command?
- What is the preferred ID strategy for persisted entities (UUID vs bigint) given future sharding considerations?
