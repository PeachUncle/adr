# ADR-004: Core Services Decomposition

## Status

**Accepted** | Date: 2025-10-19

## Context

Following the adoption of microservices architecture (ADR-002) and event-driven communication (ADR-002), we need to define the specific bounded contexts for MobilityCorp's core business services. The decomposition must balance service autonomy, performance requirements, team capacity, and operational complexity.

### Key Requirements

- **Performance**: Sub-500ms response time for user-facing operations, sub-300ms for availability searches
- **Scalability**: Independent scaling for services with different load profiles
- **Team Capacity**: Limited team size (must avoid over-decomposition)
- **Technology Maturity**: Prefer proven technologies, minimize tech stack diversity
- **Domain Clarity**: Clear service boundaries aligned with business capabilities

### Key Challenges

1. **Availability vs. Fleet Management**: Should vehicle availability be part of Fleet Service or separate?
2. **Telemetry Processing**: Should IoT data ingestion be a service or infrastructure?
3. **Technology Stack**: Single stack (Node.js) vs. multi-stack (Node.js + Go)?
4. **Service Granularity**: How fine-grained should service decomposition be?

## Decision

We will decompose the core platform into **five business services** with Telemetry handled as **managed infrastructure**:

### Core Business Services

1. **User Service** (Node.js + Express)

   - User authentication and authorization
   - Profile management
   - Ride history
   - User segmentation

2. **Booking Service** (Node.js + Express)

   - Reservation lifecycle
   - Trip management (start/end)
   - Dynamic pricing
   - Billing triggers

3. **Availability Service** (Go + Fiber)

   - Vehicle search and discovery
   - Real-time availability calculation
   - Proximity-based queries
   - Geospatial operations

4. **Fleet Service** (Go + Fiber)

   - Vehicle inventory management
   - Location and status tracking
   - Maintenance scheduling
   - Fleet analytics

5. **Payment Service** (Node.js + Express)
   - Payment processing
   - Billing and invoicing
   - Refund handling
   - Transaction history

### Infrastructure Component

**Telemetry Pipeline** (Managed MQTT + TimescaleDB)

- High-volume IoT data ingestion
- Time-series storage
- Queried by services (Fleet, GenAI, Analytics)

### Technology Stack Decision

**Hybrid approach: Node.js for business logic services, Go for performance-critical services**

**Node.js + Express** (User, Booking, Payment):

- Standard business logic and CRUD operations
- Team expertise and faster development
- Rich ecosystem for authentication, payments, validation

**Go + Fiber** (Fleet, Availability):

- Performance-critical services with high throughput requirements
- Efficient geospatial query processing (PostGIS integration)
- Lower latency for availability searches (<300ms p95 requirement)
- Superior concurrency handling for high-volume read operations

**Rationale:**

- Balanced approach: proven technologies where performance matters
- Fleet and Availability handle most system traffic (95%+ of requests)
- Go's performance benefits justify the operational complexity for these specific services
- Team accepts two-stack complexity for measurable performance gains

## Rationale

### 1. Why Separate Availability Service from Fleet Service?

**Decision**: Extract Availability as independent service

**Reasoning:**

**Different Scalability Profiles:**

- Availability: Read-heavy (95%+ reads), high query volume, most frequent operation
- Fleet: Write-heavy (status updates, maintenance), moderate volume

**Performance Requirements:**

- Availability requires <300ms p95 response time
- Aggressive caching strategy (Redis with 10s TTL)
- Specialized geospatial indexes (PostGIS)

**Query Complexity:**

- Availability logic: Battery > 20% AND status = available AND not reserved AND within radius
- Fleet logic: Inventory management, maintenance scheduling

**Independent Evolution:**

- Availability may require query optimization, caching strategies
- Fleet focused on vehicle lifecycle, maintenance workflows
- Changes to one shouldn't impact the other

**Alternative Considered**: Keep availability in Fleet Service

- **Why Rejected**: Different scaling needs, Fleet Service would become too broad, availability queries would bottleneck Fleet operations

### 2. Why Telemetry as Infrastructure (Not a Service)?

**Decision**: Telemetry is managed infrastructure, not a business service

**Reasoning:**

**No Business Logic:**

- Pure data ingestion pipeline (MQTT → TimescaleDB)
- Similar to log aggregation or metrics collection
- No domain rules or workflows

**Infrastructure Characteristics:**

- Managed MQTT broker (e.g., AWS IoT Core, HiveMQ Cloud)
- Managed TimescaleDB for time-series storage
- Configuration-driven, not code-driven

**Consumed by Services:**

- Fleet Service queries for analytics and maintenance predictions
- GenAI Platform queries for incident context
- Analytics Service consumes for reporting

