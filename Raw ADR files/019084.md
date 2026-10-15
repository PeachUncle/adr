# ADR-006: Event Sourcing Implementation Strategy

## Status

Accepted

## Context

We need to define our event sourcing implementation including event store design, ordering strategy, projection handling, and failure recovery mechanisms. We must ensure our projection workers remain portable across serverless providers.

## Decision

### Event Store Design

- **PostgreSQL-based event store** using Neon database
- **Single events table** with columns: event_id, aggregate_id, aggregate_type, event_type, event_data, metadata, version, timestamp
- **Optimistic concurrency control** using aggregate version numbers
- **Event serialization** using JSON format initially
- **Event encryption** for sensitive data to ensure compliance and protect user privacy

### Event Schema Evolution

- **Eager upcasting** for initial implementation to minimize complexity
- Transform and replace events in store during schema migrations
- Consider migrating to lazy or additive upcasting as data volume grows and data loss risk increases
- Implement migration scripts with careful validation and rollback capabilities

### Event Ordering Strategy

- **Per-aggregate ordering** with version numbers
- **Global timestamp ordering** for cross-aggregate reads
- **Partition by aggregate_id** for performance

### Projection Strategy

- **Eventual consistency** tolerance: up to a few minutes during high load (considerable lag acceptable)
- **Provider-agnostic projection workers** with adapter pattern
- **Projection state tracking** table to monitor lag and failures
- **Rebuilding capability** from full event history

### Provider-Agnostic Projection Architecture

**Core Projection Interface:**

```typescript
interface ProjectionHandler {
  handle(event: DomainEvent): Promise<ProjectionResult>;
  getProjectionState(): Promise<ProjectionState>;
  rebuild(fromVersion?: number): Promise<void>;
}

interface ProjectionAdapter {
  deploy(handler: ProjectionHandler): Promise<DeploymentResult>;
  scale(instances: number): Promise<void>;
  monitor(): Promise<HealthStatus>;
}
```

**Initial Provider Implementation:**

- **CloudflareWorkerAdapter**: Primary serverless provider for MVP
- **LocalAdapter**: For development and testing
- **Future providers**: AWS Lambda and Vercel adapters to be added based on demand

**Deployment Configuration:**

```yaml
projections:
  user-profile:
    handler: './src/projections/user-profile'
    provider: 'cloudflare' # configurable
    config:
      memory: '128MB'
      timeout: '30s'
      concurrency: 10
```

### Error Handling

- **Dead letter queue** for failed events using provider-agnostic message queue interface
- **Exponential backoff retry** policy (3 retries max)
- **Manual intervention alerts** for persistent failures

### Security Implementation

- **Event encryption** for sensitive data fields using envelope encryption
- **Field-level encryption** for PII and sensitive domain data
- **Key rotation** support for long-term security maintenance
- **Audit logging** for all encryption/decryption operations

## Alternatives Considered

1. **EventStore DB**: More complex deployment, overkill for our scale
2. **Apache Kafka as primary store**: Good for streaming, but complex for queries
3. **MongoDB event store**: Less ACID guarantees than PostgreSQL
4. **Provider-specific projection workers**: Would create vendor lock-in
5. **Container-based projections**: More complex deployment than serverless
6. **Lazy upcasting from day one**: Added complexity without immediate benefit for our scale

## Provider Independence Strategy

**Shared Infrastructure Contracts:**

- Event streaming interface (Kafka, SQS, PubSub adapters)
- Database connection interface (connection pooling, transactions)
- Monitoring interface (metrics, logging, tracing)
- Secret management interface (provider credential systems)

**Testing Strategy:**

- **Unit tests**: Provider-agnostic projection logic
- **Integration tests**: Test each provider adapter
- **Contract tests**: Ensure adapters fulfill interfaces
- **Local development**: Use LocalAdapter for fast iteration

**Migration Path:**

1. Implement new provider adapter
2. Deploy projection to new provider
3. Run parallel processing with lag monitoring
4. Switch traffic once new provider catches up
5. Decommission old provider

## Implementation Details

**Event Store Schema:**

```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    version INTEGER NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    encrypted_fields TEXT[], -- Track which fields are encrypted
    UNIQUE(aggregate_id, version)
);

-- Index for efficient event replay
CREATE INDEX idx_events_aggregate_version ON events(aggregate_id, version);
-- Index for cross-aggregate temporal queries
CREATE INDEX idx_events_timestamp ON events(timestamp);
-- Index for event type filtering during projections
CREATE INDEX idx_events_type_timestamp ON events(event_type, timestamp);
```

## Consequences

- All state changes captured as immutable events with encryption for sensitive data
- Full audit trail and temporal queries capability
- Provider independence through adapter pattern with initial focus on Cloudflare Workers
- Complexity in handling eventual consistency (up to few minutes acceptable)
- Rich integration possibilities through event streams
- Easy migration between serverless providers when needed
- Eager upcasting provides simple evolution path with planned migration to safer strategies

## Trade-offs

**Benefits:**

- Complete audit trail with privacy protection
- Time-travel queries
- Provider independence and migration flexibility
- Robust integration patterns
- Scalable read models
- Reduced vendor lock-in risk
- Simple schema evolution initially

**Drawbacks:**

- Learning curve for development team
- Eventual consistency complexity
- Additional abstraction layer complexity
- Storage growth over time
- Initial overhead of encryption implementation
- Risk of data loss during eager upcasting (mitigated by careful migration practices)
