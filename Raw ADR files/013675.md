# ADR-010: Message Consumer Abstraction for Event Hubs and Kafka

## Status
Accepted

## Context
The Payments Ingestion system needs to consume messages from event streaming platforms. Initially designed for Azure Event Hubs, but requirements expanded to support:
- Azure Event Hubs (primary)
- Apache Kafka (alternative/additional)
- Future: Other messaging systems

Different messaging systems have:
- Different SDKs and APIs
- Different connection models
- Different batch processing approaches
- Different acknowledgment mechanisms
- Different checkpointing strategies

We need an abstraction that:
- Provides consistent interface across messaging systems
- Enables easy switching between providers
- Supports testing without actual messaging infrastructure
- Maintains type safety and IDE support
- Allows provider-specific optimizations

## Decision
We will implement a **MessageConsumer abstraction** using the Abstract Base Class (ABC) pattern:

1. **Base Interface**: `MessageConsumer` ABC
   - Defines common operations: connect, disconnect, consume_batch, acknowledge_batch, checkpoint
   - Enforces consistent interface across implementations
   - Supports type hints and IDE autocomplete

2. **Concrete Implementations**:
   - `EventHubsConsumer`: Azure Event Hubs implementation
   - `KafkaConsumer`: Apache Kafka implementation
   - Future: Additional implementations as needed

3. **Message Data Structures**:
   - `Message`: Immutable message wrapper with body, properties, metadata
   - `MessageBatch`: Collection of messages with helper methods
   - Provider-agnostic data structures

4. **Factory Pattern** (future):
   - Factory function to create appropriate consumer based on configuration
   - Enables runtime selection of messaging provider

## Consequences

### Positive
- **Flexibility**: Easy to switch between Event Hubs and Kafka
- **Testability**: Can mock MessageConsumer interface for testing
- **Consistency**: Same code works with different providers
- **Extensibility**: Easy to add new messaging providers
- **Type Safety**: ABC enforces interface compliance
- **Code Reuse**: Common logic can be shared across implementations
- **Provider Optimization**: Each implementation can optimize for its provider

### Negative
- **Abstraction Overhead**: Additional layer adds complexity
- **Provider Differences**: Some provider-specific features may be hard to abstract
- **Learning Curve**: Developers need to understand abstraction
- **Maintenance**: Must maintain multiple implementations
- **Performance**: Abstraction layer may add slight overhead

## Alternatives Considered

### Provider-Specific Code Only
**Pros**: Direct use of provider APIs, no abstraction overhead
**Cons**: Code duplication, harder to switch providers, more testing complexity
**Reason rejected**: Need flexibility and code reuse

### Adapter Pattern
**Pros**: Wraps existing SDKs, less code to write
**Cons**: May not provide clean abstraction, wrapper complexity
**Reason rejected**: ABC provides cleaner interface definition

### Strategy Pattern with Dependency Injection
**Pros**: Very flexible, testable
**Cons**: More complex, may be overkill
**Reason rejected**: ABC pattern simpler and sufficient

### Single Implementation (Event Hubs Only)
**Pros**: Simplest, no abstraction needed
**Cons**: No flexibility, vendor lock-in
**Reason rejected**: Requirements specify Kafka support needed

## Implementation Details

### Base Interface
```python
class MessageConsumer(ABC):
    @abstractmethod
    def connect(self) -> None: ...
    
    @abstractmethod
    def consume_batch(
        self, 
        max_messages: int, 
        timeout: float
    ) -> Optional[MessageBatch]: ...
    
    @abstractmethod
    def acknowledge_batch(
        self, 
        batch: MessageBatch
    ) -> None: ...
```

### Message Structures
- `Message`: Immutable dataclass with body, properties, partition info
- `MessageBatch`: Collection with iteration, length, helper methods
- Provider-agnostic, works with any messaging system

### Implementation Pattern
- Each consumer implements all abstract methods
- Provider-specific logic encapsulated in implementation
- Common error handling and retry logic can be shared

## References
- Source: `src/function_app/consumer/base.py`
- Source: `src/function_app/consumer/event_hubs.py`
- Source: `src/function_app/consumer/kafka.py`
- Source: `src/function_app/messaging/message.py`

