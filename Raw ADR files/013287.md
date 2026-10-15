# ADR-001: Adopt a Modular Monolith with 4 Containers

**Status:** Accepted  
**Date:** 2025-12-28  
**Decision Type:** Architectural Baseline  
## Changelog
- **2025-12-29** — Terminology refined; aligned with ADR-003; decision unchanged


---

## Context

The Order Processing System (OPS) manages the lifecycle of customer orders and must:

- separate responsibilities clearly
- ensure maintainability and testability
- integrate with multiple external systems (Payment, Inventory, Notifications, Accounting)
- support incremental delivery and future scaling options
- enable an Architecture-as-Code (AaC) workflow for traceability and automation

Based on the **primary NFRs identified in `requirements-refined.md`**:

- **Maintainability**
- **Time-to-Market**
- **Reliability**

there is *no present justification* for distributed deployment or independently scalable services.

## Decision

OPS will be structured as **four containers** within a  
**Modular Monolith architecture**:

| Container | Responsibility | Tech Stack |
|-----------|----------------|-------------|
| **Order API** | Entry point, request handling, routing | REST API (Spring Boot) |
| **Order Service** | Domain workflows & business logic | Java / Spring Boot |
| **Order Database** | Persistent data storage | PostgreSQL |
| **Integration Service** | Gateway to all external systems | Java / Spring Boot |

This structure is defined and versioned as code in `c4/workspace.dsl`.

**Architecture Style Chosen:**
> **Modular Monolith with intentional container boundaries**


## Rationale

This structure:

- aligns directly with the **primary NFRs**
- reduces cognitive & infrastructure load for early delivery
- simplifies local development & CI/CD for the demo
- supports iterative refinement (key for AaC)
- keeps communication in-process for speed & simplicity
- allows future decomposition if justified

It is the **simplest architecture that can work** for the current context,  
while preserving future evolution paths.

## Alternatives Considered

| Option | Status | Reason |
|--------|--------|--------|
| Microservices | **Deferred** | Premature distribution; no primary NFR justification *(See ADR-003)* |
| Event-driven modules | **Deferred** | Future option if async becomes a requirement |
| Single-layer monolith | Rejected | Sacrifices maintainability & modularity |
| Multiple deployable components | Deferred | Delivery velocity and overhead conflict with demo goals |

## Consequences

### Positive
- Supports fast feedback cycles
- Simplified IAM & networking boundaries on AWS
- Lower operational complexity

### Negative / Trade-offs
- Modules are not independently deployable (by design)
- Scaling requires selective extraction in the future
- Requires discipline to maintain container boundaries in code

## Evolution Strategy

This ADR assumes **future evolution is possible**:

- Extract containers → microservices if NFR priorities change *(See ADR-003)*
- Introduce async messaging (SNS/SQS/EventBridge) when required

The architecture is intentionally **evolvable, not fixed**.

---

## Decision Scope

This ADR applies to:

- high-level structure
- module boundaries
- deployment shape (single unit)
- synchronous communication baseline (extended in ADR-002)

It does *not* define:

- internal module code structure
- data schema
- API contract formats
- deployment infrastructure

Those will be addressed in later ADRs.

## References

- `requirements-refined.md` — primary NFRs
- `ADR-002` — synchronous integration model
- `ADR-003` — deferred microservices & distribution
- `c4/workspace.dsl` — container model definition

---

**Decision Accepted — Modular Monolith established as the baseline architecture style, with distribution intentionally *deferred*, not *dismissed*.**
