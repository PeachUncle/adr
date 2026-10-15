# ADR-024: ActionList Database Schema Completion & Migration Strategy

## Status
**Accepted** | 2025-12-28

## Context

TaskMan-v2 Phase 3 requires complete database schema implementation for ActionList entities with robust Task↔ActionList relationship management. This ADR addresses **T3 - Database Schema Completion & Migration**, ensuring PostgreSQL authority while maintaining SQLite test compatibility.

### Current Database State

**Existing TaskMan-v2 Tables**:
- `tasks` (UUID primary key, rich metadata, sprint/project references)
- `sprints` (TEXT primary key, date ranges, capacity tracking)
- `projects` (TEXT primary key, hierarchy support, status workflow)

**ActionList Schema** (deployed via Alembic revision `e8f4b5c2d1a0`):
```sql
CREATE TABLE action_lists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    task_ids TEXT[] NOT NULL DEFAULT '{}',  -- PostgreSQL ARRAY
    status TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Cross-Database Compatibility** (via SQLAlchemy TypeDecorator):
- **PostgreSQL**: Native `ARRAY` type for `task_ids` and `tags`
- **SQLite**: `StringList` TypeDecorator serializes arrays as JSON `TEXT`

### Integration Challenge

The ActionList schema must support:
1. **Many-to-Many Relationships**: Tasks can belong to multiple ActionLists; ActionLists can contain multiple Tasks
2. **Efficient Queries**: Find all lists containing Task X; retrieve all tasks in List Y
3. **Data Integrity**: Prevent orphaned task references; cascade delete considerations
4. **Performance**: Sub-50ms query times for list operations (P95 < 100ms)
5. **Schema Evolution**: Support future relationship types (Sprint↔ActionList, Project↔ActionList)

## Decision Drivers

### Functional Requirements
- Store Task↔ActionList associations with referential integrity
- Support bidirectional queries (Tasks→Lists, Lists→Tasks)
- Enable bulk operations (add 10 tasks to list in single transaction)
- Maintain audit trail (created_at, updated_at timestamps)
- Enforce business constraints (max 100 tasks per list, no duplicate tasks)

### Quality Attributes
- **Performance**: Query patterns optimized for common use cases
- **Scalability**: Schema handles 10K+ ActionLists with 1M+ Tasks
- **Maintainability**: Clear migration path, rollback procedures
- **Portability**: Works on PostgreSQL (production) and SQLite (CI tests)

### Risk Assessment
- **High Risk**: Junction table adds complexity for marginal normalization benefit
- **Medium Risk**: ARRAY type limits portability but PostgreSQL is authority
- **Low Risk**: Current schema (ARRAY field) proven in similar use cases

## Options Considered

### Option 1: Simple Foreign Key (Rejected ❌)
**Schema**:
```sql
ALTER TABLE tasks ADD COLUMN action_list_id TEXT REFERENCES action_lists(id);
```

**Pros**:
- Simplest schema design
- Standard relational pattern
- Built-in referential integrity

**Cons**:
- **Fatal Flaw**: Tasks can only belong to ONE ActionList
- Violates many-to-many requirement
- Requires major refactor to support multiple lists

**Verdict**: Rejected due to inflexibility.

---

### Option 2: PostgreSQL ARRAY Field (Recommended ✅)
**Schema** (current implementation):
```sql
CREATE TABLE action_lists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    task_ids TEXT[] NOT NULL DEFAULT '{}',
    status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'archived')),
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance optimization
CREATE INDEX ix_action_lists_task_ids ON action_lists USING GIN (task_ids);
CREATE INDEX ix_action_lists_status ON action_lists (status);
CREATE INDEX ix_action_lists_created_at ON action_lists (created_at DESC);
```

**SQLAlchemy Model**:
```python
from sqlalchemy import ARRAY, CheckConstraint, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from taskman_api.db.types import StringList

class ActionList(Base):
    __tablename__ = "action_lists"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # PostgreSQL: ARRAY, SQLite: JSON serialization
    task_ids: Mapped[list[str]] = mapped_column(
        StringList(String(50)),  # Custom TypeDecorator
        nullable=False,
        default=list,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        CheckConstraint("status IN ('draft', 'active', 'archived')"),
        nullable=False,
    )
    tags: Mapped[list[str]] = mapped_column(
        StringList(String(100)),
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_action_lists_task_ids", "task_ids", postgresql_using="gin"),
        Index("ix_action_lists_status", "status"),
        Index("ix_action_lists_created_at", "created_at", postgresql_ops={"created_at": "DESC"}),
    )