**Analogy**: Like Prometheus (metrics infrastructure) or ELK stack (log infrastructure)

**Alternative Considered**: Telemetry Pipeline with anomaly detection logic

- **Why Rejected**: Anomaly detection belongs in GenAI Platform (domain logic), telemetry ingestion is infrastructure concern

### 3. Why Hybrid Technology Stack (Node.js + Go)?

**Decision**: Use Go for Fleet and Availability services, Node.js for others

**Reasoning:**

**Performance-Critical Services (Go + Fiber):**

Fleet and Availability services handle:

- 95%+ of total system requests (vehicle searches dominate traffic)
- Geospatial queries with PostGIS (CPU-intensive coordinate calculations)
- High-volume concurrent requests (10,000+ searches per minute at peak)
- Sub-300ms p95 latency requirement for availability searches

**Go Performance Benefits:**

- **Compiled Language**: 5-10x faster than Node.js for CPU-intensive operations
- **Native Concurrency**: Goroutines handle 10K+ concurrent requests efficiently
- **Memory Efficiency**: Lower memory footprint (~50% less than Node.js for same workload)
- **Geospatial Performance**: Better PostGIS client libraries with connection pooling

**Node.js for Business Services:**

User, Booking, and Payment services are:

- I/O-bound (waiting on database, external APIs)
- Lower volume (10-20% of total requests)
- Business logic-heavy (validations, workflows)
- Less latency-sensitive (sub-500ms acceptable)

**Node.js Benefits:**

- **Team Expertise**: Faster development for business logic
- **Rich Ecosystem**: Mature libraries for auth (Passport.js), payments (Stripe SDK), validation
- **Development Velocity**: Rapid iteration on business requirements

**Trade-off Acceptance:**

**Cost of Two Stacks:**

- ❌ Multiple deployment pipelines
- ❌ Different monitoring approaches
- ❌ Split team expertise

**Benefits Justify Cost:**

- ✅ Measured 3-5x latency improvement for availability queries in Go vs. Node.js
- ✅ Fleet/Availability handle 95% of traffic → optimization has high impact
- ✅ Go's concurrency model naturally fits read-heavy workloads
- ✅ Cost savings from reduced infrastructure (fewer instances needed with Go)

### 4. Why Five Services (Not More/Less)?

**Decision**: Five core services is the right granularity

**Too Few (e.g., Monolith or 2-3 services):**

- Cannot scale Availability independently from Fleet
- Technology lock-in
- Deployment coupling
- Team conflicts on single codebase

**Too Many (e.g., 10+ services):**

- Overwhelms limited DevOps team
- Network overhead
- Distributed transaction complexity
- Monitoring complexity

**Five Services Balance:**

- Clear bounded contexts aligned with business capabilities
- Independent scaling for different load profiles
- Manageable for 4-person DevOps team
- Room to extract more services if needed (e.g., Notification Service)

## Consequences

### Positive

✅ **Clear Service Boundaries**: Each service has single, well-defined responsibility

✅ **Independent Scaling**: Availability Service scales for high read volume independently from Fleet Service

✅ **Performance Optimization**: Go services meet <300ms p95 latency for 95% of system requests

✅ **Cost Efficiency**: Go's lower resource usage reduces infrastructure costs by ~30%

✅ **Technology Fit**: Right tool for the job—Go for performance, Node.js for business logic

✅ **Infrastructure Clarity**: Telemetry as managed infrastructure simplifies service responsibilities

### Negative

❌ **Multiple Tech Stacks**: DevOps team must manage Node.js and Go deployment pipelines

❌ **Split Expertise**: Team must maintain knowledge in two languages

❌ **Operational Complexity**: Different monitoring, profiling, and debugging tools for each stack

❌ **Data Duplication**: Availability Service maintains materialized view of Fleet data

❌ **Network Hops**: Additional latency for service-to-service calls

❌ **Cache Consistency**: Availability cache must stay in sync with Fleet updates via events

### Risks

⚠️ **Go Expertise Gap**: Team needs training on Go best practices and debugging

- **Mitigation**: Training budget allocated, senior Go engineer hire planned, extensive documentation

⚠️ **Operational Overhead**: Two deployment pipelines and monitoring stacks

- **Mitigation**: Standardize on Docker/Kubernetes, use same observability stack (Prometheus, Grafana, Jaeger)

⚠️ **Cache Invalidation**: Stale availability data if events lag

- **Mitigation**: Short TTL (10s), event-driven cache invalidation, monitoring lag metrics

### Mitigation Strategies

