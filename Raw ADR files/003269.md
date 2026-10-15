# ADR-004: Multi-Layer Caching Strategy

## Status
Accepted - December 2024

## Context
Application requires sub-50ms response times for 90% of requests while handling 10,000 requests/second during peak traffic. Database queries are becoming a bottleneck.

## Problem
- Database CPU hitting 80% during peak hours
- Average API response time: 250ms
- Cache miss rate: 45%
- No cache invalidation strategy
- Memory usage unpredictable

## Decision
Implement **multi-layer caching strategy** with:
1. **L1 Cache**: Application in-memory (Node.js)
2. **L2 Cache**: Redis distributed cache
3. **L3 Cache**: CDN for static assets

## Architecture

```typescript
// Multi-layer cache implementation
import Redis from 'ioredis';
import NodeCache from 'node-cache';

interface CacheConfig {
  l1TTL: number;      // L1 cache TTL in seconds
  l2TTL: number;      // L2 cache TTL in seconds
  maxL1Size: number;  // Max L1 cache entries
}

class MultiLayerCache {
  private l1Cache: NodeCache;
  private l2Cache: Redis;
  private config: CacheConfig;

  constructor(config: CacheConfig) {
    this.config = config;

    // L1: In-memory cache
    this.l1Cache = new NodeCache({
      stdTTL: config.l1TTL,
      checkperiod: 60,
      maxKeys: config.maxL1Size,
      useClones: false
    });

    // L2: Redis cache
    this.l2Cache = new Redis({
      host: process.env.REDIS_HOST,
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      retryStrategy: (times) => Math.min(times * 50, 2000),
      enableReadyCheck: true,
      maxRetriesPerRequest: 3
    });
  }

  async get<T>(key: string): Promise<T | null> {
    // Try L1 cache first
    const l1Value = this.l1Cache.get<T>(key);
    if (l1Value !== undefined) {
      this.recordMetric('cache.hit.l1', 1);
      return l1Value;
    }

    // Try L2 cache
    try {
      const l2Value = await this.l2Cache.get(key);
      if (l2Value) {
        this.recordMetric('cache.hit.l2', 1);
        const parsed = JSON.parse(l2Value) as T;

        // Populate L1 cache
        this.l1Cache.set(key, parsed);
        return parsed;
      }
    } catch (error) {
      console.error('L2 cache error:', error);
      this.recordMetric('cache.error.l2', 1);
    }

    this.recordMetric('cache.miss', 1);
    return null;
  }

  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    const l2TTL = ttl || this.config.l2TTL;

    // Set in both caches
    this.l1Cache.set(key, value, this.config.l1TTL);

    try {
      await this.l2Cache.setex(
        key,
        l2TTL,
        JSON.stringify(value)
      );
    } catch (error) {
      console.error('L2 cache set error:', error);
      this.recordMetric('cache.error.l2.set', 1);
    }
  }

  async delete(key: string): Promise<void> {
    this.l1Cache.del(key);
    await this.l2Cache.del(key);
  }

  async invalidatePattern(pattern: string): Promise<void> {
    // Clear L1 cache matching pattern
    const l1Keys = this.l1Cache.keys();
    l1Keys.forEach(key => {
      if (key.match(pattern)) {
        this.l1Cache.del(key);
      }
    });

    // Clear L2 cache matching pattern
    const stream = this.l2Cache.scanStream({
      match: pattern,
      count: 100
    });

    stream.on('data', async (keys: string[]) => {
      if (keys.length) {
        const pipeline = this.l2Cache.pipeline();
        keys.forEach(key => pipeline.del(key));
        await pipeline.exec();
      }
    });
  }

  private recordMetric(metric: string, value: number): void {
    // Send to monitoring system
    // Implementation depends on your monitoring solution
  }
}

// Usage example
const cache = new MultiLayerCache({
  l1TTL: 60,           // 1 minute
  l2TTL: 3600,         // 1 hour
  maxL1Size: 1000
});

// In your service layer
class ProductService {
  async getProduct(id: string): Promise<Product> {
    const cacheKey = `product:${id}`;

    // Try cache first
    let product = await cache.get<Product>(cacheKey);
    if (product) {
      return product;
    }

    // Cache miss - fetch from database
    product = await this.db.products.findById(id);

    if (product) {
      // Cache for future requests
      await cache.set(cacheKey, product);
    }

    return product;
  }

  async updateProduct(id: string, data: Partial<Product>): Promise<Product> {
    const product = await this.db.products.update(id, data);

    // Invalidate cache
    await cache.delete(`product:${id}`);

    // Invalidate related caches
    await cache.invalidatePattern(`product:*:related:${id}`);
    await cache.invalidatePattern(`category:${product.categoryId}:*`);

    return product;
  }
}
```

