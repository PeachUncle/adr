# ADR-010: Use Microservices Architecture

**Status**: Accepted

**Date**: 2024-01-15

**Deciders**: Engineering Team, CTO, VP Engineering

## Context

We need to decide on the overall system architecture for House Helper. The application has multiple distinct concerns:

- **API Service**: RESTful API for mobile app
- **Real-time Notifications**: Push notifications via Firebase
- **Background Workflows**: Task rotation, recurring chores, reminders
- **Event Processing**: Audit logging, analytics, cross-service communication
- **Future Features**: Web app, third-party integrations, AI/ML features

Key considerations:
- Team size: 5-10 engineers
- Expected scale: 10,000+ families, 1000+ concurrent users
- Development velocity: Ship features weekly
- System reliability: 99.9% uptime target
- Technology flexibility: Ability to use different tech for different services
- Maintenance: Need clear boundaries and ownership

## Decision

We will use a **microservices architecture** with the following services:

1. **API Service** (Go): Main RESTful API for mobile clients
2. **Notifier Service** (Go): Real-time push notifications
3. **Temporal Worker** (Go): Background workflow execution
4. **Temporal API** (Go): Workflow management API
5. **Kafka Consumer** (Go): Event processing and analytics

Communication:
- **Synchronous**: Direct HTTP calls for critical paths
- **Asynchronous**: Kafka events for non-critical operations
- **Workflows**: Temporal for long-running, stateful processes

## Consequences

### Positive

