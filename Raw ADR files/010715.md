# ADR-006: Transactional Outbox Pattern Integration for Python Microservice

## Status
Proposed

## Date
2025-07-06

## Context

After analyzing the reference implementation from `handsonarchitects/transactional-outbox-pattern-example`, we need to validate and refine our Python transcript processing microservice to properly integrate with the transactional outbox pattern already implemented in our .NET modular monolith.

### Reference Implementation Analysis

The analyzed repository demonstrates a complete outbox pattern with three components:
1. **Data Producer**: Creates records with `outbox_sent: false` flag
2. **Outbox Relay**: Polls for unsent records and publishes to message queue
3. **Consumer**: Processes messages from the queue

### Current M3.Net Architecture

Our existing .NET implementation already has:
- ✅ **Outbox Tables**: Implemented in Infrastructure layer
- ✅ **Domain Events**: Published when transcripts are requested
- ✅ **Background Processing**: Outbox processor publishes integration events
- ✅ **Integration Events**: `TranscriptRequestedIntegrationEvent` available

### Integration Challenge

Our Python microservice needs to:
1. **Receive** transcript processing requests via message queue
2. **Send progress updates** back to .NET via message broker
3. **Ensure reliability** without duplicating the outbox pattern
4. **Handle failures** gracefully with proper retry logic
5. **Avoid temporal coupling** between .NET and Python services

## Decision

We will implement a **Distributed Asynchronous Integration Pattern** where the Python microservice communicates with our .NET modular monolith exclusively through message queues, maintaining proper distributed system principles and avoiding temporal coupling.

### Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    .NET Modular Monolith                    │
├─────────────────────────────────────────────────────────────┤
│  Domain Events → Outbox → Integration Events → Message Queue │
└─────────────────────────┬───────────────────────────────────┘
                          │ Async Message
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Message Broker (RabbitMQ)                │
├─────────────────────────────────────────────────────────────┤
│  Queues: transcript.requested, transcript.progress,         │
│          transcript.completed, transcript.failed            │
└─────────────────────────┬───────────────────────────────────┘
                          │ Async Message
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Transcript Service                   │
├─────────────────────────────────────────────────────────────┤
│  Message Consumer → Process Video → Publish Progress/Result │
└─────────────────────────┬───────────────────────────────────┘
                          │ Async Messages
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    .NET Inbox Pattern                       │
├─────────────────────────────────────────────────────────────┤
│  Message Handlers → Update Database → Trigger Domain Events │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Strategy

#### 1. Message Definitions and Queues

Based on the reference implementation patterns, we'll define message contracts for the distributed communication:

```csharp
// Integration Events (Published by .NET via Outbox)
public sealed record TranscriptRequestedIntegrationEvent(
    Guid RequestId,
    Guid UserId, 
    string YouTubeUrl,
    DateTime RequestedAt) : IntegrationEvent(Guid.NewGuid());

// Integration Events (Consumed by .NET via Inbox)
public sealed record TranscriptProgressUpdatedIntegrationEvent(
    Guid RequestId,
    int ProgressPercentage,
    string StatusMessage,
    DateTime UpdatedAt) : IntegrationEvent(Guid.NewGuid());

public sealed record TranscriptCompletedIntegrationEvent(
    Guid RequestId,
    string TranscriptContent,
    string Language,
    decimal ConfidenceScore,
    DateTime CompletedAt) : IntegrationEvent(Guid.NewGuid());

public sealed record TranscriptFailedIntegrationEvent(
    Guid RequestId,
    string ErrorMessage,
    string ErrorDetails,
    DateTime FailedAt) : IntegrationEvent(Guid.NewGuid());
```

#### 2. .NET Outbox Publisher (Already Implemented)

Our existing outbox pattern will publish transcript requests:

```csharp
// Domain Event Handler (publishes to outbox)
public class TranscriptRequestedDomainEventHandler 
    : IDomainEventHandler<TranscriptRequestedDomainEvent>
{
    private readonly IIntegrationEventPublisher _publisher;
    
    public async Task Handle(TranscriptRequestedDomainEvent domainEvent)
    {
        var integrationEvent = new TranscriptRequestedIntegrationEvent(
            domainEvent.RequestId,
            domainEvent.UserId,
            domainEvent.YouTubeUrl,
            domainEvent.OccurredOnUtc
        );
        
        // This gets stored in outbox and published asynchronously
        await _publisher.PublishAsync(integrationEvent);
    }
}
```

