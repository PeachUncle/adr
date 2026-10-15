# ADR-003: Event-Driven Architecture

## Status
Accepted

## Context

Need observability into system behavior without tight coupling between modules.

**Requirements:**
- Audit trail of all write operations (create, update, delete)
- Plugin system for extending behavior without modifying code
- Notification system (Slack alerts for errors, new orders, etc.)
- Ability to add new event handlers without changing services
- Async operations that don't block main request flow

**Challenges:**
- Direct service-to-service calls create tight coupling
- Adding new features (notifications, logging) requires modifying existing code
- Difficult to track operation lifecycle across system
- Cross-cutting concerns (audit, metrics) scattered throughout codebase

**Example Without Events:**
```javascript
// AccountService directly calls NotificationService
async create(data, { trx }) {
  const account = await this.repository.create(data, { trx });
  await notificationService.sendAccountCreated(account);  // Tight coupling
  await auditService.logAccountCreation(account);         // Tight coupling
  await metricsService.recordAccountCreation();           // Tight coupling
  return account;
}
```

This violates Open/Closed Principle (open for extension, closed for modification).

## Decision

Implement event bus with before/after/failed event emissions for all write operations.

### Architecture

**Event Bus:**
- Singleton instance (`src/common/event-bus/`)
- Memory-based implementation (can swap for Redis/SQS later)
- Publish-subscribe pattern
- Async event delivery (doesn't block caller)

**Event Emission Pattern:**
```javascript
async create(data, opts) {
  this.emit('entity.before.create', { data });
  try {
    const result = await super.create(data, opts);
    this.emit('entity.after.create', { data, result });
    return result;
  }
  catch (error) {
    this.emit('entity.failed.create', { data, error });
    throw error;
  }
}
```

**Event Naming Convention:**
```
{entity}.{phase}.{operation}

Examples:
- account.before.create
- account.after.update
- account.failed.delete
- order.after.create
- payment.failed.process
```

**Phases:** `before`, `after`, `failed`

**Operations:** `create`, `update`, `delete`, `upsert`, `activate`, `deactivate`

### Implementation via Mixin

Events implemented via `PluggableService` mixin:

```javascript
// src/common/mixins/service/PluggableService.js
const Pluggable = (Base) => class extends Base {
  constructor(args) {
    super(args);
    this.events = args.events || { enabled: true };
    this.eventBus = initEventBus();
  }

  _emit(phase, op, payload) {
    if (!this.events?.enabled) return;
    const name = `${this.events.prefix}.${phase}.${op}`;
    this.eventBus.emit(name, payload);
  }

  async create(data, opts) {
    this._emit('before', 'create', { data });
    try {
      const result = await super.create(data, opts);
      this._emit('after', 'create', { data, result });
      return result;
    }
    catch (error) {
      this._emit('failed', 'create', { data, error });
      throw error;
    }
  }
};
```

### Event Subscribers

Plugins subscribe to events:

```javascript
// Plugin: Slack notifications for new orders
const eventBus = initEventBus();

eventBus.on('order.after.create', async (payload) => {
  const { result: order } = payload;
  await slackService.sendMessage({
    channel: '#sales',
    message: `New order: ${order.id} - $${order.total}`
  });
});
```

## Consequences

### Positive

**Decoupling:**
- Services don't know about downstream consumers
- Adding new event handlers doesn't require changing services
- Easy to add observability, notifications, metrics

**Audit Trail:**
- Complete lifecycle of every operation
- Before/after/failed events capture full context
- Can reconstruct operation history from events

**Plugin System:**
- Features added via event listeners, not code changes
- Plugins can be enabled/disabled without redeploying
- External systems can subscribe (future: webhook delivery)

**Testability:**
- Test services in isolation (events optional)
- Mock event bus for unit tests
- Integration tests can verify events emitted

**Observability:**
- All operations emit events
- Single place to add logging, metrics, tracing
- Failed events capture errors automatically

**Async Operations:**
- Event handlers run asynchronously
- Don't block main request flow
- Example: Email notifications sent after response

### Negative

**Event Ordering:**
- No guaranteed order for event delivery
- Mitigated by: timestamps in payload
- Not suitable for operations requiring strict sequencing

**Debugging:**
- Harder to trace execution across event handlers
- Requires trace IDs to follow request flow
- Event handlers fail silently (by design, shouldn't block main flow)

**Testing Complexity:**
- Integration tests need to account for async event handlers
- May need to wait for event processing
- Harder to test error conditions in event handlers

**No Immediate Feedback:**
- Event handlers run async, caller doesn't see failures
- If notification fails, service succeeds anyway
- Mitigated by: monitoring event handler failures separately

## Alternatives Considered

### Direct Service Calls
**Approach:** Services directly call other services (e.g., `notificationService.send()`).

**Rejected Because:**
- Creates tight coupling between services
- Adding new features requires modifying existing code
- Difficult to test in isolation
- Violates Single Responsibility Principle

### Message Queue (SQS/RabbitMQ)
**Approach:** Services publish to external message queue.

**Rejected Because:**
- Operational overhead for current scale
- Additional infrastructure to maintain
- Network latency for queue operations
- Memory-based event bus sufficient for now
- Can swap implementation later if needed

### Database Triggers
**Approach:** PostgreSQL triggers emit events on table changes.

**Rejected Because:**
- Business logic in database layer
- Harder to test and debug
- Limited error handling
- Can't emit events for non-database operations

### Webhook Callbacks
**Approach:** Services accept webhook URLs and call them.

**Rejected Because:**
- Caller must provide webhook URL
- Not suitable for internal observability
- Synchronous (blocks request)
- Future: can add webhook delivery as event subscriber

## Implementation Notes

### Event Bus Location
```
src/common/event-bus/
  ├── index.js              # Singleton initialization
  ├── EventBus.js           # Memory-based implementation
  └── __tests__/            # Event bus tests
```

### Event Payload Structure
```javascript
{
  data: { ... },           // Input data
  result: { ... },         // Operation result (after events)
  error: Error,            // Error object (failed events)
  actor: 'user:123',       // Who performed operation (optional)
  user_id: 123,            // User ID (optional)
  trace_id: 'abc-123',     // Trace ID for distributed tracing (optional)
  timestamp: Date.now()    // When event occurred
}
```

### Disabling Events (Testing)

Services can disable events:

```javascript
const service = new AccountService({
  repository,
  entityClass: AccountEntity,
  events: { enabled: false }  // No events emitted
});
```

### Future Enhancements

**Redis Event Bus:**
- Replace memory-based with Redis pub/sub
- Enables multi-instance deployments
- Events shared across API servers

**SQS Event Bus:**
- Deliver events to AWS SQS
- Lambda consumers process events
- External system integration

**Event Replay:**
- Store events in database
- Rebuild state from event history
- Event sourcing pattern

## Related Decisions

- [ADR-001: Service-Oriented Architecture](./ADR-001-service-oriented-architecture.md) - Services emit events
- [ADR-002: Mixin Pattern](./ADR-002-mixin-pattern.md) - PluggableService mixin implements events
- [Ecosystem: Messenger Stack](../ECOSYSTEM.md#observability--alerts) - SNS → Slack notifications

## References

- Event bus implementation: `src/common/event-bus/`
- Pluggable mixin: `src/common/mixins/service/PluggableService.js`
- Example subscriber: `src/common/plugins/` (future)

---

**Date:** 2025-10-17
**Author:** Scott Lewis
