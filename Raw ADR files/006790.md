# 3. Use Event Sourcing for Payment State

Date: 2025-03-10

## Status

Accepted

## Context

Payment transactions go through multiple state transitions:
- Created → Processing → Succeeded/Failed
- Succeeded → Refund Requested → Refunded
- Processing → Chargeback Initiated → Chargeback Resolved

Requirements:
- Complete audit trail of all payment state changes
- Ability to reconstruct payment history
- Support for debugging payment issues
- Compliance and regulatory requirements
- Analysis of payment patterns

Traditional state storage (last-write-wins) loses historical information and makes debugging difficult.

## Decision

We will implement **Event Sourcing** for payment state management:

1. Store all state changes as immutable events
2. Rebuild current state by replaying events
3. Use PostgreSQL for event storage
4. Publish events to Kafka for downstream consumers

### Event Types

```typescript
- PaymentCreated
- PaymentProcessing
- PaymentSucceeded
- PaymentFailed
- RefundInitiated
- RefundProcessed
- ChargebackReceived
```

### Event Schema

```typescript
interface PaymentEvent {
  id: string;
  aggregateId: string;  // payment_id
  eventType: string;
  payload: object;
  timestamp: Date;
  version: number;
}
```

## Consequences

### Positive

- **Complete Audit Trail**: Every state change is recorded permanently
- **Time Travel**: Can reconstruct state at any point in time
- **Debugging**: Full history makes troubleshooting easier
- **Compliance**: Meets regulatory audit requirements
- **Analytics**: Rich data for payment analysis and reporting
- **Event-Driven**: Natural fit for publishing to Kafka

### Negative

- **Complexity**: More complex than CRUD operations
- **Storage Growth**: Event table grows continuously (requires archival strategy)
- **Query Performance**: Rebuilding state from events can be slow
- **Learning Curve**: Team needs to understand event sourcing patterns

### Mitigation Strategies

1. **Snapshots**: Create periodic state snapshots to speed up rebuilds
2. **Archival**: Move old events to cold storage after 2 years
3. **Projections**: Maintain read-optimized views of current state
4. **Monitoring**: Track event replay performance

## Implementation Plan

### Phase 1: Core Events (2 weeks)
- Event store implementation
- Basic payment events
- Event replay logic

### Phase 2: Projections (1 week)
- Current state projection
- Read-optimized views

### Phase 3: Snapshots (1 week)
- Snapshot creation
- Snapshot-based replay

## Example Usage

```typescript
// Create payment
const event = new PaymentCreatedEvent({
  paymentId: '123',
  amount: 1000,
  currency: 'USD',
  customerId: 'cust_456',
});
await eventStore.append(event);

// Rebuild state
const events = await eventStore.getEvents('123');
const payment = Payment.fromEvents(events);

// Current state is sum of all events
console.log(payment.status); // 'succeeded'
```

## Alternatives Considered

### Traditional CRUD
- **Pros**: Simpler, familiar pattern
- **Cons**: Loses history, poor auditability
- **Decision**: Rejected due to audit requirements

### Change Data Capture (CDC)
- **Pros**: Captures all database changes
- **Cons**: Infrastructure dependent, harder to reason about
- **Decision**: Rejected as too infrastructure-heavy

## References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Greg Young - CQRS and Event Sourcing](https://www.youtube.com/watch?v=JHGkaShoyNs)
