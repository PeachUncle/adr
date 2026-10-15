# ADR 002: Event-Driven Architecture with Outbox Pattern

**Status**: Accepted  
**Date**: 2026-01-10  
**Deciders**: Architecture Team

## Context

Modules need to communicate changes to other modules and external systems. We need asynchronous, reliable inter-module communication.

**Requirements**:

- Reliable event delivery (no message loss)
- At-least-once delivery semantics
- Decouple modules (no direct HTTP calls between modules)
- Enable event-driven workflows (AI agents, automation)

## Decision

**Implement event-driven architecture using RabbitMQ with the Outbox Pattern** for reliable event publishing.

### Outbox Pattern

1. **Write Phase** (within business transaction):
   - Insert/update business entity (e.g., Product)
   - Insert event into Outbox table (same DB transaction)
   - Commit transaction atomically

2. **Publish Phase** (background job):
   - Poll Outbox table for unpublished events
   - Publish to RabbitMQ
   - Mark as published in Outbox table

### Event Naming Convention

`{module}.{entity}.{action}`

Examples:

- `ims.product.created`
- `billing.invoice.paid`
- `booking.appointment.cancelled`

## Consequences

### Positive

- **Reliability**: Outbox pattern garanties ensures event publishing (no dual-write problem)
- **Decoupling**: Modules don't need to know about consumers
- **Scalability**: Asynchronous processing, can handle bursts
- **Audit trail**: Outbox table provides event history
- **Flexibility**: Easy to add new event consumers

### Negative

- **Complexity**: Additional infrastructure (RabbitMQ, background job)
- **Eventual consistency**: Events are not published immediately (small delay)
- **Outbox cleanup**: Need periodic cleanup of published events
- **Testing**: Harder to test event flows end-to-end

### Neutral

- **Message ordering**: RabbitMQ doesn't guarantee global ordering (acceptable for our use cases)
- **Idempotency**: Consumers must handle duplicate events (at-least-once delivery)

## Alternatives Considered

### Direct HTTP Calls

**Pros**:

- Simple, synchronous
- Immediate feedback

**Cons**:

- Tight coupling between modules
- Cascading failures (if target module is down)
- No async workflows

**Why not chosen**: Violates loose coupling principle

### Database Triggers

**Pros**:

- Automatic event publishing

**Cons**:

- Logic in database (harder to test, version control)
- Performance impact
- Limited to single database type

**Why not chosen**: Poor maintainability

### Change Data Capture (CDC)

**Pros**:

- No code changes needed
- Captures all changes

**Cons**:

- Infrastructure complexity (Debezium, Kafka)
- Harder to control event schema
- Overkill for our scale

**Why not chosen**: Unnecessary complexity for current requirements

## Implementation Notes

**Outbox Table Schema**:

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    published_at TIMESTAMP NULL,
    published BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_outbox_unpublished 
ON outbox_events (published, created_at) 
WHERE NOT published;
```

**Background Job** (Hangfire, Quartz):

- Run every 5 seconds
- Process in batches (100 events at a time)
- Retry failed publishes with exponential backoff

## References

- [Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
- [Event Sourcing vs Event-Driven](https://martinfowler.com/articles/201701-event-driven.html)
- [RabbitMQ Best Practices](https://www.rabbitmq.com/best-practices.html)

---

**Version**: 1.0
