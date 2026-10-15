# ADR-010: Idempotency Strategy for Message Processing

## Status
**Proposed** - 2025-01-15

## Context

The Online Communities platform processes various types of messages through event-driven architecture, including notifications, data ingestion, and system events. To ensure reliable processing and prevent duplicate operations, we need a robust idempotency strategy that can handle message retries, system failures, and distributed processing scenarios.

## Decision

We will implement a comprehensive idempotency strategy using:

- **Message Processing Records** for tracking message state and processing history
- **Correlation IDs** for message identification and deduplication
- **Database-based Idempotency Service** for reliable state management
- **Dead Letter Queue Handling** for failed message processing
- **Exponential Backoff** for retry mechanisms

## Architecture Components

### 1. Message Processing Record
- **Purpose**: Track message processing state and history
- **Storage**: Database table with comprehensive metadata
- **Key Fields**: MessageId, Status, AttemptCount, ProcessingDuration, ErrorDetails

### 2. Idempotency Service
- **Purpose**: Central service for idempotency checking and management
- **Responsibilities**:
  - Message deduplication
  - Processing state tracking
  - Retry logic coordination
  - Dead letter queue management

### 3. Dead Letter Queue Handler
- **Purpose**: Process failed messages and manage retry logic
- **Responsibilities**:
  - Failed message analysis
  - Retry decision making
  - Manual intervention support
  - Statistics and reporting

### 4. Common Data Model (CDM) Ingestion
- **Purpose**: Smart ingestion of external data with validation
- **Responsibilities**:
  - Data validation and transformation
  - Duplicate detection
  - Schema validation
  - Quality scoring

## Implementation Details

### Message Processing Record

```csharp
public class MessageProcessingRecord : BaseEntity
{
    public Guid TenantId { get; set; }
    public string MessageId { get; set; }
    public string MessageType { get; set; }
    public string SourceTopic { get; set; }
    public ProcessingStatus Status { get; set; }
    public int AttemptCount { get; set; }
    public int MaxAttempts { get; set; }
    public DateTime ReceivedAt { get; set; }
    public DateTime? ProcessingStartedAt { get; set; }
    public DateTime? ProcessingCompletedAt { get; set; }
    public long? ProcessingDurationMs { get; set; }
    public string? ErrorMessage { get; set; }
    public string? ExceptionDetails { get; set; }
    public string? MessageMetadata { get; set; }
    public string? MessageHash { get; set; }
    public bool IsDeadLettered { get; set; }
    public DateTime? DeadLetteredAt { get; set; }
    public string? DeadLetterReason { get; set; }
    public int RetryDelaySeconds { get; set; }
    public DateTime? NextRetryAt { get; set; }
    public string? ProcessingResult { get; set; }
    public MessagePriority Priority { get; set; }
}
```

### Idempotency Service Interface

```csharp
public interface IIdempotencyService
{
    Task<bool> IsMessageProcessedAsync(string messageId, Guid tenantId);
    Task<MessageProcessingRecord?> GetProcessingRecordAsync(string messageId, Guid tenantId);
    Task<MessageProcessingRecord> CreateProcessingRecordAsync(string messageId, string messageType, 
        string sourceTopic, Guid tenantId, string? messageMetadata = null);
    Task<bool> UpdateProcessingStatusAsync(string messageId, Guid tenantId, ProcessingStatus status, 
        string? errorMessage = null, string? exceptionDetails = null);
    Task<bool> MarkAsDeadLetteredAsync(string messageId, Guid tenantId, string reason);
    Task<IEnumerable<MessageProcessingRecord>> GetMessagesReadyForRetryAsync(Guid tenantId, int maxCount = 100);
    Task<DateTime> CalculateNextRetryTime(int attemptCount, int baseDelaySeconds = 30, int maxDelaySeconds = 3600);
}
```

### Processing Status Enum

```csharp
public enum ProcessingStatus
{
    Pending = 0,
    Processing = 1,
    Completed = 2,
    Failed = 3,
    DeadLettered = 4,
    Cancelled = 5
}
```

## Idempotency Patterns

