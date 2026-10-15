# ADR 0005: Event Sourcing + CQRS

## Context:
After experimenting with a standard Event-Driven Architecture (EDA) using Kafka, the project team wanted a more precise way to model domain state changes, improve auditability, and optimize read/write performance. While EDA allows asynchronous communication, it does not inherently provide a replayable state history or separation of concerns between reads and writes.

## Decision:
Adopt Event Sourcing combined with CQRS (Command Query Responsibility Segregation) as the core architectural pattern.

## Rationale:
Event Sourcing advantages over plain EDA:
- **Auditability**: Every state change is persisted as an immutable event, providing a full historical log of the domain.
- **Replayability**: The current state can be reconstructed from the event log, allowing recovery, debugging, or new projections.
- **Consistency across services**: Events are the single source of truth, reducing divergence in state between microservices.
- **Domain clarity**: Forces explicit modeling of domain events, improving code readability and maintainability.

CQRS provides clear separation between write operations (commands) and read operations (queries):
- **Scalability**: Read models can be denormalized and optimized for queries independently of write operations.
- **Flexibility**: Multiple projections can be derived from the same event stream for dashboards, reporting, and analytics.
- **Performance optimization**: Read-heavy and write-heavy workloads can scale independently, avoiding bottlenecks.
- **Easier evolution**: Each read/write model can evolve independently, reducing tight coupling in distributed systems.


## Consequences:
- **Increased initial complexity**: Designing event schemas, projections, and CQRS separation requires careful planning.
- **Higher operational overhead**: Must manage event stores, projections, and eventual consistency.
- **Team learning curve**: Developers must understand Event Sourcing concepts, CQRS, and integration with Kafka or similar event buses.
- **Long-term benefits**:
  - Clear, auditable domain logic.
  - Resilient, replayable state for debugging or feature evolution.
  - Optimized, independent scaling of reads and writes.
  - Easier integration with analytics, dashboards, and future CQRS-driven features.