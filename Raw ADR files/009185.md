# ADR 0010: Event Metadata and Correlation Strategy

## Context:

In a distributed system based on Event Sourcing, CQRS, and SAGA orchestration, understanding why, when, and in which context an event was produced is as important as the event payload itself.

Without standardized metadata:

- Tracing a business flow across services is difficult.
- Correlating logs, metrics, and traces becomes unreliable.
- Debugging SAGA failures requires manual reconstruction.
- Idempotency and deduplication are harder to implement safely.

## Decision:

Define and enforce a **standard event metadata model** attached to every published event.

Each event includes a metadata envelope containing:

- `eventId`: Unique identifier for the event
- `eventType`: Logical name and version of the event
- `aggregateId`: Identifier of the aggregate that produced the event
- `correlationId`: Groups all events belonging to the same business transaction
- `causationId`: Identifies the event or command that caused this event
- `sagaId`: Identifier of the SAGA instance (when applicable)
- `traceId`: Distributed tracing identifier (OpenTelemetry compatible)
- `occurredAt`: Event creation timestamp (UTC)
- `schemaVersion`: Avro schema version

Metadata is:

- Persisted in the event store / outbox
- Propagated through Kafka headers
- Injected into logs, metrics, and traces automatically

## Rationale:

- **End-to-end traceability:** Enables full reconstruction of distributed workflows.
- **SAGA observability:** Makes SAGA state transitions explicit and debuggable.
- **Operational debugging:** Correlates logs, metrics, and traces with no guesswork.
- **Idempotency support:** `eventId` enables safe deduplication in consumers.
- **Schema evolution safety:** Explicit versioning avoids silent incompatibilities.

## Consequences:
### Positive

- Drastically improved debugging and root cause analysis
- Clear causal chains between commands and events
- Strong alignment between Kafka, tracing, and logging layers
- Simplifies observability tooling integration

### Negative

- Slight increase in event size
- Requires strict discipline and validation across all producers
- Metadata propagation must be enforced consistently