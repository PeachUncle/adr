# ADR-001: Extract Generic Cache Manager from TablebaseService

**Status:** Accepted  
**Date:** 2025-01-09  
**Issue:** #93

## Context

The `TablebaseService` had a tightly coupled, in-memory caching mechanism that presented several challenges:

- **Not reusable**: The caching logic was embedded directly in `TablebaseService`, making it unavailable to other services
- **Hard to test**: The cache and business logic were intertwined, making isolated unit testing difficult
- **Inflexible**: No way to swap caching strategies (e.g., Redis, different eviction policies) without modifying core service logic
- **No performance guarantees**: Informal cache implementation without documented performance characteristics or memory management

The service managed 646 lines of mixed concerns (business logic + cache management), violating the Single Responsibility Principle.

## Decision

We will extract the caching logic into a generic, reusable architecture:

1. **Create `CacheManager<K, V>` interface**: Generic type-safe caching contract
2. **Implement `LRUCacheManager`**: High-performance default implementation with TTL and LRU eviction
3. **Use constructor dependency injection**: Services receive `CacheManager` instances, decoupling them from specific implementations
4. **Maintain backward compatibility**: Existing `TablebaseService` API unchanged

## Implementation

```typescript
// Generic interface
interface CacheManager<K, V> {
  get(key: K): V | undefined;
  set(key: K, value: V, ttlMs?: number): void;
  has(key: K): boolean;
  delete(key: K): boolean;
  clear(): void;
  readonly size: number;
}

// Default implementation
class LRUCacheManager<K, V> implements CacheManager<K, V> {
  // O(1) operations using Map insertion order
  // Automatic TTL cleanup and LRU eviction
}

// Service integration
class TablebaseService {
  constructor(
    apiClient?: LichessApiClient,
    cacheManager?: CacheManager<string, TablebaseCacheEntry> // <-- Injected
  ) {
    this.cacheManager = cacheManager || new LRUCacheManager(200, 300000);
  }
}
```

## Consequences

### Positive

- **Decoupling**: Services are no longer concerned with cache implementation details
- **Testability**: `TablebaseService` can be unit-tested with mock `CacheManager`, and cache logic is tested in isolation
- **Flexibility**: Easy to swap caching strategies (Redis, different algorithms) by implementing `CacheManager` interface
- **Reusability**: `LRUCacheManager` is now a generic utility available across the application
- **Performance**: Dedicated performance testing shows excellent characteristics (0.0014ms/op, O(1) complexity)
- **Memory safety**: Proper TTL cleanup prevents memory leaks

### Performance Results

Based on comprehensive benchmark testing:

| Metric              | Result      | Notes                       |
| ------------------- | ----------- | --------------------------- |
| **Execution Speed** | 0.0014ms/op | Sub-millisecond performance |
| **Complexity**      | O(1)        | Independent of cache size   |
| **Hit Rate**        | 33.3%       | Realistic chess workload    |
| **Memory**          | No leaks    | TTL cleanup verified        |
| **Concurrency**     | Race-safe   | No async corruption         |

### Negative

- **Slight complexity increase**: New interface and dependency injection pattern (minimal trade-off for significant benefits)
- **Learning curve**: Developers need to understand proper integration patterns to avoid cache stampedes

## Validation

- ✅ **Unit tests**: 31 tests, 100% coverage of `LRUCacheManager`
- ✅ **Integration tests**: 4 tests validating `TablebaseService` integration
- ✅ **Performance tests**: 9 comprehensive benchmarks covering micro-performance, memory usage, and realistic workloads
- ✅ **Backward compatibility**: All existing `TablebaseService` tests (25 tests) continue to pass

## Related Documents

- [Cache Manager Usage Guide](../shared/lib/cache/README.md)
- [Performance Characteristics](../shared/lib/cache/PERFORMANCE.md)
- [Integration Patterns](../shared/lib/cache/INTEGRATION.md)
