# ADR-022: Message Bus Architecture and Integration Patterns

## Status

Proposed

## Decision Drivers

- Event sourcing integration requirements from ADR-006
- Inter-bounded-context communication needs
- Vendor independence and portability requirements
- Integration with projection workers from ADR-012
- Reliable event publishing patterns (outbox pattern)

## Context

We need to define our message bus strategy for event-driven communication between bounded contexts in our event-sourced architecture. The solution must support vendor independence and strict adherence to Domain-Driven Design principles.

**Relationship to Event Sourcing (ADR-006):**
This ADR defines the message bus for **inter-bounded-context communication**, while ADR-006 defines the event store for **intra-bounded-context event sourcing**. The message bus publishes selected domain events from the event store to enable loose coupling between bounded contexts.

## Decision

### Event Store and Message Bus Integration

**Clear Separation of Concerns:**

- **Event Store**: Authoritative source of truth for domain events within each bounded context
- **Message Bus**: Communication channel for publishing selected events across bounded contexts
- **Outbox Pattern**: Reliable publishing from event store to message bus

```typescript
// src/shared/messaging/ports/EventPublisher.ts
interface EventPublisher {
  publishDomainEvent<T extends DomainEvent>(event: T): Promise<void>;
  publishIntegrationEvent<T extends IntegrationEvent>(event: T): Promise<void>;
}

// Integration with Event Store (from ADR-006)
interface EventStoreRepository {
  save(aggregate: AggregateRoot): Promise<void>;
  load<T extends AggregateRoot>(aggregateId: string): Promise<T>;
  // Events are published to message bus via outbox pattern
}
```

### Message Bus Abstraction Layer

**Domain-Centric Message Bus Interface:**

```typescript
// src/shared/messaging/ports/MessageBus.ts
interface MessageBus {
  publish<T extends IntegrationEvent>(event: T): Promise<void>;
  publishBatch<T extends IntegrationEvent>(events: T[]): Promise<void>;
  subscribe<T extends IntegrationEvent>(
    eventType: string,
    handler: EventHandler<T>,
    options?: SubscriptionOptions
  ): Promise<Subscription>;
  unsubscribe(subscription: Subscription): Promise<void>;
}

// Aligned with ADR-006 DomainEvent structure
interface IntegrationEvent extends DomainEvent {
  readonly eventId: string;
  readonly eventType: string;
  readonly aggregateId: string;
  readonly aggregateType: string;
  readonly version: number;
  readonly timestamp: Date;
  readonly causationId?: string;
  readonly correlationId?: string;
  readonly metadata: EventMetadata;
  // Additional field for integration events
  readonly publishedAt: Date;
}

interface EventMetadata {
  readonly boundedContext: string;
  readonly tenant?: string;
  readonly userId?: string;
  readonly source: string;
  readonly schemaVersion: string;
  // Aligned with ADR-006 encryption requirements
  readonly encryptedFields?: string[];
}
```

### Outbox Pattern Implementation

**Reliable Event Publishing:**

```typescript
// src/infrastructure/messaging/OutboxPublisher.ts
class OutboxPublisher {
  constructor(
    private eventStore: EventStore, // From ADR-006
    private messageBus: MessageBus,
    private eventSelector: IntegrationEventSelector
  ) {}

  async publishPendingEvents(): Promise<void> {
    const unpublishedEvents = await this.eventStore.getUnpublishedEvents();

    for (const domainEvent of unpublishedEvents) {
      if (this.eventSelector.shouldPublish(domainEvent)) {
        const integrationEvent = this.transformToIntegrationEvent(domainEvent);
        await this.messageBus.publish(integrationEvent);
        await this.eventStore.markAsPublished(domainEvent.eventId);
      }
    }
  }

  private transformToIntegrationEvent(
    domainEvent: DomainEvent
  ): IntegrationEvent {
    return {
      ...domainEvent,
      publishedAt: new Date(),
      metadata: {
        ...domainEvent.metadata,
        boundedContext: this.getBoundedContextName(),
        source: 'event-store',
      },
    };
  }
}
```

### Event Selection Strategy

**Integration Event Selection:**

