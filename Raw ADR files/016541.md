# ADR-005: Row-Level Tenant Isolation Strategy

## Status

**Accepted** - January 2026

## Context

Sentinel RFP is a multi-tenant SaaS platform where each organization's data must be completely isolated. We need to choose an isolation strategy:

1. **Database-per-tenant**: Separate database for each tenant
2. **Schema-per-tenant**: Separate PostgreSQL schemas
3. **Row-level isolation**: Shared tables with tenant ID filter
4. **Hybrid**: Combination approaches

### Requirements

- Strong data isolation for compliance (SOC2, future FedRAMP)
- Cost-effective for large number of tenants
- Simple operational model
- Railway deployment compatibility
- Future support for dedicated infrastructure (enterprise)

## Decision

**Implement Row-Level Isolation with PostgreSQL RLS as defense-in-depth, plus application-level enforcement via Prisma middleware.**

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TENANT ISOLATION LAYERS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LAYER 1: APPLICATION (Primary)                                      │
│  ──────────────────────────────                                      │
│  • Prisma middleware adds organization_id filter to ALL queries     │
│  • Tenant context extracted from JWT token                          │
│  • Explicit validation in services                                  │
│                                                                      │
│  LAYER 2: DATABASE (Defense-in-Depth)                               │
│  ─────────────────────────────────────                              │
│  • PostgreSQL Row-Level Security (RLS) policies                     │
│  • Tenant ID set in session context                                 │
│  • Blocks direct SQL bypass attempts                                │
│                                                                      │
│  LAYER 3: AUDIT (Monitoring)                                         │
│  ────────────────────────────                                        │
│  • All cross-tenant access attempts logged                          │
│  • Alerts on anomalous patterns                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

#### 1. Prisma Middleware (Primary Enforcement)

```typescript
// packages/database/src/middleware/tenant.middleware.ts
import { Prisma } from '@prisma/client';

export function tenantMiddleware(tenantId: string): Prisma.Middleware {
  return async (params, next) => {
    // Tables that require tenant isolation
    const tenantTables = [
      'Proposal',
      'Question',
      'Response',
      'Document',
      'LibraryEntry',
      'Chunk',
      'Integration',
      'User',
    ];

    if (tenantTables.includes(params.model)) {
      // Add filter on read operations
      if (['findMany', 'findFirst', 'findUnique', 'count', 'aggregate'].includes(params.action)) {
        params.args.where = {
          ...params.args.where,
          organizationId: tenantId,
        };
      }

      // Add tenant ID on create
      if (params.action === 'create') {
        params.args.data.organizationId = tenantId;
      }

      // Add filter on update/delete
      if (['update', 'updateMany', 'delete', 'deleteMany'].includes(params.action)) {
        params.args.where = {
          ...params.args.where,
          organizationId: tenantId,
        };
      }
    }

    return next(params);
  };
}
```

#### 2. PostgreSQL RLS (Defense-in-Depth)

```sql
-- Enable RLS on all tenant tables
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE library_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY tenant_isolation_policy ON proposals
  FOR ALL
  USING (organization_id = current_setting('app.tenant_id')::uuid)
  WITH CHECK (organization_id = current_setting('app.tenant_id')::uuid);

-- Repeat for other tables...

-- Set tenant context on connection
-- (Called at start of each request)
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_id UUID)
RETURNS VOID AS $$
BEGIN
  PERFORM set_config('app.tenant_id', tenant_id::text, true);
END;
$$ LANGUAGE plpgsql;
```

#### 3. Request-Scoped Tenant Context

```typescript
// apps/api/src/common/tenant/tenant.context.ts
import { Injectable, Scope } from '@nestjs/common';
import { REQUEST } from '@nestjs/core';
import { Inject } from '@nestjs/common';
import { Request } from 'express';

@Injectable({ scope: Scope.REQUEST })
export class TenantContext {
  constructor(@Inject(REQUEST) private request: Request) {}

  get tenantId(): string {
    return this.request.user?.organizationId;
  }

  get userId(): string {
    return this.request.user?.id;
  }
}

// Usage in service
@Injectable()
export class ProposalService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly tenantContext: TenantContext,
  ) {
    // Prisma client automatically filtered by tenant
    this.prisma.$use(tenantMiddleware(this.tenantContext.tenantId));
  }
}
```

### Schema Design

```sql
-- Every tenant-scoped table MUST have organization_id
CREATE TABLE proposals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  -- other columns...

  CONSTRAINT fk_organization
    FOREIGN KEY (organization_id)
    REFERENCES organizations(id)
    ON DELETE CASCADE
);

-- Index for efficient tenant queries
CREATE INDEX idx_proposals_organization
  ON proposals(organization_id);

-- Composite indexes for common queries
CREATE INDEX idx_proposals_org_status
  ON proposals(organization_id, status);
```

### Testing Strategy

```typescript
describe('Tenant Isolation', () => {
  let tenantA: Organization;
  let tenantB: Organization;
  let proposalA: Proposal;

  beforeEach(async () => {
    tenantA = await createOrganization();
    tenantB = await createOrganization();
    proposalA = await createProposal({ organizationId: tenantA.id });
  });

  it('should not allow tenant B to access tenant A proposals', async () => {
    const service = new ProposalService(prismaWithTenant(tenantB.id));

    const result = await service.findById(proposalA.id);
    expect(result).toBeNull();
  });

  it('should not allow tenant B to update tenant A proposals', async () => {
    const service = new ProposalService(prismaWithTenant(tenantB.id));

    await expect(service.update(proposalA.id, { title: 'Hacked' })).rejects.toThrow('Not found');
  });
});
```

## Consequences

### Positive

- **Strong isolation**: Double enforcement (app + DB)
- **Cost-effective**: Single database, shared infrastructure
- **Simple ops**: One database to backup/monitor
- **Compliance**: Meets SOC2 isolation requirements
- **Audit trail**: All access logged with tenant context

### Negative

- **Performance**: Extra WHERE clause on every query
- **Complexity**: Must ensure middleware always applied
- **Noisy neighbor**: Shared resources could impact performance
- **Migration complexity**: Schema changes affect all tenants

### Mitigations

- Index all organization_id columns
- Connection pooling per tenant (future)
- Monitoring for slow queries by tenant
- Automated tests for isolation

## Future: Dedicated Infrastructure

For Enterprise/GovCon customers requiring dedicated resources:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEDICATED TENANT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Standard Tenants                    Enterprise Tenant              │
│  ────────────────                    ─────────────────              │
│                                                                      │
│  ┌─────────────────┐                ┌─────────────────┐            │
│  │ Shared          │                │ Dedicated       │            │
│  │ PostgreSQL      │                │ PostgreSQL      │            │
│  │                 │                │ (Own Railway    │            │
│  │ • Tenant A      │                │  instance)      │            │
│  │ • Tenant B      │                │                 │            │
│  │ • Tenant C      │                │ • Enterprise X  │            │
│  └─────────────────┘                └─────────────────┘            │
│                                                                      │
│  Routing: Tenant config determines connection string               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Related ADRs

- ADR-001: Event-Driven Architecture
- ADR-003: Vector Storage Strategy

## References

- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Multi-Tenant SaaS Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/overview)
