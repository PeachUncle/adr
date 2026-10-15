# ADR-003: Multi-Layer Caching Strategy

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-013 (Redis)](./ADR-013-redis-caching.md), [ADR-004 (Repository Pattern)](./ADR-004-repository-pattern.md)

## Context

Sovren's backend was experiencing performance issues due to repeated database queries and expensive computations:

- **Database Load**: Same user data queried multiple times per request
- **NOSTR Events**: Relay queries expensive and slow (200-500ms per relay)
- **Lightning Invoices**: Payment status checks hitting Lightning node repeatedly
- **Analytics**: Complex aggregations recalculated on every page load
- **API Rate Limits**: External services (NOSTR relays, Lightning nodes) throttling requests

**Performance Impact**:
- Average response time: 800ms (target: <200ms)
- Database CPU: 85% (frequent queries for same data)
- Lightning node: 429 rate limit errors during peak usage
- NOSTR relay roundtrips adding 400ms latency per request

We needed a caching strategy that:
- Reduces database load by caching frequently accessed data
- Minimizes external API calls (NOSTR, Lightning)
- Provides fast access to computed results
- Supports different TTL strategies by data type
- Handles cache invalidation correctly

## Decision

We will implement a **multi-layer caching architecture** with in-memory L1 cache and Redis L2 cache.

**Architecture**:
```
Request → L1 (Memory) → L2 (Redis) → Database/External API
          ↑ 50-200ms      ↑ 1-5ms      ↑ 20-500ms
```

**Implementation**:
```typescript
@injectable()
class CacheService implements ICacheService {
  private memoryCache = new Map<string, CacheEntry>(); // L1
  private redisClient: Redis; // L2

  async get<T>(key: string): Promise<T | null> {
    // L1: Check memory cache first
    const memoryCached = this.memoryCache.get(key);
    if (memoryCached && !this.isExpired(memoryCached)) {
      return memoryCached.value as T;
    }

    // L2: Check Redis
    const redisCached = await this.redisClient.get(key);
    if (redisCached) {
      const value = JSON.parse(redisCached);

      // Populate L1 for next access
      this.memoryCache.set(key, {
        value,
        expiresAt: Date.now() + 60000 // 1 min in L1
      });

      return value;
    }

    return null;
  }

  async set<T>(key: string, value: T, ttl: number): Promise<void> {
    // Set in both layers
    this.memoryCache.set(key, {
      value,
      expiresAt: Date.now() + Math.min(ttl, 60000) // Max 1 min in L1
    });

    await this.redisClient.setex(key, ttl / 1000, JSON.stringify(value));
  }
}
```

**TTL Strategy by Data Type**:
```typescript
const CACHE_TTL = {
  // User data - moderate changes
  user_profile: 5 * 60 * 1000,      // 5 minutes
  user_settings: 10 * 60 * 1000,    // 10 minutes

  // Content - rarely changes
  content_metadata: 30 * 60 * 1000, // 30 minutes
  creator_profile: 15 * 60 * 1000,  // 15 minutes

  // Payments - short-lived
  lightning_invoice: 2 * 60 * 1000, // 2 minutes (status changes)
  payment_status: 1 * 60 * 1000,    // 1 minute

  // Analytics - expensive to compute
  analytics_daily: 60 * 60 * 1000,  // 1 hour
  analytics_realtime: 30 * 1000,    // 30 seconds

  // NOSTR - external API calls
  nostr_events: 5 * 60 * 1000,      // 5 minutes
  relay_metadata: 60 * 60 * 1000,   // 1 hour
};
```

**Cache Invalidation Patterns**:
```typescript
// Event-driven invalidation
class UserService {
  async updateProfile(userId: string, data: ProfileData) {
    await this.userRepo.update(userId, data);

    // Invalidate cache
    await this.cache.delete(`user:${userId}`);

    // Publish event for distributed invalidation
    await this.eventBus.publish({
      type: 'user.updated',
      payload: { userId }
    });
  }
}

// Tag-based invalidation
await cache.set('user:123', userData, TTL.user_profile, {
  tags: ['user', 'user:123']
});

// Invalidate all user caches
await cache.invalidateByTag('user');
```

## Consequences

### Positive

1. **Dramatic Performance Improvement**:
   - Response time: 800ms → 120ms (85% reduction)
   - Database CPU: 85% → 35% (50% reduction)
   - Lightning API calls reduced by 90%
   - NOSTR relay latency eliminated for cached events

2. **Cost Reduction**:
   - Fewer database queries = lower RDS costs
   - Reduced Lightning node API usage
   - Less NOSTR relay bandwidth
   - Can handle 10x traffic with same infrastructure

3. **Better User Experience**:
   - Sub-200ms response times for cached data
   - No delays from external API calls
   - Consistent performance under load

