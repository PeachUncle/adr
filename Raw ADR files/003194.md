# ADR: Backend Stack — Node.js + Express + TypeScript

- Status: Accepted
- Date: 2025-11-11
- Owners: Backend Team <backend@example.com>
- Links: Issue: TBD, PR: TBD, Docs: Express docs, TypeScript config

## Context

The project currently includes an Express-based TypeScript backend (see `backend/server.ts` and `package.json`). We need a clear, maintainable backend architecture that supports API endpoints, auth middleware, and AI orchestration services (ChatService, ProjectService, TaskService).

## Decision

We will standardize the backend on Node.js + TypeScript using Express (v4.x/v5 compatible patterns) and the existing `@supabase/supabase-js` client for DB access. Services will follow a simple layered pattern:

- `controllers/` — express route handlers
- `services/` — business logic (ProjectService, TaskService, ChatService)
- `repositories/` or `db/` — DB access wrappers for Supabase
- `middleware/` — auth, validation, error handling

Rationale: Express is already in use in the repo and is well documented. Express middleware patterns align with current codebase and developer experience.

## Alternatives Considered

- Fastify: higher throughput and better TypeScript ergonomics, but migration cost from Express is non-trivial given existing code.
- NestJS: more structure (+DI) but introduces framework lock-in and higher initial learning curve.

## Consequences

- Positive: Minimal churn, quick developer ramp, large ecosystem of middleware.
- Negative: Slightly less performance than Fastify under extreme loads; mitigations include caching, clustering, and reverse-proxy.

## Implementation Plan

- [ ] Enforce project layout and create service/repository scaffolding
- [ ] Add standard middlewares: `helmet`, `compression`, `cors`, body parsers
- [ ] Add global error handler and request logging middleware
- [ ] Add `express-rate-limit` and configure store (Redis if scale requires)
- [ ] Define `ChatService` interface and initial implementation placeholder using LangChain orchestrator
- [ ] Add tests (unit for services, integration for controllers)

## Test Cases

- [ ] Unit tests for `ProjectService`, `TaskService`, `ChatService` behaviors
- [ ] Integration test of auth flow + one protected endpoint
- [ ] End-to-end smoke test covering create project + create tasks

## Traceability

| RF ID | RF Description | RNF | Component(s) Impacted |
|-------|----------------|-----|-----------------------|
| RF-API-001 | Public API endpoints | Reliability | backend, infra |

## Effort Estimate

Dev:
- Project scaffolding & middleware: 6h
- Service implementations (initial): 8h
- Tests and CI: 4h

Ops/QA: 4h
