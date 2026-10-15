# ADR-002: Kafka Message Format Strategy

## Status
✅ **ACCEPTED** - Implemented in `services/data_collector/`

## Context

The system requires a standardized message format for Kafka topics to ensure reliable data processing across microservices. Message format affects serialization, schema evolution, and system interoperability.

## Decision

Use JSON serialization with standardized message structure based on the data normalization patterns established in the data collector service.

## Rationale

### JSON Serialization Benefits
- **Human Readable**: Easy debugging and monitoring
- **Language Agnostic**: Compatible with multiple programming languages
- **Existing Implementation**: Already used in `StockKafkaProducer`
- **Tooling Support**: Extensive ecosystem and debugging tools

### Standardized Structure
Based on `DataNormalizer.normalize_price_data()` implementation:
```python
@staticmethod
def normalize_price_data(price_data) -> Dict[str, Any]:
    return {
        'symbol': price_data.symbol,
        'time': price_data.time.isoformat(),
        'open': float(price_data.open),
        'high': float(price_data.high),
        'low': float(price_data.low),
        'close': float(price_data.close),
        'volume': int(price_data.volume),
        'collected_at': datetime.utcnow().isoformat()
    }
```

## Implementation Details

### Current Message Format ✅
```json
{
  "symbol": "VCB",
  "time": "2024-12-04T09:15:00+07:00",
  "open": 85.5,
  "high": 86.2,
  "low": 85.0,
  "close": 86.0,
  "volume": 1250000,
  "collected_at": "2024-12-04T09:15:30.123456"
}
```

### Serialization Configuration ✅
```python
# From services/data_collector/src/producers/kafka_producer.py
self.producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)
```

### Message Key Strategy ✅
- **Key**: Stock symbol (e.g., "VCB", "VNM")
- **Purpose**: Ensure messages for same symbol go to same partition
- **Benefits**: Ordered processing per symbol, even load distribution

## Message Schema Standards

### Required Fields
All messages must include:
- `symbol`: Stock identifier
- `timestamp`: Event timestamp in ISO 8601 format
- `collected_at`: Processing timestamp for tracking

### Data Type Conventions
- **Timestamps**: ISO 8601 strings with timezone
- **Prices**: Float with appropriate precision
- **Volumes**: Integer values
- **Symbols**: Uppercase string identifiers

### Planned Message Types 📋

#### News Messages
```json
{
  "news_id": "hash_abc123",
  "symbol": "VCB",
  "title": "Company announcement",
  "content": "Full article content",
  "published_at": "2024-12-04T08:30:00+07:00",
  "collected_at": "2024-12-04T09:00:00+07:00",
  "source": "VnExpress"
}
```

#### Analysis Trigger Messages
```json
{
  "trigger_id": "uuid-123",
  "symbol": "VCB",
  "trigger_type": "price_update",
  "timestamp": "2024-12-04T09:15:00+07:00",
  "metadata": {
    "data_count": 1,
    "priority": "normal"
  }
}
```

## Consequences

### Positive
- **Simplicity**: Easy to implement and debug
- **Compatibility**: Works with existing infrastructure
- **Flexibility**: Schema can evolve without breaking changes
- **Debugging**: Human-readable message content

### Negative
- **Size Overhead**: JSON is verbose compared to binary formats
- **Performance**: Slower serialization/deserialization than binary
- **Schema Evolution**: No built-in schema validation

## Alternatives Considered

### Avro Serialization
- **Pros**: Schema evolution, compact size, strong typing
- **Cons**: Additional complexity, schema registry required
- **Decision**: Consider for future optimization

### Protocol Buffers
- **Pros**: Compact, fast, strong typing
- **Cons**: Not human-readable, requires code generation
- **Decision**: Rejected for initial implementation

### MessagePack
- **Pros**: Compact binary format, JSON-compatible
- **Cons**: Less tooling support, debugging difficulty
- **Decision**: Rejected for complexity

## Migration Strategy

### Phase 1: JSON Foundation ✅
- Implement JSON serialization
- Establish message structure standards
- Build producer/consumer patterns

### Phase 2: Schema Validation 📋
```python
# Add JSON schema validation
import jsonschema

price_schema = {
    "type": "object",
    "required": ["symbol", "time", "open", "high", "low", "close", "volume"],
    "properties": {
        "symbol": {"type": "string"},
        "time": {"type": "string", "format": "date-time"},
        "open": {"type": "number"},
        "high": {"type": "number"},
        "low": {"type": "number"},
        "close": {"type": "number"},
        "volume": {"type": "integer", "minimum": 0}
    }
}
```

### Phase 3: Performance Optimization 📋
- Evaluate Avro for high-volume topics
- Implement compression strategies
- Consider binary formats for internal services

## Monitoring and Validation

### Message Quality Metrics
- **Serialization Errors**: Track failed message serialization
- **Schema Violations**: Monitor invalid message formats
- **Size Distribution**: Track message size patterns
- **Processing Latency**: Measure serialization/deserialization time

### Validation Implementation 📋
```python
class MessageValidator:
    def __init__(self, schema: dict):
        self.schema = schema
    
    def validate_message(self, message: dict) -> bool:
        try:
            jsonschema.validate(message, self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Message validation failed: {e}")
            return False
```

## Error Handling

### Serialization Errors ✅
```python
# From actual implementation
try:
    future = self.producer.send(topic, key=symbol, value=data)
    future.get(timeout=10)
except Exception as e:
    logger.error(f"Failed to send price data for {symbol}: {e}")
    raise
```

### Planned Error Recovery 📋
- **Invalid Messages**: Send to dead letter queue
- **Serialization Failures**: Log and retry with fallback format
- **Schema Evolution**: Maintain backward compatibility

## Future Considerations

### Schema Registry Integration
- Implement Confluent Schema Registry
- Version management for message schemas
- Automatic schema evolution validation

### Performance Optimization
- Benchmark JSON vs. Avro performance
- Implement message compression
- Consider batch serialization for high-volume topics

### Multi-Format Support
- Support multiple serialization formats per topic
- Content-type headers for format identification
- Gradual migration between formats