#### 3. Python Message Consumer (Following Reference Implementation Pattern)

```python
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

import aio_pika
from aio_pika import Message, DeliveryMode

class TranscriptMessageConsumer:
    """
    Message consumer following the reference implementation patterns
    Handles transcript processing requests asynchronously
    """
    
    def __init__(self, rabbitmq_url: str, transcript_processor: TranscriptProcessor):
        self.rabbitmq_url = rabbitmq_url
        self.transcript_processor = transcript_processor
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None
        self.exchange: aio_pika.Exchange = None
        
    async def start(self) -> None:
        """Start the message consumer"""
        logger.info("Starting Transcript Message Consumer")
        
        # Connect to RabbitMQ
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        
        # Declare exchanges and queues
        await self._setup_messaging_infrastructure()
        
        # Start consuming messages
        await self._start_consuming()
        
    async def stop(self) -> None:
        """Stop the message consumer"""
        logger.info("Stopping Transcript Message Consumer")
        
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
    
    async def _setup_messaging_infrastructure(self):
        """Setup exchanges and queues following reference implementation patterns"""
        
        # Exchanges for different message types
        self.request_exchange = await self.channel.declare_exchange(
            "transcript.requests", aio_pika.ExchangeType.DIRECT, durable=True
        )
        
        self.progress_exchange = await self.channel.declare_exchange(
            "transcript.progress", aio_pika.ExchangeType.DIRECT, durable=True
        )
        
        self.results_exchange = await self.channel.declare_exchange(
            "transcript.results", aio_pika.ExchangeType.DIRECT, durable=True
        )
        
        # Queue for incoming transcript requests
        arguments = {"x-queue-type": "quorum"}  # Following reference implementation
        self.request_queue = await self.channel.declare_queue(
            "transcript.processing.queue", 
            durable=True, 
            arguments=arguments
        )
        
        # Bind queue to exchange
        await self.request_queue.bind(self.request_exchange, routing_key="transcript.requested")
        
    async def _start_consuming(self):
        """Start consuming messages from the queue"""
        
        # Set QoS to limit concurrent processing (following reference implementation)
        await self.channel.set_qos(prefetch_count=5)
        
        async with self.request_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await self._handle_transcript_request(message)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        # Message will be rejected and potentially requeued
                        raise
    
    async def _handle_transcript_request(self, message: aio_pika.Message):
        """Handle incoming transcript request message"""
        
        try:
            # Parse message
            message_data = json.loads(message.body.decode())
            request_id = message_data["RequestId"]
            user_id = message_data["UserId"]
            youtube_url = message_data["YouTubeUrl"]
            
            logger.info(f"Processing transcript request: {request_id}")
            
            # Start processing asynchronously (fire and forget)
            asyncio.create_task(
                self._process_transcript_async(request_id, user_id, youtube_url)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse transcript request message: {e}")
            raise
    
    async def _process_transcript_async(self, request_id: str, user_id: str, youtube_url: str):
        """Process transcript request and publish progress updates"""
        
        try:
            # Step 1: Validate and start processing
            await self._publish_progress_update(request_id, 5, "Starting transcript processing")
            
            # Step 2: Download video
            await self._publish_progress_update(request_id, 15, "Downloading video")
            video_info = await self.transcript_processor.download_video(youtube_url)
            
            # Step 3: Extract audio  
            await self._publish_progress_update(request_id, 35, "Extracting audio")
            audio_file = await self.transcript_processor.extract_audio(video_info)
            
            # Step 4: Transcribe
            await self._publish_progress_update(request_id, 60, "Transcribing audio")
            transcript_result = await self.transcript_processor.transcribe_audio(audio_file)
            
            # Step 5: Format results
            await self._publish_progress_update(request_id, 90, "Formatting results")
            formatted_result = await self.transcript_processor.format_result(transcript_result)
            
            # Step 6: Publish completion
            await self._publish_completion(request_id, formatted_result)
            
        except Exception as e:
            logger.error(f"Transcript processing failed for {request_id}: {e}")
            await self._publish_failure(request_id, str(e))
        
        finally:
            # Cleanup temporary files
            await self.transcript_processor.cleanup_temp_files()
    
    async def _publish_progress_update(self, request_id: str, progress: int, message: str):
        """Publish progress update message"""
        
        progress_message = {
            "RequestId": request_id,
            "ProgressPercentage": progress,
            "StatusMessage": message,
            "UpdatedAt": datetime.utcnow().isoformat()
        }
        
        await self._publish_message(
            self.progress_exchange,
            "transcript.progress.updated",
            progress_message
        )
        
    async def _publish_completion(self, request_id: str, result: Dict[str, Any]):
        """Publish transcript completion message"""
        
        completion_message = {
            "RequestId": request_id,
            "TranscriptContent": result["transcript_content"],
            "Language": result["language"],
            "ConfidenceScore": result["confidence_score"],
            "CompletedAt": datetime.utcnow().isoformat()
        }
        
        await self._publish_message(
            self.results_exchange,
            "transcript.completed",
            completion_message
        )
        
    async def _publish_failure(self, request_id: str, error_message: str):
        """Publish transcript failure message"""
        
        failure_message = {
            "RequestId": request_id,
            "ErrorMessage": error_message,
            "ErrorDetails": "",  # Could include stack trace in debug mode
            "FailedAt": datetime.utcnow().isoformat()
        }
        
        await self._publish_message(
            self.results_exchange,
            "transcript.failed",
            failure_message
        )
    
    async def _publish_message(self, exchange: aio_pika.Exchange, routing_key: str, message_data: Dict[str, Any]):
        """Publish message to exchange with routing key"""
        
        try:
            message_body = json.dumps(message_data).encode()
            message = Message(
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT,  # Ensure message durability
                timestamp=datetime.utcnow()
            )
            
            await exchange.publish(message, routing_key=routing_key)
            logger.debug(f"Published message: {routing_key}")
            
        except Exception as e:
            logger.error(f"Failed to publish message {routing_key}: {e}")
            raise
```