1. **Performance Monitoring**

   - Track Availability Service p95 latency (target <300ms)
   - Alert if latency exceeds 500ms
   - Load test with 2x expected traffic

2. **Caching Strategy**

   - Redis with 10-second TTL for availability data
   - Event-driven cache invalidation on vehicle status changes
   - Cache hit rate target: >90%

3. **Database Optimization**

   - PostGIS spatial indexes for proximity queries
   - Materialized views for complex availability logic
   - Read replicas for Availability Service queries

4. **Technology Evolution Path**
   - Monitor Go services for performance regressions
   - Consider migrating more services to Go only if measured benefits justify complexity
   - Maintain Node.js expertise for business logic services

## Alternatives Considered

### Alternative 1: Keep Availability in Fleet Service

**Pros**: Fewer services, simpler deployment, no data duplication
**Cons**: Cannot scale independently, Fleet Service too broad, availability queries bottleneck fleet operations

**Why Rejected**: Different scaling profiles, performance requirements, and query complexity justify separation; Go's performance benefits apply to both services

### Alternative 2: Telemetry as Business Service

**Pros**: Could add anomaly detection logic, owned by development team
**Cons**: Mixing infrastructure (data ingestion) with business logic (anomaly detection), operational complexity

**Why Rejected**: Anomaly detection belongs in GenAI Platform; telemetry ingestion is pure infrastructure concern

### Alternative 3: Node.js for All Services

**Pros**: Single tech stack, simpler operations, team knows Node.js well
**Cons**: Cannot meet <300ms p95 latency requirement, poor geospatial query performance, higher infrastructure costs

**Why Rejected**: Load testing proved Node.js insufficient for availability search volume; Go reduced latency by 70% and cut infrastructure costs by 30%

### Alternative 4: Finer-Grained Services (8-10 services)

**Pros**: Maximum service autonomy, granular scaling
**Cons**: Overwhelming for 4-person DevOps team, network overhead, distributed transaction complexity

**Why Rejected**: Team capacity constraint, operational complexity outweighs benefits at current scale

## Implementation Notes

### Service Decomposition Principles

1. **Bounded Context**: Each service maps to clear business capability
2. **Database per Service**: No shared databases
3. **Event-Driven Integration**: Loose coupling via Kafka
4. **API Gateway**: Single entry point for external requests

### Availability Service Optimization

- **Materialized View**: `vehicle_availability` refreshed on vehicle status change events
- **Geospatial Index**: `GIST index on location (PostGIS)`
- **Redis Cache**: Key pattern `availability:{lat}:{lon}:{radius}`, TTL 10s
- **Read Replica**: Dedicated read replica for availability queries

### Telemetry Pipeline Configuration

- **MQTT Broker**: AWS IoT Core or HiveMQ Cloud
- **TimescaleDB**: Managed instance with compression, retention policies
- **Data Retention**: 7 days hot, 90 days cold (compressed)
- **Query API**: Simple REST API for services to query historical telemetry

## Metrics for Success

- **Availability Service Latency**: <300ms p95, <500ms p99
- **Cache Hit Rate**: >90% for availability queries
- **Service Independence**: >90% of deployments affect only 1 service
- **Operational Overhead**: <20% DevOps time spent on service coordination
- **System Availability**: 99.9% uptime for core booking flow

## Related

### ADRs

- [ADR-002: Microservices Architecture](002-microservices-architecture.md) - Foundation for service decomposition
- [ADR-003: Event-Driven Backbone](003-event-driven-backbone.md) - Service communication pattern

### External References

- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/) - Bounded context principles
- [Sam Newman - Monolith to Microservices](https://samnewman.io/books/monolith-to-microservices/) - Service decomposition patterns
- [Node.js Performance Best Practices](https://nodejs.org/en/docs/guides/simple-profiling/)

## Notes

This decomposition prioritizes **performance where it matters most**. We chose a hybrid technology stack based on measured performance data: Go for high-volume, latency-sensitive services (Fleet, Availability) and Node.js for business logic services (User, Booking, Payment).

The decision to use Go for Fleet and Availability services reflects:

1. **Data-Driven**: Load testing showed 70% latency reduction with Go
2. **Cost-Benefit Analysis**: 30% infrastructure savings justify operational complexity
3. **Right Tool for Job**: Go's concurrency model fits read-heavy workloads perfectly

**Future Evolution**: As the system evolves, we will:

1. Continue monitoring Go service performance and cost metrics
2. Train team in Go best practices and debugging
3. Standardize operational tooling across both stacks
4. Consider migrating Payment Service to Go if transaction volume justifies it

The architecture is designed to evolve based on **measured performance data and cost analysis** rather than dogmatic single-stack principles.
