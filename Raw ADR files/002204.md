# ADR-003: Caching Strategy

## Status
✅ **ACCEPTED** - Partially implemented in `libs/vnstock/`

## Context

The system requires efficient caching to reduce API calls to vnstock, improve response times, and handle high-frequency data access patterns. Caching strategy affects performance, data freshness, and system reliability.

## Decision

Implement multi-layer caching strategy with in-memory caching for vnstock API responses and Redis for application-level caching.

## Rationale

### Current Implementation ✅
The vnstock wrapper already implements basic caching:
```python
# From libs/vnstock/vnstock_client.py
@cached(ttl=3600)
def get_all_symbols(self) -> List[StockListing]:
    # Implementation with 1-hour cache
```

### Multi-Layer Approach Benefits
- **L1 Cache**: In-memory for frequently accessed data
- **L2 Cache**: Redis for shared cache across services
- **L3 Cache**: Database for persistent storage

## Implementation Details

### Layer 1: In-Memory Caching ✅

#### Current Implementation
```python
# libs/vnstock/cache.py
from functools import wraps
import time

def cached(ttl: int):
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        
        return wrapper
    return decorator
```

#### Cache Configuration
- **Stock Symbols**: 1 hour TTL (rarely changes)
- **Price Data**: 5 minutes TTL (frequent updates)
- **News Data**: 15 minutes TTL (moderate updates)

### Layer 2: Redis Caching 📋

#### Planned Implementation
```python
# libs/common/redis_cache.py
import redis
import json
from typing import Any, Optional

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        try:
            self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def delete(self, key: str):
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
```

#### Cache Key Patterns
```python
# API response caching
CACHE_KEYS = {
    'stock_summary': 'stock_ai:summary:{symbol}',
    'price_history': 'stock_ai:prices:{symbol}:{days}',
    'analysis_result': 'stock_ai:analysis:{symbol}:{type}',
    'news_sentiment': 'stock_ai:sentiment:{symbol}',
    'final_scores': 'stock_ai:scores:{symbol}'
}
```

### Layer 3: Database Caching 📋

#### Materialized Views
```javascript
// MongoDB aggregation pipeline for cached results
db.createView("stock_summaries", "stocks", [
  {
    $lookup: {
      from: "price_history",
      localField: "symbol",
      foreignField: "symbol",
      as: "recent_prices"
    }
  },
  {
    $lookup: {
      from: "final_scores",
      localField: "symbol", 
      foreignField: "symbol",
      as: "latest_score"
    }
  }
])
```

## Cache Invalidation Strategy

### Time-Based Invalidation ✅
```python
# Current TTL-based approach
@cached(ttl=3600)  # 1 hour for symbols
@cached(ttl=300)   # 5 minutes for prices
```

### Event-Based Invalidation 📋
```python
# Planned cache invalidation on data updates
class CacheInvalidator:
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
    
    def invalidate_symbol_cache(self, symbol: str):
        patterns = [
            f'stock_ai:summary:{symbol}',
            f'stock_ai:prices:{symbol}:*',
            f'stock_ai:analysis:{symbol}:*',
            f'stock_ai:scores:{symbol}'
        ]
        
        for pattern in patterns:
            keys = self.cache.redis_client.keys(pattern)
            if keys:
                self.cache.redis_client.delete(*keys)
```

### Cache Warming 📋
```python
# Pre-populate cache with frequently accessed data
class CacheWarmer:
    def __init__(self, cache: RedisCache, data_service):
        self.cache = cache
        self.data_service = data_service
    
    async def warm_popular_stocks(self):
        popular_symbols = ['VCB', 'VNM', 'VIC', 'MSN', 'HPG']
        
        for symbol in popular_symbols:
            # Pre-load stock summary
            summary = await self.data_service.get_stock_summary(symbol)
            self.cache.set(f'stock_ai:summary:{symbol}', summary, ttl=1800)
            
            # Pre-load recent analysis
            analysis = await self.data_service.get_latest_analysis(symbol)
            self.cache.set(f'stock_ai:analysis:{symbol}:latest', analysis, ttl=900)
```

