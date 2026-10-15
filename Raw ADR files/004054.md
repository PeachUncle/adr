# ADR-001: Message Broker Choice - RabbitMQ vs Apache Kafka

## Status

Accepted

## Context

SwiftTrack requires a message broker for asynchronous communication between microservices. The system needs to handle order events, tracking updates, and integration events with external systems. We need to choose between RabbitMQ and Apache Kafka as our primary message broker.

## Decision

We will use **RabbitMQ** as our primary message broker, with an abstraction layer that allows future migration to Kafka if needed.

## Rationale

### RabbitMQ Advantages

1. **Operational Simplicity**: RabbitMQ is easier to deploy, configure, and maintain
2. **Development Speed**: Faster to implement with existing Node.js libraries (amqplib)
3. **Message Patterns**: Built-in support for request-reply, publish-subscribe, and routing patterns
4. **Management UI**: Excellent web-based management interface for monitoring and debugging
5. **Team Expertise**: Team has more experience with RabbitMQ
6. **Resource Requirements**: Lower memory and storage requirements for our expected load

### Kafka Considerations

While Kafka offers superior performance and scalability, it comes with:

- Higher operational complexity
- Steeper learning curve
- Over-engineering for our current scale (< 10K orders/day)
- Additional infrastructure requirements (Zookeeper/KRaft)

### Mitigation Strategy

- Implement a message bus abstraction layer (`@swifttrack/message-bus` package)
- Design event schemas to be Kafka-compatible
- Monitor system growth and revisit decision when approaching Kafka's sweet spot

## Consequences

### Positive

- Faster development and deployment
- Lower operational overhead
- Better debugging and monitoring tools
- Sufficient performance for projected load

### Negative

- May need to migrate to Kafka for very high-scale scenarios
- Less suitable for high-throughput event streaming

### Migration Path

If we reach scale limits (~100K orders/day), we can:

1. Implement Kafka adapter in our abstraction layer
2. Gradually migrate event types to Kafka
3. Run hybrid setup during transition
4. Complete migration with minimal application code changes

## Review Date

This decision will be reviewed in 12 months or when system load exceeds 50K orders/day.
