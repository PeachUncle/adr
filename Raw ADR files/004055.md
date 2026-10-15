# ADR-002: Distributed Transaction Pattern - Saga vs Two-Phase Commit

## Status

Accepted

## Context

SwiftTrack needs to handle distributed transactions across multiple services and external systems (CMS, ROS, WMS). When an order is created, it must be registered in CMS, allocated in WMS, optimized in ROS, and assigned to a driver. This process spans multiple services and can fail at any step.

## Decision

We will implement the **Saga Pattern** using orchestration for managing distributed transactions, rather than Two-Phase Commit (2PC).

## Rationale

### Saga Pattern Advantages

1. **Fault Tolerance**: Better handling of service failures and network partitions
2. **Scalability**: No global locks or blocking resources
3. **External System Integration**: Works well with external systems that don't support 2PC
4. **Observability**: Clear audit trail of compensation actions
5. **Flexibility**: Can implement business-specific compensation logic

### Two-Phase Commit Limitations

1. **Blocking Protocol**: Resources locked during transaction coordination
2. **Coordinator Failure**: Single point of failure in distributed environment
3. **External Systems**: CMS, ROS, and WMS don't support 2PC
4. **Network Partitions**: Poor performance under network issues
5. **Timeout Complexity**: Difficult to set appropriate timeout values

## Implementation Approach

### Orchestration-Based Saga

We'll implement orchestration rather than choreography:

```typescript
// Order Processing Saga Steps
1. CreateOrderInCMS
2. AllocateInventoryInWMS
3. OptimizeRouteInROS
4. AssignToDriver
5. NotifyClient

// Compensation Actions
1. CancelOrderInCMS
2. DeallocateInventoryInWMS
3. CancelRouteInROS
4. UnassignFromDriver
5. NotifyClientOfFailure
```

### Key Components

1. **Saga Orchestrator**: Central coordinator in Order Service
2. **Outbox Pattern**: Ensures reliable event publishing
3. **Idempotency**: All saga steps and compensations are idempotent
4. **State Machine**: Clear state transitions with timeout handling
5. **Circuit Breakers**: Protect against cascading failures

## Technical Implementation

### Saga State Management

```typescript
enum SagaState {
  STARTED = 'started',
  CMS_COMPLETED = 'cms_completed',
  WMS_COMPLETED = 'wms_completed',
  ROS_COMPLETED = 'ros_completed',
  DRIVER_ASSIGNED = 'driver_assigned',
  COMPLETED = 'completed',
  COMPENSATING = 'compensating',
  COMPENSATION_COMPLETED = 'compensation_completed',
  FAILED = 'failed',
}
```

### Compensation Logic

- Each saga step has a corresponding compensation action
- Compensations are executed in reverse order
- Semantic rollback rather than system rollback
- Business-meaningful compensation (e.g., notify customer of cancellation)

### Error Handling

- Transient failures: Retry with exponential backoff
- Permanent failures: Execute compensation saga
- Timeout handling: Configurable timeouts per step
- Dead letter queues: For manual intervention

## Consequences

### Positive

- Resilient to service failures and network issues
- Works with external systems regardless of their transaction support
- Better performance under normal conditions (no global locks)
- Clear audit trail for business users
- Eventual consistency model fits business requirements

### Negative

- More complex implementation than simple transactions
- Eventual consistency requires careful API design
- Compensation logic must be carefully designed and tested
- More monitoring and observability requirements

### Monitoring Requirements

- Saga execution dashboards
- Compensation frequency alerts
- Step execution time metrics
- Failure rate by step
- Manual intervention queue monitoring

## Alternative Patterns Considered

### Event Choreography

- Pros: Decentralized, good for simple workflows
- Cons: Difficult to track overall state, hard to implement timeouts

### TCC (Try-Confirm-Cancel)

- Pros: More traditional transaction semantics
- Cons: Requires all services to support TCC, complex reservation logic

## Review Date

This decision will be reviewed in 6 months or if compensation rates exceed 5% of transactions.
