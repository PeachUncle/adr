# ADR-003: Caching Strategy

**Status**: Accepted  
**Date**: 2025-12-02  
**Decision Makers**: Development Team  

---

## Context

The application makes frequent external API calls:
- **YFinance**: Stock market data (rate limited)
- **CoinGecko**: Cryptocurrency data (100 calls/minute free tier)
- **OpenAI**: GPT-4 analysis ($0.03 per 1K tokens)

Without caching:
- ❌ High API costs (especially OpenAI)
- ❌ Slow response times (network latency)
- ❌ Risk of rate limit violations
- ❌ Poor user experience with repeated requests

---

## Decision

We implement a **multi-layered caching strategy** with TTL (Time-To-Live) expiration:

### 1. **In-Memory TTL Cache**
- **Implementation**: Custom `TTLCache` class in `cache.py`
- **TTL Values**:
  - Stock data: 5 minutes (market changes quickly)
  - Crypto data: 2 minutes (high volatility)
  - AI analysis: 30 minutes (expensive, slower changing)
  - ML predictions: 5 minutes (sync with stock data)
- **Max Size**: Unlimited (memory-bound by container limits)
- **Eviction**: Automatic on TTL expiration

### 2. **Rate Limiter**
- **Purpose**: Prevent bursting API calls even with cache misses
- **Implementation**: Token bucket algorithm
- **Limits**:
  - YFinance: 2 calls/second per endpoint
  - CoinGecko: 10 calls/second (well below 100/min limit)
  - OpenAI: 1 call every 2 seconds (cost control)

### 3. **Cache Warming**
- **Trigger**: Application startup
- **Strategy**: Pre-fetch top 10 stocks and top 20 cryptos
- **Benefit**: Instant response for first user requests

---

## Cache Architecture

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ HTTP Request
       ▼
┌──────────────────┐
│  FastAPI Server  │
└──────┬───────────┘
       │
       ▼
  ┌────────┐
  │ Cache? │───Yes──> Return cached data
  └────┬───┘
       │ No
       ▼
┌──────────────────┐
│  Rate Limiter    │ (Wait if needed)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  External API    │ (YFinance/CoinGecko/OpenAI)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Store in Cache  │ (TTL=5min/2min/30min)
└──────┬───────────┘
       │
       ▼
   Return data
```

---

## Alternatives Considered

### 1. **Redis Cache**
- **Pros**: 
  - Persistent across restarts
  - Distributed caching for multiple instances
  - Rich data structures
- **Cons**: 
  - Additional infrastructure (Redis server)
  - Network overhead (localhost but still latency)
  - Overkill for POC with single instance
  - Higher operational complexity

**Decision**: Use Redis for production, in-memory for POC

### 2. **No Caching**
- **Pros**: Simplest implementation, always fresh data
- **Cons**: 
  - High API costs ($100s/month for OpenAI)
  - Slow response times (2-5 seconds per request)
  - Rate limit violations
  - Poor UX

### 3. **CDN Caching (Cloudflare)**
- **Pros**: Edge caching, global distribution
- **Cons**: 
  - Can't cache POST requests (AI analysis)
  - Can't cache authenticated API calls
  - Static content only
  - Not applicable to our use case

### 4. **Browser Cache (HTTP Cache-Control)**
- **Pros**: No server-side storage needed
- **Cons**: 
  - User-specific (no sharing across users)
  - Limited control over eviction
  - Doesn't help with API rate limits
  - Still need server-side cache

---

## Consequences

### Positive
- ✅ **Cost Reduction**: 90%+ reduction in OpenAI API calls
- ✅ **Fast Response**: <100ms for cached requests (vs 2-5s uncached)
- ✅ **Reliability**: No rate limit errors
- ✅ **Scalability**: Can handle 100+ concurrent users
- ✅ **Simple**: No external dependencies (Redis) for POC

### Negative
- ⚠️ **Stale Data**: Up to 5 minutes old (acceptable for POC)
- ⚠️ **Memory Usage**: Cache grows with unique requests (~50MB typical)
- ⚠️ **No Persistence**: Cache lost on restart (mitigated with cache warming)

### Risks
- **Memory Exhaustion**: Unbounded cache could use all RAM → Mitigated with Docker memory limits
- **Cache Stampede**: Many requests for expired key hit API simultaneously → Mitigated with rate limiter
- **Inconsistent Data**: Different users see different data during TTL → Acceptable trade-off

---

## Implementation Details

### TTL Cache Class
```python
from typing import Any, Optional
import time

class TTLCache:
    """In-memory cache with TTL expiration"""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int):
        """Set value with TTL in seconds"""
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
```

### Usage in Endpoints
```python
from market_predictor.cache import cache

@app.get("/api/stocks/{ticker}")
async def get_stock_data(ticker: str):
    cache_key = f"stock:{ticker}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Fetch from API
    data = await fetch_stock_data(ticker)
    
    # Store in cache (5 min TTL)
    cache.set(cache_key, data, ttl=300)
    
    return data
```

### Rate Limiter
```python
from market_predictor.rate_limiter import RateLimiter

yfinance_limiter = RateLimiter(max_calls=2, period=1.0)

async def fetch_stock_data(ticker: str):
    async with yfinance_limiter:
        # API call protected by rate limiter
        return yf.Ticker(ticker).history(period="1y")
```

---

## Monitoring

### Cache Metrics
- **Hit Rate**: `cache_hits / (cache_hits + cache_misses)`
- **Average TTL**: Time until expiration for cached items
- **Memory Usage**: Size of cache in MB
- **Eviction Rate**: Items expired per minute

### Target Metrics
- Hit Rate > 80% (indicates effective caching)
- Memory Usage < 100MB (acceptable overhead)
- Average TTL > 50% of max TTL (items used before expiry)

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

cache_hits = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['cache_type'])
cache_latency = Histogram('cache_lookup_seconds', 'Cache lookup latency')
```

---

## Future Enhancements

### Phase 2 (Production)
- **Redis Integration**: For multi-instance deployments
- **Cache Invalidation**: Webhook-based updates for real-time data
- **Tiered Caching**: L1 (in-memory) + L2 (Redis)
- **Cache Analytics**: Dashboard for hit rates and performance

### Phase 3 (Scale)
- **CDN**: For static assets and public API responses
- **Edge Computing**: Cloudflare Workers for global latency
- **Smart Prefetching**: ML-based prediction of next requests

---

## Related Decisions
- [ADR-001: Architecture Overview](./ADR-001-architecture-overview.md)
- [ADR-002: Model Training Strategy](./ADR-002-model-training-strategy.md)

---

## References
- [Redis vs In-Memory Cache](https://redis.io/topics/lru-cache)
- [HTTP Caching Best Practices](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
