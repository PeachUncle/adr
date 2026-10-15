# ADR 0003: High Availability and Resilience Design

## Status

Accepted

## Date

2025-03-10

## Context

LlamaCalc is designed to be an enterprise-grade calculator service. Enterprise environments require high availability, fault tolerance, and resilience to various types of failures. We need to design a system that can maintain operational integrity even during partial system failures, network issues, or high load conditions.

## Decision Drivers

- Requirement for 99.99% uptime (52.6 minutes of downtime per year)
- Need to handle component failures gracefully
- Ability to scale horizontally under load
- Requirement to maintain correctness during failure modes
- Recovery time objectives (RTO) of less than 30 seconds

## Decision

LlamaCalc will implement a comprehensive high availability and resilience design with the following key components:

1. **Stateless Service Architecture**: The core calculation service will be completely stateless
2. **Distributed Deployment**: Support for multi-node, multi-zone deployment
3. **Health Checking and Self-Healing**: Comprehensive health checking with automated recovery
4. **Circuit Breaking and Bulkheading**: Isolation of failures to prevent cascading issues
5. **Rate Limiting and Load Shedding**: Controlled degradation under extreme load
6. **Retry with Exponential Backoff**: Smart client retry mechanisms

## Rationale

### Stateless Service Architecture

A stateless design allows any instance to handle any request, enabling:

1. **Horizontal Scaling**: Add more instances to handle load
2. **No Session Affinity**: Clients can connect to any instance
3. **Simplified Recovery**: Failed nodes can be replaced without state transfer
4. **Zero Downtime Deployments**: Blue/green or rolling deployments

### Distributed Deployment

Multi-node, multi-zone deployment provides:

1. **Geographic Redundancy**: Protection against data center or zone failures
2. **Load Distribution**: Even distribution of traffic across regions
3. **Latency Optimization**: Clients connect to nearest zone
4. **Failover Capability**: Automatic redirection if a zone becomes unavailable

Implementation will use Kubernetes with pod anti-affinity rules to ensure distribution across nodes and zones.

### Health Checking and Self-Healing

Comprehensive health checking includes:

1. **Readiness Probes**: Determine if an instance can receive traffic
2. **Liveness Probes**: Detect and restart hung or deadlocked instances
3. **Dependency Checks**: Verify connections to dependent services
4. **Custom Health Metrics**: CPU, memory, goroutine count, etc.

```go
// Health check handler
func (s *Server) HealthCheck(context.Context, *pb.HealthCheckRequest) (*pb.HealthCheckResponse, error) {
    // Check all dependencies
    if !s.checkDependencies() {
        return &pb.HealthCheckResponse{Status: pb.HealthCheckResponse_NOT_SERVING}, nil
    }
    
    // Verify internal components
    if !s.checkInternalHealth() {
        return &pb.HealthCheckResponse{Status: pb.HealthCheckResponse_NOT_SERVING}, nil
    }
    
    return &pb.HealthCheckResponse{Status: pb.HealthCheckResponse_SERVING}, nil
}
```

### Circuit Breaking and Bulkheading

Failure isolation mechanisms:

1. **Circuit Breakers**: Fast-fail when dependencies are unhealthy
2. **Bulkheads**: Separate resource pools for different operations
3. **Timeouts**: Strict timeouts on all operations
4. **Fallbacks**: Degraded functionality when components are unavailable

### Rate Limiting and Load Shedding

Controlled degradation under load:

1. **Global Rate Limiting**: Cap on total request volume
2. **Per-Client Rate Limiting**: Prevents client monopolization
3. **Prioritization**: Higher priority for critical operations
4. **Graceful Rejection**: Clear error responses under overload

### Retry with Exponential Backoff

Client-side resilience:

1. **Smart Retries**: Only for idempotent operations or transient failures
2. **Exponential Backoff**: Increasing delay between retries
3. **Jitter**: Randomized delay to prevent thundering herd
4. **Retry Budgets**: Caps on retry attempts

## Implementation Details

### Deployment Architecture

Kubernetes deployment with:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llamacalc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llamacalc
  template:
    metadata:
      labels:
        app: llamacalc
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values:
                      - llamacalc
              topologyKey: "kubernetes.io/hostname"
```

### Health Checking Implementation

1. Kubernetes probes configuration
2. gRPC Health Checking Protocol implementation
3. Custom health metrics exposed via Prometheus

### Circuit Breaking Implementation

Using a circuit breaker pattern:

```go
// Circuit breaker implementation
type CircuitBreaker struct {
    failureThreshold int
    resetTimeout     time.Duration
    failureCount     int
    lastFailure      time.Time
    state            int // CLOSED, OPEN, HALF_OPEN
    mutex            sync.Mutex
}

func (cb *CircuitBreaker) Execute(command func() error) error {
    cb.mutex.Lock()
    state := cb.state
    cb.mutex.Unlock()
    
    if state == OPEN {
        if time.Since(cb.lastFailure) > cb.resetTimeout {
            // Try again in half-open state
            cb.mutex.Lock()
            cb.state = HALF_OPEN
            cb.mutex.Unlock()
        } else {
            return ErrCircuitOpen
        }
    }
    
    err := command()
    
    cb.mutex.Lock()
    defer cb.mutex.Unlock()
    
    if err != nil {
        cb.failureCount++
        cb.lastFailure = time.Now()
        
        if cb.state == HALF_OPEN || cb.failureCount >= cb.failureThreshold {
            cb.state = OPEN
        }
        return err
    }
    
    if cb.state == HALF_OPEN {
        cb.state = CLOSED
        cb.failureCount = 0
    }
    
    return nil
}
```

## Consequences

### Positive

- Ability to achieve 99.99% uptime target
- Graceful handling of partial system failures
- Linear scalability under increased load
- Automatic recovery from most failure conditions
- Protection against cascading failures

### Negative

- Increased operational complexity
- More complex testing requirements
- Higher resource overhead for redundancy
- Need for careful configuration

## Alternatives Considered

### Active-Passive Standby

Simpler but does not provide the same level of availability and requires complex state replication.

### Single Region Deployment

Would not meet geographic redundancy requirements and increases risk of regional outages.

### No Circuit Breaking

Simpler implementation but increases risk of cascading failures and system-wide outages.

## Related Documents

- [Performance Benchmarks](../performance.md)
- [Deployment Guide](../deployment.md) 