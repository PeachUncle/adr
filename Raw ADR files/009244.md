# ADR-003: PostgreSQL as Primary Database

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template requires a relational database for storing multi-tenant application data including tenants, users, OAuth providers, and tenant-scoped business entities. The database must support:

1. **Row-Level Security (RLS)**: Native support for database-enforced tenant isolation
2. **UUID Primary Keys**: Efficient storage and indexing of UUIDs for security (prevents enumeration attacks)
3. **JSON/JSONB Support**: Flexible schema for tenant settings and extensible configuration
4. **Async Driver Support**: Non-blocking database operations for FastAPI's async architecture
5. **Enterprise Reliability**: Production-grade stability, backup/recovery, and tooling ecosystem
6. **Timezone-Aware Timestamps**: Proper handling of UTC timestamps for multi-region deployments

The application uses SQLAlchemy 2.0 with async sessions and requires tight integration with Alembic for migrations.

## Decision

We chose **PostgreSQL 18** as the primary database.

PostgreSQL provides the advanced features required for secure multi-tenant architecture, particularly Row-Level Security which is central to the data isolation strategy.

**Database Configuration** (`backend/app/core/database.py`):
```python
# Create async engine with connection pooling optimized for multi-tenant load
engine: AsyncEngine = create_async_engine(
    database_url,
    pool_size=20,  # Support 20 concurrent database operations
    max_overflow=10,  # Allow bursts up to 30 total connections
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_reset_on_return="rollback",  # Reset connections on return to pool
)
```

**UUID Primary Keys** (`backend/app/models/tenant.py`):
```python
from sqlalchemy.dialects.postgresql import UUID

id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
    index=True,
    comment="UUID primary key for security and distributed ID generation",
)
```

**JSONB for Tenant Settings**:
```python
settings: Mapped[dict] = mapped_column(
    JSON,  # PostgreSQL JSONB for efficient querying
    nullable=False,
    default=dict,
    comment="Tenant-specific configuration as JSON",
)
```

**RLS Policy Creation** (`alembic/versions/e10757622a70_*.py`):
```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON users
USING (tenant_id = COALESCE(
    NULLIF(current_setting('app.current_tenant_id', TRUE), '')::UUID,
    '00000000-0000-0000-0000-000000000000'::UUID
));
```

## Consequences

### Positive

1. **Native RLS Support**: PostgreSQL's Row-Level Security is the foundation of tenant isolation. Unlike application-level filtering, RLS enforces data boundaries at the database level:
   ```sql
   -- All queries automatically filtered by tenant context
   SELECT * FROM users;  -- Only returns current tenant's users
   ```

2. **Efficient UUID Handling**: PostgreSQL's native UUID type uses 16 bytes (vs 36 bytes for string storage) with optimized indexing via B-tree. Combined with `uuid_generate_v4()`, provides secure, non-enumerable identifiers

3. **JSONB Performance**: PostgreSQL's JSONB stores data in decomposed binary format, enabling:
   - Efficient indexing with GIN indexes
   - JSON path queries for tenant settings
   - Atomic JSON updates without full document replacement

4. **Asyncpg Driver**: The `asyncpg` driver provides true async I/O, yielding 2-3x performance improvement over synchronous drivers for I/O-bound workloads

5. **Connection Pooling**: Built-in SQLAlchemy pooling with `pool_reset_on_return="rollback"` ensures RLS context doesn't leak between requests

6. **Timezone-Aware Timestamps**: `DateTime(timezone=True)` columns store UTC timestamps correctly, essential for multi-region deployments

7. **Mature Ecosystem**: Extensive tooling (pgAdmin, pg_dump, pgBouncer), monitoring (pg_stat_statements), and cloud support (AWS RDS, Cloud SQL, Azure Database)

### Negative

1. **Operational Complexity**: PostgreSQL requires more operational expertise than simpler databases (MySQL, SQLite). Connection tuning, vacuuming, and RLS policy management require PostgreSQL knowledge

2. **Vendor Lock-in**: RLS, JSONB queries, and UUID type are PostgreSQL-specific. Migration to another database would require significant code changes

3. **Memory Usage**: PostgreSQL uses significant memory for caching and connection handling. The configured pool of 30 connections (20 + 10 overflow) requires tuning based on available memory

4. **Docker Resource Requirements**: PostgreSQL container requires dedicated resources, increasing development environment complexity

### Neutral

1. **Version 18 Features**: Using latest PostgreSQL version provides JSON improvements and performance optimizations, but requires keeping Docker image updated

2. **Connection Pool Size**: 20 connections with 10 overflow chosen to balance concurrency with resource usage; may need adjustment for high-traffic deployments

## Alternatives Considered

### MySQL / MariaDB

**Why Not Chosen**:
- No native Row-Level Security - would require views or stored procedures
- JSONB equivalent (JSON type) has less mature indexing
- UUID storage less efficient (requires BINARY(16) or CHAR(36))
- Async drivers less mature than asyncpg

### MongoDB

**Why Not Chosen**:
- No RLS equivalent - tenant isolation requires application-level enforcement
- Schema flexibility is a liability for multi-tenant data (harder to enforce consistency)
- Transaction support (multi-document) is newer and less battle-tested
- Doesn't integrate with SQLAlchemy/Alembic migration workflow

### SQLite

**Why Not Chosen**:
- No Row-Level Security
- No native UUID type
- Single-writer limitation doesn't scale for concurrent access
- Not suitable for production multi-tenant workloads

### CockroachDB

**Why Not Chosen**:
- More complex operational model (distributed by default)
- RLS support is PostgreSQL-compatible but less documented
- Overkill for single-region deployments
- Higher resource requirements

---

## Related ADRs

- [ADR-005: Row-Level Security for Multi-Tenancy](./005-row-level-security-multitenancy.md) - RLS implementation details
- [ADR-006: Dual Database Users Pattern](./006-dual-database-users.md) - User separation for RLS enforcement

## Implementation References

- `backend/app/core/database.py` - Engine configuration and connection pooling
- `backend/app/core/config.py` - Database URL configuration
- `backend/app/models/tenant.py` - UUID and JSONB column definitions
- `backend/alembic/versions/e10757622a70_*.py` - RLS policy creation
- `backend/app/services/tenant_context.py` - RLS context management
