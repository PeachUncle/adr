# ADR-0013: Dapr Abstraction Layer for Event-Driven Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-30
- **Feature:** 002-phase-5-cloud-deploy
- **Context:**

Phase 5 transforms the application into an event-driven, distributed microservices platform. The system requires reliable event streaming for task operations, real-time sync across clients, and asynchronous processing of reminders and recurring tasks. Message broker infrastructure is needed to decouple services and enable at-least-once delivery guarantees.

Key requirements:
- Task CRUD events must be published for consumption by multiple services (FR-EDA-001)
- Real-time sync requires task updates to be broadcast to connected clients (US16)
- Reminders require exact-time scheduling via Dapr Jobs API (US11)
- Services must communicate securely via mTLS (NFR-SEC-001)
- System must gracefully handle message broker unavailability (NFR-REL-001)

Constitution Principle XVIII requires: "No direct Kafka clients, use Dapr Pub/Sub" as the abstraction layer for all event-driven communication.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines communication pattern for all services
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Direct Kafka vs Dapr considered
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all 7 services
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use Dapr Pub/Sub as the abstraction layer for all Kafka event streaming.

**Component Stack:**
- **Event Streaming Abstraction**: Dapr Pub/Sub (sidecar pattern)
- **Message Broker**: Kafka (Strimzi for local, Redpanda Cloud for production)
- **Dapr Runtime**: 1.14+ (sidecar injection via annotations)
- **Building Blocks Used**: Pub/Sub, State Management, Secrets, Service Invocation, Jobs API, Resiliency
- **Topic Strategy**: task-events, reminders, task-updates (3 topics)
- **Consumer Pattern**: Dapr subscription handlers (HTTP callbacks)

All services (Backend, WebSocket, Notification, Recurring, Audit) communicate via Dapr Pub/Sub API. Kafka client libraries are not used directly in application code.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

**Infrastructure Abstraction:**
- Kafka can be swapped for RabbitMQ, NATS, or AWS SNS without code changes
- Single configuration file change per environment
- Enables cloud provider portability (local Strimzi vs production Redpanda)

**Built-in Resilience:**
- Automatic retries with exponential backoff (configurable)
- Dead letter queue for failed events (DLQ topic)
- Circuit breaker patterns out-of-the-box

**Security:**
- mTLS between all services via Dapr Sentry (automatic)
- Service-to-service encryption without additional configuration
- No need to manage certificates in application code

**Developer Experience:**
- Consistent API across all building blocks (Pub/Sub, State, Secrets, Jobs)
- Language-agnostic SDK (Python for backend services)
- Local development matches production (same Dapr components, different broker backend)

**Scalability:**
- Independent scaling of producer and consumer services
- Horizontal pod autoscaling works transparently with Dapr sidecars
- Consumer group management handled by Dapr

### Negative

**Complexity:**
- Dapr learning curve for team unfamiliar with sidecar pattern
- Additional operational component (Dapr runtime) to monitor and maintain
- Sidecar overhead (~20MB per pod) increases resource consumption

**Latency:**
- Extra hop through Dapr sidecar for each Pub/Sub call
- Adds ~10-20ms latency to event publishing
- May require tuning for extremely low-latency requirements

**Debugging:**
- Distributed tracing required (correlation_id needed)
- Two failure surfaces to investigate (app vs sidecar)
- More complex local debugging (dapr sidecar must run)

**Vendor Ecosystem:**
- Dapr adoption required for all services
- Less community resources compared to Kafka-native implementations
- Potential long-term commitment to Dapr ecosystem

## Alternatives Considered

**Alternative A: Direct Kafka Client (kafka-python, aiokafka)**

**Rejected because:**
- Tight coupling to Kafka - swapping broker requires code changes
- Manual implementation of retries, DLQ, circuit breakers
- mTLS setup and certificate management for each service
- Inconsistent resilience patterns across services

**Why rejected:** Dapr provides abstraction and resilience patterns out-of-the-box, aligning with Constitution Principle XVIII. Direct clients require more operational overhead for achieving same guarantees.

**Alternative B: RabbitMQ with Spring Cloud Stream**

**Rejected because:**
- Different programming model (requires Java SDK for best experience)
- Not Kafka-compatible (different consumer semantics)
- Smaller community and fewer integration options
- Does not align with spec requirement for Kafka-compatible broker

**Why rejected:** Spec specifies Redpanda Cloud (Kafka-compatible). RabbitMQ would require additional bridging or broker change.

**Alternative C: AWS EventBridge / GCP PubSub (Cloud Native)**

**Rejected because:**
- Vendor lock-in to specific cloud provider
- Different local vs production experience (no local equivalent)
- More complex local development setup
- Does not support DigitalOcean DOKS target environment

**Why rejected:** DigitalOcean DOKS is the sole production target. Cloud-native services would require cross-region setup and higher complexity.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: [specs/002-phase-5-cloud-deploy/spec.md](../../specs/002-phase-5-cloud-deploy/spec.md)
- Implementation Plan: [specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions](../../specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions)
- Constitution Phase 5: [constitution-prompt-phase-5.md](../../constitution-prompt-phase-5.md)
- Dapr Documentation: [https://docs.dapr.io/developing-applications/building-blocks/pubsub/](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- Related ADRs: ADR-0009 (Three-Container Microservice Architecture), ADR-0010 (Service Discovery and Networking)
- Evaluator Evidence: None (initial decision)