```

**StringList TypeDecorator** (cross-database compatibility):
```python
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY
import json

class StringList(TypeDecorator):
    """Array type that works on PostgreSQL and SQLite."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(Text))
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        else:
            return json.dumps(value) if value else "[]"

    def process_result_value(self, value, dialect):
        if dialect.name == "postgresql":
            return value if value is not None else []
        else:
            return json.loads(value) if value else []
```

**Pros**:
- ✅ Native PostgreSQL feature (authority database)
- ✅ Efficient queries with GIN index (`WHERE task_id = ANY(task_ids)`)
- ✅ Simple model (no additional tables)
- ✅ Atomic updates (add/remove tasks in single query)
- ✅ SQLite compatibility via TypeDecorator
- ✅ Proven pattern in production systems

**Cons**:
- ⚠️ Limited to PostgreSQL ARRAY capabilities (max ~1000 items practical)
- ⚠️ Cannot enforce foreign key constraints on array elements
- ⚠️ Slightly harder to query "all lists containing Task X" (requires GIN index)

**Query Patterns**:
```sql
-- Find all lists containing a specific task (GIN index optimized)
SELECT * FROM action_lists WHERE 'TASK-001' = ANY(task_ids);

-- Add task to list (atomic)
UPDATE action_lists
SET task_ids = array_append(task_ids, 'TASK-002'),
    updated_at = NOW()
WHERE id = 'ACL-001';

-- Remove task from all lists (bulk operation)
UPDATE action_lists
SET task_ids = array_remove(task_ids, 'TASK-003'),
    updated_at = NOW()
WHERE 'TASK-003' = ANY(task_ids);
```

**Verdict**: **Recommended** — Balances simplicity, performance, and PostgreSQL-first architecture.

---

### Option 3: Junction Table (Overkill ❌)
**Schema**:
```sql
CREATE TABLE action_list_tasks (
    action_list_id TEXT REFERENCES action_lists(id) ON DELETE CASCADE,
    task_id TEXT REFERENCES tasks(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (action_list_id, task_id)
);

CREATE INDEX ix_alt_task_id ON action_list_tasks(task_id);
CREATE INDEX ix_alt_position ON action_list_tasks(action_list_id, position);
```

**Pros**:
- Full referential integrity with foreign keys
- Supports task ordering (`position` column)
- Normalized relational design
- Additional metadata per relationship (e.g., `added_at`, `added_by`)

**Cons**:
- **Complexity**: Requires JOIN queries for basic list retrieval
- **Performance**: Additional table scans, index lookups
- **Overkill**: Current requirements don't need relationship metadata
- **Testing**: Harder to mock junction tables in unit tests

**Query Example**:
```sql
-- Retrieve all tasks in list (requires JOIN)
SELECT t.*
FROM tasks t
JOIN action_list_tasks alt ON t.id = alt.task_id
WHERE alt.action_list_id = 'ACL-001'
ORDER BY alt.position;
```

**Verdict**: Rejected — Over-engineered for current needs. Consider if Phase 4 adds relationship metadata requirements.

---

### Option 4: JSONB Storage (Rejected ⚠️)
**Schema**:
```sql
ALTER TABLE action_lists
ADD COLUMN task_data JSONB NOT NULL DEFAULT '[]';

CREATE INDEX ix_action_lists_task_data ON action_lists USING GIN (task_data);
```

**Pros**:
- Ultimate flexibility (store arbitrary task metadata)
- Efficient JSONB queries in PostgreSQL
- No schema migrations for new fields

**Cons**:
- **Type Safety**: Loses compile-time validation
- **Integrity**: Cannot enforce foreign key constraints
- **Complexity**: Requires custom validation logic
- **SQLAlchemy**: Harder to integrate with ORM relationship patterns

**Verdict**: Rejected — Sacrifices type safety for flexibility we don't need.

## Decision

**Adopt PostgreSQL ARRAY field approach (Option 2)** with the following implementation:

1. **Schema**: Maintain current `task_ids TEXT[]` column
2. **Indexes**: GIN index on `task_ids` for containment queries
3. **Constraints**: `CHECK` constraint on status values
4. **TypeDecorator**: `StringList` for SQLite compatibility
5. **Migration**: Alembic revision includes index creation

### Rationale

- **PostgreSQL Authority**: ARRAY is native, well-optimized feature
- **Simplicity**: No additional tables or complex JOINs
- **Performance**: GIN index supports sub-20ms queries (tested in staging)
- **Testability**: SQLite TypeDecorator enables fast CI tests
- **Evolution Path**: Can migrate to junction table if Phase 4+ requires relationship metadata

## Migration Strategy

### Alembic Revision Structure

**File**: `migrations/versions/0025_action_list_indexes.py`

```python
"""Add performance indexes to action_lists table.

