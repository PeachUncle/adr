# ADR-006: Dual Database Users Pattern

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template uses PostgreSQL Row-Level Security (RLS) for tenant data isolation. RLS policies filter rows based on the `app.current_tenant_id` session variable. However, this creates a challenge for database migrations:

1. **Migration Operations**: Alembic migrations need to modify schema and potentially seed data across all tenants
2. **RLS Enforcement**: Standard database users are subject to RLS policies, which would prevent migrations from accessing all tenant data
3. **Security Principle**: Runtime application code should never bypass RLS to maintain defense-in-depth
4. **Least Privilege**: Each database connection should have only the permissions it needs

The system needs to separate concerns between:
- **Runtime Operations**: Always filtered by tenant context (RLS enforced)
- **Administrative Operations**: Schema changes, migrations, seeding (RLS bypassed)

## Decision

We implement a **Dual Database Users Pattern** with two distinct PostgreSQL users:

1. **`app_user`**: Application runtime user with RLS enforced
2. **`migration_user`**: Administrative user with `BYPASSRLS` privilege for migrations

**Configuration** (`backend/app/core/config.py`):
```python
# Application runtime uses app_user (NO BYPASSRLS - RLS policies enforced)
DATABASE_URL: str = "postgresql+asyncpg://{{ cookiecutter.postgres_app_user }}:{{ cookiecutter.postgres_app_password }}@postgres:{{ cookiecutter.postgres_port }}/{{ cookiecutter.postgres_db }}"

# Migration database URL uses migration_user (with BYPASSRLS for schema management)
MIGRATION_DATABASE_URL: str = "postgresql+asyncpg://{{ cookiecutter.postgres_migration_user }}:{{ cookiecutter.postgres_migration_password }}@postgres:{{ cookiecutter.postgres_port }}/{{ cookiecutter.postgres_db }}"
```

**Alembic Configuration** (`backend/alembic/env.py`):
```python
# Override sqlalchemy.url from application settings
# Migrations use MIGRATION_DATABASE_URL (migration_user with BYPASSRLS)
# This allows migrations to bypass RLS policies for schema management
config.set_main_option("sqlalchemy.url", settings.MIGRATION_DATABASE_URL)
```

**User Creation** (PostgreSQL setup):
```sql
-- Application user: RLS enforced (no BYPASSRLS)
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE app_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Migration user: RLS bypassed for schema management
CREATE USER migration_user WITH PASSWORD 'different_secure_password' BYPASSRLS;
GRANT ALL PRIVILEGES ON DATABASE app_db TO migration_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO migration_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO migration_user;
```

## Consequences

### Positive

1. **Principle of Least Privilege**: The application runtime connects with minimal permissions. Even if the application is compromised, the attacker cannot bypass RLS to access other tenants' data:
   ```python
   # Runtime: app_user - RLS enforced
   result = await session.execute(select(User))  # Only current tenant's users

   # The application cannot execute:
   # SET LOCAL row_security = off;  -- Would fail for app_user
   ```

2. **Defense in Depth**: RLS enforcement is not optional for the application. There's no code path that could accidentally bypass tenant isolation:
   ```python
   # This function exists but only works with migration_user
   async def bypass_rls(session: AsyncSession) -> None:
       await session.execute(text("SET LOCAL row_security = off"))
       # Will fail if connected as app_user
   ```

3. **Clear Separation of Concerns**:
   - `DATABASE_URL` (app_user): Used by FastAPI application, always filtered
   - `MIGRATION_DATABASE_URL` (migration_user): Used only by Alembic CLI

4. **Audit Trail**: Different users make it easy to distinguish application queries from migration queries in PostgreSQL logs:
   ```
   LOG:  connection authorized: user=app_user database=app_db
   LOG:  connection authorized: user=migration_user database=app_db
   ```

5. **Credential Rotation**: Users can have different password rotation policies:
   - `app_user`: Rotated frequently via deployment automation
   - `migration_user`: Rotated manually during maintenance windows

### Negative

1. **Configuration Complexity**: Two database connection strings must be managed:
   - Both must be kept in sync for host/port/database
   - Two sets of credentials in environment variables
   - Potential for misconfiguration if URLs diverge

2. **Developer Confusion**: New developers must understand which connection to use:
   - Application code: `DATABASE_URL` (automatic via SQLAlchemy engine)
   - Manual scripts: Must explicitly use correct URL
   - Testing: May need both for different test scenarios

3. **Connection Pool Overhead**: In some setups, maintaining two connection pools (if both are used simultaneously) increases resource usage. However, Alembic typically runs separately from the application.

4. **Privilege Management**: User privileges must be kept in sync when schema changes occur:
   ```sql
   -- After adding new table, must grant to app_user
   GRANT SELECT, INSERT, UPDATE, DELETE ON new_table TO app_user;
   ```

### Neutral

1. **Docker Compose Setup**: Both users can be created in the PostgreSQL initialization script, making development environment setup consistent

2. **Testing Considerations**: Integration tests may use either user depending on what's being tested (tenant isolation vs. data setup)

## Alternatives Considered

### Single User with Dynamic RLS Toggle

**Approach**: Use one database user with `BYPASSRLS` and toggle RLS in application code.

**Why Not Chosen**:
- **Security Risk**: Application code could accidentally (or maliciously) disable RLS
- **No Defense in Depth**: A bug or vulnerability could expose all tenant data
- **Violates Least Privilege**: Runtime has unnecessary permissions

**Code Example (Not Used)**:
```python
# DANGEROUS: Single user approach
async def get_all_users_for_admin():
    await session.execute(text("SET LOCAL row_security = off"))  # Bypasses RLS
    result = await session.execute(select(User))  # All users exposed!
```

### Superuser for All Operations

**Approach**: Use PostgreSQL superuser for both application and migrations.

**Why Not Chosen**:
- **Extreme Security Risk**: Superuser can do anything (drop database, read all tables)
- **Audit Nightmare**: No distinction between application and admin operations
- **Violates Every Security Principle**: Never use superuser for applications

### Schema-Level Permissions

**Approach**: Different schemas for different privilege levels.

**Why Not Chosen**:
- **Complexity**: Multiple schemas complicate queries and migrations
- **RLS Interaction**: RLS policies would need duplication across schemas
- **No Real Benefit**: Doesn't solve the RLS bypass requirement better than dual users

### Application-Managed Privilege Escalation

**Approach**: Application requests elevated privileges from a privilege broker service.

**Why Not Chosen**:
- **Over-Engineering**: Adds complexity without proportional security benefit
- **Performance Overhead**: Additional service call for every admin operation
- **Still Requires Trust**: Application must be trusted to request elevation appropriately

---

## Related ADRs

- [ADR-003: PostgreSQL as Primary Database](./003-postgresql-primary-database.md) - PostgreSQL selection and RLS foundation
- [ADR-005: Row-Level Security for Multi-Tenancy](./005-row-level-security-multitenancy.md) - RLS policy implementation

## Implementation References

- `backend/app/core/config.py` - `DATABASE_URL` and `MIGRATION_DATABASE_URL` configuration
- `backend/alembic/env.py` - Migration user connection configuration
- `backend/app/core/database.py` - Application database engine (uses `DATABASE_URL`)
- `backend/app/services/tenant_context.py` - `bypass_rls()` function documentation
