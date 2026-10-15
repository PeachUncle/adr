# ADR-002: Integration Model & Service Communication Approach

**Status:** Accepted  
**Date:** 2025-12-28  
**Decision Type:**  Architectural Baseline (Integration & Communication Strategy)   

## Related
- ADR-001 — Modular Monolith Architecture
- ADR-003 — Deferred Microservices & Distribution Strategy
- `requirements-refined.md` (Primary NFR drivers)
## Changelog
- **2025-12-29** — Terminology refined; aligned with ADR-003; decision unchanged  

## Context

The Order Processing System (OPS) interacts with multiple external systems:
- Payment System
- Inventory System
- Notification System
- Accounting System

The architecture must define **how OPS communicates** with those external systems and how internal modules collaborate.

Key drivers (the primary NFRs from `requirements-refined.md`):

- **Maintainability**
- **Time-to-Market**
- **Reliability**

Supporting constraints:

- Architecture-as-Code (AaC) as a guiding methodology
- Low-latency operations
- Fast feature delivery for the demo
- Single developer context (initial scope)
- No scale pressure or team distribution (see ADR-003)

## Decision

We will use a **synchronous request/response integration model** for communication:
- **Internal communication:** In-process function calls (within the Modular Monolith)
- **External communication:** HTTPS REST via **Integration Service**

### Integration Mechanism Summary

| Boundary | Communication Style | Protocol/Technology |
|----------|----------------------|-----------|
| Order API → Order Service | In-process call | Java / Spring |
| Order Service → Database | Stateful | JDBC |
| Integration Service → External Systems | Remote call | HTTPS / REST |

The **Integration Service** acts as the **single outbound gateway** to all external dependencies, centralizing:
- communication patterns  
- error handling  
- retry behavior  
- basic observability hooks

In this way the **Integration Service** prevents domain services from depending directly on external systems,
preserving architectural integrity, simplifying testing boundaries, and enabling future extraction.  

The defined communication strategy aligns with ADR-001 (Modular Monolith) and ADR-003 (deferred distribution).

## Rationale

This decision directly supports the **primary NFRs**:

| NFR | How this decision supports it |
|-----|-------------------------------|
| **Maintainability** | Single communication boundary simplifies refactoring and future evolution. |
| **Time-to-Market** | Minimal infrastructure & cognitive load → faster delivery. |
| **Reliability** | Centralized integration logic enables consistent retry/fallback mechanisms. |

Additional rationale:

- Reduces cognitive load for development & deployment 
- Faster AWS deployment path (`API Gateway → Service → DB`)  
- Enables traceability across ADR → C4 → IaC → code (AaC narrative)

##  Alternatives Considered

| Option | Status | Reason |
|--------|--------|--------|
| Microservices per module | **Deferred** | Would introduce premature distribution (see ADR-003) |
| Event-driven integration (SNS/SQS/Kafka) | **Deferred** | NFRs do not justify async yet |
| Direct calls from services to external systems | Rejected | Coupling risks; breaks separation |
| Hybrid (partial decomposition) | Rejected | Adds complexity without NFR justification |

> The alternatives above may become viable if **secondary NFRs (Scalability, High Availability, Observability)** become primary drivers.

## Consequences

### Positive
- Faster development and deployment
- Easier to demonstrate Architecture-as-Code workflows
- Clear evolution path for scaling and distribution
- Compatible with IaC-first deployment on AWS

### Negative / Trade-offs
- Integration Service may become **a bottleneck** at scale
- Limited resilience compared to event-driven design
- Additional effort required to add async patterns later

### Reliability Scope Clarification
This decision satisfies the reliability requirement for **baseline resilience**, meaning:
- failure isolation at the Integration Service
- retry/circuit breaker candidates (not yet implemented)
- no high availability guarantees in this delivery

**High Availability and Scalability are recognized as future NFRs**, not baseline drivers.

## Future Evolution Path (Guided by ADR-003)

This decision allows for:

- Extracting **Integration Service** as first microservice candidate
- Introducing SNS/SQS/EventBridge for async communication
- Scaling containers independently once justified
- Distributed architecture evolution based on updated NFRs

Reevaluation triggers include:

- throughput/latency pressure
- team scaling or domain ownership changes
- SLA/performance divergence per module
- event-driven workflows as primary business driver

## References

- ADR-001 — Modular Monolith Architecture
- ADR-003 — Deferred Microservices & Distribution Strategy
- `requirements-refined.md`
- `c4/workspace.dsl` (Container View)

---

**Decision Accepted — synchronous integration baseline established, with distribution intentionally *deferred*, not *dismissed*.**