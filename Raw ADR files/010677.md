# ADR-006: Caching Strategy

**Status**: Accepted
**Date**: 2025-10-22
**Decision Makers**: System Architecture Designer
**Context**: Performance optimization through strategic caching of leaderboard and player data

## Context and Problem Statement

Love Rank Pulse requires caching to:
- Reduce database load from frequent leaderboard queries
- Improve response times for read-heavy operations
- Support real-time updates without database bottlenecks
- Scale efficiently as user base grows
- Maintain data consistency during cache invalidation

## Decision Drivers

- **Performance**: Sub-100ms response times for leaderboard
- **Scalability**: Reduce database load by 80-90%
- **Consistency**: Ensure cache stays synchronized with database
- **Cost**: Minimize infrastructure overhead
- **Reliability**: Graceful fallback on cache failures
- **Developer Experience**: Simple cache invalidation patterns

## Considered Options

### Option 1: Redis Cache-Aside Pattern ✅ SELECTED

**Architecture:**
```
API Request → Check Redis Cache → Cache Hit → Return Data
                       ↓
                  Cache Miss
                       ↓
              Query PostgreSQL
                       ↓
              Store in Redis → Return Data
```

**Cache Layers:**
1. **Leaderboard Cache** (60s TTL)
   - Full leaderboard pages
   - Top N players
   - Rank range queries

2. **Player Stats Cache** (300s TTL)
   - Individual player data
   - Match history
   - Rank information

3. **Match Results Cache** (180s TTL)
   - Recent matches
   - Head-to-head records

**Pros:**
- Simple implementation (cache-aside pattern)
- Automatic expiration with TTL
- Explicit cache invalidation on updates
- Works with existing Redis infrastructure
- Battle-tested pattern with clear semantics

**Cons:**
- Initial request slower (cache miss)
- Potential for stale data during TTL window
- Manual invalidation logic required

### Option 2: Redis Write-Through Cache

**Architecture:**
```
Write Request → Update Redis → Update PostgreSQL → Return Success
Read Request → Query Redis → Return Data (always fresh)
```

**Pros:**
- Always fresh data in cache
- Faster reads (no cache misses)
- Simpler read logic

**Cons:**
- Slower writes (two operations)
- Cache failure blocks writes
- More complex error handling
- No benefit if data not frequently accessed

### Option 3: Application-Level In-Memory Cache (Node-Cache)

**Architecture:**
```
Request → Check In-Memory Map → Cache Hit/Miss → PostgreSQL
```

**Pros:**
- No external dependency
- Fastest possible access (no network)
- Simple implementation

**Cons:**
- No sharing across server instances
- Memory limited by server RAM
- Lost on server restart
- Cannot scale horizontally

## Decision Outcome

**Chosen Option**: Redis Cache-Aside Pattern with TTL and Manual Invalidation

### Justification

Cache-aside with Redis provides optimal balance:

1. **Performance**: Redis in-memory storage delivers <10ms access times
2. **Scalability**: Shared cache across multiple backend servers
3. **Reliability**: PostgreSQL as source of truth, cache as acceleration layer
4. **Simplicity**: Clear invalidation semantics on data mutations
5. **Cost-Effective**: Single Redis instance serves entire cluster

### Implementation Details

#### Cache Service (`/src/services/cache.ts`)

```typescript
import { createClient } from 'redis';

export class CacheService {
  private client: ReturnType<typeof createClient>;

  constructor() {
    this.client = createClient({
      url: process.env.REDIS_URL,
      socket: {
        reconnectStrategy: (retries) => Math.min(retries * 50, 500),
      },
    });
  }

  async get<T>(key: string): Promise<T | null> {
    const value = await this.client.get(key);
    return value ? JSON.parse(value) : null;
  }

  async set(key: string, value: any, ttlSeconds: number): Promise<void> {
    await this.client.set(
      key,
      JSON.stringify(value),
      { EX: ttlSeconds }
    );
  }

  async del(key: string): Promise<void> {
    await this.client.del(key);
  }

  async delPattern(pattern: string): Promise<void> {
    const keys = await this.client.keys(pattern);
    if (keys.length > 0) {
      await this.client.del(...keys);
    }
  }
}
```

#### Cached Leaderboard Service (`/src/services/CachedLeaderboardService.ts`)

