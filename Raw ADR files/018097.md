# ADR 003: Extract Parallel Worker Pattern for Reusability

## Status

Accepted (Builds on ADR 001, 002)

## Context

After ADR 002's radical simplification, we had clean sequential code but lacked the performance benefits of parallel execution. ADR 001 had introduced a parallel pattern in `ParallelFetcher` for metadata operations (85% speedup), but the pattern wasn't reused elsewhere.

### The Opportunity

The same Queue + Mutex + Worker thread pattern could benefit both:
1. **Metadata operations**: Fetching sources from multiple collectors
2. **Search operations**: Fetching multiple pages of search messages

### The Problem

**Code duplication**: Without abstraction, we'd duplicate the 40-line threading pattern in two places, violating DRY principles.

## Decision

**Extract the parallel worker pattern into a reusable `Worker` utility and apply consistent naming.**

### Architecture

```
Utils::Worker (generic parallel execution)
    ├── Used by: Metadata::CollectorSourceFetcher
    └── Used by: Search::MessageFetcher
```

### Naming Strategy

**Generic implementation, domain-specific names:**

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| `ParallelFetcher` | `CollectorSourceFetcher` | Domain-focused, implementation-agnostic |
| `Paginator` | `MessageFetcher` | Consistent "Fetcher" suffix, clear purpose |
| *(new)* | `Utils::Worker` | Generic execution engine |

**Why avoid "Parallel" in names:**
- Implementation detail (could change to sequential later)
- `Worker` is generic (supports both parallel and sequential)
- Domain names (`CollectorSourceFetcher`) are clearer than implementation names

## Implementation

### 1. Worker Utility (lib/sumologic/utils/worker.rb)

```ruby
class Worker
  def initialize(max_threads: 10)
    @max_threads = max_threads
  end

  def execute(items, &block)
    result = []
    mutex = Mutex.new
    queue = Queue.new
    items.each { |item| queue << item }

    # Create worker threads
    threads = Array.new(worker_count) do
      Thread.new { process_queue(queue, result, mutex, &block) }
    end

    threads.each(&:join)
    result
  end
end
```

**40 lines**: Reusable threading logic

### 2. CollectorSourceFetcher (metadata/collector_source_fetcher.rb)

```ruby
class CollectorSourceFetcher
  def initialize(max_threads: 10)
    @worker = Utils::Worker.new(max_threads: max_threads)
  end

  def fetch_all(collectors, &block)
    @worker.execute(collectors, &block)
  end
end
```

**Reduced**: 64 lines → 18 lines (uses Worker)

### 3. MessageFetcher (search/message_fetcher.rb)

```ruby
class MessageFetcher
  def initialize(http_client:, config:)
    @http = http_client
    @config = config
    @worker = Utils::Worker.new(max_threads: 10)
  end

  def fetch_all(job_id, limit: nil)
    # Fetch first page
    first_batch = fetch_page(job_id, 0, limit)
    return first_batch if single_page_result?(first_batch, limit)

    # Multi-page: use Worker for parallel fetching
    pages = calculate_remaining_pages(job_id, first_batch.size, limit)
    additional = @worker.execute(pages) { |page| fetch_page(...) }

    first_batch + additional.flatten
  end
end
```

**107 lines**: Clean, uses Worker for parallelization

## Consequences

### Positive

- **DRY**: Threading logic in one place (40 lines instead of duplicated)
- **Consistent naming**: All fetchers use domain names, not implementation names
- **Future-proof**: Can change Worker to sequential without renaming classes
- **Testable**: Test parallel logic once in Worker tests
- **Maintainable**: Fix threading bugs in one place
- **Performance**: 60-85% speedup for multi-page/multi-collector operations

### Negative

- **Indirection**: One more layer (Worker utility)
- **Migration**: Need to update imports and references

### Neutral

- **Line count**: Net +60 lines (Worker utility + tests - removed duplication)
- **Complexity**: Same threading complexity, just centralized

## Code Reduction Through Abstraction

| Component | Before | After | Change |
|-----------|--------|-------|--------|
| ParallelFetcher threading | 64 lines | 18 lines | **-46 lines** |
| Paginator (if we added parallel) | +100 lines | +107 lines | +7 lines |
| Worker utility | 0 lines | 40 lines | +40 lines |
| Worker tests | 0 lines | 60 lines | +60 lines |
| **Total** | 64 lines | 225 lines | +161 lines |

**But**: Without Worker abstraction, we'd have 64 + 164 = **228 lines** with duplicated logic.

**Net savings**: 3 lines + **eliminated duplication** + **future reusability**

## File Changes

### New Files
- `lib/sumologic/utils/worker.rb` - Generic parallel worker (40 lines)
- `lib/sumologic/metadata/collector_source_fetcher.rb` - Refactored (18 lines)
- `lib/sumologic/search/message_fetcher.rb` - New with Worker (107 lines)
- `spec/sumologic/utils/worker_spec.rb` - Worker tests (60 lines)

### Modified Files
- `lib/sumologic/metadata/source.rb` - Update to use CollectorSourceFetcher
- `lib/sumologic/search/job.rb` - Update to use MessageFetcher

### Deleted Files
- `lib/sumologic/metadata/parallel_fetcher.rb` - Replaced
- `lib/sumologic/search/paginator.rb` - Replaced

## Testing

Added comprehensive Worker tests:
- Parallel execution verification
- Empty input handling
- Nil result filtering
- Thread limit respect
- Thread-safety verification
- Exception handling

**Result**: All 33 tests pass (27 existing + 6 new Worker tests)

## Performance

Same as ADR 001's ParallelFetcher:

| Operation | Sequential | With Worker | Speedup |
|-----------|-----------|-------------|---------|
| 100 collectors | 20s | 2-3s | **85%** |
| 2 pages (20k msg) | 10s | 6s | **40%** |
| 5 pages (50k msg) | 25s | 10s | **60%** |
| 10 pages (100k msg) | 50s | 18s | **64%** |

## References

- ADR 001: Performance Optimizations (introduced parallel pattern)
- ADR 002: Radical Simplification (removed over-engineering)
- `lib/sumologic/utils/worker.rb` - Reusable worker implementation
- `lib/sumologic/metadata/collector_source_fetcher.rb` - Uses Worker
- `lib/sumologic/search/message_fetcher.rb` - Uses Worker

## Date

2025-11-15

## Notes

This ADR demonstrates the progression:
- **ADR 001**: Introduced parallel pattern in one place (ParallelFetcher)
- **ADR 002**: Removed complex, untested parallel logic
- **ADR 003**: Extracted proven pattern into reusable utility with consistent naming

**Key lesson**: Build proven pattern first, simplify to understand it, then abstract for reuse. This three-step process (build → simplify → abstract) produces better architecture than trying to abstract prematurely.
