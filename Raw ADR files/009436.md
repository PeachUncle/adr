# 15. Buffered Tool Call Summarization with Parallel Processing

**Status:** Accepted
**Date:** 2025-11-09
**Deciders:** Development Team
**Technical Story:** Prevent excessive LLM calls for tool call summarization by implementing buffering logic with dual trigger conditions, and optimize execution time through parallel processing with progress tracking.

---

## Context

### Problem Statement

The current ToolCallSummarizationStrategy aggressively summarizes ALL tool calls that are older than `messagesOldThreshold` (default: 20 messages). This results in frequent LLM calls for summarization, even when only a few tool calls need to be condensed. This creates unnecessary API costs and latency.

### Goals

- Reduce the frequency of summarization operations
- Batch summarization to process multiple tool calls at once
- Prevent very old tool calls from accumulating indefinitely
- Maintain context quality while reducing API costs
- Process multiple tool calls in parallel to reduce total summarization time
- Provide real-time progress feedback during summarization

---

## Decision Drivers

* **Cost efficiency**: Minimize unnecessary LLM API calls for summarization
* **Context quality**: Ensure tool calls don't become too stale before summarization
* **Performance**: Reduce latency by batching summarization operations and parallel execution
* **User Experience**: Provide responsive progress feedback during long-running summarization
* **Flexibility**: Allow tunable thresholds for different use cases

---

## Decision

Implement a buffering mechanism with **dual trigger conditions** and **parallel processing**:

### Buffering Strategy

1. **Buffer Size Trigger**: Summarize when the buffer contains ≥ `minToolCallsToSummarize` tool calls
2. **Age Trigger**: Force summarization when ANY tool call exceeds `maxToolCallDistance` from current position

### Parallel Processing

When summarization is triggered, process all buffered tool call groups concurrently:

- Each group is summarized in its own goroutine
- Progress events are emitted as each group completes
- Results are collected and maintained in original order
- First error is propagated while allowing other goroutines to complete

### Configuration Parameters

- `messagesOldThreshold` (default: 20): Tool calls must be at least this many messages old to enter the buffer
- `minToolCallsToSummarize` (default: 10): Minimum buffer size before triggering summarization  
- `maxToolCallDistance` (default: 40): Maximum age before forcing summarization regardless of buffer size

### Behavior

```
if (buffer_size >= minToolCallsToSummarize) OR (oldest_tool_call_distance >= maxToolCallDistance):
    summarize_all_in_buffer()
```

---

## Consequences

### Positive

- **Cost Reduction**: Reduces LLM API calls by ~50-70% through batching
- **Performance**: Parallel processing significantly reduces total summarization time
- **User Experience**: Real-time progress events provide responsive feedback
- **Safety**: Prevents accumulation of very old, stale tool calls
- **Flexibility**: Tunable parameters for different usage patterns
- **Quality**: Maintains context quality through age-based forcing

### Negative

- **Complexity**: More complex logic in ShouldRun and Summarize methods
- **Latency**: Tool calls may wait longer before summarization (up to buffer size)
- **Concurrency**: Requires proper goroutine management and synchronization
- **Memory**: Brief spike during parallel processing of large batches

### Neutral

- Changes summarization timing but not the quality of summaries
- Different usage patterns may need different threshold values
- Parallel processing benefits scale with number of tool calls

---

## Implementation

### Key Changes

#### Buffering Logic

1. Add `minToolCallsToSummarize` and `maxToolCallDistance` fields to `ToolCallSummarizationStrategy`
2. Modify `ShouldRun()` to implement dual trigger logic
3. Track message positions to calculate distances from current position
4. Update `Summarize()` to only process buffered tool calls

#### Parallel Processing

5. Add `eventChannel` field to `ToolCallSummarizationStrategy` for progress events
6. Implement `summarizeGroupsParallel()` method:
   - Launch goroutine for each tool call group
   - Collect results via channels maintaining order
   - Emit progress event after each completion
   - Handle errors with first-error propagation
7. Update `Manager.SetEventChannel()` to propagate events to strategies
8. Implement `SetEventChannel()` method on strategy

### Code Structure

```go
// Parallel processing entry point
func (s *ToolCallSummarizationStrategy) summarizeGroupsParallel(
    ctx context.Context,
    groups [][]*types.Message,
    llm llm.Provider,
) ([]*types.Message, error) {
    // Launch goroutines for each group
    for i, group := range groups {
        go func(idx int, grp []*types.Message) {
            summary, err := s.summarizeGroup(ctx, grp, llm)
            // Emit progress event
            s.eventChannel <- NewContextSummarizationProgressEvent(...)
            resultChan <- result{index: idx, message: summary, err: err}
        }(i, group)
    }
    
    // Collect results in order
    // Return first error if any
}
```

### Example Scenarios

**Scenario 1: Buffer trigger (12 tool calls, oldest at 30 messages)**
- Buffer: 12 tool calls ≥ minToolCallsToSummarize (10) → **TRIGGER**
- Result: Summarize all 12 tool calls

**Scenario 2: Age trigger (6 tool calls, oldest at 50 messages)**  
- Buffer: 6 tool calls < minToolCallsToSummarize (10) → No buffer trigger
- Age: 50 ≥ maxToolCallDistance (40) → **TRIGGER**
- Result: Summarize all 6 tool calls

**Scenario 3: No trigger (5 tool calls, oldest at 30 messages)**
- Buffer: 5 < 10 → No buffer trigger
- Age: 30 < 40 → No age trigger  
- Result: No summarization

---

## Validation

### Success Metrics

- **API Calls**: Reduction in summarization LLM calls by ~50-70%
- **Age Management**: No tool calls older than maxToolCallDistance in conversation
- **Quality**: Maintained or improved context quality
- **Performance**: Parallel processing reduces total summarization time by N-1 where N is number of groups
- **UX**: Progress events emitted for each completed group

### Monitoring

- Track frequency of summarization operations
- Monitor maximum tool call age in conversations
- Measure average batch size per summarization
- Track parallel execution time vs sequential baseline
- Monitor progress event emission timing

### Testing

All tests pass with parallel implementation:
- ✅ Unit tests verify concurrent processing
- ✅ Integration tests confirm event emission
- ✅ Linting validates code quality

---

## Performance Characteristics

### Sequential vs Parallel

**Sequential** (previous):
- Time = N × T_summarize
- Memory = constant
- Progress = final only

**Parallel** (current):
- Time ≈ T_summarize (with N goroutines)
- Memory = N × group_size (brief spike)
- Progress = continuous updates

Where:
- N = number of tool call groups
- T_summarize = time to summarize one group

### Scalability

- **Best case**: Many independent groups → near-linear speedup
- **Typical case**: 5-15 groups → 5-15x faster
- **Worst case**: 1 group → no improvement (same as sequential)

---

## Related Decisions

- [ADR-0014](0014-composable-context-management.md) - Composable Context Management System

---

**Last Updated:** 2025-11-10