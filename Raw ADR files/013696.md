# ADR 0003: Caching Strategy

**Status:** Accepted  
**Date:** 2026-12-10  
**Decision Makers:** Architecture Team  
**Category:** Performance / Infrastructure

---

## Context

POC-3 requires advanced caching strategies to improve performance and reduce server load. The application needs caching at multiple layers: browser, CDN/nginx, service worker, and backend (Redis).

### Requirements

1. **Static Asset Caching** - JS, CSS, images with long cache times
2. **API Response Caching** - Reduce database queries
3. **Offline Support** - Allow basic functionality offline
4. **Cache Invalidation** - Update cached data when it changes

---

## Decision

Implement a multi-layer caching strategy:

### Layer 1: Browser Cache (HTTP Headers)

**Static Assets (JS, CSS, Images, Fonts):**

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**HTML Files:**

```nginx
location ~* \.html$ {
    expires -1;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

**API Responses:**

```nginx
# Public data - short cache
location /api/public/ {
    add_header Cache-Control "public, max-age=300";  # 5 minutes
}

# User data - no cache
location /api/ {
    add_header Cache-Control "no-store";
}
```

### Layer 2: Service Worker (Workbox)

**Strategy by Route Type:**

| Resource Type | Strategy | Description |
|---------------|----------|-------------|
| Static Assets | CacheFirst | Serve from cache, update in background |
| API GET | NetworkFirst | Try network, fallback to cache |
| API POST/PUT | NetworkOnly | Never cache mutations |
| HTML | StaleWhileRevalidate | Serve cache, update in background |

**Implementation:**

```typescript
// Service Worker registration
import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import {
  CacheFirst,
  NetworkFirst,
  StaleWhileRevalidate,
} from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';

// Precache static assets
precacheAndRoute(self.__WB_MANIFEST);

// API responses - NetworkFirst with cache fallback
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-cache',
    networkTimeoutSeconds: 5,
    plugins: [
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 5 * 60, // 5 minutes
      }),
    ],
  })
);

// Images - CacheFirst
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
    ],
  })
);
```

### Layer 3: Redis Cache (Backend)

**Caching Patterns:**

```typescript
// libs/backend/cache/src/lib/cache-service.ts
interface CacheOptions {
  ttl?: number; // Time to live in seconds
  tags?: string[]; // For invalidation
}

class CacheService {
  async get<T>(key: string): Promise<T | null>;
  async set<T>(key: string, value: T, options?: CacheOptions): Promise<void>;
  async delete(key: string): Promise<void>;
  async invalidateByTag(tag: string): Promise<void>;
}

// Usage in service
class UserService {
  async getUser(id: string): Promise<User> {
    const cacheKey = `user:${id}`;

    // Try cache first
    const cached = await this.cache.get<User>(cacheKey);
    if (cached) return cached;

    // Fetch from database
    const user = await this.prisma.user.findUnique({ where: { id } });

    // Store in cache
    await this.cache.set(cacheKey, user, { ttl: 300, tags: ['users'] });

    return user;
  }

  async updateUser(id: string, data: UpdateUserDto): Promise<User> {
    const user = await this.prisma.user.update({ where: { id }, data });

    // Invalidate cache
    await this.cache.delete(`user:${id}`);

    return user;
  }
}
```

**Cache Key Patterns:**

| Entity | Key Pattern | TTL | Tags |
|--------|-------------|-----|------|
| User | `user:{id}` | 5 min | `users` |
| Payment | `payment:{id}` | 1 min | `payments`, `user:{userId}` |
| Payment List | `payments:user:{userId}:page:{page}` | 1 min | `payments`, `user:{userId}` |
| Profile | `profile:{userId}` | 5 min | `profiles`, `user:{userId}` |

### Layer 4: TanStack Query (Frontend)

**Configuration:**

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 seconds
      gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
      refetchOnWindowFocus: true,
      retry: 3,
    },
  },
});
```

**Query-Specific Settings:**

| Query | staleTime | gcTime | refetchInterval |
|-------|-----------|--------|-----------------|
| User Profile | 5 min | 30 min | - |
| Payment List | 30 sec | 5 min | - |
| Payment Detail | 10 sec | 5 min | - |
| Dashboard Metrics | 10 sec | 1 min | 30 sec |

---

## Cache Invalidation Strategy

### Real-Time Invalidation (WebSocket)

```typescript
// On payment update event via WebSocket
socket.on('payment:updated', data => {
  queryClient.invalidateQueries({ queryKey: ['payments'] });
  queryClient.invalidateQueries({ queryKey: ['payment', data.paymentId] });
});
```

### Tag-Based Invalidation (Backend)

```typescript
// On user update, invalidate all user-related caches
await cacheService.invalidateByTag(`user:${userId}`);
```

---

## Consequences

### Positive

1. **Improved Performance** - Reduced server load, faster response times
2. **Offline Support** - Users can access cached data offline
3. **Scalability** - Better handling of high traffic
4. **Cost Reduction** - Fewer database queries

### Negative

1. **Complexity** - Multiple caching layers to manage
2. **Stale Data Risk** - Must carefully manage invalidation
3. **Storage Requirements** - Redis memory, browser storage

### Neutral

1. **Development Overhead** - Cache invalidation logic required
2. **Debugging** - Cache issues can be hard to diagnose

---

## Verification

- [ ] Static assets cached with correct headers
- [ ] Service worker caches API responses
- [ ] Redis cache reduces database queries
- [ ] TanStack Query configured correctly
- [ ] WebSocket invalidates queries on events
- [ ] Cache hit rate > 80%
- [ ] Offline mode works for basic features

---

## References

- [Workbox Documentation](https://developers.google.com/web/tools/workbox)
- [TanStack Query Caching](https://tanstack.com/query/latest/docs/react/guides/caching)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)
