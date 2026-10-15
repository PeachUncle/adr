# ADR 004: Enhanced Progress Tracking and User Experience

## Status

Accepted

## Context

After implementing the Worker pattern (ADR 003), users had no visibility into what was happening during query execution. The CLI output was minimal:

```
Querying Sumo Logic: 2025-11-13T16:14:00 to 2025-11-13T16:44:00
Query: *sidekiq* | limit 10000
This may take 1-3 minutes depending on data volume...

Message count: 10000
```

### Problems

1. **No transparency**: Users couldn't see search job progress
2. **No job ID**: Couldn't reference job in Sumo Logic UI for debugging
3. **No worker visibility**: Parallel optimization was invisible to users
4. **Generic timing**: "1-3 minutes" was unhelpful
5. **Missing context**: No indication of what phase was executing

## Decision

**Add comprehensive progress tracking throughout the search lifecycle with customizable Worker callbacks.**

### Implementation

#### 1. Structured CLI Output

Add clear sections with visual separators:

```ruby
def log_search_info
  warn '=' * 60
  warn 'Sumo Logic Search Query'
  warn '=' * 60
  warn "Time Range: #{options[:from]} to #{options[:to]}"
  warn "Query: #{options[:query]}"
  warn "Limit: #{options[:limit] || 'unlimited'}"
  warn '-' * 60
  warn 'Creating search job...'
end
```

#### 2. Always Show Job ID

Users can reference job in Sumo Logic UI:

```ruby
def log_info(message)
  if message.start_with?('Created search job:')
    warn "  #{message}"  # Always visible
  end
end
```

#### 3. Real-time Poll Status

Show progress during job execution:

```ruby
def log_poll_status(state, data, interval, count)
  msg_count = data['messageCount'] || 0
  rec_count = data['recordCount'] || 0
  warn "  Status: #{state} | Messages: #{msg_count} | Records: #{rec_count}"
end
```

#### 4. Worker Progress Callbacks

Add callbacks to Worker utility for customizable progress:

```ruby
@worker.execute(pages, callbacks: {
  start: ->(workers, total) {
    warn "  Created #{workers} workers for #{total} pages"
  },
  progress: ->(done, total) {
    warn "  Progress: #{done}/#{total} pages fetched"
  },
  finish: ->(results, duration) {
    warn "  All workers completed in #{duration.round(2)}s"
  }
})
```

#### 5. Context Object Pattern

Avoid parameter list violations by using context hash:

```ruby
context = {
  result: [],
  completed: { count: 0 },
  mutex: Mutex.new,
  total_items: items.size,
  callbacks: callbacks
}
```

## Consequences

### Positive

- **Transparency**: Users see exactly what's happening
- **Debuggability**: Job ID available for Sumo Logic UI lookup
- **Progress awareness**: Real-time updates during long queries
- **Worker visibility**: Users see parallel optimization in action
- **Customizable**: Different progress for different operations (metadata vs messages)
- **Clean code**: Context object avoids parameter pollution

### Negative

- **More output**: Some users may prefer minimal output
- **Complexity**: Callbacks add code (mitigated by clean design)
- **Thread safety**: Callbacks must be thread-safe (handled by mutex)

### Neutral

- **Performance**: Minimal overhead (~1ms for progress logging)
- **Backward compatible**: Callbacks are optional

## Output Comparison

### Before

```
Querying Sumo Logic: 2025-11-13T16:14:00 to 2025-11-13T16:44:00
Query: *sidekiq* | limit 10000
This may take 1-3 minutes depending on data volume...

Message count: 10000
```

### After

```
============================================================
Sumo Logic Search Query
============================================================
Time Range: 2025-11-13T16:14:00 to 2025-11-13T16:44:00
Query: *sidekiq* | limit 10000
Limit: unlimited
------------------------------------------------------------
Creating search job...
  Created search job: 1D8775832AEE1CD3
  Status: GATHERING RESULTS | Messages: 2500 | Records: 0
  Status: DONE GATHERING RESULTS | Messages: 10000 | Records: 0
Search job completed in 10.6s
Fetching messages...
  Fetched 10000 messages (total: 10000)
  Created 9 workers for 10 pages
  Progress: 5/10 pages fetched
  Progress: 10/10 pages fetched
  All workers completed in 4.53s
============================================================
Results: 10000 messages
============================================================
```

## Design Decisions

### Why Callbacks Pattern?

**Alternative 1**: Pass logger to Worker
```ruby
worker = Worker.new(logger: logger)
```
**Rejected**: Couples Worker to specific logging implementation

**Alternative 2**: Events/Observer pattern
```ruby
worker.on(:progress) { |data| ... }
```
**Rejected**: Over-engineering for simple use case

**Alternative 3**: Callbacks hash ✅
```ruby
worker.execute(items, callbacks: { start: ..., progress: ..., finish: ... })
```
**Accepted**: Simple, flexible, decoupled

### Why Context Object?

**Problem**: Rubocop violation (>5 parameters)
```ruby
def process_queue(queue, result, mutex, completed, total_items, callbacks, &block)
  # 6 parameters!
end
```

**Solution**: Group related data
```ruby
context = { result:, completed:, mutex:, total_items:, callbacks: }
def process_queue(queue, context, &block)
  # 2 parameters
end
```

### When to Show Progress?

**Job status**: Always (users need feedback)
**Worker details**: Only when workers are used (multi-page)
**Fetch progress**: Always (shows data volume)
**Debug details**: Only with SUMO_DEBUG flag

## Performance Impact

| Operation | Overhead | Acceptable? |
|-----------|----------|-------------|
| Print job ID | ~0.1ms | ✅ Negligible |
| Poll status | ~0.5ms/poll | ✅ Negligible |
| Worker callbacks | ~0.1ms/page | ✅ Negligible |
| Progress updates | ~0.2ms | ✅ Negligible |

**Total overhead**: <2ms per query (0.02% of typical 10s query)

## Future Enhancements

Potential additions (not implemented yet):
- **Progress bar**: Visual progress indicator
- **ETA calculation**: Estimated time remaining
- **Quiet mode**: `--quiet` flag to suppress progress
- **JSON progress**: `--json-progress` for machine parsing
- **Async mode**: `--async` to return job ID and exit

## Implementation Notes

### Callback Signature

```ruby
callbacks: {
  start: ->(worker_count, total_items) { },
  progress: ->(completed_count, total_items) { },
  finish: ->(results, duration) { }
}
```

### Thread Safety

Progress callback is mutex-protected:

```ruby
mutex.synchronize do
  completed[:count] += 1
  callbacks[:progress].call(completed[:count], total_items)
end
```

### Customization Per Use Case

**MessageFetcher** (always visible):
```ruby
start: ->(workers, _total) { warn "Created #{workers} workers..." }
```

**CollectorSourceFetcher** (debug only):
```ruby
start: ->(workers, total) {
  warn "..." if ENV['SUMO_DEBUG'] || $DEBUG
}
```

## References

- ADR 003: Extract Parallel Worker Pattern (introduced Worker utility)
- `lib/sumologic/utils/worker.rb` - Callbacks implementation
- `lib/sumologic/search/message_fetcher.rb` - Message fetch progress
- `lib/sumologic/metadata/collector_source_fetcher.rb` - Collector fetch progress
- `lib/sumologic/cli.rb` - Enhanced CLI output

## Date

2025-11-15

## Notes

This ADR demonstrates **progressive enhancement**: Start with working code (ADR 003), then add observability (ADR 004) without changing behavior. The callbacks pattern allows each component to customize progress output for its specific use case while keeping the Worker utility generic and reusable.
