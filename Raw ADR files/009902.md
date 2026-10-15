# ADR 004: Event-Driven Microservices Architecture

**Status:** 📋 PROPOSED  
**Date:** 2025-11-22  
**Decision Makers:** Architecture Team  
**Priority:** MEDIUM (Future Enhancement)

## Context

Currently, Interstellar Tracker uses a hybrid architecture where:

- Domain, Application, and Infrastructure layers are shared libraries
- Services communicate via synchronous HTTP calls
- WebUI directly calls CalculationService REST API

While this approach works well for the initial MVP, it has limitations:

- **Tight coupling** between services via HTTP dependencies
- **Synchronous blocking** - services wait for responses
- **Limited scalability** - can't independently scale components
- **No resilience** - if CalculationService is down, WebUI fails
- **No event history** - lost context of what happened when

As the system grows, we need to evolve toward a truly distributed, event-driven architecture where:

- Services are autonomous and loosely coupled
- Communication is asynchronous via message queues
- Each service has its own data store
- Complex workflows are orchestrated via Saga pattern
- System is resilient to individual service failures

## Decision

We will evolve the architecture to **Event-Driven Microservices** using:

### 1. Message Broker: RabbitMQ (Preferred Choice)

**Why RabbitMQ over Kafka:**

- ✅ **Simplicity**: Easier to set up and operate for smaller teams
- ✅ **Message Patterns**: Native support for publish/subscribe, routing, topics
- ✅ **Low Latency**: Better for command/query patterns with immediate responses
- ✅ **Mature Ecosystem**: MassTransit library provides excellent .NET integration
- ✅ **Resource Efficient**: Lower memory/CPU footprint than Kafka
- ✅ **Dead Letter Queues**: Built-in error handling and retry mechanisms
- ✅ **Management UI**: Excellent web-based monitoring console

**When to Consider Kafka:**

- Need for massive throughput (>100k msgs/sec)
- Log retention and replay critical
- Stream processing requirements
- Multi-datacenter replication

For Interstellar Tracker's use case (orbital calculations, user requests, notifications), **RabbitMQ is the optimal choice**.

### 2. Communication Patterns

#### Command Pattern (Point-to-Point)

Commands represent actions that must be executed by a specific service.

**Example: Calculate Orbital Position**

```csharp
public record CalculatePositionCommand
{
    public Guid CommandId { get; init; }
    public Guid CorrelationId { get; init; }
    public string CelestialBodyId { get; init; }
    public DateTimeOffset TargetDate { get; init; }
    public string RequestedBy { get; init; }
}

// Published by: WebUI
// Consumed by: CalculationService
// Response: PositionCalculatedEvent
```

#### Event Pattern (Publish/Subscribe)

Events represent facts that have occurred. Multiple services can react.

**Example: Position Calculated**

```csharp
public record PositionCalculatedEvent
{
    public Guid EventId { get; init; }
    public Guid CorrelationId { get; init; }
    public string CelestialBodyId { get; init; }
    public DateTimeOffset CalculationDate { get; init; }
    public Vector3 Position { get; init; }
    public Vector3 Velocity { get; init; }
    public TimeSpan CalculationDuration { get; init; }
    public DateTimeOffset OccurredAt { get; init; }
}

// Published by: CalculationService
// Consumed by: WebUI, CacheService, AuditService, NotificationService
```

### 3. Saga Pattern for Complex Workflows

For multi-step processes that span multiple services, we'll use **Choreography-based Sagas** with MassTransit.

**Example: Interstellar Object Discovery Workflow**

```
┌─────────────────────────────────────────────────────────┐
│  1. User submits new interstellar object data           │
│     → PublishNewInterstellarObjectCommand               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. ValidationService validates orbital parameters       │
│     → ObjectValidatedEvent (success)                    │
│     → ObjectValidationFailedEvent (failure)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. CalculationService computes initial orbit           │
│     → OrbitCalculatedEvent                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. PersistenceService stores to database               │
│     → ObjectPersistedEvent                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  5. NotificationService notifies subscribers            │
│     → NotificationSentEvent                             │
└─────────────────────────────────────────────────────────┘

If any step fails → Compensating transactions rollback
```

**Saga State Machine Example (MassTransit):**

