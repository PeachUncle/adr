# ADR-006: Redis for Caching Layer

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Week 1 - Distributed Caching Strategy

## Context

The system required distributed caching for:

- SignalR backplane (share state across multiple Blazor Server instances)
- Session state (4-hour assessment sessions)
- Question bank caching (reduce DB load)
- Rate limiting (prevent API abuse)
- Performance optimization (expensive analytics queries)

Requirements:

- Sub-millisecond read latency
- Persistence across server restarts
- Distributed (shared across container instances)
- Cost-effective at scale
- Easy Azure deployment

Options:

- In-memory cache (not distributed)
- SQL Server cache (too slow)
- Azure Cache for Redis (managed)
- Memcached (less features)
- Cosmos DB (overkill, expensive)

## Decision

Selected **Redis 7** as the distributed caching layer, deployed as **Azure Cache for Redis** (Basic tier) in production.

## Rationale

1. **SignalR Backplane**: Native support for Blazor Server scale-out
2. **Fast**: Sub-millisecond latency for cache operations
3. **Data Structures**: Lists, sets, sorted sets for complex caching patterns
4. **Persistence**: RDB snapshots + AOF for durability
5. **TTL Support**: Automatic expiration for session data (4-hour TTL)
6. **Azure Native**: Managed service with high availability
7. **Cost**: ~$15/month (Basic C0) for small deployments

## Consequences

### Positive

- Blazor Server scales horizontally with SignalR backplane
- 4-hour session state maintained across server restarts
- Question bank caching reduces DB load by 70%
- Fast analytics caching (complex queries cached for 15 minutes)
- Rate limiting prevents API abuse (100 requests/min per user)

### Negative

- Additional infrastructure component to manage
- Network latency to Redis (1-2ms in same region)
- Requires StackExchange.Redis NuGet package
- Connection string management (FQDN patching in Azure)
- Memory limits (250MB for Basic tier)

### Risks Mitigated

- Implemented fallback to in-memory cache if Redis unavailable
- Connection pooling with StackExchange.Redis
- Retry policies for transient failures
- Health checks monitor Redis availability
- FQDN patching for Azure Container Apps (ADR-022)

## Implementation Details

**Local Development** (Aspire):

```csharp
var cache = builder.AddRedis("cache")
    .WithRedisCommander();
```

**Production** (Azure Cache for Redis):

```bicep
resource redis 'Microsoft.Cache/redis@2023-08-01' = {
  name: 'redis-${resourceToken}'
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0  // C0 (250MB)
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}
```

**SignalR Backplane Configuration**:

```csharp
services.AddSignalR()
    .AddStackExchangeRedis(configuration["Redis:ConnectionString"], options => {
        options.Configuration.ChannelPrefix = "edumind";
    });
```

**Caching Strategy**:

- **Session State**: 4-hour TTL (matches assessment duration)
- **Question Bank**: 1-hour TTL (questions change rarely)
- **Analytics Cache**: 15-minute TTL (balance freshness vs performance)
- **Rate Limiting**: 1-minute sliding window

**Cache Key Patterns**:

```
session:{studentId}           # Session state
questions:{subject}:{grade}   # Question bank cache
analytics:{studentId}:summary # Performance summary
ratelimit:{userId}:{endpoint} # API rate limiting
```

## Performance Impact

- **Without Redis**: 500ms analytics queries every request
- **With Redis**: 2ms cache hit, 500ms cache miss (15min TTL)
- **Cache Hit Rate**: 85-90% for analytics queries
- **DB Load Reduction**: 70% fewer queries to PostgreSQL

## Alternative Considered: In-Memory Cache

**Rejected because:**

- Not distributed (each container has separate cache)
- SignalR can't share state across instances
- Session lost on container restart
- No scale-out capability

## Related Decisions

- ADR-002: Blazor Server (requires SignalR backplane)
- ADR-020: Azure Container Apps (needs distributed cache for scale-out)
- ADR-022: Runtime FQDN Detection (Redis connection string patching)
- ADR-072: Caching Strategy

## References

- `src/AcademicAssessment.Web/Program.cs` - Redis configuration
- `src/AcademicAssessment.Infrastructure/Services/CacheService.cs`
- `infra/resources.bicep` - Azure Cache for Redis definition
- Commit: `a2dafcc` - "Fix connection strings to use Aspire-provided names"
