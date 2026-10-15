# ADR-001: Database ORM Choice (SQLAlchemy)

**Status**: Accepted
**Date**: 2025-12-02 (Retroactive)
**Decision Makers**: Development Team
**Supersedes**: N/A

---

## Context

The NFL SIM application requires robust database access for managing teams, players, games, seasons, and complex relational data. We needed to choose an ORM (Object-Relational Mapping) framework that would:

1. Support complex queries for game simulation and statistics
2. Handle asynchronous operations for API performance
3. Provide type safety and IDE autocomplete
4. Support database migrations
5. Work well with FastAPI backend
6. Support both PostgreSQL (production) and SQLite (development/testing)

**Constraints**:

- Python 3.11+ required
- Must integrate seamlessly with FastAPI
- Need migration support for evolving schema
- Team has Python expertise but limited DBA resources

---

## Decision

**We chose SQLAlchemy 2.0 as our ORM framework with Alembic for migrations.**

Specifically:

- SQLAlchemy 2.0 Core and ORM
- Async support via `asyncpg` (PostgreSQL) and `aiosqlite` (SQLite)
- Alembic for database migrations
- Pydantic models for API schemas (separate from DB models)

---

## Rationale

1. **Maturity & Community**: SQLAlchemy is the most mature and widely-used Python ORM with extensive documentation and community support.

2. **Async Support**: SQLAlchemy 2.0 has first-class async support, critical for high-performance API endpoints.

3. **Flexibility**: Supports both high-level ORM operations and low-level SQL when needed for complex game simulation queries.

4. **Type Safety**: Works well with type hints and modern Python features.

5. **Migration Support**: Alembic (built by the SQLAlchemy team) provides robust schema migration capabilities.

6. **Multi-Database Support**: Seamlessly supports PostgreSQL for production and SQLite for local development/testing.

7. **FastAPI Integration**: FastAPI has excellent examples and patterns for SQLAlchemy integration.

---

## Consequences

### Positive Consequences

- ✅ Rich querying capabilities for complex game statistics
- ✅ Automatic relationship handling reduces boilerplate
- ✅ Strong typing with SQLAlchemy 2.0 improves IDE experience
- ✅ Migration system allows safe schema evolution
- ✅ Async support enables high-concurrency API performance
- ✅ Well-documented patterns for testing with fixtures

### Negative Consequences

- ⚠️ Learning curve for complex queries (requiresdunderstanding of SQLAlchemy's API)
- ⚠️ N+1 query problems require careful relationship configuration
- ⚠️ Migrations must be carefully managed (can't be auto-generated blindly)
- ⚠️ Dual model system (SQLAlchemy + Pydantic) creates some duplication

### Neutral Consequences

- Database schema is defined in Python rather than SQL DDL
- Requires running migrations as part of deployment process

---

## Alternatives Considered

### Alternative 1: Django ORM

- **Description**: Use Django's built-in ORM
- **Pros**:
  - Batteries-included with admin panel
  - Excellent migration system
  - Great documentation
- **Cons**:
  - Requires full Django framework (overkill for FastAPI)
  - Less flexible for complex queries
  - Async support not as mature
- **Reason for rejection**: Too heavyweight for a FastAPI project; weaker async support

### Alternative 2: Peewee

- **Description**: Lightweight Python ORM
- **Pros**:
  - Simpler API than SQLAlchemy
  - Less boilerplate
  - Good for small projects
- **Cons**:
  - Limited async support
  - Smaller community
  - Less powerful for complex queries
- **Reason for rejection**: Insufficient for complex simulation queries and async requirements

### Alternative 3: Tortoise ORM

- **Description**: Modern async-first ORM
- **Pros**:
  - Built for async from the ground up
  - Django-like API
  - Good FastAPI integration
- **Cons**:
  - Relatively new (less battle-tested)
  - Smaller ecosystem
  - Less flexibility for raw SQL
- **Reason for rejection**: Less mature; team preferred SQLAlchemy's proven track record

### Alternative 4: Raw SQL with asyncpg

- **Description**: Use raw SQL queries without ORM
- **Pros**:
  - Maximum performance
  - Full control over queries
  - No abstraction overhead
- **Cons**:
  - No automatic migrations
  - Manual relationship management
  - More boilerplate code
  - Higher maintenance burden
- **Reason for rejection**: Too much manual work for complex relational models

---

## Implementation Notes

**How this decision is implemented:**

1. **Database Connection** (`backend/app/core/database.py`)

   - Async engine creation
   - Session management with `async_sessionmaker`
   - Dependency injection for FastAPI routes

2. **Models** (`backend/app/models/*.py`)

   - Declarative base with mapped columns
   - Relationships defined with `relationship()` and proper lazy loading
   - Indexes for performance-critical queries

3. **Migrations** (`backend/alembic/`)

   - Alembic configuration for auto-generation
   - Manual review of all generated migrations
   - Versioned migration files in source control

4. **Schemas** (`backend/app/schemas/*.py`)
   - Separate Pydantic models for API requests/responses
   - Conversion utilities where needed

**Migration Strategy**:

- All schema changes go through Alembic migrations
- Migrations are reviewed before running in production
- Rollback scripts created for risky migrations

---

## Validation Criteria

**Success Metrics:**

1. **Performance**: API endpoints respond in <200ms for typical queries
2. **Reliability**: Zero data corruption incidents related to ORM
3. **Developer Experience**: New developers can write queries within 1 week
4. **Maintainability**: Schema changes take <1 hour including migration

**Review Timeline**: Reassess after 6 months or if major performance issues arise.

---

## References

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [FastAPI SQLAlchemy Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- Migration to async: `docs/DEVELOPMENT.md` (Async API Refactor section)
