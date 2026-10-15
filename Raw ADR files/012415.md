# [ADR-0011] Event-Driven Architecture

## Status

Accepted

## Date

2023-07-20

## Context

As part of our MACH architecture implementation ([ADR-0001](0001-adopt-mach-architecture.md)), we need to establish patterns for communication between microservices. While synchronous REST APIs are suitable for many interactions, asynchronous event-driven communication offers advantages for certain scenarios, including:

- Decoupling services for better resilience
- Handling workload spikes through buffering
- Enabling complex workflows across multiple services
- Supporting eventual consistency patterns
- Implementing audit trails and event sourcing
- Facilitating real-time features and notifications

We need to select an event-driven architecture pattern and supporting technologies that integrate well with our Kubernetes-based infrastructure and complement our existing architectural decisions.

## Decision

We will implement an event-driven architecture using **Apache Kafka** as the event streaming platform, with the following key components and patterns:

1. **Apache Kafka** as the central event streaming platform:
   - Deployed in Kubernetes using Strimzi operator
   - Configured for high availability with appropriate replication
   - Integrated with our observability stack for monitoring

2. **Event Schema Registry** for schema management:
   - Confluent Schema Registry for Avro schema management
   - Schema evolution governance
   - Compatibility checking

3. **Event Patterns**:
   - Event Notification: For lightweight notifications between services
   - Event-Carried State Transfer: For sharing state changes
   - Event Sourcing: For critical business entities
   - Command Query Responsibility Segregation (CQRS): For complex query requirements

4. **Kafka Streams** for stream processing:
   - Real-time data processing
   - Aggregations and transformations
   - Stateful operations

5. **Kafka Connect** for integration:
   - Database change data capture (CDC)
   - Integration with external systems
   - Data synchronization

## Consequences

### Positive

- **Decoupling**: Services are less dependent on each other's availability.
- **Scalability**: Better handling of traffic spikes through buffering.
- **Resilience**: Services can continue functioning when downstream services are unavailable.
- **Flexibility**: Easier to add new consumers without modifying producers.
- **Audit Trail**: Natural audit trail of all system events.
- **Real-time Capabilities**: Foundation for real-time features and analytics.
- **Eventual Consistency**: Better support for eventual consistency patterns.
- **Replay Capability**: Events can be replayed for recovery or new consumers.

### Negative

- **Complexity**: Event-driven systems are more complex to design, develop, and debug.
- **Eventual Consistency**: Requires handling eventual consistency in the business logic.
- **Operational Overhead**: Kafka cluster requires monitoring and maintenance.
- **Learning Curve**: Team needs to learn event-driven patterns and Kafka concepts.
- **Testing Challenges**: More difficult to test event-driven flows end-to-end.
- **Schema Management**: Requires careful management of event schemas and evolution.
- **Resource Usage**: Kafka requires significant resources for optimal performance.

## Alternatives Considered

### Synchronous REST APIs Only

**Pros**:
- Simplicity in implementation and understanding
- Immediate consistency
- Easier debugging and tracing
- Familiar to most developers
- Simpler testing

**Cons**:
- Tight coupling between services
- Limited resilience to service outages
- Challenges with traffic spikes
- Potential for cascading failures
- Less suitable for long-running processes

This option was rejected for all use cases but will still be used where synchronous communication is appropriate.

### RabbitMQ or Other Message Brokers

**Pros**:
- Lighter weight than Kafka
- Good for simple messaging patterns
- Lower resource requirements
- Mature and stable
- Good support for various messaging patterns

**Cons**:
- Limited stream processing capabilities
- Less suitable for high-throughput event streaming
- Limited replay capabilities
- Less scalable for very high volumes
- Fewer ecosystem tools

This option was rejected in favor of Kafka's stronger event streaming capabilities and ecosystem.

### Cloud Provider Event Services (AWS EventBridge, Azure Event Grid, etc.)

**Pros**:
- Fully managed services
- Reduced operational overhead
- Built-in scaling and high availability
- Integration with other cloud services
- Serverless options available

**Cons**:
- Vendor lock-in
- Potentially higher costs at scale
- Limited control over implementation details
- Less flexibility for hybrid or multi-cloud deployments
- Potential feature limitations compared to Kafka

This option was rejected due to concerns about vendor lock-in and the desire for a cloud-agnostic solution.

### GraphQL Subscriptions

**Pros**:
- Real-time updates to clients
- Integrated with GraphQL query language
- Client-specified subscription data
- Good for frontend-focused real-time updates
- Simpler implementation for certain use cases

**Cons**:
- Not designed for service-to-service communication
- Limited to pub/sub pattern
- Scalability concerns for high-volume events
- Less suitable for event sourcing or CQRS
- Primarily focused on client-server communication

This option was rejected for service-to-service communication but may be considered for frontend real-time updates.

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Strimzi Kafka Operator](https://strimzi.io/docs/)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Event Sourcing Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [Kafka Streams Documentation](https://kafka.apache.org/documentation/streams/)
- [Kafka Connect Documentation](https://kafka.apache.org/documentation/#connect)