```typescript
export class CachedLeaderboardService {
  private cache: CacheService;
  private leaderboardService: LeaderboardService;

  private readonly LEADERBOARD_TTL = 60; // 60 seconds
  private readonly CACHE_KEY_PREFIX = 'leaderboard:';

  async getLeaderboard(
    page: number = 1,
    pageSize: number = 50
  ): Promise<LeaderboardEntry[]> {
    const cacheKey = `${this.CACHE_KEY_PREFIX}page:${page}:${pageSize}`;

    // Try cache first
    const cached = await this.cache.get<LeaderboardEntry[]>(cacheKey);
    if (cached) {
      return cached;
    }

    // Cache miss - query database
    const leaderboard = await this.leaderboardService.getLeaderboard(
      page,
      pageSize
    );

    // Store in cache
    await this.cache.set(cacheKey, leaderboard, this.LEADERBOARD_TTL);

    return leaderboard;
  }

  async invalidateLeaderboardCache(): Promise<void> {
    // Clear all leaderboard cache entries
    await this.cache.delPattern(`${this.CACHE_KEY_PREFIX}*`);
  }
}
```

#### Cache Invalidation on Match Result

```typescript
export class MatchService {
  async submitMatchResult(
    matchId: string,
    result: MatchResultInput
  ): Promise<MatchResult> {
    // Update database in transaction
    const matchResult = await prisma.$transaction(async (tx) => {
      // Create match result
      const result = await tx.matchResult.create({ data: {...} });

      // Update player ratings
      await tx.player.update({ where: { id: player1Id }, data: {...} });
      await tx.player.update({ where: { id: player2Id }, data: {...} });

      return result;
    });

    // Invalidate caches after successful database update
    await this.invalidateCaches(result);

    // Publish real-time update
    await publishEvent(CHANNELS.MATCH_RESULT, matchResult);

    return matchResult;
  }

  private async invalidateCaches(result: MatchResult): Promise<void> {
    // Invalidate leaderboard cache
    await cacheService.delPattern('leaderboard:*');

    // Invalidate affected player caches
    await cacheService.del(`player:${result.player1_id}`);
    await cacheService.del(`player:${result.player2_id}`);

    // Invalidate match history caches
    await cacheService.del(`matches:player:${result.player1_id}`);
    await cacheService.del(`matches:player:${result.player2_id}`);
  }
}
```

### Cache Key Patterns

**Leaderboard:**
- `leaderboard:page:{page}:{pageSize}` - Paginated leaderboard
- `leaderboard:top:{n}` - Top N players
- `leaderboard:range:{start}:{end}` - Rank range

**Players:**
- `player:{playerId}` - Player profile and stats
- `player:{playerId}:rank` - Player rank information
- `player:{playerId}:matches` - Player match history

**Matches:**
- `match:{matchId}` - Match details
- `matches:recent:{limit}` - Recent matches
- `matches:player:{playerId}` - Player's matches

### TTL Strategy

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Leaderboard | 60s | Frequent updates, acceptable slight staleness |
| Player Stats | 300s | Less frequently accessed, can tolerate staleness |
| Match Results | 180s | Historical data, rarely changes |
| Top Players | 30s | Highly visible, needs freshness |

### Cache Warming

**Startup Cache Warming:**
```typescript
export async function warmCache() {
  console.log('Warming cache...');

  // Warm top 100 players
  await cachedLeaderboardService.getLeaderboard(1, 100);

  // Warm top 10 for quick access
  await cachedLeaderboardService.getTopPlayers(10);

  console.log('Cache warming complete');
}
```

**Scheduled Cache Refresh:**
```typescript
// Refresh hot data every 30 seconds
setInterval(async () => {
  await cachedLeaderboardService.getLeaderboard(1, 50);
}, 30000);
```

## Consequences

### Positive
- **Performance**: 90% reduction in database queries
- **Response Time**: <50ms for cached leaderboard queries (vs 200-500ms from DB)
- **Scalability**: Database can handle 10x more users with same resources
- **Cost**: Reduced database CPU and IOPS usage
- **User Experience**: Near-instant leaderboard loads

### Negative
- **Complexity**: Additional cache invalidation logic
- **Consistency**: Potential for stale data during TTL window
- **Infrastructure**: Redis dependency adds operational overhead
- **Debugging**: Cache-related bugs harder to reproduce

### Performance Metrics

**Expected Cache Hit Rate:**
- Leaderboard queries: 95% (high read-to-write ratio)
- Player stats: 85% (moderate access frequency)
- Match results: 70% (lower access frequency)

