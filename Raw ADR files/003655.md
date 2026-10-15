# ADR-007: Asynchronous Message Processing Pattern

## Status
Accepted

## Context
The SMS messaging platform needs to handle message processing in a way that provides:

- **Scalability**: Handle high volumes of messages without blocking API responses
- **Reliability**: Ensure messages are not lost during processing
- **Responsiveness**: Provide immediate response to API clients
- **Fault Tolerance**: Handle failures gracefully with retry mechanisms
- **Monitoring**: Track message processing status and performance
- **Decoupling**: Separate message reception from message processing

Synchronous processing would block API responses until SMS delivery is complete, leading to poor user experience and potential timeouts. Direct coupling between API and SMS delivery would create tight dependencies and limit scalability.

## Decision
We will implement an asynchronous message processing pattern using the following components:

1. **Message Queue**: Apache Kafka for reliable message queuing
2. **Producer-Consumer Pattern**: SMS Service produces, Processor Service consumes
3. **Callback Mechanism**: Processor Service notifies SMS Service of completion
4. **Status Tracking**: Database persistence for message status tracking

**Processing Flow**:
```
Client Request → SMS Service → Kafka Queue → Processor Service → Callback → SMS Service
     ↓              ↓                           ↓              ↓
   202 Response   Database                  Processing      Status Update
```

## Consequences

### Positive
- **Immediate Response**: API returns immediately with 202 Accepted
- **High Throughput**: Process thousands of messages concurrently
- **Fault Tolerance**: Messages persist in queue during failures
- **Scalability**: Independent scaling of API and processing components
- **Reliability**: At-least-once delivery guarantees from Kafka
- **Monitoring**: Full visibility into message processing pipeline
- **Loose Coupling**: Services can evolve independently

### Negative
- **Complexity**: More complex than synchronous processing
- **Eventual Consistency**: Status updates are not immediate
- **Debugging Difficulty**: Distributed tracing required for troubleshooting
- **Message Ordering**: Need to handle potential out-of-order processing
- **Duplicate Processing**: Need idempotency handling

### Neutral
- **Operational Overhead**: Need to monitor and maintain message queue
- **Development Complexity**: Asynchronous programming patterns required
- **Testing Complexity**: Need to test async workflows

## Implementation Details

### Message Producer (SMS Service)

**Kafka Producer Configuration**:
```properties
# Quarkus Kafka configuration
mp.messaging.outgoing.sms-requests.connector=smallrye-kafka
mp.messaging.outgoing.sms-requests.topic=sms.requests
mp.messaging.outgoing.sms-requests.value.serializer=io.quarkus.kafka.client.serialization.JsonbSerializer
mp.messaging.outgoing.sms-requests.acks=all
mp.messaging.outgoing.sms-requests.retries=3
```

**Producer Implementation**:
```java
@ApplicationScoped
public class MessageProducer {

    @Channel("sms-requests")
    Emitter<Message> emitter;

    public void sendSmsRequest(Message message) {
        try {
            emitter.send(message);
            LOG.infof("Message %s sent to processing queue", message.getId());
        } catch (Exception e) {
            LOG.errorf(e, "Failed to send message %s to queue", message.getId());
            throw new MessageProcessingException("Failed to queue message", e);
        }
    }
}
```

### Message Consumer (Processor Service)

**Kafka Consumer Configuration**:
```properties
# Consumer configuration
mp.messaging.incoming.sms-requests.connector=smallrye-kafka
mp.messaging.incoming.sms-requests.topic=sms.requests
mp.messaging.incoming.sms-requests.value.deserializer=io.quarkus.kafka.client.serialization.JsonbDeserializer
mp.messaging.incoming.sms-requests.group.id=processor-service
mp.messaging.incoming.sms-requests.auto.offset.reset=earliest
mp.messaging.incoming.sms-requests.enable.auto.commit=false
```

**Consumer Implementation**:
```java
@ApplicationScoped
public class MessageConsumer {

    @Inject
    ProcessingService processingService;

    @Incoming("sms-requests")
    @Acknowledgment(Acknowledgment.Strategy.MANUAL)
    public CompletionStage<Void> processMessage(KafkaRecord<String, Message> record) {
        Message message = record.getPayload();
        
        return processingService.processMessage(message)
            .handle((result, throwable) -> {
                if (throwable != null) {
                    LOG.errorf(throwable, "Failed to process message %s", message.getId());
                    // Could implement retry logic or dead letter queue
                } else {
                    LOG.infof("Successfully processed message %s", message.getId());
                }
                record.ack(); // Acknowledge message
                return null;
            });
    }
}
```

### Processing Service