#### 4. .NET Inbox Message Handlers

The .NET side will consume progress and completion messages via the inbox pattern:

```csharp
// Inbox Message Handlers
public class TranscriptProgressUpdatedIntegrationEventHandler 
    : IIntegrationEventHandler<TranscriptProgressUpdatedIntegrationEvent>
{
    private readonly ITranscriptRequestRepository _repository;
    
    public async Task Handle(TranscriptProgressUpdatedIntegrationEvent integrationEvent)
    {
        // Update processing status in database
        var transcriptRequest = await _repository.GetByIdAsync(integrationEvent.RequestId);
        if (transcriptRequest != null)
        {
            transcriptRequest.UpdateProgress(
                integrationEvent.ProgressPercentage, 
                integrationEvent.StatusMessage
            );
            
            await _repository.UpdateAsync(transcriptRequest);
        }
    }
}

public class TranscriptCompletedIntegrationEventHandler 
    : IIntegrationEventHandler<TranscriptCompletedIntegrationEvent>
{
    private readonly ITranscriptRequestRepository _transcriptRequestRepository;
    private readonly ITranscriptRepository _transcriptRepository;
    
    public async Task Handle(TranscriptCompletedIntegrationEvent integrationEvent)
    {
        // Create completed transcript
        var transcript = Transcript.Create(
            integrationEvent.RequestId,
            integrationEvent.TranscriptContent,
            integrationEvent.Language,
            integrationEvent.ConfidenceScore
        );
        
        await _transcriptRepository.AddAsync(transcript);
        
        // Update request status
        var request = await _transcriptRequestRepository.GetByIdAsync(integrationEvent.RequestId);
        if (request != null)
        {
            request.MarkAsCompleted();
            await _transcriptRequestRepository.UpdateAsync(request);
        }
    }
}

public class TranscriptFailedIntegrationEventHandler 
    : IIntegrationEventHandler<TranscriptFailedIntegrationEvent>
{
    private readonly ITranscriptRequestRepository _repository;
    
    public async Task Handle(TranscriptFailedIntegrationEvent integrationEvent)
    {
        var transcriptRequest = await _repository.GetByIdAsync(integrationEvent.RequestId);
        if (transcriptRequest != null)
        {
            transcriptRequest.MarkAsFailed(integrationEvent.ErrorMessage);
            await _repository.UpdateAsync(transcriptRequest);
        }
    }
}
```

#### 4. .NET Inbox Message Handlers

The .NET side will consume progress and completion messages via the inbox pattern:

