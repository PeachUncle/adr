# ADR: Adoption of RabbitMQ for Logger Service and API Gateway Communication

## Description

This document outlines the decision to adopt RabbitMQ as the messaging broker for facilitating communication between the Logger Service and the API Gateway. 

## Context

Our system requires a reliable and asynchronous communication mechanism between the Logger Service and the API Gateway. The decision-making team recognizes the need for a messaging broker to enhance decoupling, scalability, and fault tolerance in this communication flow.

## Decision

After thorough consideration, the decision has been made to adopt RabbitMQ as the messaging broker for communication between the Logger Service and the API Gateway.

## Rationale

1. **Asynchronous Communication:**
   - RabbitMQ supports asynchronous messaging, allowing the Logger Service to publish log events without blocking the API Gateway, leading to improved responsiveness.

2. **Decoupling of Services:**
   - Using RabbitMQ decouples the Logger Service and the API Gateway, enabling them to evolve independently without direct dependencies on each other's implementation details.

3. **Fault Tolerance:**
   - RabbitMQ provides features such as message persistence and high availability, enhancing fault tolerance and ensuring that log events are not lost in the case of failures.

4. **Scalability:**
   - RabbitMQ's support for distributed message queues allows for scalable communication, accommodating increased load and ensuring reliable delivery of log events.

5. **Flexible Routing:**
   - RabbitMQ supports flexible routing and message filtering through exchanges and queues, allowing for targeted delivery of log events to specific components.

6. **Maintainability:**
   - RabbitMQ simplifies maintenance by providing a reliable and centralized messaging solution, reducing the complexity associated with direct communication between services.

## Status

Accepted

## Consequences

While adopting RabbitMQ brings numerous benefits, it's important to consider potential consequences:

1. **Learning Curve:**
   - The adoption of RabbitMQ may require teams to familiarize themselves with messaging concepts and RabbitMQ-specific configurations.

2. **Operational Overhead:**
   - Proper monitoring and management of RabbitMQ instances are crucial to ensure optimal performance and availability. Operational overhead should be considered.

3. **Message Ordering:**
   - RabbitMQ does not guarantee the order of message delivery, which may impact scenarios where log events need to be processed in a specific sequence.

## Conclusion

The decision to adopt RabbitMQ for communication between the Logger Service and the API Gateway is accepted, recognizing its potential to enhance the reliability, scalability, and decoupling of the communication flow. The team will actively manage the identified consequences and invest in necessary training to ensure a successful integration of RabbitMQ into our system.