**Message Processing Logic**:
```java
@ApplicationScoped
public class ProcessingService {

    @Inject
    SmsCallbackClient callbackClient;

    public CompletionStage<Void> processMessage(Message message) {
        return CompletableFuture
            .supplyAsync(() -> simulateMessageProcessing(message))
            .thenCompose(result -> sendDeliveryReport(message, result))
            .exceptionally(throwable -> {
                LOG.errorf(throwable, "Processing failed for message %s", message.getId());
                return sendFailureReport(message, throwable);
            });
    }

    private ProcessingResult simulateMessageProcessing(Message message) {
        // Simulate SMS processing logic
        try {
            Thread.sleep(1000 + random.nextInt(2000)); // 1-3 second delay
            
            // Simulate occasional failures (10% failure rate)
            if (random.nextDouble() < 0.1) {
                throw new ProcessingException("Simulated delivery failure");
            }
            
            return ProcessingResult.success();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new ProcessingException("Processing interrupted", e);
        }
    }
}
```

### Callback Mechanism

**Delivery Report Client**:
```java
@ApplicationScoped
@RegisterRestClient(configKey = "sms-service")
public interface SmsCallbackClient {

    @POST
    @Path("/v1/internal/delivery-report")
    @Consumes(MediaType.APPLICATION_JSON)
    CompletionStage<Response> sendDeliveryReport(DeliveryReportRequest request);
}
```

**Callback Handler (SMS Service)**:
```java
@Path("/v1/internal/delivery-report")
public class InternalController {

    @Inject
    MessageService messageService;

    @POST
    @Transactional
    public Response processDeliveryReport(@Valid DeliveryReportRequest deliveryReport) {
        LOG.infof("Received delivery report for message %s with status %s", 
                 deliveryReport.getMessageId(), deliveryReport.getStatus());

        boolean processed = messageService.processDeliveryReport(deliveryReport);
        
        if (processed) {
            LOG.infof("Delivery report processed successfully for message %s", 
                     deliveryReport.getMessageId());
            return Response.ok().build();
        } else {
            LOG.warnf("Message not found for delivery report: %s", 
                     deliveryReport.getMessageId());
            return Response.status(Response.Status.NOT_FOUND).build();
        }
    }
}
```

### Message Status Tracking

**Status Enum**:
```java
public enum MessageStatus {
    PENDING,    // Message queued for processing
    SENT,       // Message successfully delivered
    FAILED      // Message delivery failed
}
```

**Status Update Logic**:
```java
@Transactional
public boolean processDeliveryReport(DeliveryReportRequest deliveryReport) {
    Optional<Message> messageOpt = messageRepository.findByIdOptional(deliveryReport.getMessageId());
    
    if (messageOpt.isEmpty()) {
        return false;
    }
    
    Message message = messageOpt.get();
    
    switch (deliveryReport.getStatus()) {
        case SENT:
            message.markAsSent();
            meterRegistry.counter("sms_sent_total").increment();
            break;
        case FAILED:
            message.markAsFailed(deliveryReport.getFailureReason());
            meterRegistry.counter("sms_failed_total").increment();
            break;
    }
    
    messageRepository.persist(message);
    return true;
}
```

## Error Handling and Resilience

### Retry Mechanisms

**Producer Retries**:
```properties
# Kafka producer retry configuration
mp.messaging.outgoing.sms-requests.retries=3
mp.messaging.outgoing.sms-requests.retry.backoff.ms=1000
mp.messaging.outgoing.sms-requests.max.in.flight.requests.per.connection=1
```

**Consumer Retry Logic**:
```java
@Retry(maxRetries = 3, delay = 1000, delayUnit = ChronoUnit.MILLIS)
public CompletionStage<Void> processMessageWithRetry(Message message) {
    return processingService.processMessage(message);
}
```

### Circuit Breaker

**Callback Circuit Breaker**:
```java
@CircuitBreaker(requestVolumeThreshold = 4, failureRatio = 0.75, delay = 5000)
public CompletionStage<Response> sendDeliveryReportWithCircuitBreaker(DeliveryReportRequest request) {
    return callbackClient.sendDeliveryReport(request);
}
```

### Dead Letter Queue

**Failed Message Handling**:
```java
@Outgoing("sms-requests-dlq")
public Message<FailedMessage> handleFailedMessage(Message message, Throwable error) {
    FailedMessage failedMessage = new FailedMessage(message, error.getMessage(), Instant.now());
    return Message.of(failedMessage);
}
```

## Performance Characteristics

### Throughput Metrics
- **API Throughput**: ~10,000 requests/second (limited by database writes)
- **Message Processing**: ~100,000 messages/second (Kafka capacity)
- **End-to-End Latency**: 1-5 seconds (including processing simulation)

### Scaling Considerations

**Horizontal Scaling**:
```yaml
# Scale consumer instances
processor-service:
  deploy:
    replicas: 3
    
# Increase Kafka partitions
sms.requests:
  partitions: 6  # Allow up to 6 consumer instances
```

**Vertical Scaling**:
```yaml
# Increase consumer resources
processor-service:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1Gi
```

## Monitoring and Observability

### Key Metrics

**Producer Metrics**:
- `kafka_producer_record_send_rate` - Messages sent per second
- `kafka_producer_record_send_total` - Total messages sent
- `kafka_producer_record_error_rate` - Failed sends per second

