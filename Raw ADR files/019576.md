# ADR-002: Microservices Architecture

## Status

**Accepted** | Date: 2025-10-18

## Context

MobilityCorp's vehicle-sharing platform needs to support multiple vehicle types (electric scooters, eBikes, cars, vans), handle real-time telemetry from thousands of IoT devices, process payments, manage user accounts, and integrate GenAI capabilities for intelligent operations. The system must scale independently across different concerns, enable team autonomy, and allow for rapid iteration on AI features without impacting core booking functionality.

### Key Requirements

- **Independent Scalability**: Fleet telemetry processing (high volume) vs. booking operations (transaction-heavy) have different scaling profiles
- **Team Autonomy**: Separate teams working on GenAI, payments, fleet management, and customer-facing features
- **Technology Flexibility**: GenAI Platform requires GPU infrastructure and Python/ML stack, while core services use Node.js/Go
- **Fault Isolation**: AI service failures shouldn't impact critical booking and payment flows
- **Compliance**: GenAI Platform requires strict audit trails and EU AI Act compliance controls

### Constraints

- Must support real-time operations (<500ms booking response time)
- Need clear boundaries for compliance auditing (especially GenAI subsystem)
- Limited DevOps team size (need manageable operational complexity)
- Must integrate with existing payment gateways and map services

## Decision

We will adopt a **microservices architecture** with the following bounded contexts:

### Core Services

1. **User Service**

   - User authentication, profiles, preferences
   - Payment methods, ride history
   - Technology: Node.js, PostgreSQL

2. **Booking Service**

   - Vehicle search, reservation, ride management
   - Pricing calculations, availability checks
   - Technology: Node.js, PostgreSQL + Redis cache

3. **Fleet Service**

   - Vehicle inventory, locations, status tracking
   - Maintenance scheduling, vehicle assignments
   - Technology: Go, PostgreSQL + PostGIS

4. **Payment Service**

   - Payment processing, refunds, billing
   - Integration with external payment gateway
   - Technology: Node.js, PostgreSQL (PCI compliance)

5. **Telemetry Pipeline**
   - Real-time IoT data ingestion via MQTT
   - Time-series storage, anomaly detection triggers
   - Technology: Go, TimescaleDB

### GenAI Platform (Bounded Context)

6. **GenAI Platform** ⭐
   - Conversational support, incident summarization
   - Safety anomaly explanations, personalized engagement
   - RAG pipeline, TEVV verification, HITL gateway, audit store
   - Technology: Python (FastAPI), PostgreSQL + pgvector, MLflow

### Service Communication

- **Synchronous**: REST APIs via API Gateway for user-facing requests
- **Asynchronous**: Apache Kafka event bus for service-to-service communication
- **Database**: Database-per-service pattern (no shared databases)

## Consequences

### Positive

✅ **Independent Deployment**: GenAI Platform can be updated multiple times per day without touching core booking logic

✅ **Technology Optimization**: Each service uses the best-fit technology (Python for AI, Go for high-throughput telemetry)

✅ **Scalability**: Telemetry Pipeline can scale to 10K messages/sec independently from booking service (50 requests/sec)

✅ **Fault Isolation**: GenAI Platform failure degrades to manual operations team support, booking still works

✅ **Team Autonomy**: 3 parallel teams (Core Platform, Fleet Ops, AI/ML) can work independently

✅ **Compliance Boundaries**: Clear audit boundaries for GenAI Platform (EU AI Act requirement)

✅ **Testing**: Smaller codebases enable faster testing cycles and easier unit test coverage

### Negative

❌ **Operational Complexity**: Need to manage 6+ services with separate deployments, monitoring, and logging

❌ **Network Latency**: Additional network hops for inter-service communication (mitigated with caching and async events)

❌ **Data Consistency**: Eventually consistent across services (acceptable for our domain)

❌ **Distributed Tracing**: Requires sophisticated observability (Jaeger/OpenTelemetry implementation needed)

❌ **Transaction Management**: No distributed transactions (mitigated with event-driven patterns and saga pattern)

### Mitigation Strategies

- **Kubernetes + Helm**: Standardized deployment patterns reduce operational overhead
- **Shared Libraries**: Common authentication, logging, metrics libraries
- **API Gateway**: Single entry point simplifies routing and authentication
- **Service Mesh (Future)**: Consider Istio/Linkerd if complexity grows beyond 10 services
- **Contract Testing**: Pact or similar for API contract validation

## Alternatives Considered

### 1. Monolithic Architecture

**Pros**: Simpler deployment, easier transactions, lower latency
**Cons**: Cannot isolate GenAI for compliance, scaling becomes all-or-nothing, technology lock-in, team conflicts

**Why Rejected**: GenAI compliance requirements demand clear isolation, and team scaling would bottleneck on single codebase

### 2. Modular Monolith

**Pros**: Internal modularity, single deployment, shared database
**Cons**: Still can't isolate GenAI infrastructure (needs GPUs), eventual scaling pain, harder to achieve team autonomy

**Why Rejected**: Doesn't solve GenAI isolation requirement or technology flexibility needs

### 3. Serverless Functions (FaaS)

**Pros**: Extreme scalability, minimal ops, pay-per-use
**Cons**: Cold start latency unacceptable for booking, GenAI requires long-running GPU instances, vendor lock-in

**Why Rejected**: Not suitable for real-time requirements or stateful GenAI Platform

## Implementation Plan

### Phase 1: Foundation

- User Service + Booking Service
- PostgreSQL + Redis setup
- API Gateway (Kong/AWS API Gateway)

### Phase 2: Fleet Operations

- Fleet Service + Telemetry Pipeline
- MQTT broker setup
- TimescaleDB for time-series data

### Phase 3: GenAI Integration

- GenAI Platform with RAG pipeline
- Event-driven integration via Kafka
- Audit store implementation

### Phase 4: Production Hardening

- Monitoring (Prometheus + Grafana)
- Distributed tracing (Jaeger)
- Load testing and optimization

## Metrics for Success

- **Service Independence**: >90% of deployments affect only 1 service
- **Response Times**: Booking API <500ms p95, GenAI API <2s p95
- **Availability**: 99.9% uptime per service (composite ~99.4% for full journey)
- **Team Velocity**: Features delivered in parallel across 3 teams

## Related

### ADRs

- [ADR-003: Event-Driven Backbone](003-event-driven-backbone.md) - Communication between microservices

### External References

- [Sam Newman - Building Microservices](https://samnewman.io/books/building_microservices_2nd_edition/)
- [Martin Fowler - Microservices Guide](https://martinfowler.com/microservices/)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)

## Notes

This decision aligns with our AI-first strategy by treating GenAI as a first-class bounded context rather than a cross-cutting concern. The microservices approach enables us to innovate rapidly on AI features while maintaining stability in core booking operations.
