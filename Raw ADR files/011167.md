# ADR-0011: GHL Phaseout & Proprietary CRM Strategy

**Status**: Under Review (awaiting team decision)  
**Date**: 2025-10-30  
**Deciders**: Architecture team, Team Lead, Product  
**Links**: 
- [Strategic Analysis](./ARCH-GHL-PHASEOUT-strategic-analysis.md)
- [Invoice Investigation Findings](./07-invoice-investigation-findings.md)
- [Issue #14](https://github.com/raming/hakim-platform-ops/issues/14)

---

## Context

### Current Situation
- **Phase 1** (current) uses GHL as primary CRM adapter
- **Invoice investigation (#14)** revealed GHL lacks critical APIs:
  - ❌ No invoice creation endpoint
  - ❌ No task creation endpoint  
  - ❌ All billing endpoints are READ-ONLY
- **Architecture is vendor-agnostic**: ICRMPort abstraction already supports multiple implementations
- **Billing is self-hosted**: Stripe integration complete, no dependency on GHL for invoicing
- **Portal is customer-facing**: Customers never see GHL UI directly (ADR-0001)

### Problem
GHL was designed as a CRM-only tool, not a billing platform. While adequate for Phase 1 MVP, GHL's limitations prevent:
1. **Autonomous invoicing** — No API to create invoices programmatically
2. **Task automation** — No API to create tasks programmatically
3. **Full customization** — Limited to GHL's schema
4. **Cost efficiency** — Paying ~$1–3/customer/month + operational overhead

These limitations become **critical blockers for Phase 2/3** (autonomous agent operations, invoice generation, task management).

---

## Decision

**We will phase out GHL in favor of a proprietary CRM, implemented in phases to minimize customer disruption.**

### Rationale

1. **Architecture Already Supports It**: ICRMPort abstraction is vendor-agnostic; GHL is just one adapter
2. **Invoice Gap is Fundamental**: GHL cannot do invoicing by design (not a billing platform)
3. **Enables Differentiation**: Proprietary CRM becomes platform differentiator
4. **Reduces Dependency Risk**: No longer locked into GHL's roadmap/pricing
5. **Cost Savings**: Eliminate ~$3–12k/year in GHL fees as customer base grows
6. **Unlocks Autonomous Billing**: Can generate invoices programmatically once owned
7. **Better UX**: Unified portal (not "portal + GHL redirect")

### Phasing Strategy

| Phase | Scope | Timeline | GHL Role |
|-------|-------|----------|----------|
| **Phase 1** | MVP with GHL | Oct–Dec 2025 | Primary CRM |
| **Phase 2** | Build proprietary CRM (internally) | Jan–Mar 2026 | Coexists (dual-write) |
| **Phase 3** | Migrate early customers | Apr–Jun 2026 | Legacy (optional) |
| **Phase 4** | Sunset GHL | Jul+ 2026 | Optional for workflows |

**Key: Zero customer disruption** — Phasing ensures seamless migration.

---

## Consequences

### Positive
- ✅ **Full autonomy**: Can create invoices, tasks, custom fields, workflows
- ✅ **No vendor lock-in**: Data owned by customers (us), not GHL
- ✅ **Competitive advantage**: Proprietary CRM becomes differentiator
- ✅ **Cost reduction**: $3–12k/year saved (per customer base size)
- ✅ **Better margins**: Remove GHL cost from customer bill or keep as margin
- ✅ **Incremental migration**: Phases 1–4 allow time to build and validate

### Negative
- ❌ **Engineering effort**: ~4–6 months (Phases 2–3) for CRM + migration
- ❌ **Operational overhead**: Maintain proprietary CRM (database, scaling, support)
- ❌ **Risk**: Data migration requires careful testing and rollback procedures
- ❌ **Team capacity**: Requires allocation of 2–3 engineers during Phase 2

### Mitigations
- **Dual-write mode** during Phase 2 to ensure data consistency
- **Feature flags** to enable/disable per-tenant
- **Rollback procedure** < 5 minutes if issues detected
- **Load testing** before Phase 3 customer migrations

---

## Implementation Plan

### Phase 2: Proprietary CRM MVP (Jan–Mar 2026)
**Deliverables**:
- PostgreSQL schema (contacts, opportunities, tasks, custom fields)
- API endpoints (CRUD for contacts/opps/tasks)
- Portal UI updates (use proprietary CRM data)
- Data sync from GHL → proprietary DB
- Test suite (≥95% coverage)
- Feature flag infrastructure

**Success Metrics**:
- ✅ All ICRMPort methods implemented
- ✅ Zero data loss during sync
- ✅ API response < 200ms (90th percentile)
- ✅ ≥3 internal test customers on proprietary CRM

### Phase 3: Customer Migration (Apr–Jun 2026)
**Deliverables**:
- Migration tooling (backup, import, validate)
- Early customer cohort (5–10 customers)
- Rollback procedure documented & tested
- Monitoring & alerting

**Success Metrics**:
- ✅ 5–10 customers successfully migrated
- ✅ Zero data loss
- ✅ NPS maintained or improved
- ✅ <5 min rollback time verified

### Phase 4: Full Replacement & Sunset (Jul 2026+)
**Deliverables**:
- Remaining customers migrated
- GHL adapter in maintenance mode (disabled by default)
- Cost savings realized

---

## Alternatives Considered

### Option A: Keep GHL Indefinitely ❌
- Pros: No dev effort
- Cons: Cannot build autonomous invoicing, locked into GHL limits, higher cost

### Option B: Alternative CRM (Salesforce, HubSpot) ❌
- Pros: More powerful
- Cons: Even higher cost ($10–50/mo), still vendor-locked

### Option C: Hybrid (GHL + Proprietary) ⚠️
- Pros: Customers can choose GHL workflows
- Cons: Operational complexity, still pay GHL fees

### Option D: Full Proprietary Replacement ✅ **CHOSEN**
- Pros: Full control, no vendor lock-in, enables autonomy, cost savings
- Cons: Engineering effort, migration complexity

---

## Governance & Decisions

### Go/No-Go Checkpoints

**Checkpoint 1 (End Phase 1 — Dec 2025)**:
- ✅ >5 paying customers
- ✅ NPS > 50
- ✅ Invoice investigation complete (DONE)
- **Decision**: Proceed with Phase 2 planning?

**Checkpoint 2 (Midway Phase 2 — Feb 2026)**:
- ✅ CRM MVP 50% complete
- ✅ Dual-write working
- ✅ Performance benchmarks met
- **Decision**: Continue toward Phase 3 migration?

**Checkpoint 3 (End Phase 2 — Mar 2026)**:
- ✅ Production-ready CRM
- ✅ ≥3 internal test customers
- ✅ 95%+ coverage, all benchmarks met
- **Decision**: Begin Phase 3 customer migrations?

### Approval Process
1. **Architecture team review**: This ADR + strategic analysis
2. **Team Lead alignment**: Resource allocation for Phase 2
3. **Product approval**: Customer communication strategy
4. **Final sign-off**: CTO/Leadership

---

## Success Criteria (Overall)

| Metric | Target | Timeline |
|--------|--------|----------|
| **Proprietary CRM MVP** | Complete | Mar 2026 |
| **Customers migrated** | 100% | Sep 2026 |
| **GHL fees eliminated** | $3–12k/year | Sep 2026 |
| **Data integrity** | 100% (zero loss) | Ongoing |
| **API performance** | < 200ms (p90) | Mar 2026 |
| **Test coverage** | ≥95% | Mar 2026 |

---

## References

- ADR-0001: GHL Encapsulation Strategy
- ADR-0004: Payments (Gateway-Agnostic)
- Document 07: Invoice Investigation Findings (#14)
- Strategic Analysis: ARCH-GHL-PHASEOUT-strategic-analysis.md
- ICRMPort Design: docs/design/integrations/crm-port.md

---

**Status**: DRAFT — Pending team review and approval
