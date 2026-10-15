# ADR-0002: Event-Driven Architecture with Kafka

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-29
- **Feature:** 007-phase5-cloud-deployment
- **Context:** Phase V requires decoupling recurring task generation from the main application to enable horizontal scaling and independent service failures. The system must propagate task completion events, reminder scheduling events, and task update events across microservices while maintaining per-user ordering and isolation. Direct database triggers would create tight coupling, while synchronous service calls would create single points of failure.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: ✅ Long-term consequence - affects all microservices, service boundaries, and scalability strategy
     2) Alternatives: ✅ Multiple viable options - direct DB triggers, synchronous calls, RabbitMQ, cloud-specific queues
     3) Scope: ✅ Cross-cutting concern - impacts Task Service, Recurring Task Service, Notification Service, event schemas
     All three tests passed - ADR justified. -->

## Decision

Use Apache Kafka for event-driven architecture with the following configuration:

- **Topics**: 3 topics with user_id partitioning (task-events, reminders, task-updates)
- **Partitioning**: 12 partitions per topic with user_id as partition key (guarantees per-user FIFO ordering)
- **Retention**: 7 days for Minikube (local), 30 days for production (per Clarification #3 - balances debugging + cost)
- **Local Deployment**: Bitnami Kafka Helm chart (single replica, PLAINTEXT protocol)
- **Production Deployment**: Redpanda Cloud Serverless (free tier: 10GB storage, 10MB/s throughput) - PRIMARY, with fallback to self-hosted Strimzi on OKE if free tier insufficient
- **Consumer Groups**: Separate consumer groups per service (recurring-task-service-cg, notification-service-cg) for independent scaling

All event publishing and consuming uses Dapr Pub/Sub API (http://localhost:3500/v1.0/publish/pubsub/{topic}) instead of direct Kafka clients. Kafka configuration is swappable via Dapr component YAML (dapr/components/pubsub-kafka.yaml).

## Consequences

### Positive

- **Loose Coupling**: Services communicate via events, no direct service-to-service dependencies (Task Service can be down while Recurring Task Service processes events)
- **Horizontal Scaling**: Can scale Recurring Task Service and Notification Service to 12 instances each (one per partition)
- **Per-User Ordering**: user_id partitioning guarantees FIFO processing for a single user's events (prevents race conditions)
- **User Isolation**: Events for user A never processed by same consumer instance as user B (security + performance isolation)
- **Reliable Event Delivery**: Kafka provides durable storage (messages survive consumer restarts), automatic retry, dead letter queues
- **Audit Trail**: 30-day retention provides event replay capability for debugging production incidents
- **Multi-Cloud Portability**: Dapr Pub/Sub abstraction allows swapping Kafka→RabbitMQ, Redpanda→Confluent without code changes
- **Cost Efficiency**: Redpanda Cloud free tier (10GB, 10MB/s) sufficient for 100 events/day × 30 days = 30MB storage

### Negative

- **Operational Complexity**: Kafka cluster management (monitoring consumer lag, partition rebalancing, broker health)
- **Learning Curve**: Engineers must understand Kafka concepts (partitions, offsets, consumer groups, rebalancing)
- **Eventually Consistent**: Event processing is asynchronous (task completion → next occurrence creation may take 1-2 seconds)
- **Resource Overhead**: Kafka local deployment uses ~1 core, 2GB RAM (significant for Minikube 4 cores, 8GB total)
- **Network Dependency**: Production relies on external Redpanda Cloud service (requires internet connectivity)
- **Message Ordering Limitations**: Only per-partition ordering guaranteed (no total ordering across all users)

## Alternatives Considered

### Alternative A: Direct Database Triggers

**Components**:
- PostgreSQL triggers on `tasks` table to detect INSERT/UPDATE
- Trigger function calls recurring task calculation logic directly
- Store next occurrence in same transaction

**Why rejected**:
- Tight coupling: Recurring task logic embedded in database (hard to test, scale, version independently)
- No horizontal scaling: Triggers run on single database instance (bottleneck for high load)
- Limited language support: PostgreSQL triggers written in PL/pgSQL (not Python/TypeScript)
- No audit trail: Events not persisted (can't replay failures or debug issues)
- Violates microservices pattern: Business logic in database instead of application layer

### Alternative B: Synchronous Service-to-Service Calls

**Components**:
- Task Service directly invokes Recurring Task Service via HTTP POST
- Notification Service directly invoked when reminder needed
- Retry logic implemented in each service

**Why rejected**:
- Single point of failure: If Recurring Task Service is down, Task Service create operation fails (poor user experience)
- No decoupling: Services must know about each other (tight coupling, harder to change independently)
- No load balancing: Direct calls don't distribute load across multiple service instances
- Manual retry implementation: Must implement exponential backoff, circuit breakers manually (reinventing Kafka features)
- No event history: Can't replay events or debug "what happened 2 days ago" issues

### Alternative C: RabbitMQ

**Components**:
- RabbitMQ for message queue (AMQP protocol)
- Exchanges and queues for task events
- Direct exchange for routing messages

**Why rejected**:
- No partitioning: RabbitMQ doesn't guarantee per-user ordering (round-robin distribution to consumers)
- Limited throughput: RabbitMQ optimized for low-latency, not high-throughput (Kafka handles 100k+ msgs/sec)
- No long retention: RabbitMQ messages deleted after consumption (no audit trail, can't replay events)
- Less mature Dapr support: Dapr Kafka Pub/Sub more battle-tested than RabbitMQ binding
- Lower adoption for event streaming: Kafka is industry standard for event-driven architectures (better documentation, community support)

### Alternative D: Cloud-Specific Message Queues

**Components**:
- Azure Service Bus (Pub/Sub + Topics)
- Google Pub/Sub
- AWS SQS/SNS

**Why rejected**:
- Vendor lock-in: Cannot run on OKE without full rewrite (violates multi-cloud requirement)
- No local development: Cannot run Azure Service Bus on Minikube (requires cloud connection or expensive emulators)
- Cost: Managed services exceed free tier quickly (Service Bus pricing: $0.05/million operations)
- Violates specification requirement (FR-026, FR-027): Spec explicitly requires infrastructure abstraction

## References

- Feature Spec: [specs/007-phase5-cloud-deployment/spec.md](../../specs/007-phase5-cloud-deployment/spec.md)
- Implementation Plan: [specs/007-phase5-cloud-deployment/plan.md](../../specs/007-phase5-cloud-deployment/plan.md)
- Technical Research: [specs/007-phase5-cloud-deployment/research.md](../../specs/007-phase5-cloud-deployment/research.md) (Section 2: Apache Kafka Configuration)
- Event Schemas: [specs/007-phase5-cloud-deployment/contracts/event-schemas.yaml](../../specs/007-phase5-cloud-deployment/contracts/event-schemas.yaml)
- Dapr Pub/Sub Component: [specs/007-phase5-cloud-deployment/contracts/pubsub-kafka.yaml](../../specs/007-phase5-cloud-deployment/contracts/pubsub-kafka.yaml)
- Related ADRs: ADR-0001 (Infrastructure Abstraction with Dapr), ADR-0003 (Reminder Scheduling Strategy)
- Clarifications: PHR-0002 Clarification #1 (user_id partitioning), Clarification #3 (retention policy)
- Evaluator Evidence: PHR-0004 (planning phase - Constitution Check passed all 5 principles)
