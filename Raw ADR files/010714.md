# ADR-004: Python Transcript Processing Microservice

## Status
Proposed

## Date
2025-07-06

## Context

Following the implementation of the Transcripts Module (.NET) as defined in ADR-002, we need to implement the Python microservice responsible for the actual YouTube video processing and speech-to-text transcription. This service will be a standalone microservice that communicates with the .NET modular monolith via HTTP APIs and message queues.

### Business Requirements
- Process YouTube videos asynchronously for transcription
- Extract audio from YouTube videos efficiently
- Convert speech to text with high accuracy
- Handle multiple video formats and languages
- Provide real-time progress updates during processing
- Support batch processing for scalability
- Robust error handling and retry mechanisms

### Technical Constraints
- Must integrate with existing .NET API via HTTP
- Should utilize Python's ML/AI ecosystem advantages
- Must be containerized and scalable
- Should handle video processing without storing sensitive data long-term
- Must provide comprehensive logging and monitoring
- Should be stateless for horizontal scaling

## Decision

We will implement a **Python FastAPI microservice** with the following architecture:

### Core Technology Stack
- **FastAPI**: Modern, fast web framework with automatic OpenAPI documentation
- **Celery**: Distributed task queue for asynchronous processing
- **Redis**: Message broker and result backend for Celery
- **yt-dlp**: YouTube video downloading library (successor to youtube-dl)
- **OpenAI Whisper**: State-of-the-art speech recognition model
- **FFmpeg**: Video/audio processing and format conversion
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Transcript Service                │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Web Layer                                          │
│  ├── Health Check Endpoints                                 │
│  ├── Webhook Endpoints (receive from .NET)                  │
│  ├── Status Query Endpoints                                 │
│  └── Admin/Monitoring Endpoints                             │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  ├── Video Processing Service                               │
│  ├── Transcription Service                                  │
│  ├── Progress Tracking Service                              │
│  └── Result Delivery Service                                │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                       │
│  ├── Celery Task Workers                                    │
│  ├── Redis Client                                           │
│  ├── HTTP Client (.NET API Integration)                     │
│  ├── File Storage (Temporary)                               │
│  └── Logging & Monitoring                                   │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Project Structure

```
transcript-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py          # Health check endpoints
│   │   ├── webhooks.py        # Receive processing requests
│   │   ├── status.py          # Job status queries
│   │   └── admin.py           # Admin endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── video_processor.py # YouTube video handling
│   │   ├── transcriber.py     # Speech-to-text processing
│   │   ├── progress_tracker.py# Progress updates
│   │   └── result_handler.py  # Result delivery
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py        # Pydantic request models
│   │   ├── responses.py       # Pydantic response models
│   │   └── enums.py           # Status enums, etc.
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dotnet_client.py   # HTTP client for .NET API
│   │   ├── storage.py         # Temporary file management
│   │   └── monitoring.py      # Logging and metrics
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── video_tasks.py     # Video processing tasks
│   │   └── transcript_tasks.py# Transcription tasks
│   │
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py      # Custom exceptions
│       ├── helpers.py         # Utility functions
│       └── validators.py      # Input validation
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_core/
│   └── test_tasks/
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.override.yml
│
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
└── .env.example
```

### 2. Core Processing Workflow

```python
# Simplified workflow representation
async def process_transcript_request(request_id: str, youtube_url: str, user_id: str):
    """Main processing pipeline"""
    
    # 1. Update status to Processing
    await update_processing_status(request_id, "Processing", 10)
    
    # 2. Download and extract audio
    audio_file = await extract_audio_from_youtube(youtube_url)
    await update_processing_status(request_id, "Processing", 30)
    
    # 3. Transcribe audio using Whisper
    transcript_result = await transcribe_audio(audio_file)
    await update_processing_status(request_id, "Processing", 80)
    
    # 4. Clean up temporary files
    await cleanup_temp_files(audio_file)
    
    # 5. Send completion result to .NET API
    await complete_transcript(request_id, transcript_result)
    await update_processing_status(request_id, "Completed", 100)
```