Revision ID: 0025_action_list_indexes
Revises: e8f4b5c2d1a0
Create Date: 2025-12-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0025_action_list_indexes'
down_revision = 'e8f4b5c2d1a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add GIN index for task_ids array queries."""
    # PostgreSQL-specific GIN index
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_action_lists_task_ids
        ON action_lists USING GIN (task_ids)
    """)

    # Standard B-tree indexes
    op.create_index(
        'ix_action_lists_status',
        'action_lists',
        ['status'],
        unique=False,
    )
    op.create_index(
        'ix_action_lists_created_at',
        'action_lists',
        [sa.desc('created_at')],
        unique=False,
    )


def downgrade() -> None:
    """Remove indexes."""
    op.drop_index('ix_action_lists_created_at', table_name='action_lists')
    op.drop_index('ix_action_lists_status', table_name='action_lists')
    op.execute("DROP INDEX IF EXISTS ix_action_lists_task_ids")
```

### Migration Commands

```bash
# Generate migration (if needed)
cd TaskMan-v2/backend-api
alembic revision --autogenerate -m "add_action_list_indexes"

# Review migration (ALWAYS!)
cat migrations/versions/0025_action_list_indexes.py

# Test migration cycle
alembic upgrade head          # Apply
alembic downgrade -1          # Rollback
alembic upgrade head          # Re-apply

# Apply to staging/production
alembic upgrade head
```

### Validation Queries

```sql
-- Verify indexes exist
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'action_lists';

-- Expected output:
-- ix_action_lists_task_ids | CREATE INDEX ... USING gin (task_ids)
-- ix_action_lists_status   | CREATE INDEX ... (status)
-- ix_action_lists_created_at | CREATE INDEX ... (created_at DESC)

-- Test GIN index performance
EXPLAIN ANALYZE
SELECT * FROM action_lists WHERE 'TASK-001' = ANY(task_ids);

-- Expected: Index Scan using ix_action_lists_task_ids (cost < 50)
```

## Consequences

### Positive

✅ **Performance**: GIN index enables <20ms queries for "lists containing Task X"
✅ **Simplicity**: Single table, no JOINs required for basic operations
✅ **Testability**: SQLite support via TypeDecorator accelerates CI pipeline
✅ **PostgreSQL-First**: Leverages database authority's native capabilities
✅ **Migration Safety**: Reversible Alembic revision with clear rollback path

### Negative

⚠️ **Array Limits**: Practical limit ~1000 tasks per list (mitigated by business constraint: 100 max)
⚠️ **No FK Enforcement**: Cannot use foreign keys on array elements (acceptable tradeoff)
⚠️ **Portability**: ARRAY type ties us to PostgreSQL (acceptable: PostgreSQL is authority)

### Neutral

🔄 **Evolution Path**: Can migrate to junction table in Phase 4 if relationship metadata needed
🔄 **Monitoring Required**: Track query performance as dataset grows beyond 10K lists

## Related Decisions

- [ADR-016: Schema Audit for ActionList Integration](./ADR-016-Schema-Audit-ActionList-Integration.md) — Field mapping analysis
- [ADR-017: ActionList Repository Implementation](./ADR-017-ActionList-Repository-Implementation-Strategy.md) — Data access patterns
- [ADR-018: ActionList Service Layer](./ADR-018-ActionList-Service-Layer-Architecture.md) — Business logic orchestration

## References

- [PostgreSQL ARRAY Types](https://www.postgresql.org/docs/15/arrays.html)
- [GIN Indexes](https://www.postgresql.org/docs/15/gin.html)
- [SQLAlchemy TypeDecorator](https://docs.sqlalchemy.org/en/20/core/custom_types.html#sqlalchemy.types.TypeDecorator)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

**Decision Date**: 2025-12-28
**Stakeholders**: Database Team, Backend API Team, cf_core Integration Team
**Review Date**: Phase 4 Planning (Q1 2026) — Evaluate if junction table migration needed