## Cache Configuration

### TTL Settings
```python
# Cache TTL configuration
CACHE_TTL = {
    # Static data (changes rarely)
    'stock_symbols': 3600,      # 1 hour
    'company_info': 86400,      # 24 hours
    
    # Dynamic data (frequent updates)
    'price_data': 300,          # 5 minutes
    'news_articles': 900,       # 15 minutes
    
    # Computed data (expensive to calculate)
    'technical_analysis': 1800, # 30 minutes
    'sentiment_analysis': 3600, # 1 hour
    'final_scores': 600,        # 10 minutes
    
    # API responses (user-facing)
    'api_responses': 60,        # 1 minute
    'search_results': 300       # 5 minutes
}
```

### Cache Size Limits
```python
# Redis configuration
REDIS_CONFIG = {
    'maxmemory': '2gb',
    'maxmemory_policy': 'allkeys-lru',  # Evict least recently used
    'timeout': 5,                       # Connection timeout
    'retry_on_timeout': True,
    'health_check_interval': 30
}
```

## Consequences

### Positive
- **Performance**: Reduced API calls and faster response times
- **Reliability**: Fallback when external APIs are unavailable
- **Cost Efficiency**: Reduced vnstock API usage
- **Scalability**: Better handling of concurrent requests

### Negative
- **Complexity**: Additional infrastructure and code complexity
- **Data Freshness**: Potential stale data issues
- **Memory Usage**: Increased memory requirements
- **Consistency**: Cache invalidation complexity

## Monitoring and Metrics

### Cache Performance Metrics 📋
```python
# Cache monitoring
class CacheMetrics:
    def __init__(self, metrics_client):
        self.metrics = metrics_client
    
    def record_cache_hit(self, cache_type: str, key: str):
        self.metrics.increment(f'cache.hit.{cache_type}')
    
    def record_cache_miss(self, cache_type: str, key: str):
        self.metrics.increment(f'cache.miss.{cache_type}')
    
    def record_cache_latency(self, cache_type: str, latency: float):
        self.metrics.timing(f'cache.latency.{cache_type}', latency)
```

### Key Metrics
- **Hit Rate**: Percentage of cache hits vs. total requests
- **Miss Rate**: Percentage of cache misses
- **Latency**: Cache operation response times
- **Memory Usage**: Cache memory consumption
- **Eviction Rate**: Rate of cache key evictions

## Error Handling

### Cache Failures ✅
```python
# Graceful degradation when cache fails
def get_with_fallback(self, key: str, fallback_func):
    try:
        # Try cache first
        cached_result = self.cache.get(key)
        if cached_result:
            return cached_result
    except Exception as e:
        logger.warning(f"Cache error: {e}")
    
    # Fallback to original function
    result = fallback_func()
    
    # Try to cache the result
    try:
        self.cache.set(key, result)
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
    
    return result
```

### Circuit Breaker Pattern 📋
```python
# Disable cache when failure rate is high
class CacheCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call_with_circuit_breaker(self, cache_operation):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = cache_operation()
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e
```

## Future Enhancements

### Distributed Caching 📋
- **Redis Cluster**: Scale cache across multiple nodes
- **Cache Replication**: Ensure high availability
- **Geo-distributed**: Cache closer to users

### Advanced Features 📋
- **Cache Compression**: Reduce memory usage for large objects
- **Cache Analytics**: Detailed usage patterns and optimization
- **Predictive Caching**: Pre-load data based on usage patterns
- **Cache Versioning**: Handle schema changes gracefully

### Integration with CDN 📋
- **Static Content**: Cache static assets and API responses
- **Edge Caching**: Reduce latency for global users
- **Cache Purging**: Automated cache invalidation