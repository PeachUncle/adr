# ADR-008: Choosing RabbitMQ (RMQ) Over Apache Pulsar

## Date:
2024-04-04

## Status:
Accepted

## Context:
The context for this decision is to explain why RabbitMQ (RMQ) was chosen as the message broker for the Fishy Watch system over Apache Pulsar. This decision is based on thorough evaluation and analysis of both options, considering factors such as scalability, performance, reliability, feature set, integration capabilities, and alignment with system requirements.

## Decision:
After careful consideration and evaluation, we have decided to choose RabbitMQ (RMQ) as the message broker for the Fishy Watch system over Apache Pulsar. Here are the reasons for our decision:

### Reasons for Choosing RabbitMQ (RMQ):
1. **Mature Technology and Community Support**:
   - RabbitMQ is a mature and widely adopted message broker with a strong community and extensive documentation. This maturity and community support provide confidence in stability, reliability, and troubleshooting capabilities.

2. **Integration Flexibility**:
   - RMQ supports multiple protocols such as AMQP, MQTT, and STOMP, offering flexibility in integrating with diverse systems, clients, and programming languages. This aligns well with our system's integration needs and ecosystem.

3. **Feature-Rich Capabilities**:
   - RabbitMQ provides a rich set of features including message queues, exchanges, bindings, routing, and plugins. These features offer flexibility in message routing, processing logic, and extensibility, allowing us to customize and optimize message handling.

4. **Scalability and Performance**:
   - While Apache Pulsar offers scalability and performance benefits, RabbitMQ can also be scaled horizontally and tuned for high throughput and low latency. With proper configuration and clustering, RMQ meets our scalability and performance requirements effectively.

5. **Compatibility and Familiarity**:
   - Our development team is already familiar with RabbitMQ, its APIs, configuration, and management tools. This familiarity reduces learning curve, accelerates development, and ensures smoother integration with existing components.

6. **Ecosystem and Tooling**:
   - RabbitMQ's ecosystem includes a range of plugins, monitoring tools, management interfaces, and integrations with other services. These tools and resources enhance our operational capabilities, monitoring, and management of message queues.

## Consequences:
### Pros:
- Chosen message broker (RabbitMQ) offers maturity, community support, integration flexibility, feature-rich capabilities, scalability, and performance aligned with Fishy Watch system requirements.
- Familiarity with RabbitMQ among the development team streamlines development, integration, and maintenance efforts.
- RabbitMQ's ecosystem, tooling, and plugin support enhance operational capabilities and monitoring of message queues.

### Cons:
- While RabbitMQ meets our current requirements, ongoing monitoring, tuning, and optimization may be necessary to ensure optimal performance and scalability as system demands evolve.
- Dependency on RabbitMQ's ecosystem and compatibility with future system upgrades and enhancements need to be managed effectively.
