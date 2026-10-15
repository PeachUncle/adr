# ADR-002: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-26
- **Feature:** Todo Web Application
- **Context:** The backend requires a Python-based stack that provides type safety, async performance, and seamless integration with the chosen database and authentication strategy.

## Decision

- **Runtime:** Python 3.13+
- **Package Manager:** UV (latest)
- **Web Framework:** FastAPI 0.115+
- **ORM:** SQLModel 0.0.24+
- **Validation:** Pydantic 2.0+
- **Authentication:** JWT via python-jose[cryptography] 3.3.0+
- **Password Hashing:** passlib[bcrypt] 1.7.4+
- **HTTP Client:** httpx 0.28.0+ (for async requests)
- **Server:** uvicorn[standard] 0.32.0+
- **Testing:** pytest 8.0+

## Consequences

### Positive

- **Type safety:** SQLModel + Pydantic ensures end-to-end type safety from database to API responses
- **Async performance:** FastAPI + uvicorn provides excellent concurrent request handling
- **Modern Python:** UV offers fast dependency resolution and installation
- **Database integration:** SQLModel works seamlessly with Pydantic models, reducing boilerplate
- **Security:** JWT authentication with bcrypt password hashing follows industry best practices
- **OpenAPI docs:** FastAPI auto-generates comprehensive API documentation
- **Testing:** pytest + httpx provides clean async test infrastructure

### Negative

- **Runtime overhead:** Python's interpreted nature vs compiled languages
- **Async complexity:** Requires understanding async/await patterns throughout codebase
- **UV adoption:** UV is newer than pip/poetry, may require team familiarity
- **SQLModel limitations:** Some advanced SQL patterns require raw SQL

## Alternatives Considered

**Alternative Stack A: Django + Django ORM + DRF**
- Rejected: Heavier framework with more conventions, less flexible for modern async patterns
- More boilerplate for simple CRUD operations
- DRF adds another layer to learn and maintain

**Alternative Stack B: Flask + SQLAlchemy + manual JWT**
- Rejected: Requires manual API structure, no automatic OpenAPI generation
- More configuration needed for async support
- Less cohesive type safety across layers

**Alternative Stack C: FastAPI + Prisma (via bridge)**
- Rejected: Prisma is Node.js-first, adds unnecessary complexity for Python backend

## References

- Feature Spec: [specs/features/1-todo-web-app/spec.md](../specs/features/1-todo-web-app/spec.md)
- Implementation Plan: [specs/1-todo-web-app/plan.md](../specs/1-todo-web-app/plan.md)
- Data Model: [specs/1-todo-web-app/data-model.md](../specs/1-todo-web-app/data-model.md)
- Backend Guidelines: [backend/CLAUDE.md](../backend/CLAUDE.md)