```typescript
interface IntegrationEventSelector {
  shouldPublish(event: DomainEvent): boolean;
}

class ConfigurableEventSelector implements IntegrationEventSelector {
  private publishableEvents = new Set([
    'UserRegistered',
    'ProjectCreated',
    'ProjectAccessGranted',
    'ContactRequestSubmitted',
    // ***please check*** which other events should be published
  ]);

  shouldPublish(event: DomainEvent): boolean {
    return this.publishableEvents.has(event.eventType);
  }
}
```

### Message Bus Adapter Pattern

**Provider Independence:**

```typescript
interface MessageBusAdapter {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  publish(topic: string, message: string): Promise<void>;
  subscribe(topic: string, handler: MessageHandler): Promise<void>;
}

class MessageBusFactory {
  static create(config: MessageBusConfig): MessageBus {
    switch (config.provider) {
      case 'kafka':
        return new KafkaMessageBusAdapter(config.kafka);
      case 'redis':
        return new RedisMessageBusAdapter(config.redis);
      case 'eventbridge':
        return new AWSEventBridgeAdapter(config.aws);
      case 'memory':
        return new InMemoryMessageBusAdapter(); // For testing
      default:
        throw new Error(`Unsupported message bus provider: ${config.provider}`);
    }
  }
}
```

### Topic Naming Strategy

**DDD-Aligned Topic Naming:**

```typescript
// src/shared/messaging/TopicNamingStrategy.ts
class BoundedContextTopicNamingStrategy implements TopicNamingStrategy {
  getTopicName(event: IntegrationEvent): string {
    // Format: {environment}.{bounded-context}.{aggregate-type}.{event-type}
    // Aligned with ADR-005 aggregate design
    return `${this.environment}.${event.metadata.boundedContext}.${event.aggregateType}.${event.eventType}`
      .toLowerCase()
      .replace(/([A-Z])/g, '-$1')
      .replace(/^-/, '');
  }

  // Examples aligned with ADR-005 aggregates:
  // prod.portfolio-management.user.user-registered
  // prod.portfolio-management.project.project-created
  // dev.portfolio-management.contact.contact-request-submitted
}
```

### Projection Worker Integration

**Message Bus to Projection Worker Communication:**

```typescript
// src/infrastructure/projections/MessageBusProjectionWorker.ts
class MessageBusProjectionWorker implements ProjectionWorker {
  constructor(
    private messageBus: MessageBus,
    private projectionStore: ProjectionStore, // From ADR-012
    private eventHandler: ProjectionEventHandler
  ) {}

  async start(): Promise<void> {
    // Subscribe to relevant integration events for this projection
    await this.messageBus.subscribe(
      'UserRegistered',
      this.handleUserRegistered.bind(this),
      {
        consumerGroup: this.getConsumerGroupId(),
        autoCommit: false, // Manual commit for exactly-once processing
      }
    );

    await this.messageBus.subscribe(
      'ProjectCreated',
      this.handleProjectCreated.bind(this),
      {
        consumerGroup: this.getConsumerGroupId(),
        autoCommit: false,
      }
    );
  }

  private async handleUserRegistered(event: UserRegistered): Promise<void> {
    try {
      await this.eventHandler.handle(event);
      await this.updateCheckpoint(event);
      // Commit after successful processing (ADR-012 checkpoint management)
    } catch (error) {
      // Implement retry logic from ADR-012
      throw error;
    }
  }
}
```

## Rationale

### Outbox Pattern Benefits

- **Guaranteed delivery**: Events are stored before publishing
- **Atomicity**: Event storage and outbox entry in single transaction
- **Reliability**: Failed publishes can be retried
- **Ordering**: Maintains event order within aggregates

### Adapter Pattern Benefits

- **Vendor independence**: Easy switching between message brokers
- **Testing**: In-memory implementation for unit tests
- **Environment flexibility**: Different brokers for different environments

### Integration Event Design

- **Backward compatibility**: Events include version information from ADR-007
- **Rich context**: Metadata supports debugging and routing
- **Security**: Encrypted fields maintained from ADR-006

## Implementation Guidance

### Prerequisites

- ADR-006 (Event Sourcing) must be implemented
- ADR-005 (Domain Model) defines events to publish
- ADR-012 (Projection Strategy) for consumption patterns