### 1. Message Deduplication
- **Correlation ID**: Unique identifier for each message
- **Message Hash**: Content-based deduplication
- **Database Check**: Query processing records before processing
- **Atomic Operations**: Database transactions for consistency

### 2. State Tracking
- **Processing States**: Clear state transitions
- **Attempt Counting**: Track retry attempts
- **Timing Information**: Processing duration and timestamps
- **Error Details**: Comprehensive error information

### 3. Retry Logic
- **Exponential Backoff**: Increasing delays between retries
- **Maximum Attempts**: Configurable retry limits
- **Jitter**: Random delay variation to prevent thundering herd
- **Circuit Breaker**: Stop retrying after consecutive failures

### 4. Dead Letter Queue
- **Failure Analysis**: Analyze failure reasons
- **Manual Review**: Human intervention for complex failures
- **Retry Decision**: Determine if retry is appropriate
- **Permanent Failure**: Mark messages as permanently failed

## CDM Ingestion Strategy

### Smart Ingestion Process
1. **Data Validation**: Validate against CDM schema
2. **Duplicate Detection**: Check for existing data
3. **Quality Scoring**: Assess data quality
4. **Transformation**: Convert to standardized format
5. **Storage**: Store processed data
6. **Audit**: Log ingestion results

### Data Quality Metrics
- **Completeness**: Required fields present
- **Accuracy**: Data format and value validation
- **Consistency**: Cross-field validation
- **Timeliness**: Data freshness assessment
- **Uniqueness**: Duplicate detection

### Validation Framework
```csharp
public class ValidationResult
{
    public bool IsValid { get; set; }
    public List<string> Errors { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
    public int QualityScore { get; set; }
    public string SchemaVersion { get; set; }
}
```

## Configuration

### Idempotency Configuration
```json
{
  "Idempotency": {
    "MaxRetryAttempts": 3,
    "BaseRetryDelaySeconds": 30,
    "MaxRetryDelaySeconds": 3600,
    "RetentionDays": 30,
    "EnableDeadLetterQueue": true,
    "DeadLetterRetentionDays": 90
  }
}
```

### CDM Configuration
```json
{
  "CDM": {
    "DefaultSchemaVersion": "1.0",
    "ValidationEnabled": true,
    "QualityThreshold": 80,
    "DuplicateDetectionEnabled": true,
    "TransformationEnabled": true,
    "AuditEnabled": true
  }
}
```

## Benefits

### Reliability
- **Duplicate Prevention**: No duplicate processing
- **State Consistency**: Reliable state tracking
- **Error Recovery**: Comprehensive error handling
- **Audit Trail**: Complete processing history

### Scalability
- **Distributed Processing**: Multiple processor instances
- **Load Distribution**: Even workload distribution
- **Horizontal Scaling**: Add more processors as needed
- **Performance Monitoring**: Track processing performance

### Maintainability
- **Clear State Management**: Explicit state transitions
- **Comprehensive Logging**: Detailed processing logs
- **Error Analysis**: Rich error information
- **Manual Intervention**: Support for manual processing

### Flexibility
- **Configurable Retry**: Adjustable retry policies
- **Multiple Message Types**: Support for various message types
- **Custom Processing**: Extensible processing logic
- **Quality Metrics**: Data quality assessment

## Trade-offs

### Complexity
- **Additional Infrastructure**: Database and service complexity
- **State Management**: Complex state tracking logic
- **Error Handling**: More error scenarios to handle
- **Monitoring**: Additional monitoring requirements

### Performance
- **Database Queries**: Additional database operations
- **Processing Overhead**: Idempotency checking overhead
- **Storage Requirements**: Message processing records storage
- **Network Latency**: Additional service calls

### Cost
- **Database Storage**: Processing records storage costs
- **Compute Resources**: Additional service instances
- **Monitoring**: Enhanced monitoring and alerting
- **Development Time**: Implementation complexity

## Alternatives Considered

### 1. In-Memory Idempotency
- **Pros**: Fast, simple implementation
- **Cons**: Not persistent, single instance only, memory limitations