4. **Reduced External Dependencies**:
   - Less vulnerable to relay/Lightning node outages
   - Can serve stale data if external services down
   - Circuit breaker can use cached data as fallback

5. **Two-Layer Efficiency**:
   - L1 (memory): Ultra-fast for hot data (1-5ms)
   - L2 (Redis): Fast and persistent (10-20ms)
   - Auto-promotion of frequently accessed data to L1

### Negative

1. **Cache Consistency Complexity**:
   - Stale data if cache not invalidated properly
   - Race conditions between write and invalidation
   - Mitigation: Event-driven invalidation, short TTLs for critical data

2. **Memory Overhead**:
   - L1 cache consumes application memory
   - Risk of memory pressure under high load
   - Mitigation: LRU eviction, memory limits (max 100MB for L1)

3. **Debugging Difficulty**:
   - Hard to know if seeing cached vs fresh data
   - Cache state not visible in database
   - Mitigation: Cache headers in responses, cache monitoring dashboard

4. **Development Complexity**:
   - Developers must think about cache invalidation
   - Testing requires cache clearing between tests
   - Mitigation: Comprehensive developer guide, test utilities

5. **Cold Start Penalty**:
   - First request after deployment slower (cache empty)
   - Mitigation: Cache warming on startup for critical data

## Alternatives Considered

### 1. Database-Level Caching Only (PostgreSQL Query Cache)
**Pros**:
- No application code changes
- Automatic invalidation

**Cons**:
- Slower than in-memory cache (still hits database)
- Limited control over TTL
- Doesn't help with external API calls

**Why Rejected**: Doesn't address external API latency. Application-level cache provides more control.

### 2. CDN Caching (Cloudflare, Fastly)
**Pros**:
- Edge caching closer to users
- Reduces server load completely

**Cons**:
- Only works for HTTP GET requests
- Can't cache user-specific data
- Cost at scale
- Doesn't help with internal service calls

**Why Rejected**: Complementary to our strategy (we use CDN for static assets), but doesn't solve internal service caching needs.

### 3. Single-Layer Redis Only
**Pros**:
- Simpler architecture
- No memory management in app
- Persistent cache across restarts

**Cons**:
- Network overhead for every cache hit (5-10ms)
- Redis becomes bottleneck under high load
- Higher latency than in-memory

**Why Rejected**: Two-layer provides best of both worlds - ultra-fast L1 for hot data, persistent L2 for durability.

### 4. GraphQL with DataLoader
**Pros**:
- Automatic request batching
- Built-in caching per request

**Cons**:
- Requires GraphQL adoption
- Only caches within single request
- Doesn't persist between requests

**Why Rejected**: Would require major API rewrite. Our solution works with existing REST API.

## Implementation Notes

**Cache Key Conventions**:
```typescript
// Format: <domain>:<entity>:<id>[:<sub-resource>]
'user:123'
'user:123:profile'
'content:456'
'lightning:invoice:abc123'
'nostr:event:def456'
'analytics:daily:2025-10-27'
```

**Memory Limits**:
```typescript
class MemoryCache {
  private maxSize = 100 * 1024 * 1024; // 100MB
  private currentSize = 0;

  set(key: string, value: any) {
    const size = this.estimateSize(value);

    if (this.currentSize + size > this.maxSize) {
      this.evictLRU(); // Evict least recently used
    }

    this.cache.set(key, value);
    this.currentSize += size;
  }
}
```

**Cache Warming**:
```typescript
// On application startup
async function warmCache() {
  // Preload frequently accessed data
  await cacheService.warmup([
    { key: 'relay:metadata', fetcher: () => fetchRelayMetadata() },
    { key: 'analytics:top_creators', fetcher: () => fetchTopCreators() }
  ]);
}
```

**Performance Monitoring**:
```typescript
class CacheService {
  private metrics = {
    l1_hits: 0,
    l1_misses: 0,
    l2_hits: 0,
    l2_misses: 0
  };

  async get(key: string) {
    const l1 = this.memoryCache.get(key);
    if (l1) {
      this.metrics.l1_hits++;
      return l1;
    }
    this.metrics.l1_misses++;

    const l2 = await this.redis.get(key);
    if (l2) {
      this.metrics.l2_hits++;
      return l2;
    }
    this.metrics.l2_misses++;

    return null;
  }

  getHitRate() {
    const total = Object.values(this.metrics).reduce((a, b) => a + b, 0);
    const hits = this.metrics.l1_hits + this.metrics.l2_hits;
    return (hits / total) * 100;
  }
}
```

## Related Documentation

- [Caching Architecture Diagram](/docs/architecture/diagrams/epic-005-caching-strategy.mmd)
- [Redis Configuration Guide](/docs/deployment/redis-setup.md)
- [Performance Optimization Guide](/docs/development/performance-guide.md)
- [Cache Monitoring Dashboard](/docs/monitoring/cache-metrics.md)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
