
## Status

**Accepted** | Date: 2025-10-18

## Context

MobilityCorp's microservices architecture (ADR-002) requires a robust communication pattern between services. The system handles multiple asynchronous workflows:

- **Business Operations**: Booking lifecycle, vehicle status changes, payment processing
- **Incident Detection**: Safety anomalies trigger GenAI explanations and potential HITL workflows
- **User Engagement**: AI-driven personalized recommendations based on behavior patterns
- **Audit Logging**: All GenAI interactions must be immutably logged for compliance
- **Fleet Telemetry**: High-volume IoT data from thousands of vehicles (architecture strategy TBD in separate ADR)

### Key Challenges

1. **Service Decoupling**: GenAI Platform shouldn't block core booking operations
2. **Reliability**: Can't lose incident alerts or audit logs
3. **Ordering**: Some workflows require ordered event processing (e.g., ride lifecycle)
4. **Scalability**: Need to scale consumers independently of producers
5. **Event Replay**: Ability to reprocess events for GenAI model retraining or incident investigation
6. **Volume Variability**: Different event types have vastly different volumes (bookings vs. telemetry)

### Constraints

- Must support real-time processing (<1s latency for critical events)
- Need guaranteed delivery for audit logs (EU AI Act compliance)
- Limited budget for message broker infrastructure
- Need event retention for 90 days minimum (compliance requirement)

## Decision

We will adopt an **event-driven architecture** using **Apache Kafka** as the central event backbone for asynchronous service-to-service communication.

### Architecture Pattern

```
Producer Services → Kafka Topics → Consumer Services
```

### Topic Design Strategy

We adopt a **domain-driven topic naming** convention: `{domain}.{entity}.{event}` (e.g., `booking.created`, `vehicle.status.changed`).

**Topic Categories:**

1. **Core Business Events**

   - Booking lifecycle events (`booking.*`)
   - Vehicle status changes (`vehicle.status.*`)
   - Payment events (`payment.*`)
   - User activity events (`user.*`)

2. **GenAI Integration Events** ⭐

   - AI request/response pairs (`genai.request`, `genai.response`)
   - Human-in-the-loop workflows (`genai.hitl.*`)
   - User engagement events for personalization (`user.engagement.*`)

3. **Operational Events**

   - Incident detection and alerts (`incident.*`)
   - System health and monitoring events

4. **Telemetry Ingestion** (Architecture TBD)
   - High-volume IoT data from fleet vehicles
   - **Note**: Given the extreme data volume (10K+ messages/sec), telemetry may use a separate streaming pipeline (e.g., MQTT → Time-series DB directly, or dedicated Kafka cluster). This decision is deferred to a future ADR focused on IoT data architecture.

**Retention Strategy:**

- **Compliance-critical events** (GenAI audit, payments): 90 days minimum (EU AI Act requirement)
- **Business events** (bookings, incidents): 30-90 days for operational analysis
- **Telemetry data**: Retention strategy TBD based on storage costs and analytics requirements

### Event Schema

All events follow CloudEvents specification with JSON payloads:

```json
{
  "specversion": "1.0",
  "type": "com.mobilitycorp.incident.detected",
  "source": "/telemetry-service",
  "id": "A234-1234-1234",
  "time": "2025-10-18T12:34:56Z",
  "datacontenttype": "application/json",
  "data": {
    "incident_id": "inc_abc123",
    "vehicle_id": "veh_xyz789",
    "severity": "high",
    "anomaly_type": "sudden_stop",
    "location": {"lat": 52.520008, "lon": 13.404954},
    "telemetry_snapshot": {...}
  }
}
```

### Consumer Groups

Services subscribe to relevant event streams based on their domain responsibilities:

- **genai-service**: Consumes incident alerts and user engagement events for AI processing
- **audit-service**: Consumes all GenAI-related events for compliance logging
- **analytics-service**: Consumes business events for data warehouse and reporting
- **notification-service**: Consumes critical events requiring user/operator notifications
- **billing-service**: Consumes booking and payment events for invoicing

### Communication Patterns

1. **Synchronous (REST)**: User-facing requests via API Gateway

   - Booking creation, user profile, payment initiation

2. **Asynchronous (Kafka)**: Service-to-service, background processing

   - GenAI processing, analytics, notifications, audit logging

3. **Request-Reply**: For GenAI conversational support (uses correlation IDs)

## Consequences

### Positive

✅ **Decoupling**: Services don't need to know about each other's endpoints, reduces coupling

✅ **Scalability**: Kafka handles 10K+ messages/sec, consumer groups scale independently

✅ **Reliability**: Persistent events with replication (RF=3), guaranteed delivery

✅ **Event Replay**: Can reprocess events for GenAI retraining or incident forensics

✅ **Audit Trail**: Immutable event log meets EU AI Act record-keeping requirements

✅ **Flexibility**: New consumers can subscribe without changing producers

✅ **Resilience**: Services can process events at their own pace, buffering during failures

✅ **Observability**: Kafka metrics provide visibility into message flow and lag

### Negative

❌ **Operational Complexity**: Kafka cluster requires careful tuning, monitoring, and maintenance

