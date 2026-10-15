# ADR-006: Asynchronous Workflow Integration

## Status

Accepted

## Date

2023-05-10

## Context

The AI-driven development pipeline requires integration between different bounded contexts (Human Interaction, Task Management, Product Definition, and Orchestration) to implement the product refinement workflow. This integration must support:

1. Asynchronous communication between contexts to enable parallel processing
2. Reliable message delivery with error handling and recovery
3. Monitoring of workflow progress and detection of stalled workflows
4. Scalable agent deployment with multiple instances processing tasks concurrently
5. Consistent error handling across the system
6. Comprehensive logging for troubleshooting and analysis

The system must handle various states and transitions as tasks move through the workflow lifecycle, and must support both automated processing and human validation checkpoints.

## Decision

We will implement an event-driven, asynchronous workflow integration with the following components:

1. **Message Queue**: A central message broker for event and command exchange between bounded contexts, with both in-memory implementation for testing and RabbitMQ implementation for production.

2. **Domain Events and Commands**: Strongly typed events and commands that flow through the message queue, carrying all necessary information for processing.

3. **Task Scanning Service**: A service in the Orchestration Context that periodically scans for tasks needing attention and initiates appropriate state transitions.

4. **Task Polling Service**: A service in the Product Definition Context that polls for assigned tasks and processes them using the Product Manager Agent.

5. **Error Handling and Recovery**: A robust error handling mechanism with retry capability and dead letter queue for unprocessable messages.

6. **Event Monitoring and Logging**: A comprehensive monitoring system to track events, commands, and workflow progress, with alerts for stalled workflows.

The integration will use the Decorator pattern to add monitoring capabilities to the message queue without modifying its core interface, and will follow the Factory pattern for creating components with appropriate configurations.

## Consequences

### Positive

- Asynchronous processing enables parallel execution and better scalability
- Bounded contexts remain isolated, communicating only through message queue
- Comprehensive monitoring and logging improves observability
- Robust error handling increases system reliability
- Modular design allows for easy testing and component replacement
- Support for both in-memory and RabbitMQ implementations enables testing and production deployment

### Negative

- Increased complexity compared to synchronous processing
- Debugging asynchronous workflows can be challenging
- State management across distributed components requires careful coordination
- Additional overhead from message serialization/deserialization
- Need to handle partial failures and ensure idempotency

## Implementation Details

### Message Queue Interface

```python
class MessageQueue(ABC):
    @abstractmethod
    def publish_event(self, event_type: str, payload: Dict[str, Any], routing_key: Optional[str] = None) -> None:
        pass
    
    @abstractmethod
    def publish_command(self, command_type: str, payload: Dict[str, Any], routing_key: Optional[str] = None) -> None:
        pass
    
    @abstractmethod
    def subscribe_to_events(self, event_types: List[str], callback: Callable[[str, Dict[str, Any]], None]) -> None:
        pass
    
    @abstractmethod
    def subscribe_to_commands(self, command_types: List[str], callback: Callable[[str, Dict[str, Any]], None]) -> None:
        pass
```

### Task Scanning Service

The Task Scanning Service runs periodically in the background and performs the following operations:

1. Scans for NEW tasks and transitions them to REQUEST_VALIDATION, assigning them to the Product Manager agent pool
2. Scans for CLARIFICATION_NEEDED tasks and sends notifications to users
3. Scans for PRD_VALIDATION tasks and sends notifications to users for approval

### Task Polling Service

The Task Polling Service runs in the background and:

1. Polls for tasks assigned to the Product Manager agent pool
2. Selects the highest priority task for processing
3. Delegates task processing to the Product Manager Agent
4. Handles the result, either requesting clarification or storing the PRD and updating task status

### Error Handling

Error handling includes:

1. Retry mechanism with exponential backoff
2. Dead letter queue for unprocessable messages
3. Error classification into retryable and non-retryable errors
4. Logging of all errors with context information

### Event Monitoring

Event monitoring provides:

1. Tracking of all events and commands flowing through the system
2. Detection of stalled workflows based on configurable thresholds
3. Alerts for anomalies such as stalled workflows or error patterns
4. Comprehensive logging for debugging and analysis

## Alternatives Considered

### Synchronous Processing

We considered implementing synchronous processing with direct method calls between contexts, but this would limit scalability and parallel processing capabilities.

### Shared Database for Coordination

Using a shared database for coordination between contexts would violate bounded context isolation and introduce tight coupling.

### Workflow Engine

Implementing a dedicated workflow engine would provide more features but would introduce significant complexity and overhead for the current requirements.

## References

- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Domain-Driven Design](https://domainlanguage.com/ddd/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html) 