### Implementation Steps

1. **Implement MessageBus interface** and initial adapter (in-memory for testing)
2. **Create OutboxPublisher** with periodic and triggered publishing
3. **Add event selection configuration** for integration events
4. **Implement topic naming strategy** aligned with domain model
5. **Integrate with projection workers** from ADR-012
6. **Add monitoring and health checks** per ADR-010

### Validation Criteria

- Events published to message bus match event store content
- Outbox pattern ensures no lost events
- Projection workers successfully consume integration events
- Topic naming follows consistent strategy
- Message bus adapters are interchangeable

## Consequences

### Positive

- **Reliable publishing**: Outbox pattern ensures no lost events
- **Vendor independence**: Easy migration between message brokers
- **Projection integration**: Seamless feeding of projection workers
- **Clear boundaries**: Separation between domain and integration events
- **Testability**: In-memory adapter supports fast testing

### Negative

- **Additional complexity**: Outbox pattern adds operational overhead
- **Latency**: Small delay between event store and message bus publishing
- **Dual storage**: Events stored in both event store and message topics

### Neutral

- **Configuration complexity**: Need to configure event selection rules
- **Monitoring overhead**: Additional components to monitor and alert on

## Alternatives Considered

### Alternative 1: Direct Message Bus Publishing

- **Description**: Publish directly to message bus from aggregates
- **Pros**: Lower latency, simpler architecture
- **Cons**: Risk of lost events, coupling to message bus technology
- **Why rejected**: Reliability requirements mandate outbox pattern

### Alternative 2: Event Store as Message Bus

- **Description**: Use event store directly for inter-context communication
- **Pros**: Single storage system, strong consistency
- **Cons**: Coupling between contexts, scaling limitations
- **Why rejected**: Violates bounded context independence

### Alternative 3: Synchronous API Communication

- **Description**: REST APIs for inter-context communication
- **Pros**: Simple, widely understood, immediate consistency
- **Cons**: Tight coupling, availability dependencies, not event-driven
- **Why rejected**: Conflicts with event sourcing and DDD principles

## Related ADRs

### Dependencies

- **Requires**: ADR-006 (Event Sourcing) - Event store integration
- **Requires**: ADR-005 (Domain Model) - Defines events to publish
- **Requires**: ADR-007 (Event Versioning) - Event evolution support

### Influences

- **Influences**: ADR-012 (Projection Strategy) - Message bus feeds projections
- **Influences**: ADR-010 (Observability) - Monitoring message bus health

### Conflicts

- **None identified** - Designed to integrate with all other ADRs

## AI Agent Guidance

### Implementation Priority

**High** - Required for projection updates and system integration

### Code Generation Patterns

```typescript
// Always use outbox pattern for reliable publishing
class AggregateRepository {
  async save(aggregate: AggregateRoot): Promise<void> {
    const events = aggregate.getUncommittedEvents();
    await this.eventStore.saveEvents(aggregate.id, events);
    await this.outboxPublisher.schedulePublishing(events);
  }
}

// Always use adapter pattern for message bus
const messageBus = MessageBusFactory.create(config);
```

### Common Pitfalls

- **Skipping outbox pattern**: Always use reliable publishing, never direct publish
- **Coupling to specific broker**: Always use adapter interface
- **Publishing all events**: Only publish integration events, not internal domain events
- **Missing error handling**: Implement proper retry and dead letter patterns

### Integration Points

- Must integrate with event store from ADR-006
- Events must follow versioning from ADR-007
- Feeds projection workers from ADR-012
- Monitoring must align with ADR-010

## Technical Debt Introduced

- **Outbox processing overhead**: Periodic processing adds operational complexity
- **Message broker operations**: Additional infrastructure to maintain
- **Event selection maintenance**: Rules need updating as domain evolves

## Evolution Path

- **Review trigger**: When message volume exceeds current capacity
- **Planned evolution**: Add support for event streaming and CDC patterns
- **Migration strategy**: Adapter pattern enables seamless broker migration

---

_Last Updated: September 10, 2025_  
_Splits from: ADR-011 (Message Bus Strategy)_
