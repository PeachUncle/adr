---
docid: ADR-053
title: ADR 001 Event Driven Architecture
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-001: Event-Driven Architecture with Wolverine CQRS

**Status:** Accepted  
**Date:** December 30, 2025  
**Context:** B2X microservices architecture  
**Decision Authors:** @Architect, @TechLead

---

## Problem

B2X needs to coordinate work across multiple bounded contexts (Catalog, CMS, Identity, Customer, Order services) with:
- Loose coupling between services
- Eventual consistency guarantees
- Asynchronous processing capabilities
- Cross-service event propagation
- Command handling and query optimization

Traditional monolithic approaches (shared database, direct service calls) would create tight coupling and scalability issues.

---

## Solution

**Adopt Event-Driven Architecture using Wolverine CQRS pattern**

### Architecture

```
Service A                    Service B
  │                           │
  ├─ Command Handler          ├─ Event Handler
  │  (Process request)        │  (React to events)
  │                           │
  └─ Event Publisher    ────> └─ Local Handler
     (Publish event)          (Update local state)
     │
     ▼
Message Broker (RabbitMQ / Local Queue)
     │
     ├──> Service B (Event Handler)
     ├──> Service C (Event Handler)
     └──> Service D (Event Handler)
```

### Implementation

**Events Published:**
- `ProductCreatedEvent` - When product added to catalog
- `ProductStockUpdatedEvent` - When inventory changes
- `UserRegisteredEvent` - When new user created
- `PagePublishedEvent` - When CMS page goes live
- `OrderCreatedEvent` - When new order placed

**Commands Processed:**
- `IndexProductCommand` - Update search index
- `SendEmailCommand` - Send notifications
- `GenerateInvoiceCommand` - Create invoices
- `UpdateInventoryCommand` - Adjust stock

**Message Broker:**
- **Development:** Local in-memory queue
- **Production:** RabbitMQ with durable queues
- **Failover:** Dead letter queues for failed messages

---

## Consequences

### Positive ✅

1. **Loose Coupling**
   - Services don't know about each other
   - Can be deployed independently
   - Changes to one service don't break others

2. **Scalability**
   - Handle spikes in demand
   - Async processing prevents blocking
   - Easy to add new consumers

3. **Resilience**
   - Services can be offline temporarily
   - Messages queue until service recovers
   - Circuit breaker pattern available

4. **Auditability**
   - Event log shows all state changes
   - Historical tracking of what happened
   - Debugging aid for distributed issues

### Challenges ⚠️

1. **Eventual Consistency**
   - Data not immediately consistent across services
   - Need compensation handlers for failures
   - Requires careful saga pattern design

2. **Operational Complexity**
   - Message broker to manage (RabbitMQ)
   - Monitoring distributed events difficult
   - Debugging cross-service flows harder

3. **Testing Difficulty**
   - Async flows harder to test
   - Need specialized test strategies
   - Integration tests more complex

4. **Learning Curve**
   - Team needs to learn async patterns
   - Different mindset from synchronous code
   - Careful error handling required

---

## Implementation Details

### Wolverine Setup (Per Service)

```csharp
// Program.cs
var builder = WebApplicationBuilder.CreateBuilder(args);

// Add Wolverine messaging
builder.Services.AddWolverine(opts =>
{
    opts.UseRabbitMq(settings =>
    {
        settings.ConnectionString = configuration["RabbitMq:Uri"];
    });
    
    // Auto-register handlers
    opts.Discovery.IncludeAssembly(typeof(Program).Assembly);
    
    // Dead letter queue for failed messages
    opts.Policies.UseDurableLocalQueues()
        .AutoRetry.MaximumAttempts(3)
        .OnFailureGoToDeadLetterQueue();
});

var app = builder.Build();
app.Run();
```

### Event Publishing

```csharp
// Catalog service publishes event
public class CreateProductHandler
{
    private readonly IMessageBus _bus;
    
    public async Task Handle(CreateProductCommand command, 
        IMessageContext context)
    {
        // Create product in database
        var product = new Product { Name = command.Name, ... };
        await _repository.SaveAsync(product);
        
        // Publish event for other services
        var evt = new ProductCreatedEvent 
        { 
            ProductId = product.Id, 
            Name = product.Name,
            CreatedAt = DateTime.UtcNow
        };
        
        await context.PublishAsync(evt);
    }
}
```

### Event Handling

```csharp
// Search service subscribes to event
public class ProductSearchHandler
{
    private readonly ISearchService _searchService;
    
    public async Task Handle(ProductCreatedEvent evt)
    {
        // Index product in search
        await _searchService.IndexAsync(new SearchDocument
        {
            ProductId = evt.ProductId,
            Name = evt.Name,
            IndexedAt = DateTime.UtcNow
        });
    }
}
```

---

## Alternatives Considered

### 1. Synchronous REST Calls
- **Pros:** Simpler immediate consistency
- **Cons:** Tight coupling, cascading failures, blocking
- **Rejected:** Doesn't scale well

### 2. Database-per-Schema (Shared DB)
- **Pros:** Easier consistency
- **Cons:** Breaks service boundaries, scalability issues
- **Rejected:** Not true microservices

### 3. GraphQL Federation
- **Pros:** Flexible data queries
- **Cons:** Not designed for event notification
- **Rejected:** Doesn't solve async coordination

### 4. Kafka Instead of RabbitMQ
- **Pros:** Higher throughput, event log persistence
- **Cons:** More operational overhead, overkill for current scale
- **Status:** Can migrate later if needed

---

## Monitoring & Observability

### Key Metrics

1. **Message Throughput**
   - Messages/sec published
   - Messages/sec consumed
   - Alert if queue backs up

2. **Latency**
   - Message processing time
   - End-to-end event flow time
   - Alert on p99 latency spike

3. **Error Rates**
   - Failed message count
   - Dead letter queue size
   - Retry attempt count

4. **Durability**
   - Message persistence (RabbitMQ)
   - Acknowledgment confirmation
   - Redelivery success rate

### Monitoring Dashboard

```
Event Metrics:
├── Published Events: 15,243/sec
├── Processed Events: 15,210/sec
├── Failed Events: 33
├── Queue Depth: 45
├── Avg Latency: 120ms
└── Error Rate: 0.21%

Service Health:
├── Catalog Handler: ✅ OK
├── Search Indexer: ✅ OK
├── Email Notifier: ✅ OK
└── Inventory Updater: ✅ OK
```

---

## Related ADRs

- **ADR-002:** Multi-Database per Bounded Context
- **ADR-003:** API Gateway Pattern
- **ADR-004:** Saga Pattern for Distributed Transactions

---

## References

- [Wolverine Documentation](https://wolverine.netlify.app/)
- [Event Sourcing Patterns](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [Designing Event-Driven Systems](https://www.confluent.io/designing-event-driven-systems/)

---

**ADR Status:** ✅ Accepted  
**Implementation:** In Progress  
**Review Date:** June 30, 2026
