# ADR-001: Event-Driven Architecture

## Status

**Accepted** - January 2026

## Context

Sentinel RFP needs to handle multiple asynchronous workflows:

- Document ingestion and processing
- AI agent orchestration
- Third-party integrations (Slack, Salesforce, etc.)
- Real-time collaboration features
- Analytics and audit logging

We need to decide between:

1. **Synchronous request-response** - Traditional API calls
2. **Event-driven architecture** - Async communication via events
3. **Hybrid approach** - Mix of both

### Forces at Play

- Document processing can take 30-60 seconds
- LLM calls are slow (2-5 seconds) and expensive
- Users expect real-time feedback
- Integrations may be temporarily unavailable
- Audit trail is critical for compliance
- System must scale horizontally

## Decision

**Adopt Event-Driven Architecture as the default pattern for cross-module communication.**

### Implementation Details

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVENT FLOW ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PRODUCERS                    EVENT BUS                 CONSUMERS    │
│  ─────────                   ──────────                ──────────   │
│                                                                      │
│  API Server ───────┐                           ┌───── Worker        │
│                    │                           │                     │
│  Worker ───────────┼───▶  Redis Streams  ◀────┼───── Integrations  │
│                    │                           │                     │
│  Integrations ─────┘                           └───── Analytics     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Event Categories

| Category               | Examples                             | Persistence |
| ---------------------- | ------------------------------------ | ----------- |
| **Domain Events**      | proposal.created, response.generated | 30 days     |
| **Integration Events** | slack.message.received, crm.synced   | 7 days      |
| **System Events**      | job.failed, health.degraded          | 24 hours    |

### Event Schema

```typescript
interface DomainEvent<T = unknown> {
  id: string; // UUID v7 (time-sortable)
  type: string; // e.g., "proposal.created"
  version: string; // Schema version
  timestamp: string; // ISO 8601
  source: string; // Service name
  correlationId: string; // Request trace ID
  causationId?: string; // Parent event ID
  tenantId: string; // Organization ID
  userId?: string; // Actor
  data: T; // Event payload
  metadata: Record<string, unknown>;
}
```

### Technology Choice: Redis Streams

Selected Redis Streams over alternatives:

- **Kafka**: Overkill for Phase 1-2 scale, complex ops
- **RabbitMQ**: Additional infrastructure, not Railway native
- **SQS**: AWS lock-in, not suitable for Railway
- **Redis Streams**: Already have Redis, sufficient throughput

## Consequences

### Positive

- **Decoupling**: Services don't need to know about each other
- **Resilience**: Failed consumers don't block producers
- **Scalability**: Easy to add new consumers
- **Auditability**: Events provide natural audit trail
- **Replay**: Can replay events for debugging/recovery

### Negative

- **Complexity**: Eventual consistency requires careful handling
- **Debugging**: Harder to trace distributed flows
- **Learning curve**: Team needs to understand event patterns
- **Ordering**: Must handle out-of-order events

### Mitigations

- Implement distributed tracing (correlation IDs)
- Use idempotent event handlers
- Document event schemas with versioning
- Build event replay tooling for debugging

## Related ADRs

- ADR-008: Saga Pattern for Distributed Transactions
- ADR-007: CQRS for Proposals Domain

## References

- [Redis Streams Documentation](https://redis.io/docs/data-types/streams/)
- [Event-Driven Architecture by Martin Fowler](https://martinfowler.com/articles/201701-event-driven.html)
