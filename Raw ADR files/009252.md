# ADR-018: Always-On Multi-Tenancy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template originally provided multi-tenancy as an optional feature via a Cookiecutter variable (`enable_multitenancy`). This created significant complexity:

1. **Dual Code Paths**: Every database model, API endpoint, and middleware component needed conditional logic for tenant awareness
2. **Testing Burden**: Both tenanted and non-tenanted configurations required separate test coverage
3. **Documentation Complexity**: Guides needed to explain both modes and their implications
4. **Security Risk**: The single-tenant path was less tested and could have subtle security gaps
5. **Template Maintenance**: Jinja2 conditionals throughout the codebase made the template harder to read and maintain

Additionally, rate limiting was also originally optional, creating similar complexity for security features.

The `docs/todo.txt` file explicitly notes: "we removed the ability to generate projects without multitenancy or rate limiting."

## Decision

We chose to make **multi-tenancy always enabled** in generated projects. Rate limiting is also always enabled.

This means:
- Every generated project includes PostgreSQL Row-Level Security (RLS) policies
- Every generated project uses the dual database user pattern (migration user with BYPASSRLS, application user without)
- Every generated project includes tenant context middleware and service
- Rate limiting via Redis is always configured

**Key Implementation Components**:

**Database Initialization** (`scripts/init-db.sql`):
```sql
-- Migration User: BYPASSRLS for schema management
CREATE ROLE {{project}}_migration_user WITH
    LOGIN PASSWORD '...' BYPASSRLS;

-- Application User: NO BYPASSRLS - RLS enforced
CREATE ROLE {{project}}_app_user WITH
    LOGIN PASSWORD '...' NOSUPERUSER;
```

**Tenant Model** (`backend/app/models/tenant.py`):
- All projects include `Tenant` model with UUID primary key
- Users and other models reference `tenant_id` foreign key

**Tenant Context Service** (`backend/app/services/tenant_context.py`):
- Sets PostgreSQL session variable `app.current_tenant_id`
- RLS policies filter queries based on this variable
- Context manager ensures tenant context is always cleared after requests

**Tenant Middleware** (`backend/app/middleware/tenant.py`):
- Extracts `tenant_id` from JWT claims
- Sets tenant context in request state and contextvars
- Skips tenant resolution for public endpoints (health, OAuth)

**Compose Configuration** (`compose.yml`):
- Backend uses `DATABASE_URL` with application user (RLS enforced)
- Backend uses `MIGRATION_DATABASE_URL` with migration user (BYPASSRLS)

## Consequences

### Positive

1. **Single Code Path**: One implementation to maintain, test, and document. No conditional Jinja2 blocks for tenant logic throughout the template

2. **Security by Default**: Every generated project has robust tenant isolation. Teams cannot accidentally deploy without proper data segregation

3. **Simplified Template**: Removed ~20+ conditional blocks across models, middleware, compose files, and tests. Template is more readable and maintainable

4. **Complete Test Coverage**: All tests exercise the actual production code path. No untested "single-tenant mode" edge cases

5. **Reduced Documentation**: No need to explain two modes, their differences, or migration between them

6. **Production-Ready Default**: Multi-tenant architecture is standard for SaaS applications. Projects start with the right architecture for scaling to multiple customers

7. **Consistent Developer Experience**: All generated projects work the same way. Knowledge transfers between projects

### Negative

1. **No True Single-Tenant Option**: Teams building internal tools or single-customer applications still get multi-tenant infrastructure. This adds slight overhead:
   - Must create at least one tenant record
   - JWT tokens must include `tenant_id` claim
   - Slightly more complex local setup

2. **Architectural Complexity for Simple Use Cases**: A simple CRUD API now requires understanding tenant context, RLS policies, and dual database users

3. **Cannot Opt Out of Rate Limiting**: Even development environments have rate limiting (though limits are configurable)

### Neutral

1. **Single-Tenant Workaround**: Projects needing single-tenant behavior can:
   - Create one tenant during setup
   - Configure Keycloak to always include that tenant_id in tokens
   - Effectively have single-tenant behavior with multi-tenant infrastructure

2. **Rate Limit Configurability**: While always enabled, rate limits are configurable via environment variables. Development can use very high limits

## Alternatives Considered

### Keep Optional Multi-Tenancy (Cookiecutter Variable)

**Approach**: Maintain `enable_multitenancy` variable with conditional template content.

**Why Not Chosen**:
- Significant maintenance burden for two code paths
- Security risk from less-tested single-tenant mode
- Template complexity made contributions harder
- Most real-world applications need multi-tenancy anyway

### Separate Templates (Single-Tenant and Multi-Tenant)

**Approach**: Maintain two separate templates, one for each mode.

**Why Not Chosen**:
- Doubles maintenance effort
- Features and fixes must be applied to both templates
- Risk of templates diverging over time
- No clear demand for single-tenant template

### Runtime Feature Flag

**Approach**: Include multi-tenant code but disable via environment variable at runtime.

**Why Not Chosen**:
- Dead code in single-tenant deployments
- Still need to test both modes
- RLS policies would still be in database (just not used)
- Complexity without clear benefit

### Lightweight Single-Tenant Mode

**Approach**: Multi-tenant code present but simplified single-tenant path (fixed tenant ID).

**Why Not Chosen**:
- Still two code paths to maintain
- Confusion about which mode to use
- Partial solution that doesn't fully address concerns

---

## Related ADRs

- [ADR-005: Row-Level Security for Multi-Tenancy](./005-row-level-security-multitenancy.md) - RLS implementation that multi-tenancy uses
- [ADR-006: Dual Database Users Pattern](./006-dual-database-users.md) - Database user separation for RLS
- [ADR-014: Rate Limiting Strategy](./014-rate-limiting-strategy.md) - Rate limiting also always enabled
- [ADR-016: Cookiecutter as Template Engine](./016-cookiecutter-template-engine.md) - Template simplified by this decision

## Implementation References

- `template/{{cookiecutter.project_slug}}/backend/app/models/tenant.py` - Tenant model
- `template/{{cookiecutter.project_slug}}/backend/app/middleware/tenant.py` - Tenant resolution middleware
- `template/{{cookiecutter.project_slug}}/backend/app/services/tenant_context.py` - PostgreSQL session variable management
- `template/{{cookiecutter.project_slug}}/scripts/init-db.sql` - Dual database user creation
- `template/cookiecutter.json` - No `enable_multitenancy` variable (removed)
- `docs/todo.txt` - Documents the decision to remove optional multi-tenancy