```csharp
// Inbox Message Handlers
public class TranscriptProgressUpdatedIntegrationEventHandler 
    : IIntegrationEventHandler<TranscriptProgressUpdatedIntegrationEvent>
{
    private readonly ITranscriptRequestRepository _repository;
    
    public async Task Handle(TranscriptProgressUpdatedIntegrationEvent integrationEvent)
    {
        // Update processing status in database
        var transcriptRequest = await _repository.GetByIdAsync(integrationEvent.RequestId);
        if (transcriptRequest != null)
        {
            transcriptRequest.UpdateProgress(
                integrationEvent.ProgressPercentage, 
                integrationEvent.StatusMessage
            );
            
            await _repository.UpdateAsync(transcriptRequest);
        }
    }
}

public class TranscriptCompletedIntegrationEventHandler 
    : IIntegrationEventHandler<TranscriptCompletedIntegrationEvent>
{
    private readonly ITranscriptRequestRepository _transcriptRequestRepository;
    private readonly ITranscriptRepository _transcriptRepository;
    
    public async Task Handle(TranscriptCompletedIntegrationEvent integrationEvent)
    {
        // Create completed transcript
        var transcript = Transcript.Create(
            integrationEvent.RequestId,
            integrationEvent.TranscriptContent,
            integrationEvent.Language,
            integrationEvent.ConfidenceScore
        );
        
        await _transcriptRepository.AddAsync(transcript);
        
        // Update request status
        var request = await _transcriptRequestRepository.GetByIdAsync(integrationEvent.RequestId);
        if (request != null)
        {
            request.MarkAsCompleted();
            await _transcriptRequestRepository.UpdateAsync(request);
        }
    }
}

public class TranscriptFailedIntegrationEventHandler 
    : IIntegrationEventHandler<TranscriptFailedIntegrationEvent>
{
    private readonly ITranscriptRequestRepository _repository;
    
    public async Task Handle(TranscriptFailedIntegrationEvent integrationEvent)
    {
        var transcriptRequest = await _repository.GetByIdAsync(integrationEvent.RequestId);
        if (transcriptRequest != null)
        {
            transcriptRequest.MarkAsFailed(integrationEvent.ErrorMessage);
            await _repository.UpdateAsync(transcriptRequest);
        }
    }
}
```

#### 5. .NET Message Broker Configuration