### 2. Redis-Based Idempotency
- **Pros**: Fast, distributed, TTL support
- **Cons**: Additional infrastructure, memory limitations, persistence concerns

### 3. Message Broker Idempotency
- **Pros**: Built-in deduplication, no additional storage
- **Cons**: Limited to message broker capabilities, vendor lock-in

### 4. Database Constraints
- **Pros**: Simple, database-enforced
- **Cons**: Limited flexibility, error handling complexity

## Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Create MessageProcessingRecord entity and database table
- [ ] Implement IIdempotencyService interface
- [ ] Create IdempotencyService with basic operations
- [ ] Add database migrations and indexes

### Phase 2: Message Processing
- [ ] Integrate idempotency checking in message processors
- [ ] Implement retry logic with exponential backoff
- [ ] Add dead letter queue handling
- [ ] Create message processing commands and handlers

### Phase 3: CDM Ingestion
- [ ] Implement CDM data validation framework
- [ ] Create data transformation services
- [ ] Add quality scoring and assessment
- [ ] Implement duplicate detection logic

### Phase 4: Monitoring and Management
- [ ] Add comprehensive logging and monitoring
- [ ] Create dead letter queue management interface
- [ ] Implement statistics and reporting
- [ ] Add alerting for processing failures

### Phase 5: Advanced Features
- [ ] Add message prioritization
- [ ] Implement circuit breaker pattern
- [ ] Add batch processing capabilities
- [ ] Create automated cleanup processes

## Monitoring and Observability

### Key Metrics
- **Processing Rate**: Messages processed per minute
- **Success Rate**: Percentage of successful processing
- **Retry Rate**: Percentage of messages requiring retries
- **Dead Letter Rate**: Percentage of messages sent to DLQ
- **Processing Latency**: Average processing time

### Alerts
- **High Failure Rate**: >10% processing failures
- **Dead Letter Backlog**: >100 messages in DLQ
- **Processing Delays**: Messages older than 1 hour
- **Service Unavailability**: Idempotency service down

### Dashboards
- **Processing Volume**: Daily/weekly processing counts
- **Error Analysis**: Failure reasons and patterns
- **Performance Metrics**: Processing times and throughput
- **System Health**: Service availability and performance

## Security Considerations

### Data Protection
- **Encryption**: Sensitive data encryption
- **Access Control**: Role-based access to processing records
- **Audit Logging**: Complete audit trail
- **Data Retention**: Configurable data retention policies

### Message Security
- **Message Validation**: Input validation and sanitization
- **Correlation ID Security**: Secure correlation ID generation
- **Error Information**: Sanitized error messages
- **Access Logging**: Message access logging

## Compliance

### GDPR
- **Data Minimization**: Only store necessary data
- **Right to Erasure**: Delete user-related processing records
- **Data Portability**: Export processing history
- **Consent Management**: Track data processing consent

### SOC 2
- **Access Controls**: Role-based access to processing data
- **Audit Logging**: Complete audit trail
- **Data Encryption**: Encryption in transit and at rest
- **Incident Response**: Processing failure incident procedures

## Future Considerations

### Scalability
- **Partitioning**: Database partitioning for large datasets
- **Caching**: Redis caching for frequently accessed data
- **Sharding**: Horizontal database sharding
- **Event Sourcing**: Event sourcing for audit trails

### Features
- **Machine Learning**: ML-based failure prediction
- **Automated Recovery**: Self-healing processing failures
- **Advanced Analytics**: Processing pattern analysis
- **Integration**: Third-party system integration

### Performance
- **Async Processing**: Asynchronous processing patterns
- **Batch Processing**: Batch message processing
- **Streaming**: Real-time message processing
- **Optimization**: Performance optimization techniques

## Conclusion

The idempotency strategy provides a robust foundation for reliable message processing in the Online Communities platform. While it introduces additional complexity and infrastructure requirements, the benefits of reliability, consistency, and maintainability justify the investment. The phased implementation approach allows for incremental delivery and validation of the solution.

## References

- [Idempotency Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer)
- [Dead Letter Queue Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- [Exponential Backoff](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Event Sourcing](https://docs.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
