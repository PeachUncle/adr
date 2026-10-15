# ADR-014: Circuit Breaker Pattern for External Services

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-005 (Lightning Network)](./ADR-005-lightning-network-payments.md), [ADR-003 (Caching)](./ADR-003-multi-layer-caching.md)

## Context

Sovren depends on external services that can fail or become slow:
- **Lightning Network Nodes**: Can be temporarily unavailable
- **NOSTR Relays**: Public relays often have downtime
- **Webhook Deliveries**: Third-party endpoints may be down
- **Email Service**: SendGrid/Mailgun can have outages

**Problem**: When external services fail, our application:
- Times out on every request (30+ seconds)
- Exhausts connection pools
- Cascading failures affect entire system
- Poor user experience (long loading times)
- Waste resources on doomed requests

We needed a resilience pattern to:
- Fail fast when external service is down
- Prevent cascading failures
- Automatically recover when service returns
- Provide graceful degradation

## Decision

We will implement the **Circuit Breaker Pattern** for all external service calls using the `opossum` library.

**Circuit States**:
1. **Closed** (Normal): Requests flow through normally
2. **Open** (Failed): Fast-fail without calling service (return error immediately)
3. **Half-Open** (Testing): Try one request to test if service recovered

**Implementation**:
```typescript
import CircuitBreaker from 'opossum';

// Lightning service with circuit breaker
const lightningCircuitBreaker = new CircuitBreaker(
  async (params: InvoiceParams) => {
    return await lndClient.addInvoice(params);
  },
  {
    timeout: 3000,           // Fail after 3 seconds
    errorThresholdPercentage: 50, // Open after 50% failures
    resetTimeout: 30000,     // Try again after 30 seconds
    rollingCountTimeout: 10000,   // Track last 10 seconds
    volumeThreshold: 5,      // Need 5 requests before opening
    name: 'lightning-node',
  }
);

// Use circuit breaker
class LightningService {
  async createInvoice(params: InvoiceParams): Promise<Invoice> {
    try {
      return await lightningCircuitBreaker.fire(params);
    } catch (error) {
      if (lightningCircuitBreaker.opened) {
        // Circuit is open - service is down
        // Return cached invoice or use fallback node
        return this.useFallbackNode(params);
      }
      throw error;
    }
  }

  private async useFallbackNode(params: InvoiceParams): Promise<Invoice> {
    // Try backup Lightning node
    return await backupLightningNode.createInvoice(params);
  }
}

// Monitor circuit breaker state
lightningCircuitBreaker.on('open', () => {
  logger.error('Lightning node circuit OPENED - service degraded');
  metrics.increment('circuit_breaker.open', { service: 'lightning' });
});

lightningCircuitBreaker.on('halfOpen', () => {
  logger.warn('Lightning node circuit HALF-OPEN - testing recovery');
});

lightningCircuitBreaker.on('close', () => {
  logger.info('Lightning node circuit CLOSED - service recovered');
  metrics.increment('circuit_breaker.close', { service: 'lightning' });
});
```

**Webhook Circuit Breaker**:
```typescript
// Webhook delivery with circuit breaker per domain
class WebhookService {
  private breakers = new Map<string, CircuitBreaker>();

  private getBreaker(url: string): CircuitBreaker {
    const domain = new URL(url).hostname;

    if (!this.breakers.has(domain)) {
      const breaker = new CircuitBreaker(
        async (webhookUrl: string, payload: any) => {
          return await fetch(webhookUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
        },
        {
          timeout: 5000,
          errorThresholdPercentage: 75,
          resetTimeout: 60000,
          name: `webhook-${domain}`,
        }
      );

      this.breakers.set(domain, breaker);
    }

    return this.breakers.get(domain)!;
  }

  async sendWebhook(url: string, payload: any): Promise<void> {
    const breaker = this.getBreaker(url);

    try {
      await breaker.fire(url, payload);
    } catch (error) {
      if (breaker.opened) {
        // Circuit open - queue for retry later
        await this.queueForRetry(url, payload);
      } else {
        throw error;
      }
    }
  }
}
```

## Consequences

### Positive

1. **Fast Failure**: Don't wait 30s for timeout when service is down
   - Response time: 30s → 50ms when circuit open
   - Better user experience
   - Frees up resources immediately

