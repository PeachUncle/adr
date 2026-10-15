# ADR-0004: Redis Pub/Sub for Event Hub (POC-2)

**Status:** Accepted  
**Date:** 2026-01-XX  
**Context:** Backend POC-2 - Event-Based Inter-Microservices Communication  
**Decision Makers:** Backend Team

---

## Context

We need to choose a technology for event-based communication between microservices in POC-2. The event hub enables asynchronous, decoupled communication between services (Auth, Payments, Admin, Profile). This decision affects service coupling, scalability, reliability, and operational complexity.

**Requirements:**

- Simple to implement and understand
- Fast and low latency
- Good for POC-2 validation
- Easy migration path to production-ready solution
- Works well with Node.js
- Active maintenance

---

## Decision

We will use **Redis Pub/Sub** for the event hub in POC-2.

**Rationale:**

- **Simple** - Easy to implement and understand
- **Fast** - Low latency, high throughput
- **Lightweight** - Minimal resource usage
- **Good for POC-2** - Validates event-based architecture without complexity
- **Easy migration** - Can migrate to RabbitMQ in POC-3
- **Works well with Node.js** - Excellent Node.js libraries (ioredis)

**POC-2 Implementation:**

- Basic event publishing/subscribing
- Inter-service communication
- Event validation
- No message persistence (acceptable for POC-2)

**POC-3 Migration:**

- Migrate to RabbitMQ for production-ready event hub
- Message persistence
- Guaranteed delivery
- Dead letter queues

---

## Alternatives Considered

### 1. RabbitMQ

**Pros:**

- Production-ready
- Message persistence
- Guaranteed delivery
- Dead letter queues
- Retry mechanisms
- Management UI

**Cons:**

- More complex than Redis Pub/Sub
- Steeper learning curve
- More operational overhead
- May be overkill for POC-2

**Decision:** Not chosen for POC-2 - Too complex for POC-2 validation. Will migrate to RabbitMQ in POC-3.

---

### 2. Apache Kafka

**Pros:**

- Enterprise-grade
- High throughput
- Event streaming
- Event sourcing support
- Scalable

**Cons:**

- Very complex
- High operational overhead
- Overkill for POC-2
- Steep learning curve
- Requires Zookeeper/KRaft

**Decision:** Not chosen - Too complex for POC-2. Consider for MVP/Production if needed.

---

### 3. HTTP Polling

**Pros:**

- Simple to implement
- No additional infrastructure
- Works with existing HTTP setup

**Cons:**

- Not event-based
- Polling overhead
- Not scalable
- High latency
- Not suitable for real-time

**Decision:** Not chosen - Not event-based, doesn't validate event architecture.

---

### 4. Redis Pub/Sub (Chosen)

**Pros:**

- Simple to implement
- Fast and low latency
- Lightweight
- Good for POC-2 validation
- Easy migration to RabbitMQ

**Cons:**

- No message persistence
- No guaranteed delivery
- Messages lost if Redis restarts
- Not production-ready for critical events

**Decision:** Chosen - Best balance of simplicity and functionality for POC-2. Acceptable limitations for POC phase.

---

## Trade-offs

### Pros

- ✅ **Simplicity** - Easy to implement and understand
- ✅ **Fast** - Low latency, high throughput
- ✅ **Lightweight** - Minimal resource usage
- ✅ **Good for POC-2** - Validates event-based architecture
- ✅ **Easy Migration** - Can migrate to RabbitMQ in POC-3
- ✅ **Works with Node.js** - Excellent libraries (ioredis)

### Cons

- ⚠️ **No Message Persistence** - Messages lost if Redis restarts
- ⚠️ **No Guaranteed Delivery** - Messages may be lost
- ⚠️ **Not Production-Ready** - For critical events (but acceptable for POC-2)

---

## Consequences

### Positive

- ✅ **Architecture Validation** - Validates event-based communication patterns
- ✅ **Simple Implementation** - Fast to implement, easy to understand
- ✅ **Low Latency** - Fast event delivery
- ✅ **Migration Path** - Easy migration to RabbitMQ in POC-3
- ✅ **Good for POC** - Validates architecture without complexity

### Negative

- ⚠️ **Message Loss** - Messages lost if Redis restarts (acceptable for POC-2)
- ⚠️ **No Guaranteed Delivery** - Messages may be lost (acceptable for POC-2)
- ⚠️ **Not Production-Ready** - For critical events (but will migrate in POC-3)

### Neutral

- 🔄 **Migration Path** - Will migrate to RabbitMQ in POC-3 for production-ready event hub
- 🔄 **Performance** - Performance is excellent for POC-2 needs

---

## Implementation Notes

- Use Redis 7.x
- Use ioredis library for Node.js
- Implement event publisher/subscriber pattern
- Define event types and schemas
- Validate events before publishing
- Monitor Redis performance

**Example:**

```typescript
// Event Publisher
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export async function publishEvent(
  eventType: string,
  data: any
): Promise<void> {
  await redis.publish(
    'events',
    JSON.stringify({
      type: eventType,
      data,
      timestamp: new Date().toISOString(),
    })
  );
}

// Event Subscriber
const subscriber = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
subscriber.subscribe('events');

subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  // Handle event
});
```

---

## Migration Path

### POC-2 → POC-3

- Migrate from Redis Pub/Sub to RabbitMQ
- Implement message persistence
- Implement guaranteed delivery
- Implement dead letter queues
- Implement retry mechanisms

**Reference:** See `docs/backend-event-hub-implementation-plan.md` for detailed migration plan.

### POC-3 → MVP/Production

- Continue with RabbitMQ
- Or migrate to Apache Kafka if needed for event streaming
- Decision based on scale and requirements

---

## Related Decisions

- **ADR-0003: Shared Database Strategy** - Event hub is independent of database strategy
- **ADR-0001: Use Express Framework** - Event hub is independent of Express
- Frontend Event Bus (independent decision)

---

## References

- [Redis Pub/Sub Documentation](https://redis.io/docs/manual/pubsub/)
- `docs/backend-event-hub-implementation-plan.md` - Event hub implementation plan
- `docs/backend-poc2-architecture.md` - Architecture documentation
- `docs/backend-poc2-tech-stack.md` - Tech stack documentation

---

**Last Updated:** 2026-01-XX