❌ **Eventual Consistency**: No immediate consistency across services (acceptable for our domain)

❌ **Event Schema Evolution**: Need careful version management (mitigated with Avro/Protobuf)

❌ **Debugging**: Harder to trace request flows across async boundaries (requires correlation IDs + tracing)

❌ **Cost**: Kafka cluster infrastructure (3+ brokers, ZooKeeper/KRaft)

❌ **Learning Curve**: Team needs to understand Kafka semantics (offsets, consumer groups, rebalancing)

### Mitigation Strategies

- **Managed Kafka**: Use AWS MSK or Confluent Cloud to reduce operational burden
- **Schema Registry**: Confluent Schema Registry for event schema validation and evolution
- **Dead Letter Queue**: Separate topics for failed message processing with retry logic
- **Correlation IDs**: Every event includes correlation ID for distributed tracing
- **Monitoring**: Kafka lag monitoring with alerts for consumer falling behind
- **Testing**: Testcontainers for local Kafka testing in CI/CD

## Alternatives Considered

### 1. Synchronous REST APIs Only

**Pros**: Simpler mental model, immediate consistency
**Cons**: Tight coupling, cascading failures, can't handle telemetry volume, no audit trail

**Why Rejected**: Cannot handle IoT telemetry volume, GenAI Platform failures would cascade to core services

### 2. RabbitMQ (Message Queue)

**Pros**: Simpler operations, good for job queues, flexible routing
**Cons**: Lower throughput than Kafka, no native event replay, weaker persistence guarantees

**Why Rejected**: Insufficient throughput for telemetry, lacks event replay for GenAI retraining

### 3. AWS SQS + SNS

**Pros**: Fully managed, no ops burden, pay-per-use
**Cons**: No event replay, 14-day max retention, vendor lock-in, limited ordering guarantees

**Why Rejected**: Compliance requires 90-day retention, need event replay for audit and retraining

### 4. Redis Streams

**Pros**: Low latency, simpler than Kafka, good for real-time
**Cons**: Not designed for persistent event log, limited durability, no mature ecosystem

**Why Rejected**: Insufficient durability guarantees for audit logs and compliance

### 5. Event Sourcing (Full)

**Pros**: Complete audit trail, time-travel debugging, perfect consistency
**Cons**: Extreme complexity, snapshot management, query complexity, over-engineering

**Why Rejected**: Too complex for current requirements, can adopt later if needed

## Implementation Plan

### Phase 1: Kafka Infrastructure

- Deploy Kafka cluster (3 brokers, AWS MSK or self-hosted)
- Configure replication factor=3, min.insync.replicas=2
- Set up monitoring (Prometheus + Grafana dashboards)

### Phase 2: Core Event Topics

- Define and create initial topics: `booking.*`, `vehicle.status.*`, `payment.*`
- Implement producers in Booking Service and Fleet Service
- Build consumer in Analytics Service (validate end-to-end)
- Document topic naming conventions and schema standards

### Phase 3: GenAI Events

- Create topics: `genai.*`, `incident.detected`, `genai.hitl.*`
- Implement GenAI Platform as both producer and consumer
- Build Audit Service consumer for compliance logs

### Phase 4: User Engagement

- Create topic: `user.engagement.event`
- Implement producers in User Service and Booking Service
- GenAI Platform consumer for personalization pipeline

### Phase 5: Production Hardening

- Schema Registry setup with Avro schemas
- Dead letter queue implementation
- Load testing (simulate 10K messages/sec)
- Runbook for common operational issues

## Metrics for Success

- **Throughput**: Handle business event volume with <1s latency for critical events
- **Reliability**: 99.99% event delivery (no message loss for critical events)
- **Consumer Lag**: <10s lag for high-priority events (incident alerts, HITL workflows)
- **Durability**: Zero audit log loss over 90-day retention window (compliance requirement)
- **Availability**: Kafka cluster 99.95% uptime
- **Schema Compliance**: 100% of events validate against registered schemas

## Related

### ADRs

- [ADR-002: Microservices Architecture](002-microservices-architecture) - Foundation for event-driven communication

### External References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Designing Event-Driven Systems (Ben Stopford)](https://www.confluent.io/designing-event-driven-systems/)
- [CloudEvents Specification](https://cloudevents.io/)

## Notes

The event-driven backbone is critical for GenAI integration. By treating all GenAI interactions as events (`genai.request`, `genai.response`, `genai.hitl.*`), we automatically satisfy EU AI Act record-keeping requirements and enable future capabilities like event replay for model retraining and incident investigation.

### Why Kafka vs. Managed Alternatives?

While AWS SQS/SNS would reduce operational complexity, Kafka's event replay capability is essential for:

1. **GenAI Retraining**: Replay user queries and responses to fine-tune models
2. **Incident Forensics**: Reconstruct exact sequence of events leading to safety incidents
3. **Compliance Audits**: Reproduce decision trail for regulatory inquiries
4. **A/B Testing**: Replay same events to new model versions for comparison

This architectural investment pays dividends as the GenAI system matures.