## Cache Invalidation Strategies

### 1. Time-Based (TTL)
```typescript
// Short TTL for frequently changing data
await cache.set('stock:item123', stockData, 30); // 30 seconds

// Long TTL for rarely changing data
await cache.set('category:list', categories, 86400); // 24 hours
```

### 2. Event-Based
```typescript
// Invalidate on domain events
eventBus.on('product.updated', async (event) => {
  await cache.delete(`product:${event.productId}`);
  await cache.invalidatePattern(`search:*`);
});

eventBus.on('inventory.changed', async (event) => {
  await cache.delete(`stock:${event.productId}`);
});
```

### 3. Write-Through
```typescript
async updateProduct(id: string, data: Partial<Product>): Promise<Product> {
  // Update database
  const product = await this.db.products.update(id, data);

  // Immediately update cache
  await cache.set(`product:${id}`, product);

  return product;
}
```

## Redis Configuration

```conf
# redis.conf - Production Configuration

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Replication
repl-diskless-sync yes
repl-diskless-sync-delay 5

# Security
requirepass ${REDIS_PASSWORD}
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG "CONFIG_${RANDOM_STRING}"

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
slowlog-log-slower-than 10000
slowlog-max-len 128

# Cluster
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
```

## Monitoring Metrics

```typescript
// Key metrics to track
interface CacheMetrics {
  l1HitRate: number;
  l2HitRate: number;
  overallHitRate: number;
  avgResponseTime: number;
  evictionRate: number;
  memoryUsage: number;
}

class CacheMonitor {
  async getMetrics(): Promise<CacheMetrics> {
    const l1Stats = this.l1Cache.getStats();
    const l2Info = await this.l2Cache.info('stats');

    return {
      l1HitRate: l1Stats.hits / (l1Stats.hits + l1Stats.misses),
      l2HitRate: this.calculateL2HitRate(l2Info),
      overallHitRate: this.calculateOverallHitRate(),
      avgResponseTime: this.getAvgResponseTime(),
      evictionRate: l1Stats.vsize / l1Stats.ksize,
      memoryUsage: await this.getMemoryUsage()
    };
  }
}
```

## Performance Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Response Time | 250ms | 45ms | 82% faster |
| P95 Response Time | 800ms | 120ms | 85% faster |
| Database CPU | 80% | 35% | 56% reduction |
| Cache Hit Rate | 45% | 94% | 109% increase |
| Requests/sec | 2,000 | 12,000 | 6x throughput |

## Consequences

### Positive
- 82% reduction in response time
- 6x increase in throughput
- 56% reduction in database load
- Better user experience
- Lower infrastructure costs

### Negative
- Added complexity in cache invalidation
- Memory costs for Redis cluster
- Potential cache consistency issues
- Monitoring overhead

## Implementation Checklist
- [x] Deploy Redis cluster (3 masters, 3 replicas)
- [x] Implement multi-layer cache client
- [x] Add cache warming for critical data
- [x] Set up cache monitoring dashboards
- [x] Document cache invalidation patterns
- [x] Load test cache performance
- [x] Implement circuit breakers for Redis failures

## Related ADRs
- ADR-002: Database Strategy (planned)
- ADR-005: Comprehensive Observability Strategy
- ADR-007: Event-Driven Architecture

## References
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [Caching Strategies and Patterns](https://aws.amazon.com/caching/)