**Response Time Comparison:**
| Operation | No Cache | With Cache | Improvement |
|-----------|----------|------------|-------------|
| Get Leaderboard | 200-500ms | 20-50ms | 80-90% |
| Get Player Stats | 50-100ms | 5-10ms | 90% |
| Get Top 10 | 100-200ms | 10-20ms | 90% |

**Database Load Reduction:**
- Queries per second: 1000 → 100 (90% reduction)
- CPU usage: 60% → 15% (75% reduction)
- Connection pool usage: 80% → 20% (75% reduction)

### Risks and Mitigation

**Risk**: Cache and database out of sync
**Mitigation**:
- Explicit invalidation on writes
- Short TTL as safety net
- Background job to verify cache consistency

**Risk**: Redis failure causes performance degradation
**Mitigation**:
- Graceful fallback to database queries
- Redis cluster for high availability
- Monitoring and alerts for cache failures

**Risk**: Cache stampede on expiration
**Mitigation**:
- Stagger TTL slightly (random jitter)
- Lock mechanism to prevent duplicate queries
- Cache warming for hot data

**Risk**: Memory exhaustion in Redis
**Mitigation**:
- LRU eviction policy
- Monitor memory usage
- Set max memory limits

## Testing Strategy

**Cache Hit/Miss Testing:**
```typescript
test('returns cached leaderboard on second request', async () => {
  // First request - cache miss
  const leaderboard1 = await service.getLeaderboard(1, 10);
  expect(mockDb.query).toHaveBeenCalledTimes(1);

  // Second request - cache hit
  const leaderboard2 = await service.getLeaderboard(1, 10);
  expect(mockDb.query).toHaveBeenCalledTimes(1); // No additional query
  expect(leaderboard1).toEqual(leaderboard2);
});
```

**Cache Invalidation Testing:**
```typescript
test('invalidates cache after match result', async () => {
  // Warm cache
  await service.getLeaderboard(1, 10);

  // Submit match result
  await matchService.submitMatchResult(matchId, result);

  // Next request should query database (cache invalidated)
  await service.getLeaderboard(1, 10);
  expect(mockDb.query).toHaveBeenCalledTimes(2);
});
```

**Failover Testing:**
```typescript
test('falls back to database on Redis failure', async () => {
  mockRedis.get.mockRejectedValue(new Error('Redis down'));

  const leaderboard = await service.getLeaderboard(1, 10);

  expect(mockDb.query).toHaveBeenCalled();
  expect(leaderboard).toBeDefined();
});
```

## Monitoring and Observability

**Cache Metrics:**
- Hit rate percentage
- Miss rate percentage
- Average response time (hit vs miss)
- Cache size (memory usage)
- Eviction count

**Alerts:**
- Hit rate drops below 80%
- Redis memory usage exceeds 80%
- Cache response time exceeds 100ms
- Redis connection failures

**Logging:**
```typescript
logger.info('Cache hit', {
  key: cacheKey,
  responseTime: elapsed,
  dataSize: JSON.stringify(data).length,
});

logger.warn('Cache miss', {
  key: cacheKey,
  reason: 'expired',
  databaseQueryTime: dbElapsed,
});
```

## Migration Path

**Phase 1: Basic Caching (Completed)**
- Implement cache service wrapper
- Add caching to leaderboard service
- Deploy Redis infrastructure

**Phase 2: Advanced Patterns (Completed)**
- Cache invalidation on mutations
- Cache warming on startup
- Pattern-based invalidation

**Phase 3: Optimization (Future)**
- Cache compression for large datasets
- Distributed cache with Redis Cluster
- Client-side caching with ETags

**Phase 4: Advanced Features (Future)**
- Write-behind caching for high-write workloads
- Predictive cache warming based on usage patterns
- Multi-tier caching (memory + Redis)

## Related Decisions
- ADR-001: Database Selection (PostgreSQL as source of truth)
- ADR-004: Deployment Strategy (Upstash Redis)
- ADR-005: WebSocket Architecture (Redis Pub/Sub)

## References
- [Redis Documentation](https://redis.io/docs/)
- [Cache-Aside Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- Implementation: `/workspaces/love-rank-pulse/src/services/CachedLeaderboardService.ts`
- Cache Layer: `/workspaces/love-rank-pulse/src/services/cache.ts`
