# ADR-013: Redis for Caching and Rate Limiting

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-003 (Multi-Layer Caching)](./ADR-003-multi-layer-caching.md), [ADR-012 (PostgreSQL)](./ADR-012-postgresql-supabase.md)

## Context

We needed a high-performance caching and rate limiting solution for:
- **Caching**: L2 cache for frequently accessed data (L1 is in-memory)
- **Rate Limiting**: Prevent API abuse and DoS attacks
- **Session Storage**: User sessions and temporary data
- **Job Queues**: Background job processing (future)
- **Pub/Sub**: Real-time messaging between services (future)

**Requirements**:
- Sub-millisecond read/write latency
- Persistence across server restarts
- TTL (time-to-live) support
- Atomic operations for rate limiting
- Data structure support (strings, hashes, sets, sorted sets)

## Decision

We will use **Redis 7.x** for caching, rate limiting, and session management.

**Implementation**:
```typescript
import { createClient } from 'redis';

const redis = createClient({
  url: process.env.REDIS_URL,
  socket: {
    reconnectStrategy: (retries) => Math.min(retries * 50, 500),
  },
});

await redis.connect();

// Caching
await redis.setEx('user:123', 300, JSON.stringify(userData)); // 5 min TTL
const cached = await redis.get('user:123');

// Rate limiting with sliding window
async function checkRateLimit(userId: string): Promise<boolean> {
  const key = `ratelimit:${userId}`;
  const now = Date.now();
  const windowMs = 60000; // 1 minute
  const maxRequests = 100;

  // Add current request
  await redis.zAdd(key, { score: now, value: `${now}` });

  // Remove requests outside window
  await redis.zRemRangeByScore(key, 0, now - windowMs);

  // Count requests in window
  const count = await redis.zCard(key);

  // Set expiry
  await redis.expire(key, 60);

  return count <= maxRequests;
}
```

**Use Cases**:
1. **L2 Cache**: Persistent cache layer (L1 is in-memory)
2. **Rate Limiting**: API request throttling
3. **Session Storage**: User authentication sessions
4. **Temporary Data**: Payment invoices, verification tokens
5. **Leaderboards**: Sorted sets for creator rankings

## Consequences

### Positive

1. **Ultra-Fast Performance**: 100,000+ ops/sec per core
   - Sub-millisecond latency (avg 0.5-2ms)
   - Much faster than database queries (20-100ms)

2. **Rich Data Structures**: Beyond key-value
   - Strings: Simple cache values
   - Hashes: User sessions, structured data
   - Sets: Tags, unique items
   - Sorted Sets: Leaderboards, time-series
   - Lists: Queues, recent items

3. **Built-in Expiration**: Automatic TTL management
   - No manual cleanup required
   - Memory automatically freed
   - Perfect for caching and sessions

4. **Atomic Operations**: Race-condition free
   - INCR, DECR for counters
   - GETSET for atomic updates
   - Lua scripts for complex atomicity

5. **Persistence Options**: Data survives restarts
   - RDB: Snapshot-based persistence
   - AOF: Append-only file for durability
   - Can configure for performance vs durability tradeoff

### Negative

1. **Memory Usage**: Data stored in RAM
   - More expensive than disk storage
   - Mitigation: Use eviction policies (LRU), monitor memory

2. **Single-Threaded**: One CPU core per Redis instance
   - Limited by single-core performance
   - Mitigation: Use Redis Cluster for scaling

3. **Persistence Tradeoff**: Durability vs performance
   - RDB: Fast but can lose minutes of data
   - AOF: Durable but slower writes
   - Mitigation: Choose based on data criticality

4. **Operational Complexity**: Another service to manage
   - Need monitoring, backups, failover
   - Mitigation: Use managed Redis (Redis Cloud, AWS ElastiCache)

## Alternatives Considered

### 1. Memcached
**Pros**:
- Simpler than Redis
- Multi-threaded (uses multiple cores)
- Slightly faster for simple key-value

**Cons**:
- Only supports strings (no data structures)
- No persistence (data lost on restart)
- Limited features (no pub/sub, no Lua scripts)

**Why Rejected**: Need data structures for rate limiting, sorted sets for leaderboards. Persistence important for sessions.

