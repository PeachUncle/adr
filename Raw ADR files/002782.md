# ADR-20251116: PostgreSQL Shared Database with Tenant Discriminator

**Status**: Accepted  
**Date**: 2025-11-16  
**Deciders**: Project Founder (alecsg77)  
**Related**: Initial project architecture, Constitution v1.0.0

---

## Context

MyMoney is a multi-tenant financial accounting application inspired by GnuCash, targeting personal finance users and small businesses. The application requires tenant data isolation to prevent cross-tenant data leaks while maintaining operational simplicity for a solo developer/maintainer.

Three common multi-tenancy data isolation strategies exist:
1. Shared database with tenant discriminator column (tenant ID in each table)
2. Separate schema per tenant within shared database
3. Separate database per tenant

Key forces:
- **Security**: Financial data MUST be isolated between tenants (Constitution: Security & Privacy by Design)
- **Simplicity**: Solo developer, minimize operational overhead (Constitution: Simplicity principle)
- **Cost**: Initial deployment on modest infrastructure budget
- **Scale**: Starting small but should support hundreds of tenants without major refactor
- **Data Integrity**: Audit trails and backups must be comprehensive (Constitution: Data Integrity)
- **ABP Framework**: ABP.io provides built-in multi-tenancy support favoring shared DB approach

**Constitution Alignment Check**:
- [x] **Security & Privacy by Design**: Tenant isolation enforced at query level, audit logs track tenant context
- [x] **Test-First & Quality Gates**: Integration tests with Testcontainers verify tenant filtering
- [x] **Observability & Incident Readiness**: Logs enriched with TenantId for correlation and incident investigation
- [x] **Data Integrity & Auditability**: Immutable audit records include tenant discriminator for complete traceability
- [x] **Simplicity & Minimum Surface Area**: Single database simplifies backup, migration, monitoring compared to per-tenant DBs

---

## Decision

**Use PostgreSQL with a shared database and tenant discriminator column approach.**

All multi-tenant tables will include a `TenantId` column (nullable for host-level data). ABP Framework's `IMultiTenant` interface and data filters will automatically scope queries to the current tenant context.

### Rationale

1. **ABP Native Support**: ABP.io is designed with shared-DB multi-tenancy as the default; leverages built-in `IMultiTenant`, `ICurrentTenant`, and EF Core global query filters.
2. **Operational Simplicity**: Single connection string, single backup/restore, single migration pipeline. Aligns with Simplicity principle and solo maintainer context.
3. **Cost Efficiency**: Shared resources (connection pooling, caching, compute) reduce infrastructure cost vs per-tenant databases.
4. **Adequate Isolation**: Row-level tenant filtering + application-level enforcement prevents cross-tenant access when implemented correctly. Tests verify isolation.
5. **Proven Pattern**: Widely used in SaaS applications at similar scale; well-documented failure modes and mitigation strategies.

---

## Consequences

### Positive

- **Lower operational complexity**: Single DB to backup, monitor, tune, migrate
- **Framework alignment**: ABP's conventions and tooling work out-of-the-box
- **Fast tenant provisioning**: New tenant = new row in `Tenants` table; no DB/schema creation latency
- **Shared query optimization**: Indexes benefit all tenants; easier to diagnose slow queries globally
- **Cost-effective scaling**: Vertical scaling simpler than managing multiple DBs; horizontal via read replicas straightforward

### Negative / Trade-offs

- **Blast radius**: Database-level issue (corruption, crash) affects all tenants simultaneously
- **Noisy neighbor risk**: One tenant's heavy load can degrade performance for others (mitigated via connection pooling, query timeouts)
- **Regulatory constraints**: Some compliance regimes may mandate physical separation (not anticipated for target market but future consideration)
- **Backup granularity**: Cannot backup/restore single tenant independently without custom tooling
- **Query complexity**: Must enforce tenant filter on every query; accidental omission = security vulnerability

### Neutral / Considerations

- **Testing burden**: Must verify tenant isolation explicitly in integration tests (already planned via Constitution)
- **Migration complexity**: Schema changes affect all tenants simultaneously; requires careful coordination (but simpler than per-tenant migrations)
- **Future pivot**: Migrating to separate DBs later is possible but non-trivial (requires data migration tooling and downtime)

---

## Alternatives Considered

### Alternative 1: Separate Schema Per Tenant

**Description**: Each tenant gets a dedicated PostgreSQL schema (namespace) within the shared database. Queries reference `tenant_schema.table_name`.

**Pros**:
- Better logical isolation than shared schema
- Can set per-schema resource limits (via role permissions)
- Slightly easier to backup/restore single tenant (pg_dump schema)