### 3. API Endpoints

#### Webhook Endpoints (Called by .NET)
```python
POST /api/v1/process-transcript
{
    "request_id": "uuid",
    "youtube_url": "https://youtube.com/watch?v=...",
    "user_id": "uuid",
    "callback_url": "https://api.m3.net/transcripts/complete"
}
```

#### Status Endpoints
```python
GET /api/v1/status/{request_id}
{
    "request_id": "uuid",
    "status": "Processing",
    "progress_percentage": 45,
    "message": "Extracting audio from video",
    "started_at": "2025-07-06T10:00:00Z",
    "estimated_completion": "2025-07-06T10:05:00Z"
}
```

#### Health Check
```python
GET /health
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-07-06T10:00:00Z",
    "dependencies": {
        "redis": "healthy",
        "celery": "healthy",
        "whisper_model": "loaded"
    }
}
```

### 4. Integration with .NET API

The Python service will communicate with the .NET API through HTTP calls:

```python
class DotNetApiClient:
    async def update_processing_status(self, request_id: str, progress: int, message: str):
        """Update processing status in .NET API"""
        url = f"{self.base_url}/transcripts/processing/{request_id}/status"
        payload = {
            "progress_percentage": progress,
            "status_message": message
        }
        await self.http_client.put(url, json=payload)
    
    async def complete_transcript(self, request_id: str, result: TranscriptResult):
        """Send completed transcript to .NET API"""
        url = f"{self.base_url}/transcripts/complete"
        payload = {
            "request_id": request_id,
            "transcript_content": result.text,
            "language": result.language,
            "confidence_score": result.confidence
        }
        await self.http_client.post(url, json=payload)
```

### 5. Configuration Management

```python
class Settings(BaseSettings):
    # Service Configuration
    app_name: str = "Transcript Processing Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # .NET API Integration
    dotnet_api_base_url: str
    dotnet_api_auth_token: str
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str = "redis://localhost:6379"
    
    # Processing Configuration
    max_video_duration_minutes: int = 60
    temp_storage_path: str = "/tmp/transcripts"
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    
    # Monitoring
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    class Config:
        env_file = ".env"
```

## Deployment Strategy

### 1. Containerization

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ /app/
WORKDIR /app

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose (Development)