```csharp
// In TranscriptsModule.cs - Configure RabbitMQ integration
public static class TranscriptsModule
{
    public static IServiceCollection AddTranscriptsModule(
        this IServiceCollection services, 
        IConfiguration configuration)
    {
        // ... existing configuration ...
        
        // Configure RabbitMQ for Python service integration
        services.Configure<RabbitMqOptions>(
            configuration.GetSection("MessageBroker:RabbitMq"));
        
        // Register inbox handlers for Python service responses
        services.AddScoped<IIntegrationEventHandler<TranscriptProgressUpdatedIntegrationEvent>, 
                           TranscriptProgressUpdatedIntegrationEventHandler>();
        services.AddScoped<IIntegrationEventHandler<TranscriptCompletedIntegrationEvent>, 
                           TranscriptCompletedIntegrationEventHandler>();
        services.AddScoped<IIntegrationEventHandler<TranscriptFailedIntegrationEvent>, 
                           TranscriptFailedIntegrationEventHandler>();
        
        return services;
    }
}

// RabbitMQ configuration for exchanges and queues
public class RabbitMqTranscriptConfiguration : IRabbitMqConfiguration
{
    public void Configure(IRabbitMqConfigurationBuilder builder)
    {
        // Outbound exchange for sending requests to Python service
        builder.DeclareExchange("transcript.requests", ExchangeType.Direct)
               .WithDurability(true);
        
        // Inbound exchanges for receiving responses from Python service
        builder.DeclareExchange("transcript.progress", ExchangeType.Direct)
               .WithDurability(true);
               
        builder.DeclareExchange("transcript.results", ExchangeType.Direct)
               .WithDurability(true);
        
        // Inbound queues for processing Python service responses
        builder.DeclareQueue("transcript.progress.inbox")
               .WithDurability(true)
               .WithArgument("x-queue-type", "quorum")
               .BindTo("transcript.progress", "transcript.progress.updated");
               
        builder.DeclareQueue("transcript.results.inbox")
               .WithDurability(true)
               .WithArgument("x-queue-type", "quorum")
               .BindTo("transcript.results", "transcript.completed")
               .BindTo("transcript.results", "transcript.failed");
    }
}
```
```

#### 6. Python Service State Management (Message-Based)

```python
class ReliabilityManager:
    """
    Implements reliability patterns from the reference implementation
    for message-based integration with proper idempotency and state tracking
    """
    
    def __init__(self):
        self.state_file = "transcript_service_state.json"
        self.processed_messages: Set[str] = set()  # For idempotency
        self.active_requests: Dict[str, ProcessingState] = {}
    
    async def is_message_processed(self, message_id: str) -> bool:
        """Check if message has already been processed (idempotency check)"""
        return message_id in self.processed_messages
    
    async def mark_message_processed(self, message_id: str):
        """Mark message as processed to prevent duplicate processing"""
        self.processed_messages.add(message_id)
        await self.save_state()
    
    async def start_processing(self, request_id: str, message_id: str, request_data: dict):
        """Track processing request with persistent state"""
        
        state = ProcessingState(
            request_id=request_id,
            message_id=message_id,
            status="started",
            started_at=datetime.utcnow(),
            request_data=request_data
        )
        
        self.active_requests[request_id] = state
        await self.save_state()
    
    async def complete_processing(self, request_id: str):
        """Mark processing as complete and cleanup state"""
        
        if request_id in self.active_requests:
            del self.active_requests[request_id]
            await self.save_state()
    
    async def save_state(self):
        """Persist state to file (following reference implementation pattern)"""
        
        state_data = {
            "processed_messages": list(self.processed_messages),
            "active_requests": {
                rid: {
                    "request_id": state.request_id,
                    "message_id": state.message_id,
                    "status": state.status,
                    "started_at": state.started_at.isoformat(),
                    "request_data": state.request_data
                }
                for rid, state in self.active_requests.items()
            },
            "last_update": datetime.utcnow().isoformat()
        }
        
        try:
            async with aiofiles.open(self.state_file, "w") as f:
                await f.write(json.dumps(state_data, indent=2))
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    async def load_state(self):
        """Load state from file on startup"""
        
        if os.path.exists(self.state_file):
            try:
                async with aiofiles.open(self.state_file, "r") as f:
                    content = await f.read()
                    state_data = json.loads(content)
                    
                    # Restore processed messages for idempotency
                    self.processed_messages = set(state_data.get("processed_messages", []))
                    
                    # Restore active requests
                    for rid, data in state_data.get("active_requests", {}).items():
                        self.active_requests[rid] = ProcessingState(
                            request_id=data["request_id"],
                            message_id=data["message_id"],
                            status=data["status"],
                            started_at=datetime.fromisoformat(data["started_at"]),
                            request_data=data["request_data"]
                        )
                    
                    logger.info(f"State loaded: {len(self.processed_messages)} processed messages, "
                              f"{len(self.active_requests)} active requests")
                    
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
```
```

### 7. Configuration Management (Message-Based Integration)

```python
class Settings(BaseSettings):
    """Configuration for message-based distributed integration"""
    
    # Service Configuration
    app_name: str = "transcript-processing-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # RabbitMQ Configuration
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_connection_timeout: int = 30
    rabbitmq_heartbeat: int = 600
    
    # Processing Configuration
    max_concurrent_jobs: int = 5
    max_video_duration_minutes: int = 60
    temp_storage_path: str = "/tmp/transcripts"
    
    # Whisper API Configuration
    openai_api_key: str
    whisper_model: str = "whisper-1"
    
    # Reliability Configuration
    max_retries: int = 3
    retry_delay_seconds: int = 2
    state_file_path: str = "./transcript_service_state.json"
    message_processing_timeout: int = 300  # 5 minutes
    
    # Monitoring
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_port: int = 8080
    
    class Config:
        env_file = ".env"
```
```

## Benefits of This Integration Approach

### 1. **Leverages Existing Outbox Pattern**
- ✅ No duplication of outbox infrastructure
- ✅ .NET handles all transactional guarantees
- ✅ Integration events are properly ordered and reliable

### 2. **Maintains Service Boundaries**
- ✅ Python service remains stateless and focused
- ✅ Clear separation of concerns
- ✅ Can be scaled independently
- ✅ No temporal coupling between services

### 3. **Reliability Through Messaging**
- ✅ Message durability and persistence
- ✅ Automatic retry and dead letter handling
- ✅ Proper error handling and circuit breaking
- ✅ Idempotent message processing

### 4. **Operational Excellence**
- ✅ Health checks and monitoring endpoints
- ✅ Persistent state for recovery scenarios
- ✅ Comprehensive logging and observability
- ✅ Message-based monitoring and alerting

## Implementation Phases

### Phase 1: .NET Message Integration (Week 1)
```csharp
// Add to TranscriptsModule.cs
services.Configure<RabbitMqOptions>(configuration.GetSection("MessageBroker:RabbitMq"));

