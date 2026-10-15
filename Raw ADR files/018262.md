# Decision 001: Adoption of Event Bus Architecture

## Status

**Accepted**

---

## Context

Taly’s platform relies heavily on microservices to manage distinct business domains, such as authentication, booking, payments, and notifications. These services need to communicate efficiently and asynchronously to ensure a seamless user experience and maintain platform scalability.

Some of the specific challenges we aim to address include:

- **Decoupling Services**: Ensuring that each microservice can operate independently while still participating in workflows that require collaboration.
- **Scalability**: Handling high throughput of messages without compromising performance.
- **Error Handling**: Managing failures and retries without manual intervention.

---

## Decision

We will adopt an **Event Bus Architecture** to facilitate communication between Taly’s microservices. The event bus will serve as the backbone for all asynchronous inter-service communication.

### Key Features:

- **Message Brokers**: Use RabbitMQ as the primary message broker.
- **Event-Driven Communication**: Services will publish events to the event bus and consume relevant events as needed.
- **Idempotency**: Ensure that event consumers handle duplicate messages gracefully.
- **Retry Mechanism**: Implement retries for failed message deliveries.

---

## Rationale

### Benefits of an Event Bus Architecture:

1. **Decoupling**:

   - Services communicate indirectly via the event bus rather than direct API calls.
   - This allows services to evolve independently.

2. **Scalability**:

   - RabbitMQ supports high message throughput, making it suitable for scaling microservice communication.

3. **Reliability**:

   - The event bus ensures messages are persisted and delivered even if services are temporarily unavailable.

4. **Flexibility**:

   - New services can be added to consume existing events without requiring changes to the event producers.

5. **Observability**:
   - RabbitMQ provides tools to monitor and troubleshoot message flows.

---

## Alternatives Considered

### 1. **Direct API Communication**

- **Pros**:
  - Simple to implement for small-scale systems.
- **Cons**:
  - Strong coupling between services.
  - Increased complexity for workflows involving multiple services.
  - Higher latency due to synchronous calls.

### 2. **Event Streaming with Kafka**

- **Pros**:
  - High throughput and durability.
- **Cons**:
  - Steeper learning curve and operational complexity.
  - Overkill for the current scale of the platform.

---

## Implementation Plan

### 1. **Set Up RabbitMQ**

- Deploy RabbitMQ as a containerized service in the Kubernetes cluster.
- Configure queues for each service (e.g., `auth.events`, `booking.events`).

### 2. **Define Event Contracts**

- Establish a standardized event schema for all microservices to follow.
- Example Event:
  ```json
  {
    "eventType": "booking.created",
    "timestamp": "2025-01-27T12:00:00Z",
    "data": {
      "bookingId": "12345",
      "userId": "67890",
      "companyId": "54321",
      "service": "Haircut",
      "date": "2025-01-30T10:00:00Z"
    }
  }
  ```

### 3. **Update Microservices**

- **Producers**: Modify services to publish events to the RabbitMQ event bus.
- **Consumers**: Update services to listen for and process relevant events.

### 4. **Monitoring and Observability**

- Integrate RabbitMQ monitoring tools to track message throughput and detect issues.
- Implement logging for published and consumed events.

---

## Consequences

### Positive Impacts:

- Reduced service coupling, enabling better maintain
