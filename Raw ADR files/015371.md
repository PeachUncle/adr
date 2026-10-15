# Async Event-Driven Order Creation

* Status: proposed
* Deciders: platform-core + checkout squad
* Date: 2025-12-11

## Context and Problem Statement

Checkout-service currently stores orders directly via `orderRepository.save()` and exposes order query APIs (`GET /orders/{id}`, `GET /orders`). This creates tight coupling between checkout completion and order-service availability. If order-service or its database is slow or unavailable during checkout, the entire sale could be lost or blocked. The checkout flow must always succeed in capturing the sale, even when downstream systems experience transient failures.

We need to decide how checkout-service communicates completed orders to order-service while ensuring:
1. **Sales are never lost** - the payment has been captured; we must record the order
2. **Checkout completion is fast** - customers shouldn't wait for order persistence
3. **Downstream failures don't block sales** - order-service unavailability cannot reject a valid purchase

## Decision Drivers

1. **Sale capture is paramount** - Once payment succeeds, the order must be recorded; losing sales data is unacceptable.
2. **Checkout latency** - Customers expect fast checkout; blocking on downstream persistence adds unacceptable latency.
3. **Fault tolerance** - Order-service may be temporarily unavailable; this cannot cause checkout failures.
4. **Eventual consistency is acceptable** - Orders can take seconds to appear in order-service; immediate queryability is not required.
5. **Audit trail** - All order events must be traceable for debugging and compliance.
6. **Consistency with audit pattern** - ADR-003 established queue-first ingestion for audits; order creation should follow the same pattern.

## Considered Options

1. Async event-driven with store-and-forward (chosen)
2. Synchronous HTTP call to order-service
3. Synchronous database write with shared transaction
4. Fire-and-forget event publishing

## Decision Outcome

Chosen option: **Async event-driven with store-and-forward**

Checkout-service publishes `OrderCompleted` CloudEvents to Redis Streams after successful payment. A local transaction log tracks whether the event was published, enabling background retry if the initial publish fails. Order-service consumes events asynchronously and persists orders to its database.

This approach ensures the sale is captured immediately (in checkout's transaction log) and published asynchronously. Even if Redis is temporarily unavailable, the transaction log provides a durable record that can be retried. Order-service processes events at its own pace, with built-in retry and dead-letter handling for failures.

### Positive Consequences

- **Sales never lost**: Transaction log captures order metadata before event publish; retry scheduler handles failures.
- **Fast checkout**: No synchronous calls to order-service; checkout returns immediately after payment + local transaction record.
- **Fault tolerant**: Order-service outages don't affect checkout; events queue in Redis Streams until consumed.
- **Decoupled services**: Checkout doesn't need to know order-service's availability or schema details.
- **Consistent pattern**: Follows ADR-003 queue-first pattern established for audit events.
- **Full audit trail**: CloudEvents provide standardized, traceable event history.

### Negative Consequences

- **Eventual consistency**: Orders may not appear in order-service queries for seconds after checkout.
- **Operational complexity**: Must monitor Redis Streams lag, dead-letter queues, and retry scheduler.
- **Duplicate handling required**: Order-service must be idempotent (check `existsById` before insert).
- **More components**: Requires Redis Streams infrastructure in addition to databases.

## Pros and Cons of the Options

### 1. Async Event-Driven with Store-and-Forward (chosen)

**Good**
- Sale captured immediately in transaction log; retry handles publish failures
- Checkout latency unaffected by order-service performance
- Order-service can scale consumers independently
- CloudEvents standard provides interoperability and tooling
- Dead-letter queue prevents data loss on permanent failures
- Matches audit ingestion pattern (ADR-003)

**Bad**
- Eventual consistency window (typically <1 second)
- Requires idempotent consumers
- More infrastructure to operate (Redis Streams + retry scheduler)

### 2. Synchronous HTTP Call to Order-Service

**Good**
- Simple request/response model
- Immediate consistency
- Easy to debug with standard HTTP tools

**Bad**
- Checkout blocked by order-service latency/availability
- **Sales can be lost** if order-service is down after payment
- Cascading failures between services
- Circuit breakers add complexity but still have failure windows

### 3. Synchronous Database Write with Shared Transaction

**Good**
- Strong consistency
- Single point of failure handling
- Simpler mental model

**Bad**
- Distributed transaction complexity
- Tight coupling to database schema
- Doesn't scale; single database becomes bottleneck
- **Sales can be lost** if database unavailable

### 4. Fire-and-Forget Event Publishing

**Good**
- Simplest implementation
- Fastest checkout response
- Minimal infrastructure

**Bad**
- **Sales can be lost** if Redis unavailable at publish time
- No retry mechanism
- No guarantee of delivery
- Debugging failures is difficult

## Implementation Notes and Next Steps

1. **Checkout Service Changes** (`apps/checkout-service/`):
   - Add `checkout_transactions` table for store-and-forward pattern
   - Remove `orderRepository.save()` - orders no longer persisted in checkout
   - Remove order query APIs (`GET /orders/*`) - clients use order-service
   - Add `OrderCompletedEventPublisher` using `platform-events`
   - Add `EventRetryScheduler` for failed publishes

2. **Order Service Changes** (`apps/order-service/`):
   - Add `OrderEventConsumer` extending `EventConsumer` from `platform-events`
   - Implement idempotent `OrderEventHandler` (check `existsById` before save)
   - Configure consumer group and dead-letter handling

3. **Shared Infrastructure** (`libs/backend/platform/platform-events/`):
   - `CloudEventPublisher` interface with `publish()` and `publishAndAwait()`
   - `RedisStreamEventPublisher` implementation
   - `EventConsumer` base class with retry and dead-letter support
   - CloudEvents v1.0 serialization

4. **Monitoring**:
   - Redis Streams consumer lag
   - Dead-letter queue depth
   - Transaction log retry queue size
   - Event publish success/failure rates

## References

- Implementation plan: `docs/plans/active/055_CHECKOUT_SERVICE_REDESIGN.md`
- Platform events library: `docs/plans/active/055B_PLATFORM_EVENTS.md`
- Checkout service changes: `docs/plans/active/055C_CHECKOUT_SERVICE.md`
- Order service consumer: `docs/plans/active/055D_ORDER_SERVICE.md`
- Related ADR: `docs/ADRs/003_audit_data_store.md` (queue-first ingestion pattern)
- CloudEvents specification: https://cloudevents.io/