**Consumer Metrics**:
- `kafka_consumer_records_consumed_rate` - Messages consumed per second
- `kafka_consumer_lag` - Consumer lag behind producer
- `kafka_consumer_fetch_rate` - Fetch requests per second

**Business Metrics**:
- `sms_queued_total` - Messages queued for processing
- `sms_sent_total` - Successfully processed messages
- `sms_failed_total` - Failed message processing
- `sms_processing_duration` - Message processing time

### Distributed Tracing

**Jaeger Integration**:
```properties
# Enable tracing
quarkus.jaeger.service-name=sms-service
quarkus.jaeger.sampler-type=const
quarkus.jaeger.sampler-param=1
```

**Trace Context Propagation**:
```java
@Traced
public CompletionStage<Void> processMessage(Message message) {
    Span span = tracer.nextSpan().name("process-sms-message")
                    .tag("message.id", message.getId().toString())
                    .start();
    
    try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
        return processingService.processMessage(message);
    } finally {
        span.end();
    }
}
```

## Testing Strategy

### Unit Testing

**Producer Testing**:
```java
@QuarkusTest
class MessageProducerTest {
    
    @Inject
    @Channel("sms-requests")
    InMemoryConnector connector;
    
    @Test
    void shouldSendMessageToKafka() {
        messageProducer.sendSmsRequest(testMessage);
        
        List<? extends Message<Object>> received = connector.sink("sms-requests").received();
        assertThat(received).hasSize(1);
    }
}
```

**Consumer Testing**:
```java
@QuarkusTest  
class MessageConsumerTest {
    
    @Inject
    @Channel("sms-requests")
    InMemorySource<Message> source;
    
    @Test
    void shouldProcessReceivedMessage() {
        source.send(testMessage);
        
        // Verify processing occurred
        verify(processingService).processMessage(testMessage);
    }
}
```

### Integration Testing

**End-to-End Testing**:
```java
@QuarkusTest
@TestProfile(KafkaTestProfile.class)
class AsyncProcessingIntegrationTest {
    
    @Test
    void shouldProcessMessageEndToEnd() {
        // Send message via API
        Response response = given()
            .contentType(ContentType.JSON)
            .body(sendRequest)
        .when()
            .post("/v1/messages")
        .then()
            .statusCode(202)
            .extract().response();
            
        UUID messageId = response.jsonPath().getUUID("id");
        
        // Wait for processing
        await().atMost(10, SECONDS).until(() -> {
            MessageResponse message = getMessage(messageId);
            return message.getStatus() != MessageStatus.PENDING;
        });
        
        // Verify final status
        MessageResponse finalMessage = getMessage(messageId);
        assertThat(finalMessage.getStatus()).isIn(MessageStatus.SENT, MessageStatus.FAILED);
    }
}
```

## Alternatives Considered

### Synchronous Processing
- **Pros**: Simpler implementation, immediate feedback
- **Cons**: Poor scalability, blocking API calls, tight coupling
- **Decision**: Rejected due to scalability requirements

### Event Sourcing
- **Pros**: Complete audit trail, replay capability, temporal queries
- **Cons**: Higher complexity, eventual consistency challenges
- **Decision**: Considered for future iteration but current requirements don't justify complexity

### Saga Pattern
- **Pros**: Better for complex multi-step workflows, compensation logic
- **Cons**: Overkill for simple SMS processing, additional complexity
- **Decision**: Current workflow is simple enough for basic async pattern

### Message Queue Alternatives

**RabbitMQ**:
- **Pros**: Easier operation, better routing capabilities
- **Cons**: Lower throughput, less suitable for high-volume streaming
- **Decision**: Kafka chosen for better performance characteristics

**Amazon SQS**:
- **Pros**: Fully managed, no operational overhead
- **Cons**: Vendor lock-in, higher latency, cost implications
- **Decision**: Kafka chosen for vendor neutrality

## Future Enhancements

### Advanced Patterns

**Batch Processing**:
```java
@Incoming("sms-requests")
public CompletionStage<Void> processBatch(List<Message> messages) {
    return processingService.processBatch(messages);
}
```

**Priority Queues**:
```java
// Different topics for different priorities
mp.messaging.outgoing.sms-high-priority.topic=sms.high-priority
mp.messaging.outgoing.sms-low-priority.topic=sms.low-priority
```

**Scheduled Retry**:
```java
@Scheduled(every = "30s")
public void retryFailedMessages() {
    List<Message> failedMessages = messageRepository.findFailedMessages();
    failedMessages.forEach(messageProducer::sendSmsRequest);
}
```

## Related Decisions
- [ADR-001: Use Microservices Architecture](001-microservices-architecture.md)
- [ADR-002: Use Apache Kafka as Message Broker](002-kafka-message-broker.md)
- [ADR-003: Use Quarkus as Java Framework](003-quarkus-framework.md)
- [ADR-006: RESTful API Design Principles](006-rest-api-design.md)