```yaml
version: '3.8'
services:
  transcript-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DOTNET_API_BASE_URL=http://host.docker.internal:5000
    depends_on:
      - redis
    
  celery-worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
      - DOTNET_API_BASE_URL=http://host.docker.internal:5000
    depends_on:
      - redis
    volumes:
      - /tmp/transcripts:/tmp/transcripts
  
  celery-beat:
    build: .
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 3. Production Considerations

- **Scaling**: Deploy multiple worker instances behind a load balancer
- **Storage**: Use cloud storage for temporary files in production
- **Monitoring**: Integrate with Prometheus/Grafana for metrics
- **Security**: Implement proper authentication and rate limiting
- **Resource Management**: Configure appropriate CPU/memory limits

## Performance and Scalability

### Expected Performance Metrics
- **Video Download**: 1-3 minutes for typical YouTube videos
- **Audio Extraction**: 30-60 seconds depending on video length
- **Transcription**: 1-5 minutes depending on audio length and model size
- **Total Processing Time**: 3-10 minutes for typical 10-minute video

### Scaling Strategies
1. **Horizontal Scaling**: Add more Celery workers
2. **Model Optimization**: Use appropriate Whisper model size for use case
3. **Caching**: Cache frequently requested video metadata
4. **Resource Allocation**: Dedicated GPU instances for large-scale transcription

## Security Considerations

1. **API Authentication**: Secure communication with .NET API using JWT tokens
2. **Input Validation**: Strict validation of YouTube URLs and parameters
3. **Temporary File Cleanup**: Automatic cleanup of downloaded content
4. **Rate Limiting**: Prevent abuse of video processing resources
5. **Error Handling**: Avoid exposing internal system details in error messages

## Monitoring and Observability

### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Key Events**: Request received, processing started, progress updates, completion

### Metrics Collection
- **Processing Metrics**: Success/failure rates, processing times
- **System Metrics**: CPU usage, memory consumption, disk space
- **Business Metrics**: Videos processed per hour, user engagement

### Health Checks
- **Liveness Probe**: Basic service availability
- **Readiness Probe**: Service ready to accept requests
- **Dependency Checks**: Redis connectivity, model loading status

## Testing Strategy

### Unit Tests
- Core business logic functions
- Data validation and transformation
- Error handling scenarios

### Integration Tests
- .NET API communication
- Redis/Celery integration
- File system operations

### End-to-End Tests
- Complete workflow from request to completion
- Error scenarios and recovery
- Performance benchmarks

## Risks and Mitigations

### Technical Risks
1. **YouTube Rate Limits**: Risk of hitting download limits
   - *Mitigation*: Implement exponential backoff and respect rate limits
   
2. **Model Performance**: Whisper accuracy varies with audio quality
   - *Mitigation*: Provide confidence scores and allow manual review
   
3. **Storage Management**: Temporary files could accumulate
   - *Mitigation*: Automatic cleanup and monitoring of disk usage

### Operational Risks
1. **Service Dependencies**: Redis/Celery failures could halt processing
   - *Mitigation*: Health checks and automatic restart policies
   
2. **Resource Exhaustion**: Large videos could consume excessive resources
   - *Mitigation*: Video length limits and resource monitoring

## Success Criteria

### Functional Requirements
- ✅ Successfully download and process YouTube videos
- ✅ Generate accurate transcripts with confidence scores
- ✅ Provide real-time progress updates
- ✅ Handle errors gracefully with proper user feedback
- ✅ Integrate seamlessly with .NET API

### Non-Functional Requirements
- **Reliability**: 99.5% success rate for valid YouTube URLs
- **Performance**: Process 90% of videos within 10 minutes
- **Scalability**: Handle 100+ concurrent processing jobs
- **Availability**: 99.9% uptime for API endpoints

### Operational Requirements
- **Monitoring**: Comprehensive metrics and alerting
- **Deployment**: Automated CI/CD pipeline
- **Documentation**: Complete API documentation and runbooks

## Related ADRs
- ADR-002: Transcripts Module Architecture
- ADR-003: Event Storming Transcripts Bounded Contexts

## Future Considerations

1. **Multi-language Support**: Expand beyond English transcription
2. **Speaker Identification**: Identify and label different speakers
3. **Video Analysis**: Extract additional metadata (topics, sentiment)
4. **Batch Processing**: Optimize for processing multiple videos
5. **Real-time Streaming**: Support live video transcription

## Implementation Timeline

### Phase 1 (Week 1): Foundation Setup
- Project scaffolding and basic FastAPI setup
- Docker containerization
- Basic health check endpoints
- Redis and Celery integration

### Phase 2 (Week 2): Core Processing
- YouTube video download functionality
- Audio extraction with FFmpeg
- Basic Whisper integration
- Progress tracking implementation

### Phase 3 (Week 3): .NET Integration
- HTTP client for .NET API communication
- Webhook endpoint implementation
- Error handling and retry logic
- End-to-end workflow testing

### Phase 4 (Week 4): Production Readiness
- Comprehensive testing suite
- Monitoring and logging implementation
- Performance optimization
- Security hardening
- Documentation completion

## Next Steps

1. **Environment Setup**: Prepare development environment with required dependencies
2. **Prototype Development**: Create minimal viable service for basic transcription
3. **Integration Testing**: Test communication with existing .NET API
4. **Performance Baseline**: Establish processing time benchmarks
5. **Production Deployment**: Deploy to staging environment for testing
