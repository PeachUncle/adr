# ADR-002: Implement Event-Driven Architecture

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-001 (Inversify DI)](./ADR-001-inversify-dependency-injection.md), [ADR-013 (Redis)](./ADR-013-redis-caching.md)

## Context

As Sovren evolved, services became increasingly coupled through direct method calls. This led to several problems:

- **Tight Coupling**: Payment service directly called notification service, content service, analytics service
- **Synchronous Bottlenecks**: All side effects executed in main request flow, slowing response times
- **Fragile Dependencies**: Changes to one service required changes to all callers
- **Difficult Testing**: Testing one service required mocking all downstream services
- **Poor Scalability**: Cannot independently scale services based on load

**Example of problematic coupling**:
```typescript
// Before: Tight coupling
class PaymentService {
  async processPayment(invoice: Invoice) {
    // Process payment
    await this.paymentRepo.save(invoice);

    // Direct coupling to multiple services
    await this.notificationService.sendReceipt(invoice);
    await this.analyticsService.trackPayment(invoice);
    await this.contentService.unlockContent(invoice.contentId);
    await this.webhookService.notifyCreator(invoice);

    // What if any of these fail? Rollback entire transaction?
  }
}
```

We needed an architecture that:
- Decouples services through asynchronous event communication
- Allows services to react to events without direct dependencies
- Enables independent scaling and deployment
- Supports eventual consistency patterns
- Simplifies testing with event-based contracts

## Decision

We will implement an **in-process Event-Driven Architecture** using an event bus pattern with typed events.

**Implementation Approach**:
```typescript
// Event definitions
interface PaymentCompletedEvent {
  type: 'payment.completed';
  payload: {
    invoiceId: string;
    amount: number;
    userId: string;
    contentId: string;
    timestamp: Date;
  };
}

// Event bus (singleton)
@injectable()
class EventBus implements IEventBus {
  private handlers = new Map<string, EventHandler[]>();

  subscribe<T extends Event>(eventType: string, handler: EventHandler<T>) {
    const handlers = this.handlers.get(eventType) || [];
    handlers.push(handler);
    this.handlers.set(eventType, handlers);
  }

  async publish<T extends Event>(event: T): Promise<void> {
    const handlers = this.handlers.get(event.type) || [];

    // Execute handlers asynchronously
    await Promise.allSettled(
      handlers.map(handler => handler(event))
    );

    // Log failures but don't block
    this.logger.info(`Published ${event.type} to ${handlers.length} handlers`);
  }
}

// Refactored service - publishes event
class PaymentService {
  async processPayment(invoice: Invoice) {
    await this.paymentRepo.save(invoice);

    // Publish event - no direct coupling
    await this.eventBus.publish({
      type: 'payment.completed',
      payload: {
        invoiceId: invoice.id,
        amount: invoice.amount,
        userId: invoice.userId,
        contentId: invoice.contentId,
        timestamp: new Date()
      }
    });
  }
}

// Event subscribers - loosely coupled
class NotificationService {
  constructor(eventBus: IEventBus) {
    eventBus.subscribe('payment.completed', this.onPaymentCompleted.bind(this));
  }

  private async onPaymentCompleted(event: PaymentCompletedEvent) {
    await this.sendReceipt(event.payload);
  }
}
```

**Key Patterns Adopted**:
1. **Typed Events**: TypeScript interfaces for all events with strict typing
2. **Event Bus**: Singleton event dispatcher using pub/sub pattern
3. **Async Handlers**: Non-blocking event handlers with error isolation
4. **Event Sourcing Light**: Event log for audit trail and debugging
5. **Dead Letter Queue**: Failed events captured for retry/investigation

## Consequences

### Positive

1. **Loose Coupling**: Services communicate through events, not direct calls
   - Payment service doesn't know about notification, analytics, webhooks
   - Can add new event subscribers without modifying publishers
   - Services can be developed and deployed independently

2. **Improved Performance**: Non-blocking event handlers
   - Main request returns immediately after event publish
   - Side effects processed asynchronously
   - Better user experience with faster response times

3. **Better Testability**: Test services in isolation
   ```typescript
   // Test publisher without subscribers
   it('should publish payment.completed event', async () => {
     const eventBusSpy = jest.spyOn(eventBus, 'publish');
     await paymentService.processPayment(invoice);
     expect(eventBusSpy).toHaveBeenCalledWith({
       type: 'payment.completed',
       payload: expect.objectContaining({ invoiceId: invoice.id })
     });
   });
   ```

