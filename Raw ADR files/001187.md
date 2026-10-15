# ADR-001: Model-Database Schema Alignment

**Status**: Accepted
**Date**: 2025-12-28
**Decision**: Expand SQLAlchemy models to match production database schema

## Decision Summary

The SQLAlchemy ORM models will be expanded to include:
1. All fields present in the production PostgreSQL schema
2. Proper `relationship()` declarations for Project ↔ Sprints ↔ Tasks
3. Missing fields that tests and business logic expect (e.g., `sprints`, `tasks`, `observability`)

**Short-term**: Test fixtures are being simplified to match current models.
**Long-term**: Models will be expanded to match production schema.

## Context

The SQLAlchemy ORM models (`Project`, `Sprint`, `ActionList`, `Task`) have been simplified during development, but the production PostgreSQL database contains a more comprehensive schema with additional fields and relationships.

### Current State

**SQLAlchemy Models (Simplified)**:
- `Project`: ~30 fields, no relationships
- `Sprint`: ~35 fields, no relationships
- `ActionList`: ~5 fields, no relationships
- `Task`: Comprehensive but uses string FKs only

**Production Database** (PostgreSQL):
- Contains 40+ columns per table
- Expected relationships: Project ↔ Sprints ↔ Tasks
- JSON fields for complex nested data (OKRs, ceremonies, etc.)

### Impact

1. **Test Failures**: 42 test errors due to fixtures using fields that don't exist in models
2. **Missing Relationships**: No SQLAlchemy `relationship()` declarations
3. **Incomplete Coverage**: Models don't expose all production fields

## Decision Drivers

- Dual-database support (PostgreSQL + SQLite) complicates relationships
- Tests need accurate fixtures matching actual model definitions
- Production data integrity requires full schema coverage

## Options Considered

### Option 1: Expand Models to Match Production
- Add all missing fields to SQLAlchemy models
- Add explicit `relationship()` declarations
- **Pros**: Full feature parity, proper ORM behavior
- **Cons**: May break SQLite compatibility, more complex migrations

### Option 2: Keep Simplified Models
- Update all tests/fixtures to match simplified models
- Document which features aren't exposed via ORM
- **Pros**: Simpler codebase, dual-database compatible
- **Cons**: Manual relationship handling, incomplete API

### Option 3: Hybrid Approach
- Keep models simple for common operations
- Add computed properties for relationships when needed
- Use raw SQL for complex queries
- **Pros**: Balanced complexity
- **Cons**: Inconsistent patterns

## Recommendation

**Option 1** is recommended for long-term maintainability. Entity relationships are fundamental to the domain model.

## Action Items

- [ ] Audit production database schema for all tables
- [ ] Document required fields vs nice-to-have fields
- [ ] Update SQLAlchemy models with missing fields
- [ ] Add `relationship()` declarations (Project → Sprints → Tasks)
- [ ] Update all test fixtures to match expanded models
- [ ] Verify dual-database compatibility with new relationships

## References

- Production schema: Verified via `information_schema` query
- Related tests: `test_services.py`, `test_project_service_edge_cases.py`
- Model files: `src/taskman_api/models/`