- **Independent Deployment**: Deploy services independently
  - Faster release cycles (don't need full regression testing)
  - Reduce blast radius of bugs (failure isolated to one service)
  - Easier rollbacks (rollback individual service)
  - Example: Can deploy notification changes without touching API
  
- **Technology Flexibility**: Use best tool for each job
  - All services currently Go, but could add Python service for ML
  - Can experiment with new technologies in isolated services
  - Easier to adopt new frameworks/libraries
  
- **Scalability**: Scale services independently based on load
  - API service might need 10 instances
  - Notifier service might need only 2 instances
  - Optimize resource usage and costs
  - Example scaling:
    ```
    api:          10 replicas (high traffic)
    notifier:     2 replicas  (moderate traffic)
    temporal-worker: 5 replicas (background jobs)
    kafka-consumer: 3 replicas (event processing)
    ```
  
- **Team Autonomy**: Teams can own entire services
  - Clear ownership boundaries
  - Faster decision-making
  - Reduced coordination overhead
  - Example: Notification team owns Notifier service end-to-end
  
- **Fault Isolation**: Failure in one service doesn't bring down entire system
  - If notifier service crashes, API still works (notifications queue up)
  - If Kafka consumer crashes, doesn't affect API requests
  - Degraded functionality vs. complete outage
  
- **Development Velocity**: Parallel development on different services
  - Multiple teams work simultaneously without conflicts
  - Smaller codebases easier to understand and modify
  - Faster CI/CD pipelines (test only changed service)

### Negative

- **Operational Complexity**: More moving parts to manage
  - More deployments to coordinate
  - More monitoring dashboards
  - More logs to aggregate
  - Mitigation: Use Kubernetes, Helm, centralized logging (Loki), unified monitoring (Grafana)
  
- **Distributed System Challenges**:
  - Network calls can fail (need retries, circuit breakers)
  - Eventual consistency (async events may be delayed)
  - Distributed tracing needed (harder to debug)
  - Mitigation: Use OpenTelemetry, implement retry logic, design for eventual consistency
  
- **Data Consistency**: No distributed transactions
  - Can't use ACID transactions across services
  - Need saga pattern or event sourcing for multi-service operations
  - Mitigation: Use Temporal workflows for orchestration, design for idempotency
  
- **Testing Complexity**: Need integration tests across services
  - Unit tests for each service (straightforward)
  - Integration tests need multiple services running (complex)
  - E2E tests even more complex
  - Mitigation: Use testcontainers for integration tests, comprehensive E2E test suite
  
- **Deployment Coordination**: Some changes require coordinated deploys
  - Breaking API changes need careful coordination
  - Database migrations affecting multiple services
  - Mitigation: Versioned APIs, backward-compatible changes, feature flags
  
- **Duplication**: Some code/logic duplicated across services
  - Shared models might be duplicated
  - Common utilities duplicated
  - Mitigation: Shared libraries for common code, accept some duplication for autonomy

### Neutral

- **Service Boundaries**: Need to carefully define boundaries
  - Wrong boundaries lead to chatty services
  - Too many fine-grained services increase complexity
  - Strategy: Start with coarser boundaries, split as needed

## Alternatives Considered

### Monolith

**Pros**:
- Simpler to develop initially
- Easier to test (no network calls)
- Single deployment
- Easier debugging (everything in one place)
- ACID transactions across all features

**Cons**:
- All-or-nothing deployment (can't deploy features independently)
- Single point of failure (if it crashes, everything is down)
- Harder to scale (must scale entire application)
- Technology lock-in (must use same stack for everything)
- Codebase becomes large and harder to understand
- Team coordination overhead increases

**Why Rejected**:
- Expected scale and feature diversity better served by microservices
- Need independent deployment for different concerns (API vs. notifications vs. workflows)
- Want ability to scale services independently
- However: We start with relatively coarse services to avoid over-fragmentation

### Serverless (Lambda Functions)

**Pros**:
- No infrastructure management
- Auto-scaling
- Pay per invocation
- Good for event-driven workloads

**Cons**:
- Cold starts (latency spikes)
- Vendor lock-in (AWS Lambda)
- Limited execution time (15 min max)
- Complex orchestration for workflows
- Harder to test locally
- State management challenges

**Why Rejected**:
- Cold start latency incompatible with P95 < 500ms requirement
- Temporal workflows better for complex orchestration than Step Functions
- Want portability (not locked to AWS Lambda)
- However: Can use Lambda for specific use cases (e.g., S3 event processing)

### Service-Oriented Architecture (SOA)

**Pros**:
- Similar benefits to microservices
- More established patterns

**Cons**:
- Typically uses ESB (Enterprise Service Bus) which becomes bottleneck
- Heavier-weight communication protocols (SOAP, XML)
- More rigid service contracts

**Why Rejected**:
- Microservices more lightweight and modern
- REST/JSON and Kafka better fit than SOAP/ESB
- Want to avoid ESB single point of failure

## Service Design Principles

### 1. Domain-Driven Design

Services organized around business capabilities:
- **API Service**: User-facing operations
- **Notifier Service**: Notification delivery
- **Workflow Service**: Long-running processes
- **Event Processing**: Analytics and cross-cutting concerns

### 2. Single Responsibility

Each service has one primary responsibility:
- API: Handle HTTP requests
- Notifier: Send push notifications
- Temporal Worker: Execute workflows
- Kafka Consumer: Process events

### 3. Loose Coupling

Services are loosely coupled via:
- **APIs**: Well-defined REST interfaces
- **Events**: Kafka for async communication
- **Contracts**: Versioned schemas

### 4. High Cohesion

Related functionality kept together within service boundaries.

### 5. Independent Data Storage

Each service owns its data:
- API Service: Core domain data (users, families, tasks)
- Notifier Service: Notification queue and delivery status
- Temporal: Workflow state
- Kafka: Event stream

Note: In our case, some services share PostgreSQL database but have separate tables/schemas.

## Communication Patterns

### Synchronous (HTTP)

Use for:
- Critical path operations
- Immediate response needed
- Low latency requirements

Example:
```
Mobile App → API Service (GET /tasks)
```

### Asynchronous (Kafka Events)

Use for:
- Non-critical operations
- Event notification
- Analytics and audit logs
- Decoupling services

Example:
```
API Service → Kafka → [Notifier Service, Analytics Service]
Event: "task_completed"
```

### Orchestration (Temporal Workflows)

Use for:
- Long-running processes
- Complex state management
- Retries and error handling
- Saga pattern

Example:
```
Workflow: Recurring Chore Rotation
1. Query tasks due for rotation
2. Calculate next assignee
3. Update task assignment
4. Send notification
5. Schedule next rotation
```

## Service Dependency Graph

```
Mobile App
    ↓
API Service ←→ Redis (cache)
    ↓         ↓
    ↓     PostgreSQL
    ↓         ↓
    ↓     Temporal ←→ Temporal Worker
    ↓
  Kafka
    ↓
    ├→ Notifier Service → Firebase
    ├→ Kafka Consumer (Analytics)
    └→ Future Services...
```

## Service Sizing Guidelines

Start with:
- **Small services**: 1000-5000 lines of code
- **Focused scope**: Single business capability
- **Few dependencies**: Minimize inter-service calls

Avoid:
- **Nano-services**: Too many services (>20) creates overhead
- **Distributed monolith**: Services that must be deployed together

## Testing Strategy

### Unit Tests (70%)
- Test each service in isolation
- Mock external dependencies
- Fast feedback (< 1 minute)

### Integration Tests (20%)
- Test service with real dependencies (database, cache)
- Use testcontainers for infrastructure
- Medium speed (< 10 minutes)

### E2E Tests (10%)
- Test across all services
- Simulate real user scenarios
- Slow but comprehensive (< 30 minutes)

## Deployment Strategy

### Canary Deployments
- Deploy new version to 10% of traffic
- Monitor metrics (error rate, latency)
- Gradually increase to 100% or rollback

### Feature Flags
- Deploy code but keep features disabled
- Enable features progressively
- Quick rollback via flag toggle

### Blue-Green Deployments
- Deploy to new environment (green)
- Switch traffic from old (blue) to new (green)
- Keep blue for quick rollback

## Monitoring and Observability

### Metrics (Prometheus)
- Request rate, error rate, latency per service
- Resource usage (CPU, memory, connections)
- Business metrics (tasks created, notifications sent)

### Logs (Loki)
- Structured logging with correlation IDs
- Centralized log aggregation
- Log levels per service

### Tracing (Tempo/Jaeger)
- Distributed tracing across services
- Identify bottlenecks in request flow
- Debug performance issues

### Dashboards (Grafana)
- Service-level dashboards
- System-wide overview
- SLO tracking

## Evolution Strategy

### Phase 1 (Current): Coarse-Grained Services
- 5 services
- Start simple, reduce operational overhead
- Validate patterns and practices

### Phase 2 (6-12 months): Selective Splitting
- Split services only when needed:
  - Performance bottleneck (different scaling needs)
  - Team ownership (clear boundaries)
  - Technology mismatch (better tool available)

### Phase 3 (12+ months): Mature Architecture
- Well-defined boundaries
- Established patterns
- Strong observability
- Possible additional services:
  - Analytics Service (Python for ML)
  - Recommendation Service (Python for AI)
  - Integration Service (third-party APIs)

## References

- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/index.html)
- [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices_2nd_edition/)
- [Martin Fowler: Microservices](https://martinfowler.com/articles/microservices.html)
- [The Twelve-Factor App](https://12factor.net/)

## Revision History

- **2024-01-15**: Initial decision
- **2024-01-15**: Added service dependencies and evolution strategy

---

**Previous ADR**: [ADR-009: Use JWT for Authentication](./ADR-009-jwt-authentication.md)
