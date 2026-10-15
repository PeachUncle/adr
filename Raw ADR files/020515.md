# ADR-005: Transaction Isolation Levels Strategy

## Status
Accepted

## Context
The XAI-Forge application handles concurrent operations on shared resources (datasets, models, users). Different operations have different consistency requirements and concurrency patterns. The application needs to prevent data corruption, ensure data consistency, and handle concurrent access appropriately while maintaining good performance.

## Decision
We will implement **different transaction isolation levels** for different types of operations based on their consistency requirements and concurrency patterns.

## Consequences

### Positive Consequences
- **Data consistency**: Prevents dirty reads, phantom reads, and non-repeatable reads
- **Concurrency**: Allows appropriate level of concurrent access
- **Performance**: Optimized isolation levels for different operations
- **Data integrity**: Ensures data remains consistent under concurrent access
- **User experience**: Prevents data corruption and inconsistent states
- **Scalability**: Better performance under concurrent load

### Negative Consequences
- **Complexity**: Different isolation levels for different operations
- **Deadlocks**: Risk of deadlocks with higher isolation levels
- **Performance**: Higher isolation levels may reduce performance
- **Understanding**: Developers need to understand isolation levels
- **Testing**: More complex testing scenarios

### Risks
- **Deadlocks**: SERIALIZABLE isolation can cause deadlocks
- **Performance**: High isolation levels can impact performance
- **Complexity**: Incorrect isolation level selection
- **Lock contention**: Pessimistic locking can cause contention

## Isolation Level Strategy

### 1. SERIALIZABLE for User Registration
- **Operation**: User registration and authentication
- **Rationale**: Prevent duplicate usernames/emails
- **Risk**: Race conditions in user creation
- **Implementation**: `@Transactional(isolation = Isolation.SERIALIZABLE)`

### 2. REPEATABLE_READ for Model Training
- **Operation**: Model training and dataset access
- **Rationale**: Ensure consistent dataset state during training
- **Risk**: Dataset modification during training
- **Implementation**: `@Transactional(isolation = Isolation.REPEATABLE_READ)`

### 3. READ_COMMITTED for Dataset Operations
- **Operation**: Dataset upload, update, deletion
- **Rationale**: Balance consistency and performance
- **Risk**: Dirty reads during dataset operations
- **Implementation**: `@Transactional(isolation = Isolation.READ_COMMITTED)`

### 4. READ_UNCOMMITTED for Read-only Operations
- **Operation**: Model predictions, dataset listing
- **Rationale**: Maximum performance for read operations
- **Risk**: Inconsistent reads (acceptable for predictions)
- **Implementation**: `@Transactional(readOnly = true)`

## Alternatives Considered

### 1. Single Isolation Level (READ_COMMITTED)
- **Pros**: Simple, consistent behavior
- **Cons**: Suboptimal for different operation types
- **Decision**: Rejected due to performance concerns

### 2. Highest Isolation (SERIALIZABLE)
- **Pros**: Maximum consistency, no concurrency issues
- **Cons**: Poor performance, high deadlock risk
- **Decision**: Rejected due to performance impact

### 3. No Transaction Management
- **Pros**: Simple implementation
- **Cons**: Data corruption, inconsistent state
- **Decision**: Rejected due to data integrity concerns

## Implementation Details

### User Registration
```java
@Transactional(isolation = Isolation.SERIALIZABLE)
public User registerUser(UserDto userDto) {
    // Check for existing username/email
    // Create user atomically
}
```

### Model Training
```java
@Transactional(isolation = Isolation.REPEATABLE_READ, timeout = 300)
public MLModel trainModel(TrainRequestDto request, Long userId) {
    // Load dataset with consistent view
    // Train model with locked dataset
}
```

### Dataset Operations
```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public DatasetDto storeFile(MultipartFile file, Long userId) {
    // Upload file and save metadata atomically
}
```

## Monitoring and Optimization
- Monitor deadlock occurrences
- Track transaction duration
- Optimize isolation levels based on performance data
- Implement retry logic for deadlock recovery

## References
- [Spring Transaction Management](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction)
- [Database Isolation Levels](https://en.wikipedia.org/wiki/Isolation_(database_systems))
- [PostgreSQL Isolation Levels](https://www.postgresql.org/docs/current/transaction-iso.html)