// Add integration event handlers for Python service responses
services.AddScoped<IIntegrationEventHandler<TranscriptProgressUpdatedIntegrationEvent>, 
                   TranscriptProgressUpdatedIntegrationEventHandler>();
services.AddScoped<IIntegrationEventHandler<TranscriptCompletedIntegrationEvent>, 
                   TranscriptCompletedIntegrationEventHandler>();
services.AddScoped<IIntegrationEventHandler<TranscriptFailedIntegrationEvent>, 
                   TranscriptFailedIntegrationEventHandler>();

// Configure message routing
services.AddSingleton<IRabbitMqConfiguration, RabbitMqTranscriptConfiguration>();
```

### Phase 2: Python Message Consumer Service (Week 1-2)
- RabbitMQ consumer for transcript requests
- Async message processing pipeline
- Message publisher for progress and results
- Idempotent message handling

### Phase 3: Reliability and State Management (Week 2)
- Message deduplication and idempotency
- Persistent state for recovery scenarios
- Dead letter queue handling
- Comprehensive error handling and retry logic

### Phase 4: Production Readiness (Week 3)
- Message-based monitoring and alerting
- Performance optimization and load testing
- Docker containerization with message broker
- Comprehensive documentation and runbooks

## Testing Strategy

### Integration Testing
```python
async def test_end_to_end_message_processing():
    """Test complete message flow from .NET to Python and back"""
    
    # 1. .NET publishes domain event → outbox → integration event → message queue
    # 2. Python service consumes message from queue
    # 3. Python service processes and publishes progress messages
    # 4. Python service completes and publishes result message
    # 5. .NET consumes result message via inbox handler
    # 6. Verify transcript is saved in .NET database
    
    # Mock the YouTube video processing
    with patch('transcript_service.download_video') as mock_download:
        mock_download.return_value = MockVideoInfo()
        
        # Simulate message reception
        request_message = {
            "RequestId": "test-123",
            "UserId": "user-456", 
            "YouTubeUrl": "https://youtube.com/watch?v=test",
            "RequestedAt": datetime.utcnow().isoformat()
        }
        
        # Process message
        await message_consumer._handle_transcript_request(
            create_mock_message(request_message)
        )
        
        # Wait for completion
        await asyncio.sleep(5)
        
        # Verify completion message was published
        assert_message_published("transcript.completed", "test-123")

async def test_message_idempotency():
    """Test that duplicate messages are handled properly"""
    
    request_message = create_test_message("test-456")
    
    # Process same message twice
    await message_consumer._handle_transcript_request(request_message)
    await message_consumer._handle_transcript_request(request_message)
    
    # Verify only processed once
    assert len(transcript_service.processed_requests) == 1
```

### Failure Recovery Testing
```python
async def test_service_restart_with_message_recovery():
    """Test that service recovers active requests after restart"""
    
    # Start processing
    request_id = "test-123"
    message_id = "msg-456"
    
    await reliability_manager.start_processing(request_id, message_id, request_data)
    
    # Simulate service restart
    await transcript_service.stop()
    
    new_service = TranscriptService()
    await new_service.start()
    
    # Verify active requests and processed messages are restored
    assert request_id in new_service.reliability_manager.active_requests
    assert message_id in new_service.reliability_manager.processed_messages

async def test_message_broker_connection_recovery():
    """Test service handles message broker disconnections"""
    
    # Simulate connection loss
    await message_consumer.connection.close()
    
    # Verify service attempts reconnection
    await asyncio.sleep(5)
    
    # Verify service is healthy again
    health_status = await health_checker.check_message_broker()
    assert health_status == "healthy"
```

## Monitoring and Observability

### Message-Based Metrics
```python
# Following reference implementation monitoring patterns
@app.get("/metrics")
async def get_metrics():
    return {
        "active_requests": len(reliability_manager.active_requests),
        "processed_messages": len(reliability_manager.processed_messages),
        "total_processed": transcript_service.total_processed,
        "success_rate": transcript_service.success_rate,
        "average_processing_time": transcript_service.avg_processing_time,
        "message_queue_health": await check_message_queue_health(),
        "last_activity": transcript_service.last_activity,
        "health_status": "healthy"
    }
