# ADR 0009: Transactional Outbox Pattern for Reliable Event Publishing

## Context:

The system publishes domain events to Kafka as part of critical business workflows (Event Sourcing, CQRS updates, SAGA coordination).

Publishing events directly to Kafka inside application logic introduces failure scenarios such as:

- Database transaction succeeds but Kafka publish fails
- Kafka publish succeeds but database transaction rolls back
- Application crashes between state mutation and event publication

These scenarios lead to **data inconsistency**, lost events, or phantom side effects — which are unacceptable in a system relying on Event Sourcing and SAGA..

## Decision:

Adopt the **Transactional Outbox Pattern** for all event-producing services.

- Domain events are persisted in an outbox table within the same database transaction as the aggregate state change.
- Events are stored in serialized form with metadata (eventId, aggregateId, type, version, timestamp).
- A dedicated **outbox publisher** asynchronously reads pending events and publishes them to Kafka.
- Events are marked as published only after Kafka acknowledges successful delivery.
- Publishing is retryable and idempotent.

## Rationale:

- **Atomicity:** Database state changes and event persistence are committed together.
- **Reliability:** Prevents event loss even if Kafka or the application is temporarily unavailable.
- **Decoupling:** Business logic is isolated from messaging infrastructure concerns.
- **At-least-once delivery:** Works naturally with Kafka guarantees and complements the Inbox Pattern.
- **Event Sourcing alignment:** Ensures the event log is always consistent with persisted state.

## Consequences:

### Positive

- Eliminates dual-write problems between database and Kafka
- Enables safe retries and crash recovery
- Improves consistency across microservices
- Simplifies operational debugging and replay

### Negative

- Requires additional background processing
- Introduces eventual consistency between DB and Kafka
- Adds storage and cleanup requirements for outbox tables