4. **Resilience**: Isolated failures don't cascade
   - If notification service fails, payment still completes
   - Failed events logged and can be retried
   - Circuit breakers prevent cascading failures

5. **Audit Trail**: Event log provides complete history
   - Every system action captured as event
   - Can replay events for debugging
   - Supports compliance requirements

6. **Extensibility**: Easy to add new features
   - New service subscribes to relevant events
   - No changes to existing services required
   - Plugin-like architecture

### Negative

1. **Eventual Consistency**: Events processed asynchronously
   - Notification might arrive slightly after payment confirmation
   - Mitigation: Most use cases tolerate 100-500ms delay
   - Critical paths can still use synchronous calls if needed

2. **Debugging Complexity**: Harder to trace event flows
   - Request spans multiple asynchronous handlers
   - Mitigation: Correlation IDs in all events, comprehensive logging
   - Distributed tracing for production debugging

3. **Event Ordering**: No guaranteed order across event types
   - Two events published in sequence might process out of order
   - Mitigation: Event versioning and idempotent handlers
   - Use event timestamps for ordering when needed

4. **Testing Complexity**: Need to test event flows
   - Integration tests must verify event chains
   - Mitigation: Event bus test utilities and fixtures
   - Clear event documentation

5. **Memory Overhead**: Event queue in memory
   - Risk of memory growth under high load
   - Mitigation: Event retention policies, monitoring
   - Consider external queue for high-volume scenarios

## Alternatives Considered

### 1. External Message Queue (RabbitMQ, Kafka)
**Pros**:
- Guaranteed message delivery
- Persistent event storage
- Better for distributed systems
- Horizontal scaling

**Cons**:
- Operational complexity (another service to manage)
- Network overhead for local events
- Cost of infrastructure
- Overkill for monolithic backend

**Why Rejected**: Current scale doesn't justify external queue complexity. In-process events sufficient for 10,000+ users. Can migrate to external queue later if needed.

### 2. Database Event Store
**Pros**:
- Durable event storage
- Can replay events from database
- Simple implementation

**Cons**:
- Database writes for every event (performance)
- Polling required to consume events
- Higher latency than in-memory
- Database becomes bottleneck

**Why Rejected**: Performance overhead not justified. Event logging provides sufficient audit trail without blocking event flow.

### 3. HTTP Webhooks Between Services
**Pros**:
- Standard HTTP protocol
- Language-agnostic
- Easy to understand

**Cons**:
- Network overhead for local communication
- Requires retry logic
- Synchronous coupling
- More complex than in-process events

**Why Rejected**: Overkill for services in same process. HTTP webhooks used for external integrations, not internal events.

### 4. Direct Method Calls with Async Processing
**Pros**:
- Simple to implement
- No framework needed
- Direct code flow

**Cons**:
- Still coupled to service interfaces
- Hard to add new handlers
- Testing requires mocking all dependencies
- Doesn't scale with complexity

**Why Rejected**: Doesn't solve coupling problem. Event-driven architecture provides better long-term flexibility.

## Implementation Notes

**Event Naming Convention**:
```typescript
// Format: <domain>.<action>
'payment.completed'
'payment.failed'
'content.unlocked'
'user.subscribed'
'invoice.created'
```

**Event Structure**:
```typescript
interface BaseEvent {
  type: string;
  payload: unknown;
  metadata: {
    correlationId: string;  // Trace across services
    timestamp: Date;
    source: string;         // Publishing service
    version: number;        // Event schema version
  };
}
```

**Error Handling**:
```typescript
class EventBus {
  async publish<T extends Event>(event: T): Promise<void> {
    const handlers = this.handlers.get(event.type) || [];

    const results = await Promise.allSettled(
      handlers.map(handler => handler(event))
    );

    // Log failures but continue
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        this.logger.error(`Handler ${index} failed for ${event.type}`, {
          error: result.reason,
          event
        });

        // Add to dead letter queue
        this.deadLetterQueue.add({ event, error: result.reason });
      }
    });
  }
}
```

**Migration Path to External Queue**:
If we need to scale beyond in-process events:
1. Implement adapter pattern for event bus interface
2. Create RabbitMQ/Kafka implementation
3. Swap implementation in DI container
4. No changes to service code (loose coupling benefit)

## Related Documentation

- [Event Bus Architecture Diagram](/docs/architecture/diagrams/epic-005-event-bus.mmd)
- [Event Handler Testing Guide](/docs/development/testing-guide.md#event-handlers)
- [Service Integration Patterns](/docs/architecture/service-integration.md)
- [Backend Developer Guide](/docs/development/backend-developer-guide.md) - Event-driven patterns

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
