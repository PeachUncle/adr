# 8. Use RabbitMQ broker for queueing low-priority POST requests

Date: 2023-05-21

## Status

Accepted

## Context

In the context of selecting a message broker for communication between the API Gateway and the Kweeter service in
Kwetter's architecture, we evaluated various options, including Kafka and RabbitMQ. The goal was to choose a message
broker that would effectively support the system's requirements and provide a reliable and scalable communication
channel.

## Decision

After careful evaluation, we decided to use RabbitMQ as the message broker between the API Gateway and the Kweeter
service. The decision was influenced by the following considerations:

- Simplicity and Ease of Use: Kafka is a powerful distributed streaming platform, but it introduces additional complexity,
especially for scenarios that involve long data streams and complex event processing. In contrast, RabbitMQ offers a
simpler and more straightforward messaging model, making it easier to integrate into our architecture and maintain over
time.

- Alignment with Requirements: Kwetter's communication needs primarily involve asynchronous message exchange and
decoupling the API Gateway and the Kweeter service. RabbitMQ fulfills these requirements effectively with its reliable
queuing mechanism and support for asynchronous communication patterns.

- Scalability: While Kafka excels in handling high-volume and continuous data streams, Kwetter's messaging requirements
focus on discrete messages and event-driven communication. RabbitMQ is well-suited for this use case and offers the
scalability needed to handle message processing efficiently.

## Consequences

The decision to use RabbitMQ as the message broker and not Kafka has the following consequences:

- Reduced Complexity: Opting for RabbitMQ over Kafka simplifies the architecture and reduces the learning curve for
developers. The messaging model of RabbitMQ is easier to understand and work with, which accelerates development and
maintenance activities.

- Efficient Communication: RabbitMQ's queuing mechanism ensures reliable message delivery and allows for asynchronous
communication between the API Gateway and the Kweeter service. This enables the services to operate independently,
enhances fault tolerance, and promotes scalability.

- Potential Performance Optimization: RabbitMQ's lightweight messaging model, combined with its efficient handling of
discrete messages, can lead to better performance in scenarios where the message size and processing requirements align
with RabbitMQ's strengths.

- Limited Support for Long Data Streams: Choosing RabbitMQ may limit the system's ability to handle long data streams
efficiently. However, as Kwetter's communication requirements focus on discrete messages, this limitation is acceptable
and outweighed by the simplicity and ease of use provided by RabbitMQ.

- Maintainability and Support: RabbitMQ's maturity, extensive documentation, and strong community support contribute to
its long-term maintainability and ensure access to resources for troubleshooting and guidance.