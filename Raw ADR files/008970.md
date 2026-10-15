# ADR-001: Tenant Isolation Strategy

## Status
Accepted

## Date
2025-12-07

---

## Context

This project is a **multi-tenant e-commerce platform** where each tenant represents an independent organization.

The system must ensure:
- strict isolation of tenant data
- operational simplicity
- scalability to thousands of tenants
- maintainable development workflows

Tenant isolation is a **foundational architectural decision** that impacts:
- database design
- security
- query patterns
- testing strategy
- operational complexity

Once chosen, changing this strategy later would be costly.

---

## Decision

We will use a **single PostgreSQL database with a shared schema**, enforced by a strict application-layer framework.

### Implementation Details

1.  **Data Model**:
    *   All tenant-owned models must inherit from `tenants.models.TenantAwareModel`.
    *   This base class enforces a `tenant_id` foreign key.
    *   Database-level uniqueness is enforced via `tenants.models.UniqueTenantConstraint` (e.g., unique SKU *per tenant*).

2.  **Context Resolution**:
    *   Tenant is resolved per-request by `tenants.middleware.TenantAwareMiddleware` based on the subdomain.
    *   The tenant object is stored in context storage using `contextvars` (via `tenants.context`).

3.  **Query Filtering**:
    *   `TenantAwareModel` uses `tenants.models.TenantManager` as the default manager.
    *   `TenantManager` automatically injects `filter(tenant=current_tenant)` into every query.
    *   Cross-tenant access is strictly forbidden and requires explicit overrides (e.g., for background tasks).

---

## Alternatives Considered

### 1. Separate Database per Tenant

**Description**
Each tenant has its own PostgreSQL database.

**Pros**
- Strong physical isolation
- Low risk of data leakage
- Simple mental model

**Cons**
- High operational complexity
- Difficult migrations
- Poor scalability for large tenant counts
- Expensive infrastructure
- Complicated cross-tenant operations

**Reason Rejected**
Operational overhead and cost outweigh benefits at this stage.

---

### 2. Separate Schema per Tenant

**Description**
Each tenant has its own schema within a shared database.

**Pros**
- Better isolation than shared schema
- Single database to manage

**Cons**
- Complex migrations
- Schema management overhead
- ORM complexity
- Harder local development

**Reason Rejected**
Adds complexity without sufficient benefit for current scale.

---

### 3. Shared Schema with `tenant_id` (Chosen)

**Description**
All tenants share the same tables.
Tenant ownership is enforced via a `tenant_id` column.

**Pros**
- Simplest operational model
- Easy migrations
- Cost-effective
- Works well with Django ORM
- Scales well when disciplined

**Cons**
- Risk of tenant data leakage if filters are missed
- Requires strict code review and testing
- Authorization logic is more complex

---

## Consequences

### Positive
- Simple infrastructure
- Fast development
- Easy onboarding
- Familiar Django patterns

### Negative
- Missing a tenant filter is a **critical security bug**
- Requires discipline across the entire codebase
- Tenant safety must be enforced culturally and technically

---

## Enforcement Rules

To support this decision, the following rules are mandatory:

1.  **Inheritance**: Every tenant-owned model **must** inherit from `TenantAwareModel`.
2.  **Middleware**: `TenantAwareMiddleware` must be placed after `AuthenticationMiddleware` in `settings.MIDDLEWARE`.
3.  **No Global Queries**: Never use `.objects.all()` on tenant models without the `TenantManager` active.
4.  **Explicit Context**: Services running outside the request cycle (e.g., Celery tasks) must accept `tenant` explicitly and use `set_tenant_context()`.
5.  **Scoped Constraints**: Use `UniqueTenantConstraint` instead of `unique=True` for tenant-scoped fields.
6.  **Testing**: Tests must explicitly attempt cross-tenant access to verify isolation.

Violating any of these rules is considered a **blocking issue**.

---

## Security Considerations

### Risks & Mitigations

| Risk | Mitigation | Implementation |
|------|------------|----------------|
| **Forgotten Filters** | Automatic filtering | `TenantManager` injects filters by default. |
| **IDOR** | UUIDs + Scoped Queries | Primary keys are UUIDs; queries are always scoped to tenant. |
| **Subdomain Takeover** | Validation | `TenantAwareMiddleware` validates subdomain format and reserved words. |
| **Data Leakage** | Context Isolation | `contextvars` ensures tenant context does not leak between async tasks/threads. |

---

## Future Considerations

If risk or scale demands increase, the following may be introduced:
- PostgreSQL Row-Level Security (RLS)
- Tenant-aware base querysets
- Database-level safeguards
- Migration to schema-per-tenant (unlikely)

These are intentionally deferred to avoid premature complexity.

---

## References

- `docs/ARCHITECTURE.md`
- Django ORM best practices
- PostgreSQL multi-tenancy patterns
- `tenants/models.py` (`TenantAwareModel`, `TenantManager`)
- `tenants/middleware.py` (`TenantAwareMiddleware`)