```csharp
public class InterstellarObjectDiscoverySaga : MassTransitStateMachine<InterstellarObjectDiscoveryState>
{
    public State Validating { get; private set; }
    public State Calculating { get; private set; }
    public State Persisting { get; private set; }
    public State Completed { get; private set; }
    public State Failed { get; private set; }

    public Event<NewInterstellarObjectCommand> ObjectSubmitted { get; private set; }
    public Event<ObjectValidatedEvent> ObjectValidated { get; private set; }
    public Event<ObjectValidationFailedEvent> ValidationFailed { get; private set; }
    public Event<OrbitCalculatedEvent> OrbitCalculated { get; private set; }
    public Event<ObjectPersistedEvent> ObjectPersisted { get; private set; }

    public InterstellarObjectDiscoverySaga()
    {
        InstanceState(x => x.CurrentState);

        Event(() => ObjectSubmitted, x => x.CorrelateById(context => context.Message.CommandId));
        
        Initially(
            When(ObjectSubmitted)
                .Then(context => context.Instance.ObjectId = context.Data.ObjectId)
                .TransitionTo(Validating)
                .Publish(context => new ValidateObjectCommand
                {
                    ObjectId = context.Data.ObjectId,
                    OrbitalElements = context.Data.OrbitalElements
                }));

        During(Validating,
            When(ObjectValidated)
                .TransitionTo(Calculating)
                .Publish(context => new CalculateOrbitCommand
                {
                    ObjectId = context.Instance.ObjectId
                }),
            When(ValidationFailed)
                .TransitionTo(Failed)
                .Publish(context => new ObjectDiscoveryFailedEvent
                {
                    Reason = context.Data.Errors
                }));

        During(Calculating,
            When(OrbitCalculated)
                .TransitionTo(Persisting)
                .Publish(context => new PersistObjectCommand
                {
                    ObjectId = context.Instance.ObjectId,
                    CalculatedOrbit = context.Data.Orbit
                }));

        During(Persisting,
            When(ObjectPersisted)
                .TransitionTo(Completed)
                .Finalize());

        SetCompletedWhenFinalized();
    }
}
```

### 4. Service Autonomy & Data Ownership

Each service will own its data and expose it only via events:

```
┌──────────────────────┐     ┌──────────────────────┐
│  CalculationService  │     │   CacheService       │
│  ─────────────────── │     │   ──────────────     │
│  - OrbitCalculations │     │   - RecentQueries    │
│  - EphemerisCache    │     │   - PopularBodies    │
│  - OwnDatabase       │     │   - Redis            │
└──────────────────────┘     └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│  NotificationService │     │   AuditService       │
│  ─────────────────── │     │   ──────────────     │
│  - Subscriptions     │     │   - EventLog         │
│  - EmailQueue        │     │   - UserActions      │
│  - OwnDatabase       │     │   - OwnDatabase      │
└──────────────────────┘     └──────────────────────┘
```

### 5. Technology Stack

**Message Broker:**

- RabbitMQ 3.13+ (container: rabbitmq:3.13-management-alpine)
- Port 5672 (AMQP), 15672 (Management UI)

**.NET Integration:**

- MassTransit 8.2+ (abstraction over RabbitMQ)
- MassTransit.RabbitMQ
- MassTransit.EntityFrameworkCore (saga persistence)

**Service Discovery:**

- Consul or built-in Kubernetes DNS
- Service mesh consideration: Linkerd (lightweight)

**Observability:**

- Distributed tracing: OpenTelemetry
- MassTransit metrics exposed to Prometheus
- RabbitMQ metrics scraped by Prometheus

## Architecture Diagram

### Before (Current - Synchronous)

```
┌─────────┐  HTTP/REST  ┌────────────────────┐
│  WebUI  │ ──────────→ │ CalculationService │
└─────────┘             └────────────────────┘
     │ (Blocked waiting for response)
```

### After (Proposed - Asynchronous)

```
┌─────────┐                             ┌────────────────────┐
│  WebUI  │                             │ CalculationService │
└────┬────┘                             └─────────┬──────────┘
     │                                            │
     │ 1. Publish Command                        │
     └─────────────┐                              │
                   ▼                              │
              ┌──────────┐                        │
              │ RabbitMQ │◄───────────────────────┘
              │  Queues  │    3. Publish Event
              └────┬─────┘
                   │
                   │ 2. Consume Command
                   └─────────────────────────────┐
                                                 │
     ┌───────────────────────────────────────────┘
     │ 4. Consume Event
     ▼
┌─────────┐       ┌──────────────┐       ┌──────────────┐
│  WebUI  │       │ CacheService │       │ AuditService │
└─────────┘       └──────────────┘       └──────────────┘
```

## Message Exchange Examples

### 1. User Queries Position

```
WebUI → RabbitMQ: CalculatePositionCommand
  {
    "celestialBodyId": "earth",
    "targetDate": "2025-11-22T12:00:00Z",
    "correlationId": "guid-123"
  }

CalculationService ← RabbitMQ: (receives command)
  → Performs calculation
  → Publishes result

CalculationService → RabbitMQ: PositionCalculatedEvent
  {
    "correlationId": "guid-123",
    "position": { "x": 1.0, "y": 0.0, "z": 0.0 },
    "calculationDuration": "00:00:00.0234"
  }

WebUI ← RabbitMQ: (receives event via correlation)
CacheService ← RabbitMQ: (caches result)
AuditService ← RabbitMQ: (logs query)
```

