# 8. Resilience4j for Fault Tolerance

**Date:** 2024-01-15

## Status

Accepted

## Context

In a distributed microservices system, failures are inevitable:
- Network partitions
- Service degradation under load
- Transient errors from external APIs
- Cascading failures from one unhealthy service

Without fault tolerance patterns, a single failing service can bring down the entire platform. Traditional try-catch blocks are insufficient for handling distributed system failures.

## Decision

We adopt **Resilience4j** as our fault tolerance library with the following patterns:

### Circuit Breaker
Prevents calling a service that is likely to fail:
- **Closed**: Requests flow through normally
- **Open**: Requests fail fast without attempting the call
- **Half-Open**: Limited requests allowed to test recovery

Configuration based on failure rate and slow call thresholds.

### Rate Limiter
Protects services from being overwhelmed:
- Controls request rate per user/service
- Prevents resource exhaustion
- Enables fair usage policies

### Retry with Exponential Backoff
Handles transient failures gracefully:
- Configurable retry attempts
- Exponential backoff between retries
- Jitter to prevent thundering herd
- Excludes non-retryable errors (4xx)

### Bulkhead
Isolates failures to prevent cascade:
- Limits concurrent calls per downstream service
- Thread pool or semaphore based

### TimeLimiter
Prevents indefinite waits:
- Configurable timeout per operation
- Complements circuit breaker

### Decorator Order
```
Retry -> CircuitBreaker -> RateLimiter -> TimeLimiter -> Bulkhead
```

## Consequences

### Positive
- Graceful degradation instead of total failure
- Prevents cascading failures across services
- Auto-recovery when services become healthy
- Built-in observability with Micrometer metrics
- Idempotency enforced for retried operations

### Negative
- Additional configuration complexity
- Requires careful tuning per service interaction
- Fallback logic must be implemented
- Testing resilience patterns is non-trivial

### Mitigations
- Centralized configuration in common module
- WireMock for chaos testing scenarios
- Prometheus metrics for circuit breaker state
- Gradual tuning based on production behavior
