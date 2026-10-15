# ADR-003: Async Processing for Model Training

## Status
Accepted

## Context
Machine learning model training is a computationally intensive operation that can take significant time (seconds to minutes). In a web application, blocking the HTTP request thread during model training would result in poor user experience, timeouts, and resource inefficiency. The application needs to handle multiple concurrent training requests while maintaining responsiveness.

## Decision
We will implement **asynchronous model training** using Spring's `@Async` annotation and custom thread pools.

## Consequences

### Positive Consequences
- **Non-blocking**: HTTP requests return immediately
- **Scalability**: Multiple training operations can run concurrently
- **User experience**: Users can continue using the application during training
- **Resource utilization**: Better CPU and memory utilization
- **Progress tracking**: Can implement progress monitoring
- **Error handling**: Better error isolation and handling
- **Timeout prevention**: Avoids HTTP request timeouts

### Negative Consequences
- **Complexity**: More complex error handling and status tracking
- **Resource management**: Need to manage thread pools and memory
- **State management**: Need to track training status
- **User feedback**: Need to implement progress indicators
- **Error propagation**: Async errors need special handling

### Risks
- **Thread pool exhaustion**: Too many concurrent training operations
- **Memory usage**: Large datasets and models consume significant memory
- **Error handling**: Async operations can fail silently
- **Resource cleanup**: Need proper cleanup of training resources

## Alternatives Considered

### 1. Synchronous Processing
- **Pros**: Simple implementation, immediate results
- **Cons**: Poor user experience, timeouts, resource blocking
- **Decision**: Rejected due to user experience concerns

### 2. Message Queues (RabbitMQ, Kafka)
- **Pros**: Decoupled processing, reliable delivery, scaling
- **Cons**: Additional infrastructure, complexity, overkill
- **Decision**: Rejected as too complex for the application's needs

### 3. External ML Service
- **Pros**: Dedicated ML infrastructure, specialized tools
- **Cons**: Network latency, additional service, complexity
- **Decision**: Rejected to keep the application monolithic

### 4. Background Jobs (Quartz Scheduler)
- **Pros**: Scheduled processing, job persistence
- **Cons**: Delayed execution, complex scheduling
- **Decision**: Rejected as training should start immediately

## Implementation Notes
- Custom thread pool executor with configurable pool size
- Separate executors for training and prediction operations
- CompletableFuture for async training operations
- Progress tracking through status updates
- Proper error handling and logging
- Resource cleanup on completion or failure

## Thread Pool Configuration
```java
@Bean(name = "mlTrainingExecutor")
public Executor mlTrainingExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(5);
    executor.setMaxPoolSize(20);
    executor.setQueueCapacity(100);
    executor.setThreadNamePrefix("ML-Training-");
    executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
    return executor;
}
```

## Error Handling
- Async operations return CompletableFuture
- Exceptions are captured and logged
- User-friendly error messages
- Proper resource cleanup on failure

## References
- [Spring Async](https://docs.spring.io/spring-framework/docs/current/reference/html/integration.html#scheduling-annotation-support-async)
- [CompletableFuture](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html)
- [Thread Pool Best Practices](https://docs.oracle.com/javase/tutorial/essential/concurrency/pools.html)
