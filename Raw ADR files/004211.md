# ADR-007: Choosing Message Broker (Apache Pulsar vs. RabbitMQ)

## Date:
2024-04-03

## Status:
Accepted

## Context:
The context for this decision is to choose the right message broker for the Fishy Watch system. We have evaluated two options: Apache Pulsar and RabbitMQ (RMQ), considering factors such as scalability, performance, reliability, feature set, and compatibility with our system requirements.

## Decision:
After thorough evaluation and analysis, we have decided to use [Apache Pulsar / RabbitMQ] as the message broker for the Fishy Watch system. Here are the reasons for our decision:

### Apache Pulsar:
- **Scalability**: Apache Pulsar is designed for horizontal scalability, allowing us to handle growing message volumes and concurrent connections effectively.
- **Performance**: Pulsar's architecture, based on Apache BookKeeper and Apache ZooKeeper, offers high throughput and low latency for message processing.
- **Reliability**: Pulsar provides features like persistent storage, message replication, and automatic failover, ensuring message durability and system resilience.
- **Multi-Tenancy**: Pulsar supports multi-tenancy, allowing us to isolate message streams and resources for different customers or farms securely.
- **Geo-Replication**: Pulsar offers built-in geo-replication capabilities, enabling data replication across multiple data centers for disaster recovery and data locality.

### RabbitMQ (RMQ):
- **Mature Technology**: RabbitMQ is a mature and widely adopted message broker with a robust feature set and extensive community support.
- **Protocols and Integrations**: RMQ supports multiple protocols such as AMQP, MQTT, and STOMP, facilitating integration with diverse systems and clients.
- **Flexible Routing**: RMQ's routing mechanisms, including exchanges, queues, and bindings, provide flexibility in message routing and processing logic.
- **Plugin Ecosystem**: RabbitMQ's plugin ecosystem allows extending functionality and integrating with external services, enhancing system capabilities.

## Consequences:
### Pros:
- Chosen message broker (Apache Pulsar / RabbitMQ) offers scalability, performance, reliability, and feature-rich capabilities aligned with Fishy Watch system requirements.
- Decision based on thorough evaluation, considering factors like system architecture, integration needs, and future scalability.
- Extensive documentation, community support, and ecosystem for the selected message broker facilitate implementation, troubleshooting, and maintenance.

### Cons:
- Learning Curve: Adoption of a new message broker (Apache Pulsar) may require initial learning and training efforts for the development team.
- Integration Challenges: Integrating the chosen message broker with existing system components and workflows may require careful planning and implementation.