2. **Prevents Cascading Failures**: Isolates failing service
   - Lightning node down doesn't crash entire app
   - Other features continue working
   - System remains responsive

3. **Automatic Recovery**: Tests service periodically
   - No manual intervention needed
   - Service automatically resumes when recovered
   - Half-open state prevents thundering herd

4. **Graceful Degradation**: Fallback strategies
   - Use cached data when service unavailable
   - Try backup service (secondary Lightning node)
   - Show user-friendly error messages

5. **Observability**: Circuit events enable monitoring
   - Know immediately when service degrades
   - Track failure patterns
   - Alert on circuit opens

### Negative

1. **Complexity**: Additional abstraction layer
   - More code to understand and maintain
   - Mitigation: Centralize circuit breaker config

2. **False Positives**: May open during temporary spikes
   - Mitigation: Tune thresholds based on metrics
   - Volume threshold prevents opening on single failure

3. **State Management**: Circuit state per service instance
   - Circuit state not shared across servers
   - Mitigation: Each instance protects itself, acceptable

## Alternatives Considered

### 1. Simple Timeout + Retry
**Pros**: Simpler implementation

**Cons**:
- Still wastes time on retries
- No learning from failures
- Can make problem worse (retry storm)

**Why Rejected**: Doesn't prevent cascading failures or provide fast failure.

### 2. Manual Service Disable
**Pros**: Full control

**Cons**:
- Requires human intervention
- Slow response to incidents
- Risk of forgetting to re-enable

**Why Rejected**: Circuit breaker automates this with faster response.

### 3. Load Balancer Health Checks
**Pros**: Infrastructure-level solution

**Cons**:
- Only works for our own services
- Can't help with external APIs
- Removes server entirely (too aggressive)

**Why Rejected**: Need application-level control for external services.

## Implementation Notes

**Configuration by Service Type**:
```typescript
const CIRCUIT_BREAKER_CONFIG = {
  lightning: {
    timeout: 3000,
    errorThresholdPercentage: 50,
    resetTimeout: 30000,
  },
  nostr_relay: {
    timeout: 5000,
    errorThresholdPercentage: 75,  // More tolerant
    resetTimeout: 60000,
  },
  webhook: {
    timeout: 5000,
    errorThresholdPercentage: 80,  // Very tolerant
    resetTimeout: 120000,
  },
  email: {
    timeout: 10000,
    errorThresholdPercentage: 50,
    resetTimeout: 60000,
  },
};
```

**Fallback Strategies**:
```typescript
class ResilientService {
  async getData(id: string): Promise<Data> {
    try {
      return await this.circuitBreaker.fire(id);
    } catch (error) {
      if (this.circuitBreaker.opened) {
        // Try fallback strategies in order
        return await this.withFallback(id, [
          () => this.cache.get(id),           // 1. Try cache
          () => this.backupService.get(id),   // 2. Try backup service
          () => this.defaultValue(id),        // 3. Return safe default
        ]);
      }
      throw error;
    }
  }

  private async withFallback(
    id: string,
    strategies: (() => Promise<Data | null>)[]
  ): Promise<Data> {
    for (const strategy of strategies) {
      try {
        const result = await strategy();
        if (result) return result;
      } catch (e) {
        continue;
      }
    }
    throw new Error('All fallback strategies failed');
  }
}
```

**Monitoring Dashboard**:
```typescript
// Expose circuit breaker metrics
app.get('/health/circuit-breakers', (req, res) => {
  const states = {
    lightning: {
      state: lightningBreaker.opened ? 'open' : 'closed',
      stats: lightningBreaker.stats,
    },
    nostr: {
      state: nostrBreaker.opened ? 'open' : 'closed',
      stats: nostrBreaker.stats,
    },
    // ... other services
  };

  res.json(states);
});
```

## Related Documentation

- [Opossum Documentation](https://nodeshift.dev/opossum/)
- [Resilience Patterns](/docs/architecture/resilience-patterns.md)
- [Service Dependencies](/docs/architecture/diagrams/epic-005-service-dependencies.mmd)
- [Monitoring Guide](/docs/monitoring/circuit-breakers.md)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
