# ADR 001: Multi-Tenant Architecture Strategy

## Context
- SaaS platform with NestJS + Mongoose; tenants currently identified via JWT / guards.
- Requirements: strict data isolation, minimal cross-tenant leakage risk, scalable onboarding, and manageable operational overhead.
- Constraints: existing single MongoDB deployment, request-level tenant context already present (guards/context), preference to avoid per-tenant infra sprawl short term.

## Decision Drivers
- Security & isolation (must prevent cross-tenant data access).
- Operational complexity (DB provisioning, migrations, monitoring).
- Performance & cost (balance isolation vs. infra sprawl).
- Flexibility for future premium tenants (ability to graduate to stronger isolation if needed).
- Developer ergonomics (minimal code churn, clear abstractions).

## Considered Options
1) Shared database + `tenantId` (row-level isolation).
2) Schema-per-tenant (logical isolation).
3) Database-per-tenant (physical isolation).
4) Hybrid: default shared DB w/ `tenantId`; opt-in dedicated DB for high-sensitivity tenants.

## Decision
Adopt **Hybrid**:
- Default: shared Mongo database with strict `tenantId` scoping and query interceptors.
- Tiered: allow dedicated database connection per tenant (or per tier) via connection resolver + repository factory.

Justification:
- Meets current cost/operational constraints while enabling stronger isolation for premium tenants.
- Minimizes migration risk: start with row-level isolation; future-proof with connection resolution layer.
- Keeps developer ergonomics reasonable (shared abstractions + tenant-aware repositories).

## Consequences
**Positive**
- Clear path to stronger isolation without rewrites (switch connection resolver per tenant).
- Centralized enforcement via base repository / interceptors reduces leakage risk.
- Works with existing NestJS/Mongoose stack.

**Negative**
- Added abstraction (resolver/factory) introduces complexity.
- Dedicated DB tenants increase operational overhead (migrations, monitoring, backups).
- Need robust telemetry to detect isolation violations.

**Mitigations**
- Automated migrations per-connection; connection pooling caps; per-tenant metrics/alerts.
- Strict lint/tests to forbid unscoped queries; CI checks for missing tenant filters.

## Implementation Blueprint (NestJS + Mongoose)
- `TenantContext` (request-scoped) resolves tenant from subdomain/header/JWT.
- `ITenantEntity` shape: `{ tenantId: string; createdAt; updatedAt; }`.
- `TenantBaseRepository<T extends ITenantEntity>` wraps Mongoose models:
  - injects `tenantId` on create; filters by `tenantId` on all read/update/delete.
  - optional connection override via `TenantConnectionResolver`.
- `TenantConnectionResolver` decides shared vs dedicated connection; cache connections by tenant.
- Mongoose middleware/interceptor: pre `find/findOne/update/delete` to enforce `tenantId` filter if missing.
- Nest middleware/guard: populate `TenantContext` early; reject requests without tenant.
- Audit/log context enrichers include `tenantId` on all logs/metrics.
- Provisioning workflow: creates tenant record + (optional) dedicated DB, seeds system roles/admin, emits audit event.
- Testing: unit tests for repo filter enforcement; integration tests validating no cross-tenant leakage; perf tests for shared vs dedicated.

## Migration Steps (from current state)
1) Introduce `TenantContext` (already present) and enforce `tenantId` in all domain entities & repositories.
2) Add base repository and apply to all Mongoose repositories; add guard rails (throw if tenant missing).
3) Implement connection resolver + factory; default to shared connection; config flag for dedicated tenants.
4) Add request middleware to resolve tenant (subdomain/header/JWT) and populate context.
5) Add audit/log enrichment with `tenantId`; add per-tenant metrics.
6) Backfill tenant indexes: compound indexes on `{ tenantId, primaryKey }` and hot queries.
7) Add tests: isolation, leakage, performance; add CI check for unscoped queries.

## Open Questions / Follow-ups
- Decide which tiers warrant dedicated DB; define SLAs.
- Data export/import per tenant and disaster recovery implications.
- Tenant-specific feature flags and configuration storage strategy.
- Rollout plan for existing data (backfill tenantId, verify indexes). 
