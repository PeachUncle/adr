# ADR 007: Configurable Message Broker Implementation

## Status

Accepted

## Date

2025-03-19

## Context

The system currently uses RabbitMQ as the message broker for communication between agents. While RabbitMQ is a robust solution for production environments, it introduces complexity during development and testing:

1. Developers need to set up and maintain a RabbitMQ instance locally
2. Integration tests require a running RabbitMQ server or complex mocking
3. Running multiple agents within a single process for testing or development becomes challenging

A simpler in-memory message broker implementation would facilitate development and testing workflows while maintaining the same interface as the RabbitMQ implementation.

## Decision

We will implement a configurable message broker system with the following components:

1. An abstract `MessageBroker` interface that defines the contract for all broker implementations
2. A concrete `RabbitMQBroker` implementation for production use
3. A new `InMemoryBroker` implementation for development and testing 
4. A `MessageBrokerFactory` that creates the appropriate broker implementation based on configuration

The configuration will determine which broker implementation to use, allowing for easy switching between implementations based on the environment (development, testing, production).

## Consequences

### Positive

1. Simplifies development and testing workflows by eliminating external dependencies
2. Enables running multiple agents within a single process for testing or development
3. Maintains the same interface regardless of the broker implementation, ensuring consistent behavior
4. Follows DDD principles by using interfaces and implementations in separate layers
5. Supports the Dependency Inversion Principle by depending on abstractions rather than concrete implementations

### Negative

1. Adds additional code to maintain
2. The in-memory implementation may not precisely mimic all characteristics of a distributed message broker like RabbitMQ
3. Care must be taken to maintain feature parity between implementations 

### Note on Runtime Behavior Differences

While both implementations satisfy the same interface, there are some behavioral differences to be aware of:

1. The in-memory broker processes messages synchronously within the same process, while RabbitMQ processes messages asynchronously across potentially multiple processes
2. Error handling: In-memory broker failures directly affect the calling process, while RabbitMQ failures might be isolated
3. Message persistence: RabbitMQ can provide message persistence across restarts, which the in-memory implementation cannot

## Implementation

The implementation maintains the current Domain-Driven Design principles:

1. The abstract `MessageBroker` interface is defined in the domain layer
2. The concrete implementations (`RabbitMQBroker` and `InMemoryBroker`) are in the infrastructure layer
3. The `MessageBrokerFactory` provides a simple way to create the appropriate implementation

This structure allows the application layer to depend only on the abstract interface without knowing the concrete implementation details. 