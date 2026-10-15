# Decision to Adopt Event-Driven Design for API Events

## Status

**Proposed**

## Context

In modern distributed systems, event-driven architectures enable asynchronous communication and decoupling between components. By adopting an event-driven design, this API can emit events for significant domain actions, such as customer creation, updates, or deletions. These events can be consumed by external systems, ensuring scalability and flexibility in how the API interacts with downstream services.

This architecture introduces the concept of **eventual consistency**, ensuring external systems remain up-to-date without requiring synchronous communication. However, when the external system is unable to accept events, requests to the API that produce events should fail to maintain data integrity and reliability.

For example, if a customer creation event cannot be delivered to the external system, the API should respond with an error, preventing incomplete data propagation.

## Decision

The API will adopt an event-driven design for all significant domain actions, ensuring:

1. Events are published for domain changes, making them available to external systems.
2. Eventual consistency is achieved through asynchronous processing.
3. Requests producing events fail when the external system cannot accept them, ensuring integrity.

### Event Workflow

1. **Domain Action**: A client initiates an action (e.g., creating a customer).
2. **Event Publication**: The API publishes an event (e.g., `CustomerCreated`) to a message broker.
3. **External System Consumption**: Downstream systems consume the event and update their state.
4. **Acknowledgment**: The API confirms the action only if the event is successfully published.

### Example Event

```json
{
  "event_type": "CustomerCreated",
  "timestamp": "2024-12-17T12:34:56Z",
  "data": {
    "customer_id": "1234",
    "full_name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

### Eventual Consistency

External systems are updated asynchronously, meaning:

1. The API ensures changes are reflected in its own domain immediately.
2. External systems receive and process events at their own pace.
3. Any delay in event propagation is acceptable as long as the eventual state is consistent.

### Handling Failures

If the external system cannot accept an event (e.g., the message broker is unavailable):

1. The API will reject the originating request (e.g., `POST /customers`) with an appropriate error code (e.g., `503 Service Unavailable`).
2. The error response will include details about the failure to publish the event.
3. This ensures no action is partially completed, maintaining system integrity.

## Consequences

### Benefits

- **Scalability**: Decoupling the API from external systems improves scalability and flexibility.
- **Eventual Consistency**: Ensures external systems remain up-to-date asynchronously.
- **Auditability**: Events provide a clear trail of domain actions.
- **Fault Isolation**: Failures in external systems do not immediately impact API performance, provided event publication succeeds.

### Drawbacks

- **Complexity**: Introduces additional components, such as a message broker, to handle events.
- **Latency**: External systems may not reflect changes immediately due to asynchronous processing.
- **Error Handling**: Requires robust handling of failures in event publication.

## Alternatives Considered

1. **Synchronous Updates to External Systems**:
    - Rejected due to tight coupling and reduced scalability.

2. **No Events, Direct API Integration**:
    - Rejected because it limits flexibility and requires external systems to poll for updates.

3. **Best-Effort Event Publication**:
    - Rejected because it allows incomplete states if events fail to publish.

## Implementation Plan

1. **Message Broker**:
    - Integrate a message broker (e.g., RabbitMQ, Kafka) for event publication.

2. **Event Model**:
    - Define a schema for each event type, including metadata (e.g., event type, timestamp) and payload.

3. **API Modifications**:
    - Update API endpoints to emit events after domain actions.

4. **Error Handling**:
    - Implement robust error handling to reject requests when events fail to publish.

5. **Documentation**:
    - Document the event-driven architecture, including event schemas, workflows, and error responses.

6. **Testing**:
    - Write tests to validate event publication and failure scenarios.

## Conclusion

Adopting an event-driven design for this API enables scalability, flexibility, and eventual consistency for external systems. By ensuring requests fail when events cannot be delivered, the API maintains data integrity while embracing the benefits of asynchronous communication. While this approach introduces complexity, the long-term benefits for reliability and scalability outweigh the drawbacks.
