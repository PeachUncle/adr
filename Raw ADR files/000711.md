# ADR-002: PostgreSQL Row Level Security for Multi-Tenant Isolation

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Architecture Team, Security Team  
**Technical Story:** Multi-tenant data isolation strategy

## Context

The Dashboard Starter Kit needs to provide strong data isolation between tenants in a multi-tenant SaaS environment. We must ensure that:

1. **Data Security**: Tenants cannot access each other's data under any circumstances
2. **Performance**: Isolation mechanism doesn't significantly impact query performance
3. **Development Experience**: Developers don't need to manually add tenant filters to every query
4. **Operational Simplicity**: Single database to manage, backup, and monitor
5. **Compliance**: Meet security requirements for enterprise customers
6. **Scalability**: Solution should handle hundreds of tenants efficiently

We evaluated several multi-tenant database strategies and need to choose the most appropriate approach for our requirements.

## Decision

We will use **PostgreSQL Row Level Security (RLS)** with a **single shared database** for multi-tenant isolation.

### Implementation Approach:
- **Single Database**: All tenants share one PostgreSQL database
- **RLS Policies**: Every tenant-scoped table has RLS enabled with policies
- **Session Context**: Use `SET LOCAL app.tenant_id` in transactions to set tenant context
- **Application Role**: Database role does NOT have `BYPASSRLS` privilege
- **Automatic Enforcement**: RLS policies automatically filter all queries
- **Superuser Context**: Admin users switch tenant context, don't bypass RLS

### RLS Policy Pattern:
```sql
-- Enable RLS on tenant-scoped tables
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;

-- SELECT policy
CREATE POLICY memberships_isolation_select
  ON memberships FOR SELECT
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- WRITE policy
CREATE POLICY memberships_isolation_write
  ON memberships FOR ALL
  USING (tenant_id = current_setting('app.tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);
