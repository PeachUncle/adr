# ADR-002: Use Apache Kafka as Message Broker

## Status
Accepted

## Context
The SMS messaging platform requires asynchronous processing of messages between the SMS Service and Processor Service. We need a reliable message broker that can:

- Handle high throughput message processing
- Provide durability and reliability guarantees
- Support horizontal scaling
- Integrate well with Java/Quarkus applications
- Provide message ordering and delivery guarantees
- Enable replay capabilities for debugging and recovery

## Decision
We will use Apache Kafka as the primary message broker for asynchronous communication between services.

**Configuration Details**:
- **Mode**: KRaft (Kafka Raft) mode for simplified cluster management
- **Topics**: `sms.requests` for message processing queue
- **Integration**: Quarkus SmallRye Reactive Messaging with Kafka connector
- **Deployment**: Containerized using Confluent Platform Docker images

## Consequences

### Positive
- **High Throughput**: Kafka can handle millions of messages per second
- **Durability**: Messages are persisted to disk with configurable replication
- **Scalability**: Easy horizontal scaling by adding brokers and partitions
- **Ordering Guarantees**: Messages within a partition maintain order
- **Replay Capability**: Can replay messages from any point in time
- **Ecosystem Integration**: Excellent tooling and monitoring support
- **Quarkus Integration**: Native integration with SmallRye Reactive Messaging
- **Fault Tolerance**: Built-in replication and failure handling

### Negative
- **Operational Complexity**: Requires understanding of Kafka administration
- **Resource Usage**: Higher memory and disk usage compared to simpler brokers
- **Learning Curve**: Development team needs Kafka expertise
- **Over-engineering Risk**: May be more complex than needed for current scale
- **Latency**: Slightly higher latency compared to in-memory brokers

### Neutral
- **Configuration Management**: Need to manage Kafka-specific configurations
- **Monitoring Requirements**: Need Kafka-specific monitoring and alerting
- **Schema Evolution**: Need strategy for message schema changes

## Implementation Details

### Kafka Configuration
```yaml
# KRaft mode configuration
KAFKA_NODE_ID: 1
KAFKA_PROCESS_ROLES: broker,controller
KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:29093
KAFKA_AUTO_CREATE_TOPICS_ENABLE: true
```

### Producer Configuration (SMS Service)
```properties
# Quarkus Kafka producer
mp.messaging.outgoing.sms-requests.connector=smallrye-kafka
mp.messaging.outgoing.sms-requests.topic=sms.requests
mp.messaging.outgoing.sms-requests.value.serializer=io.quarkus.kafka.client.serialization.JsonbSerializer
```

### Consumer Configuration (Processor Service)
```properties
# Quarkus Kafka consumer
mp.messaging.incoming.sms-requests.connector=smallrye-kafka
mp.messaging.incoming.sms-requests.topic=sms.requests
mp.messaging.incoming.sms-requests.value.deserializer=io.quarkus.kafka.client.serialization.JsonbDeserializer
```

### Message Schema
```json
{
  "id": "UUID",
  "sender": "string (phone number)",
  "recipient": "string (phone number)", 
  "text": "string (message content)",
  "createdAt": "timestamp",
  "status": "string (PENDING)"
}
```

## Alternatives Considered

### RabbitMQ
- **Pros**: Easier to operate, better for complex routing, good management UI
- **Cons**: Lower throughput, less suitable for high-volume streaming
- **Decision**: Good alternative but Kafka better matches our scalability requirements

### Amazon SQS
- **Pros**: Fully managed, no operational overhead, good AWS integration
- **Cons**: Vendor lock-in, higher latency, limited replay capabilities
- **Decision**: Considered for cloud deployment but want technology-agnostic solution

### Redis Streams
- **Pros**: Lower latency, simpler setup, good for caching + messaging
- **Cons**: Less mature for enterprise messaging, limited durability guarantees
- **Decision**: Good for caching but not suitable as primary message broker

### Apache Pulsar
- **Pros**: Modern architecture, better multi-tenancy, simpler operations
- **Cons**: Smaller ecosystem, less mature tooling, steeper learning curve
- **Decision**: Promising but ecosystem not as mature as Kafka

## Monitoring and Observability

### Key Metrics
- **Producer Metrics**: Message send rate, send latency, error rate
- **Consumer Metrics**: Message consume rate, consumer lag, processing time
- **Broker Metrics**: Disk usage, memory usage, replication lag
- **Topic Metrics**: Message count, partition distribution, retention

### Tools
- **Kafka UI**: Web interface for topic and message management
- **Prometheus**: Metrics collection from Kafka JMX
- **Grafana**: Visualization of Kafka metrics
- **Application Logs**: Structured logging for message processing

## Operational Considerations

### Backup and Recovery
- **Topic Configuration**: Replication factor for durability
- **Message Retention**: Time-based and size-based retention policies
- **Disaster Recovery**: Cross-region replication strategy

### Scaling Strategy
- **Vertical Scaling**: Increase broker resources (memory, CPU, disk)
- **Horizontal Scaling**: Add more brokers and increase partition count
- **Consumer Scaling**: Multiple consumer instances for parallel processing

### Security (Future Enhancement)
- **Authentication**: SASL/SCRAM or mTLS
- **Authorization**: ACLs for topic access control
- **Encryption**: TLS for data in transit

## Related Decisions
- [ADR-001: Use Microservices Architecture](001-microservices-architecture.md)
- [ADR-003: Use Quarkus as Java Framework](003-quarkus-framework.md)
- [ADR-007: Asynchronous Message Processing Pattern](007-async-processing-pattern.md)
