# ADR-003: Deferred Microservices & Distribution Strategy

**Status:** Accepted  
**Date:** 2025-12-29  
**Related:**  
- ADR-001 — Modular Monolith Architecture  
- ADR-002 — Integration Model & Service Communication Approach  
- `requirements-refined.md` (NFR drivers)  

## Context

The Order Processing System (OPS) integrates with multiple external systems (Payment, Inventory, Notification, Accounting).  
Microservices may seem like a natural choice for such a system.

However, architectural decisions must align with **current** product context, not anticipated future scale.

Key context factors:

- Primary NFRs: **Maintainability, Time-to-Market, Reliability**
- Secondary NFRs: **Scalability, High Availability, Observability**
- Focus on Architecture-as-Code workflows
- Single developer (initial project scope)
- No current scale pressure or team distribution

## Decision

We will **not** adopt microservices at this stage.

We continue with the **Modular Monolith** defined in ADR-001 and the synchronous integration model in ADR-002.

> Microservices are **deferred**, not rejected.  
> Distribution decisions will follow evolving NFRs — not precede them.

## Rationale

Microservices would:

- Increase operational and infrastructure complexity
- Slow delivery and learning cycles
- Require advanced resilience, observability, and versioning from day one
- Undermine the presentation/demo clarity

| Current Need | Microservices Effect | Conclusion |
|--------------|--------------------|------------|
| Maintainability | More moving parts, cross-service dependencies | ❌ Negative |
| Time-to-Market | Slower due to infra/code complexity | ❌ Negative |
| Reliability | Adds network failure modes prematurely | ⚠️ Not required |
| AaC Workflow | Distributed architecture complicates traceability | ❌ Negative |
| Scalability | Not required yet | ➖ No value today |

And provide **no current architectural benefit** based on accepted drivers.

---

## Alternatives Considered

| Option | Status | Reason |
|--------|--------|--------|
| Full microservices per capability | ❌ Rejected | Delivery speed + complexity conflict with primary NFRs |
| Hybrid (2–3 services split) | ❌ Rejected | Still premature distribution |
| Modular Monolith (internal modules) | ✔️ Accepted | Evolvable and fastest to deliver |
| Monolith + Async integration | ⏳ Deferred | Re-evaluate only if NFRs change |

## Consequences

### Positive
- Lower cognitive and operational load
- Clean baseline for Architecture-as-Code demonstration
- Faster implementation & CI/CD pipeline setup
- Simplified security and IAM boundaries
- Clear path to future evolution if triggered

### Negative / Risks
- No independent deployment per module
- Scaling boundaries not separated yet
- Future extraction may require code restructuring

## Future Evolution Triggers

Microservices will be reconsidered when at least one applies:

- High throughput or latency requirements emerge
- Independent team ownership needed per domain capability
- Module-specific SLAs/scaling requirements appear
- Event-driven workflows become primary business concern
- Distributed deployment required for cost or resilience

Likely first extraction candidate:

- **Integration Service** - owns all outbound dependencies and is easiest to isolate as an independent bounded context.

## Architectural Principle

> "Architecture decisions must follow the problem —  
> not precede it."

This reinforces an Architecture-as-Code mindset:
- decisions are **intentional**
- decisions are **traceable**
- decisions are **evolvable**
- decisions are **reversible**

## References

- ADR-001 — Modular Monolith Architecture  
- ADR-002 — Synchronous Integration  
- `/requirements/requirements-refined.md`  
- `/c4/workspace.dsl`  

---

**Decision Accepted — microservices intentionally *deferred*, not *dismissed*.**
