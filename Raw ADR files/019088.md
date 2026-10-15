# ADR-012: Projection Strategy and Read Model Design

## Status

Proposed

## Context

We need to define our projection strategy for building read models from event streams, including which projections we need initially, how to handle failures, monitoring approaches, and caching strategies. This complements our event sourcing implementation (ADR-006) by defining the read side of our CQRS architecture.

## Decision

### Initial Read Models

We will implement the following read models for MVP:

1. **User Profile Projection**
   - Aggregate user registration and profile update events
   - Support login and profile display functionality
   - Fields: userId, email, firstName, lastName, profileUrl, registrationDate

2. **Project Catalog Projection**
   - Aggregate project creation, updates, and access grant events
   - Support project browsing and filtering
   - Fields: projectId, ownerId, title, description, tags, visibility, createdDate, lastUpdated

3. **Project Detail Projection**
   - Detailed project information including content and access history
   - Support individual project pages
   - Fields: projectId, content, metadata, accessGrants, viewHistory

4. **Contact Requests Projection**
   - Aggregate contact request submissions and processing
   - Support admin dashboard and request management
   - Fields: requestId, visitorEmail, message, status, submittedDate, processedDate

### Projection Failure Handling

**Retry Strategy:**

- **Transient failures**: Exponential backoff with jitter (1s, 2s, 4s, 8s)
- **Maximum retries**: 3 attempts before moving to dead letter queue
- **Poison message detection**: Events that consistently fail across multiple projection instances

**Dead Letter Queue Processing:**

- Manual review and correction of problematic events
- Alerting for dead letter queue accumulation
- Batch reprocessing capability after fixes

**Projection Recovery:**

- **Checkpoint management**: Track last processed event per projection
- **Graceful degradation**: Serve stale data during projection rebuilds
- **Rebuild triggers**: Manual triggers for full projection rebuilds from event history

### Projection Monitoring

**Key Metrics:**

- **Lag metrics**: Time difference between event timestamp and projection timestamp
- **Throughput metrics**: Events processed per second per projection
- **Error rates**: Failed events vs successful events over time windows
- **Checkpoint positions**: Current event position vs latest event position

**Alerting Thresholds:**

- **Critical lag**: > 5 minutes behind latest events
- **High error rate**: > 5% failure rate over 10-minute window
- **Dead letter accumulation**: > 10 events in dead letter queue
- **Projection offline**: No progress for > 30 seconds

**Health Checks:**

- Per-projection health endpoints exposing lag and error metrics
- Automated health reporting to monitoring dashboard
- Integration with infrastructure alerting (Cloudflare Workers monitoring)

### Simplified Caching Strategy

**Single-Layer Caching for MVP:**

1. **Database-Level Caching Only**
   - Rely on PostgreSQL built-in query caching and connection pooling
   - No application-level caching initially
   - Direct reads from projection tables with optimized indexes

**Cache Evolution Path:**

- **Phase 1 (MVP)**: No application caching - direct database reads
- **Phase 2 (Growth)**: Add Workers KV for frequently accessed data
- **Phase 3 (Scale)**: Add edge caching layer when traffic increases

**Benefits of Simplified Approach:**

- **Faster development**: No cache invalidation logic to implement
- **Fewer moving parts**: Reduced complexity and debugging surface
- **PostgreSQL optimization**: Leverage Neon's built-in caching and performance features
- **Easy monitoring**: Single data source eliminates cache consistency issues

**Performance Considerations:**

- For low traffic (< 1000 requests/day), database reads are sufficient
- PostgreSQL indexes on common query patterns provide fast lookups
- Neon connection pooling handles concurrent access efficiently
- Monitor query performance and add caching when metrics indicate need

## Implementation Details

### Projection Worker Architecture

```typescript
interface ProjectionWorker {
  projectionName: string;
  eventTypes: string[];
  process(events: DomainEvent[]): Promise<void>;
  getCheckpoint(): Promise<EventPosition>;
  setCheckpoint(position: EventPosition): Promise<void>;
  rebuild(fromPosition?: EventPosition): Promise<void>;
}

interface ProjectionStore {
  save<T>(projectionName: string, id: string, data: T): Promise<void>;
  get<T>(projectionName: string, id: string): Promise<T | null>;
  query<T>(projectionName: string, filter: QueryFilter): Promise<T[]>;
  delete(projectionName: string, id: string): Promise<void>;
}
```

### Deployment Configuration

```yaml
projections:
  user-profile:
    events: ['UserRegistered', 'UserProfileUpdated']
    store: 'postgresql'
    cache_enabled: false # Start without caching
    critical_lag_threshold: '5m'

  project-catalog:
    events:
      [
        'ProjectCreated',
        'ProjectUpdated',
        'ProjectAccessGranted',
        'ProjectAccessRevoked',
      ]
    store: 'postgresql'
    cache_enabled: false # Start without caching
    critical_lag_threshold: '2m'
```

## Alternatives Considered

1. **Single materialized view approach**: Would limit flexibility and scaling
2. **Real-time synchronous projections**: Would impact write performance
3. **Client-side projection composition**: Would increase complexity and latency
4. **Complex multi-layer caching**: Premature optimization for low traffic volumes

## Consequences

**Benefits:**

- Clear separation between write and read concerns
- Optimized read models for specific UI needs
- Robust failure handling and recovery mechanisms
- Simple, predictable data flow for debugging
- Fast initial development without cache complexity

**Drawbacks:**

- Additional complexity in managing multiple projections
- Eventual consistency requires careful UX design
- Direct database reads may become bottleneck at scale
- Manual optimization required when traffic grows

## Trade-offs

**Simplicity vs Performance:**

- Prioritizing development speed over read performance optimization
- Accepting higher database load for reduced complexity

**Present vs Future:**

- Optimizing for current low-traffic needs
- Deferring caching complexity until metrics justify the investment

**Storage vs Speed:**

- Denormalized projections use more storage but enable faster queries
- Single projection store reduces operational complexity

## Migration Strategy

**Phase 1: MVP (No Caching)**

- Implement User Profile and Project Catalog projections
- Direct PostgreSQL reads with optimized indexes
- Basic monitoring and alerting
- Performance baseline establishment

**Phase 2: Selective Caching**

- Add Workers KV caching for frequently accessed endpoints only
- Monitor cache hit rates and performance improvements
- Event-driven cache invalidation

**Phase 3: Edge Optimization**

- Add Cloudflare edge caching for public content
- Advanced monitoring dashboards
- Performance tuning based on real usage patterns
