# ADR-0004: In-Memory Caching Strategy and Cache Invalidation

**Status**: Accepted
**Date**: 2025-08-05
**Context**: Travel Memory Journal needs efficient data access patterns for 1000+ memories while maintaining data consistency and meeting performance targets.

## Problem Statement
How should we implement in-memory caching to achieve <2s memory search and <100ms CLI responsiveness while ensuring data consistency between cache and persistent storage?

## Decision Drivers
- **Business Requirements**: Fast memory search and browsing, responsive user experience
- **Technical Constraints**: Single-user CLI application, 1000+ memories (~1MB), JSON file storage
- **Team Constraints**: Simple implementation for MVP, minimal complexity
- **Non-Functional Requirements**: Search <2s, CLI response <100ms, data consistency

## Options Considered

### Option 1: Load-Once Full Cache (Recommended)
**Pros**:
- Simple implementation - load all data at startup
- Fastest possible search performance (in-memory operations)
- No cache invalidation complexity
- Perfect for CLI usage pattern (process per command)
- Guaranteed data consistency within command execution
- 1MB dataset easily fits in memory

**Cons**:
- Startup time includes full file load
- Memory usage proportional to dataset size
- Changes not reflected until app restart

**Implementation Effort**: S (Small)
**Operational Complexity**: Low

### Option 2: Lazy Loading with LRU Cache
**Pros**:
- Lower memory footprint for large datasets
- Faster startup time
- More sophisticated caching strategies

**Cons**:
- Complex cache invalidation logic
- Cache miss performance penalties
- Overkill for 1MB dataset
- Added complexity for marginal benefit

**Why Not Chosen**: Complexity doesn't justify benefits for our dataset size and usage pattern

### Option 3: Write-Through Cache
**Pros**:
- Real-time data consistency
- Immediate reflection of changes

**Cons**:
- Complex synchronization between cache and storage
- Potential race conditions
- Unnecessary for single-user, process-per-command model

**Why Not Chosen**: CLI usage pattern doesn't require persistent cache across commands

## Decision
We will use **Load-Once Full Cache** strategy where the entire dataset is loaded into memory at application startup.

**Rationale**: Given our CLI usage pattern (new process per command), small dataset size (1MB), and performance requirements, loading all data once provides optimal performance with minimal complexity.

## Consequences
**Positive**:
- Maximum search performance - all operations in-memory
- Simple and predictable behavior
- No cache invalidation or synchronization issues
- Easy to test and debug
- Meets all performance requirements with margin

**Negative**:
- Startup time includes full data load (~100-200ms for 1MB)
- Memory usage grows with dataset size
- Changes not visible across concurrent command executions

**Implementation Notes**:
- Load and parse JSON file during application initialization
- Store parsed data in Python data structures (List[Memory])
- Implement search operations using list comprehensions and filters
- No persistence of cache - each command execution loads fresh data
- Add startup performance monitoring to track load times

## Cache Implementation
```python
class MemoryCache:
    def __init__(self, storage_service: StorageService):
        self._storage = storage_service
        self._memories: List[Memory] = []
        self._loaded_at: Optional[datetime] = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load all memories from storage into memory"""
        self._memories = self._storage.load_all_memories()
        self._loaded_at = datetime.now()
    
    def search_memories(self, query: str) -> List[Memory]:
        """Search memories in-memory"""
        # Fast in-memory search operations
        pass
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """Fast O(n) lookup - acceptable for 1000 records"""
        return next((m for m in self._memories if m.id == memory_id), None)
```

## Performance Expectations
- **Data Load Time**: <200ms for 1MB JSON file
- **Search Operations**: <50ms for complex queries across 1000 memories
- **Memory Usage**: ~2-3MB for cached data structures
- **Startup Time**: <500ms total including data load

## Monitoring and Optimization
- Track data load times during startup
- Monitor memory usage growth with dataset size
- Add performance warnings if load time exceeds thresholds
- Consider optimization strategies if dataset grows beyond 5k memories

## Future Evolution
If dataset size or usage patterns change:
1. **Hybrid Approach**: Load index/metadata, lazy load full records
2. **Persistent Cache**: Implement cache invalidation for long-running processes  
3. **Incremental Updates**: Delta loading for frequently updated datasets
4. **Compression**: Compress cached data structures for large datasets