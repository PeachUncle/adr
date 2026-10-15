# ADR-0002: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Backend Stack" not separate ADRs for framework, database, ORM).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 001-phase-2-web-app
- **Context:** Phase 2 requires a secure, performant backend API to serve the web frontend. The API must support multi-user authentication, enforce user data isolation, handle 100 concurrent users, achieve <500ms p95 response times, and deploy to free-tier services. The backend must integrate with Better Auth (JWT validation) and provide RESTful endpoints for task CRUD operations.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines entire backend platform and data persistence
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Django REST, Flask, Starlette evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all backend development and database operations
-->

## Decision

We will adopt the following integrated backend technology stack:

- **Framework:** FastAPI 0.115+
- **Language:** Python 3.13+ with type hints
- **Package Manager:** UV (fast Python package installer)
- **ORM:** SQLModel 0.0.24+ (SQLAlchemy + Pydantic)
- **Database:** Neon Serverless PostgreSQL (cloud-hosted)
- **Migrations:** Alembic
- **Authentication:** PyJWT for JWT token validation
- **Testing:** pytest 8.0+ with httpx
- **Deployment:** Vercel Python runtime or Railway
- **API Documentation:** Automatic OpenAPI/Swagger (built-in)
- **Validation:** Pydantic 2.0 (integrated via SQLModel and FastAPI)

### Rationale

This stack leverages Python's async capabilities for high performance while maintaining type safety end-to-end. FastAPI + SQLModel + Pydantic form an integrated validation layer where database models, request schemas, and response schemas share the same type definitions. Neon Serverless PostgreSQL eliminates database infrastructure management and scales automatically. UV provides fast dependency resolution and virtual environment management. The entire stack is optimized for developer productivity, type safety, and operational simplicity.

## Consequences

### Positive

- **High Performance:** Async/await support enables handling 100+ concurrent users with low latency
- **Type Safety:** Type hints + Pydantic validation catch errors at development time, reducing runtime bugs
- **Automatic Documentation:** OpenAPI/Swagger generated from code, always in sync with implementation
- **Excellent DX:** FastAPI's dependency injection makes testing and auth middleware clean and testable
- **Unified Schema:** SQLModel combines SQLAlchemy (ORM) + Pydantic (validation), reducing code duplication
- **Built-in Validation:** Pydantic validates request bodies automatically, returning 422 errors with clear messages
- **Database Scalability:** Neon Serverless autoscales, provides connection pooling, and offers free tier with generous limits
- **Migration Safety:** Alembic tracks schema changes in version control, enabling safe database evolution
- **Fast Setup:** UV installs dependencies 10-100x faster than pip, improving local and CI/CD performance
- **Testing Simplicity:** pytest + httpx allows testing API endpoints without running a live server

### Negative

- **Python Runtime:** Slower than compiled languages (Go, Rust), but acceptable for 100-user scale
- **Async Learning Curve:** Requires understanding async/await, which can be confusing for Python newcomers
- **SQLModel Maturity:** Newer library (v0.0.x), but backed by FastAPI creator (Sebastián Ramírez)
- **Neon Dependency:** Reliance on third-party database host (mitigated by standard PostgreSQL compatibility)
- **Cold Start Latency:** Serverless deployments (Vercel) may have cold starts (200-500ms), acceptable for Phase 2
- **UV Adoption:** Relatively new tool, though quickly becoming Python community standard

## Alternatives Considered

### Alternative Stack A: Django REST Framework + PostgreSQL + Gunicorn
- **Pros:** Mature ecosystem, built-in admin panel, extensive packages, well-documented
- **Cons:** Heavier (more boilerplate), slower startup, synchronous by default (async support is limited), opinionated structure
- **Why Rejected:** Django's synchronous nature conflicts with our 100 concurrent user requirement; FastAPI's async approach is better suited for I/O-bound operations like database queries and JWT validation

### Alternative Stack B: Flask + SQLAlchemy + PostgreSQL
- **Pros:** Lightweight, flexible, mature, large ecosystem
- **Cons:** No built-in async support, manual request validation, no automatic API documentation, more boilerplate for CRUD operations
- **Why Rejected:** Lack of async support limits concurrency; manual validation increases error-prone code; no OpenAPI generation out-of-box

### Alternative Stack C: Starlette (lower-level ASGI framework)
- **Pros:** Minimal, high performance, flexible
- **Cons:** Lower-level abstractions, more boilerplate, no dependency injection, no automatic validation
- **Why Rejected:** FastAPI is built on Starlette and adds dependency injection, automatic validation, and OpenAPI docs; choosing Starlette means rebuilding FastAPI features manually

### Database Alternative: Supabase PostgreSQL
- **Pros:** PostgreSQL-compatible, includes auth service, real-time subscriptions
- **Cons:** Adds complexity we don't need (we're using Better Auth), larger feature set than required
- **Why Rejected:** Neon is simpler and purpose-built for serverless PostgreSQL; Supabase's auth features conflict with our Better Auth choice

### ORM Alternative: SQLAlchemy Alone
- **Pros:** Mature, feature-rich, widely adopted
- **Cons:** Verbose model definitions, no Pydantic integration, separate request/response schemas
- **Why Rejected:** SQLModel provides the same SQLAlchemy power with Pydantic integration, reducing boilerplate and ensuring consistency between database and API schemas

## References

- Feature Spec: [specs/001-phase-2-web-app/spec.md](../../specs/001-phase-2-web-app/spec.md)
- Implementation Plan: [specs/001-phase-2-web-app/plan.md](../../specs/001-phase-2-web-app/plan.md)
- Research Notes: [specs/001-phase-2-web-app/research.md](../../specs/001-phase-2-web-app/research.md)
- Data Model: [specs/001-phase-2-web-app/data-model.md](../../specs/001-phase-2-web-app/data-model.md)
- Related ADRs: ADR-0003 (Authentication Architecture)
- Context7 Research: FastAPI (/fastapi/fastapi), SQLModel (/websites/sqlmodel_tiangolo)