### 2. Batch Orbit Updates (Background Job)

```
SchedulerService → RabbitMQ: UpdateOrbitsCommand
  (no response needed, fire-and-forget)

CalculationService ← RabbitMQ: 
  → Updates all celestial body positions
  → Publishes batch complete event

CalculationService → RabbitMQ: OrbitsUpdatedEvent
  {
    "updateDate": "2025-11-22T00:00:00Z",
    "bodiesUpdated": 19,
    "duration": "00:00:15.234"
  }

CacheService ← RabbitMQ: (invalidates old cache)
NotificationService ← RabbitMQ: (notifies subscribers)
```

## Benefits

1. **Loose Coupling**: Services don't know about each other, only messages
2. **Resilience**: If CalculationService is down, messages queue up and process later
3. **Scalability**: Can scale consumers independently (10 WebUI instances, 50 CalculationService workers)
4. **Flexibility**: Easy to add new services that react to existing events
5. **Auditability**: Complete event log for debugging and compliance
6. **Performance**: Async processing doesn't block user requests
7. **Eventual Consistency**: Acceptable trade-off for astronomical data

## Drawbacks

1. **Complexity**: More moving parts, harder to debug
2. **Eventual Consistency**: WebUI may show stale data briefly
3. **Message Broker SPOF**: RabbitMQ must be highly available
4. **Development Overhead**: More code for message contracts, handlers
5. **Testing Complexity**: Need to mock message bus in unit tests

## Migration Strategy

### Phase 1: Hybrid Approach (Current)

- Keep synchronous HTTP for MVP
- Prove the domain model works
- Focus on orbital calculation correctness

### Phase 2: Add RabbitMQ Alongside HTTP ⬅️ **YOU ARE HERE**

- Introduce RabbitMQ to docker-compose
- Keep HTTP endpoints but also publish events
- Services can consume events or use HTTP
- Gradual transition without breaking existing functionality

### Phase 3: Event-First Architecture

- New features use events exclusively
- HTTP endpoints become thin facades over message bus
- Introduce Saga pattern for complex workflows

### Phase 4: Pure Microservices

- Each service has own database
- All communication via events
- API Gateway becomes message router
- Full CQRS implementation

## Implementation Checklist

### Infrastructure Setup

- [ ] Add RabbitMQ to docker-compose.yml
- [ ] Configure RabbitMQ management UI
- [ ] Add MassTransit NuGet packages to all services
- [ ] Create shared Messages library (InterstellarTracker.Messages)
- [ ] Configure Prometheus to scrape RabbitMQ metrics

### Message Contracts

- [ ] Define command messages (CalculatePosition, UpdateOrbit, etc.)
- [ ] Define event messages (PositionCalculated, OrbitUpdated, etc.)
- [ ] Create correlation ID infrastructure
- [ ] Implement message versioning strategy

### Service Modifications

- [ ] CalculationService: Add message consumers
- [ ] WebUI: Add message publishers and response handlers
- [ ] Create CacheService as first pure event-driven service
- [ ] Create AuditService for event logging

### Saga Implementation

- [ ] Set up saga state persistence (EF Core)
- [ ] Implement InterstellarObjectDiscoverySaga
- [ ] Add compensating transaction logic
- [ ] Create saga monitoring dashboard

### Observability

- [ ] Add OpenTelemetry for distributed tracing
- [ ] Create RabbitMQ Grafana dashboard
- [ ] Implement message retry and dead letter queue handling
- [ ] Add correlation ID to all log messages

### Testing

- [ ] Unit tests with InMemoryTestHarness (MassTransit)
- [ ] Integration tests for saga workflows
- [ ] Load testing with message throughput metrics
- [ ] Chaos engineering: kill RabbitMQ, verify recovery

## References

- [MassTransit Documentation](https://masstransit.io/)
- [RabbitMQ Best Practices](https://www.rabbitmq.com/best-practices.html)
- [Saga Pattern (Microsoft)](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga)
- [Event-Driven Architecture (Martin Fowler)](https://martinfowler.com/articles/201701-event-driven.html)
- [Building Microservices (Sam Newman)](https://samnewman.io/books/building_microservices_2nd_edition/)

## Decision Outcome

**Status: APPROVED for Future Implementation**

We will proceed with the hybrid approach (Phase 2) after completing:

1. Current MVP with HTTP communication
2. Azure Container Apps deployment
3. Application Insights integration
4. Authentication with Keycloak

Timeline: **Q1 2026** (After MVP is production-ready)

---

**Signed Off By:** Architecture Team  
**Next Review:** After MVP deployment to Azure