### 2. In-Memory Only (No L2 Cache)
**Pros**:
- Simplest solution
- No additional infrastructure
- Zero latency

**Cons**:
- Lost on server restart
- Not shared across instances
- Limited by process memory

**Why Rejected**: Need persistent cache across deployments and shared cache for multiple server instances.

### 3. Database for Caching
**Pros**:
- One less service to manage
- Persistent by default

**Cons**:
- Too slow (20-100ms vs <1ms)
- Wastes database resources
- Defeats purpose of caching

**Why Rejected**: Performance not acceptable. Cache should be faster than source.

### 4. DynamoDB (AWS)
**Pros**:
- Serverless, auto-scaling
- Good for AWS deployments
- Strong consistency option

**Cons**:
- Higher latency (5-20ms)
- Vendor lock-in to AWS
- More expensive than Redis
- Limited data structure support

**Why Rejected**: Higher latency and cost. Redis faster and more versatile.

## Implementation Notes

**Connection Management**:
```typescript
class RedisService {
  private client: RedisClient;
  private isConnected = false;

  async connect() {
    if (!this.isConnected) {
      await this.client.connect();
      this.isConnected = true;
    }
  }

  async disconnect() {
    if (this.isConnected) {
      await this.client.quit();
      this.isConnected = false;
    }
  }

  async get<T>(key: string): Promise<T | null> {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }

  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    const serialized = JSON.stringify(value);
    if (ttl) {
      await this.client.setEx(key, ttl, serialized);
    } else {
      await this.client.set(key, serialized);
    }
  }
}
```

**Rate Limiting Middleware**:
```typescript
function rateLimitMiddleware(options: RateLimitOptions) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const identifier = req.user?.id || req.ip;
    const allowed = await checkRateLimit(identifier);

    if (!allowed) {
      return res.status(429).json({
        error: 'Too many requests',
        retryAfter: 60,
      });
    }

    next();
  };
}

app.use('/api', rateLimitMiddleware({
  windowMs: 60000,
  maxRequests: 100,
}));
```

**Cache Invalidation Patterns**:
```typescript
// Tag-based invalidation
class CacheService {
  async setWithTags(key: string, value: any, ttl: number, tags: string[]) {
    await this.redis.setEx(key, ttl, JSON.stringify(value));

    // Add key to each tag set
    for (const tag of tags) {
      await this.redis.sAdd(`tag:${tag}`, key);
    }
  }

  async invalidateByTag(tag: string) {
    // Get all keys with this tag
    const keys = await this.redis.sMembers(`tag:${tag}`);

    // Delete all keys
    if (keys.length > 0) {
      await this.redis.del(keys);
    }

    // Delete tag set
    await this.redis.del(`tag:${tag}`);
  }
}

// Example usage
await cache.setWithTags('user:123', userData, 300, ['user', 'user:123']);

// Invalidate all user caches
await cache.invalidateByTag('user');
```

**Monitoring**:
```typescript
// Monitor Redis health
setInterval(async () => {
  const info = await redis.info('stats');
  const metrics = parseRedisInfo(info);

  console.log('Redis Metrics:', {
    connectedClients: metrics.connected_clients,
    usedMemory: metrics.used_memory_human,
    hitRate: (metrics.keyspace_hits / (metrics.keyspace_hits + metrics.keyspace_misses)) * 100,
    opsPerSec: metrics.instantaneous_ops_per_sec,
  });
}, 60000);
```

## Configuration

**Production Configuration**:
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # Evict least recently used keys
save 900 1                     # Snapshot every 15 min if ≥1 change
save 300 10                    # Snapshot every 5 min if ≥10 changes
save 60 10000                  # Snapshot every 1 min if ≥10000 changes
appendonly yes                 # Enable AOF for durability
appendfsync everysec          # Sync AOF every second (balance)
```

## Related Documentation

- [Redis Documentation](https://redis.io/docs/)
- [Caching Strategy](/docs/architecture/diagrams/epic-005-caching-strategy.mmd)
- [Rate Limiting Guide](/docs/api/rate-limiting.md)
- [Performance Optimization](/docs/development/performance-guide.md)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