```

### Health Checks for Distributed System
```python
@app.get("/health")
async def health_check():
    """Comprehensive health check for message-based architecture"""
    
    checks = {
        "service": "healthy",
        "message_broker": await check_rabbitmq_connectivity(),
        "openai_api": await check_openai_connectivity(),
        "disk_space": await check_disk_space(),
        "temp_directory": await check_temp_directory(),
        "consumer_status": await check_consumer_status(),
        "publisher_status": await check_publisher_status()
    }
    
    overall_status = "healthy" if all(
        status == "healthy" for status in checks.values()
    ) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "queue_depths": await get_queue_depths()
    }

async def check_rabbitmq_connectivity() -> str:
    """Check RabbitMQ connection health"""
    try:
        if message_consumer.connection and not message_consumer.connection.is_closed:
            return "healthy"
        else:
            return "unhealthy"
    except Exception:
        return "unhealthy"

async def get_queue_depths() -> Dict[str, int]:
    """Get current message queue depths for monitoring"""
    try:
        return {
            "transcript_requests": await get_queue_depth("transcript.processing.queue"),
            "transcript_progress": await get_queue_depth("transcript.progress.inbox"),
            "transcript_results": await get_queue_depth("transcript.results.inbox")
        }
    except Exception as e:
        logger.error(f"Failed to get queue depths: {e}")
        return {}
```

## Risk Mitigation

### Identified Risks and Solutions

1. **Message Broker Failures**
   - *Risk*: RabbitMQ becomes unavailable
   - *Mitigation*: Connection retry logic, circuit breaker pattern, clustered RabbitMQ setup

2. **Message Processing Failures**
   - *Risk*: Messages are lost or duplicated
   - *Mitigation*: Message durability, idempotency checks, dead letter queues

3. **Service Restart During Processing**
   - *Risk*: Active processing requests are lost
   - *Mitigation*: Persistent state management, message acknowledgment only after completion

4. **Network Partitions**
   - *Risk*: Python service can't communicate with message broker
   - *Mitigation*: Robust reconnection logic, local state persistence, monitoring alerts

5. **Resource Exhaustion**
   - *Risk*: Too many concurrent processing jobs
   - *Mitigation*: Message prefetch limits, resource monitoring, auto-scaling

6. **Poison Messages**
   - *Risk*: Malformed messages cause service failure
   - *Mitigation*: Message validation, error handling, dead letter queue routing

## Success Criteria

### Integration Requirements
- ✅ Seamless integration with existing .NET outbox pattern
- ✅ No duplicate processing due to message idempotency
- ✅ Proper error handling and recovery scenarios
- ✅ Zero temporal coupling between services

### Performance Requirements
- ✅ Handle 10+ concurrent processing requests
- ✅ Progress updates within 5 seconds of status changes
- ✅ Service startup/shutdown within 30 seconds
- ✅ Message processing latency under 100ms

### Reliability Requirements
- ✅ 99.9% success rate for valid YouTube URLs
- ✅ Zero data loss during service restarts
- ✅ Automatic recovery from transient failures
- ✅ Message durability and delivery guarantees

## Related ADRs
- ADR-002: Transcripts Module Architecture
- ADR-004: Python Transcript Processing Service  
- ADR-005: YouTube Whisper Tutorial Analysis

## Conclusion

The analyzed reference implementation validates our architectural approach while highlighting the importance of proper integration with existing outbox patterns. By implementing the Python service as a **message-based consumer/producer** that integrates with our existing .NET outbox pattern, we achieve:

1. **Reliability** through proven outbox pattern in .NET + message durability
2. **Scalability** through asynchronous message processing
3. **Resilience** through stateless Python service design and message-based communication
4. **Maintainability** through clear separation of concerns and proper bounded contexts

This approach leverages the best of both worlds: the transactional guarantees of our existing .NET outbox implementation and the processing capabilities of the Python ecosystem, while maintaining distributed system principles and avoiding temporal coupling between services.

**Key Architectural Decisions:**
- All cross-boundary communication uses RabbitMQ message broker
- No synchronous HTTP calls between .NET and Python services
- Idempotent message processing with persistent state management
- Full asynchronous workflow with progress reporting via messages
- Comprehensive error handling and recovery through message patterns
