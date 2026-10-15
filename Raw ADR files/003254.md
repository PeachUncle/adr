# ADR-0014: Service Timeout & Retry Policy

## Status
Accepted

## Date
2025-11-17

## Context

PolyShop’s microservices communicate using:

- REST (synchronous, via API Gateway or internal service-to-service calls)
- Kafka events (asynchronous)
- External providers (Stripe, SMS gateway, email provider)

To ensure reliability, every call must follow consistent timeout, retry, and backoff rules.

Without unified rules:
- services fail differently under load
- cascading failures occur
- Sagas break unpredictably
- external provider throttling becomes likely

A platform-wide policy is required.

---

# Decision

PolyShop defines a **unified timeout + retry policy** for all internal and external calls.

The policy is split into:

1. REST → internal service  
2. REST → external providers  
3. Kafka consumer retry policy  
4. Circuit breaker rules  

---

# 1. REST → Internal Service Policy

### HttpClient settings

```

connectTimeout = 500ms
readTimeout = 2s
writeTimeout = 2s

```

### Retry Policy (idempotent requests only — GET, PUT)
```

maxRetries = 2
backoff = exponential (250ms, 500ms)
retryOn = connection failure, 5xx

```

### Non-idempotent requests (POST)
```

NO automatic retries
If needed → use Idempotency-Key header

```

### 504 Gateway Timeout

If a service exceeds 2 seconds it must:
- Cancel the upstream call
- Emit an error metric
- NOT retry automatically

---

# 2. REST → External Provider Policy

### Stripe, Email, SMS providers

```

connectTimeout = 1s
readTimeout = 5s
writeTimeout = 5s

```

### Retry rule (provider-safe)
```

maxRetries = 3
backoff = exponential (300ms, 900ms, 1800ms)

```

Retries permitted ONLY for:
- 429 (rate limit)
- 502/503/504 gateway errors
- network-level failures

Never retry:
- 400-series semantic errors (invalid params, card declined, etc.)

---

# 3. Kafka Consumer Retry Policy

### Processing failures

```

maxAttempts = 5
backoff = exponential (1s → 2s → 4s → 8s → 16s)

```

After 5 failures:
- message is moved to DLQ
- consumer logs structured error
- alert is triggered

### Poison message handling

Any deserialization error → immediate DLQ  
This prevents consumer lock-ups.

---

# 4. Circuit Breaker Policy

Every internal service call uses a **circuit breaker**:

```

failureThreshold = 50% of last 20 requests
openDuration = 5s
halfOpenTrialRequests = 3

```

If failures exceed threshold:
- circuit opens
- traffic stops flowing
- fallback handler returns 503
- monitoring logs circuit state

If the service recovers:
- circuit closes automatically

---

# Additional Notes

### Why 2-second read timeout for internal calls?
Because PolyShop is designed for fast, responsive API behavior.  
Any operation taking >2s should be moved to:
- background worker
- event-driven flow
- async Saga

### Saga compatibility
Timeouts and retries are tuned to avoid duplicate compensations.

### Observability
Each service must log:

- retry attempts
- timeout events
- circuit breaker state changes

Logs must include:
- requestId
- service name
- upstream target
- result (success/fail/retry)

---

# Consequences

### Benefits
- Predictable latency
- No cascading failures
- Clean integration with Sagas
- Protects external providers
- Fast failure detection

### Drawbacks
- Some long operations require redesign
- Strict timeouts may reject slow requests

---

# Final Decision

PolyShop adopts a **strict, unified timeout & retry strategy** to guarantee reliability and consistent behavior across all microservices and external integrations.
