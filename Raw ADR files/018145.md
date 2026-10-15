# ADR 006: Implementation of Circuit Breaker Pattern for External Integrations

## Status
Accepted

## Context
Our system integrates with multiple external services (PPL, Zásilkovna, eBay, Aukro, Stripe) which are critical for business operations but outside of our control. We need to ensure that:
- Failures in external services don't cascade through our system
- System remains responsive even when external services are degraded
- We can gracefully handle external service outages
- We maintain system stability during high load

## Decision
We will implement Circuit Breaker pattern for all external service integrations:

1. **Shipping Circuit Breaker**
   - Monitors failed requests to PPL and Zásilkovna
   - Opens circuit after threshold of failures
   - Provides fallback to cached shipping status
   - Implements half-open state for testing recovery

2. **Sales Circuit Breaker**
   - Protects integration with eBay and Aukro
   - Manages timeouts for listing operations
   - Monitors error rates
   - Implements graceful degradation of sales features

3. **Payment Circuit Breaker**
   - Critical protection for Stripe integration
   - Implements retry logic for failed payments
   - Ensures transaction consistency
   - Provides immediate failure notifications

## Consequences

### Positive
- Prevents cascade failures
- Improves system resilience
- Provides clear failure handling strategy
- Enables graceful degradation
- Improves monitoring capabilities

### Negative
- Increased complexity in integration layer
- Need for additional configuration management
- Requires careful threshold tuning
- May need periodic adjustment of timeout values

## Technical Details
- Implementation using resilience4j library
- Configuration per integration type:
  ```yaml
  circuitbreaker:
    shipping:
      failureRateThreshold: 50
      waitDurationInOpenState: 60s
      slidingWindowSize: 100
    sales:
      failureRateThreshold: 40
      waitDurationInOpenState: 30s
      slidingWindowSize: 50
    payment:
      failureRateThreshold: 25
      waitDurationInOpenState: 15s
      slidingWindowSize: 20
  ```

## Monitoring
- Circuit state changes are logged and monitored
- Metrics collected for:
  - Failure rates
  - Response times
  - Circuit state transitions
  - Fallback invocations

## Review Trigger
This decision should be reviewed if:
- External service reliability significantly changes
- New integration patterns are introduced
- Performance metrics indicate issues with current configuration
- Business requirements for availability change 