**Cons**:
- **Increased complexity**: Must dynamically switch schema context per request; error-prone
- **ABP mismatch**: ABP's default multi-tenancy is shared-schema; requires custom implementation
- **Migration overhead**: Must run migrations against N schemas; tooling complexity
- **Connection pooling**: Less efficient (connection must be schema-aware)
- **Monitoring**: Harder to aggregate metrics across tenants

**Rejected Because**: Violates Simplicity principle without delivering proportional security benefit. Operational overhead too high for solo maintainer. ABP framework optimized for shared-schema approach.

---

### Alternative 2: Separate Database Per Tenant

**Description**: Each tenant gets a dedicated PostgreSQL database. Application routes requests to correct DB via connection string mapping.

**Pros**:
- **Maximum isolation**: DB-level boundary provides strongest security guarantee
- **Independent scaling**: Can allocate dedicated resources (CPU, memory) per tenant
- **Regulatory compliance**: Easier to satisfy requirements for physical data separation
- **Blast radius containment**: One tenant's DB failure doesn't affect others

**Cons**:
- **Operational nightmare**: N databases to backup, monitor, upgrade, tune
- **Cost explosion**: Connection pool per DB; increased infrastructure cost
- **Migration complexity**: Must orchestrate migrations across N databases; rollback challenging
- **Provisioning latency**: New tenant = create DB, run migrations (seconds to minutes)
- **Feature rollout**: Harder to deploy phased feature flags when schema differs across tenants
- **ABP overhead**: Requires custom connection string resolver and tenant DB management

**Rejected Because**: Premature optimization for scale/security needs not yet present. Violates Simplicity principle dramatically. Operational burden incompatible with solo maintainer model. Can revisit if growth demands per-tenant isolation (e.g., enterprise contracts).

---

## Implementation Notes

**Scope**: 
- **Domain Layer**: Entities implement `IMultiTenant` interface
- **Infrastructure Layer**: EF Core global query filters configured to scope by `TenantId`
- **Application Layer**: Services use `ICurrentTenant` to access current tenant context
- **Web Layer**: Middleware resolves tenant from subdomain/header/claim

**Dependencies**:
- ABP Framework multi-tenancy module (already included in Layered template)
- PostgreSQL 14+ (supports row-level security if needed for defense-in-depth later)

**Migration Path**:
1. Initial schema includes `TenantId` column on all multi-tenant tables
2. Seed host-level data (e.g., admin user) with `TenantId = null`
3. Configure EF Core global query filters in `DbContext.OnModelCreating`
4. Enable ABP multi-tenancy in module configuration

**Testing Strategy**:
- **Unit tests**: Verify `IMultiTenant` interface applied to all relevant entities
- **Integration tests (Testcontainers)**: 
  - Insert data for Tenant A and Tenant B
  - Query as Tenant A; assert Tenant B data not returned
  - Attempt cross-tenant update/delete; assert rejected
- **Security tests**: Manually bypass tenant filter (via raw SQL) to verify defense-in-depth alerts/blocks

**Rollback Plan**:
- If tenant isolation breached: immediately disable new tenant sign-ups; audit logs for cross-tenant access
- If performance untenable: vertical scale DB, add read replicas, implement query caching aggressively
- If pivot to separate DBs needed: build data export tool per tenant → provision new DBs → migrate incrementally

---

## Validation & Success Criteria

**How will we know this decision was correct?**

1. **Security**: Zero cross-tenant data leaks in audit logs over first 6 months
2. **Performance**: p95 query latency remains < 200ms with up to 100 tenants
3. **Operational ease**: Backup/restore process documented and tested in < 30 min RTO
4. **Developer velocity**: New tenant-aware features can be developed without multi-tenancy complexity slowing progress

**Review Timeline**: Revisit this decision after reaching 100 active tenants OR if a tenant requests contractual data isolation guarantee. At that point, evaluate cost/benefit of per-tenant DB option.

---

## References

- ABP Multi-Tenancy Documentation: https://abp.io/docs/latest/framework/architecture/multi-tenancy
- Constitution: `.specify/memory/constitution.md` (Security & Privacy, Simplicity principles)
- PostgreSQL Row-Level Security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html (future defense-in-depth option)
- SaaS Tenant Isolation Strategies (AWS): https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-tenant-isolation-strategies/welcome.html

---

**Notes**:
- This ADR was created during initial project setup based on questionnaire inputs (Pragmatic Layered, PostgreSQL, solo maintainer).
- Shared-DB approach is a conscious trade-off favoring simplicity and ABP alignment over maximum isolation.
- Constitution Principle V (Simplicity) was the deciding factor when comparing alternatives.
