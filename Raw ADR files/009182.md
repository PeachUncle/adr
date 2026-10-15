# ADR 0006: Implement a SAGA Orchestrator

## Context:
In the current microservices architecture, product reservation and payment processes are distributed across multiple services. 
This distribution can lead to data inconsistencies and complicate coordination between services, especially when partial failures occur during reservation or payment.


## Decision:
We will implement a microservice that acts as a centralized orchestrator for reservation and payment operations. This microservice will use Kafka for inter-service communication and apply the following architectural patterns:
- **SAGA (Orchestration)** Manage distributed transactions as a sequence of local transactions, with the ability to execute compensating transactions in case of failure. This ensures eventual consistency across services.

## Rationale:
Centralizing orchestration allows us to manage the flow of reservations and payments in a single place, making it easier to handle compensations and failures. 
By using CQRS, we can scale reads and writes independently, which is crucial for high-throughput systems. 
Kafka provides a robust event-driven backbone that ensures asynchronous communication and traceability.


## Consequences:
### Positive
- **Centralized coordination** Simplifies transaction management and compensations.
- **Improved scalability** CQRS allows independent scaling of read and write operations.
- **Eventual consistency** SAGA ensures that even if partial failures occur, the system eventually reaches a consistent state.
- **Auditability and traceability** Event storage enables full auditing and reconstruction of system state.

### Negative
- **Added complexity** Implementing SAGA and CQRS increases system complexity, requiring careful management of events and read/write model consistency.
- **Event management overhead** Handling multiple events and transactions may increase load on Kafka, especially under high traffic.
- **Kafka dependency** System reliability depends on Kafka availability and performance, requiring robust infrastructure and effective message handling.