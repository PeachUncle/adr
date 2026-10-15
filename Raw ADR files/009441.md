# 21. Early Tool Call Detection and Event Emission

**Status:** Proposed
**Date:** 2024-01-09
**Deciders:** Engineering Team
**Technical Story:** Improve UX by emitting tool call events as soon as the tool name is detected during streaming, rather than waiting for complete XML parsing.

---

## Context

Currently, the system parses streaming LLM responses and separates tool call XML from regular content. The `ToolCallParser` in `pkg/llm/parser/toolcall.go` buffers tool call content until it detects the complete closing tag, at which point it emits a `tool_call_content` event with the complete XML.

In `pkg/agent/core/stream.go`, the `handleToolCallContent` function only emits `EventTypeToolCallStart` when it first receives tool call content. However, this happens after the XML content has been buffered, meaning there's a delay between when the LLM starts generating the tool call and when the UI can show feedback to the user.

### Background

The streaming architecture works as follows:

1. **LLM Provider** streams chunks to the agent
2. **ToolCallParser** (`pkg/llm/parser/toolcall.go`) buffers content and separates tool tags from regular content
3. **Stream Processor** (`pkg/agent/core/stream.go`) handles parsed content and emits events
4. **TUI Executor** (`pkg/executor/tui/executor.go`) receives events and updates the UI

The tool call XML format includes server_name, tool_name, and arguments elements. The tool_name element appears early in the stream, typically within the first 2-3 chunks.

### Problem Statement

Users experience a delay between when the LLM starts generating a tool call and when they see visual feedback in the UI. This creates a perception of slowness and provides less transparency into what the agent is doing.

Specifically:
- The `tool_call_start` event is emitted only after buffering begins
- The tool name is available early in the XML stream (typically in the first 2-3 chunks)
- The UI could show "Calling tool: apply_diff" much earlier than it currently does
- Users see a loading spinner instead of specific tool information during the buffering phase

### Goals

- Emit a tool call event with the tool name as soon as it's detected in the stream
- Improve perceived responsiveness of the UI
- Provide more granular feedback to users about what the agent is doing
- Maintain backward compatibility with existing event handlers

### Non-Goals

- Complete XML parsing before emitting the event (we want early detection)
- Changing the existing tool execution flow
- Modifying the XML format or tool call schema
- Guaranteeing 100% accuracy (we accept that malformed XML might cause incorrect early detection)

---

## Decision Drivers

* **User Experience**: Earlier feedback creates better UX and transparency
* **Performance**: Should not introduce significant parsing overhead
* **Maintainability**: Solution should be clean and not complicate the streaming architecture
* **Reliability**: Must handle edge cases (split tags, malformed XML, etc.)
* **Backward Compatibility**: Existing event consumers should continue to work

---

## Considered Options

### Option 1: Buffer and Parse Early in ToolCallParser

**Description:** Extend `ToolCallParser` to detect and extract the tool_name element as soon as it's complete, emitting a new `tool_call_detected` event with the tool name before the full XML is buffered.

**Pros:**
- Centralized in the parser - single source of truth
- Can leverage existing XML buffering logic
- Maintains parser state consistency
- Early detection happens close to where streaming occurs

**Cons:**
- Mixes concerns (parsing and event emission logic in parser)
- Parser becomes aware of specific XML elements (tool_name)
- Harder to extend for other early-detection scenarios
- More complex parser state machine

### Option 2: Two-Phase Parsing in Stream Processor

**Description:** Modify `pkg/agent/core/stream.go` to do a quick regex scan on accumulated tool call content to extract the tool name, then emit an enhanced `tool_call_start` event with the tool name.

**Pros:**
- Parser stays simple and focused on XML structure
- Stream processor handles event timing logic
- Easy to add more early-detection patterns
- Regex is fast for this simple pattern

**Cons:**
- Duplicates some parsing logic (XML structure knowledge in two places)
- Regex might fail on edge cases (split tags, unusual whitespace)
- Adds complexity to stream processor

### Option 3: Incremental XML Parsing with Event Callbacks

**Description:** Use a streaming XML parser that fires callbacks as elements are encountered, allowing us to emit events as specific tags are parsed.

**Pros:**
- Proper XML parsing (handles all edge cases)
- No regex or string parsing heuristics
- Could extend to parse other elements early

**Cons:**
- XML decoder needs complete elements, not streaming fragments
- Would need to buffer anyway until element is complete
- More complex implementation
- Overhead of XML parser for simple use case

---

## Decision

**Chosen Option:** Option 2 - Two-Phase Parsing in Stream Processor

### Rationale

Option 2 provides the best balance of simplicity, separation of concerns, performance, flexibility, and maintainability. The tool_name element always appears early in the XML (after server_name), and its format is simple and predictable. A regex pattern is sufficient for reliable detection in 99%+ of cases.

Edge cases where it fails (malformed XML, unusual whitespace) will simply fall back to the existing behavior of showing the tool call without a name until the full XML is parsed.

---

## Consequences

### Positive

- **Immediate User Feedback**: Users see "Calling: apply_diff" within 1-2 chunks instead of waiting for full XML
- **Better UX**: Reduced perceived latency and more transparency
- **Progressive Enhancement**: Existing functionality is unaffected if detection fails
- **Simple Implementation**: Approximately 30 lines of code change in stream processor
- **Extensible Pattern**: Can easily add detection for other elements if needed

### Negative

- **Potential False Positives**: Malformed XML might cause incorrect tool name detection (mitigated by regex strictness)
- **Duplicate Parsing**: Tool name is effectively parsed twice (once for early detection, once in full XML parse)
- **Testing Complexity**: Need tests for edge cases (split tags, incomplete XML, etc.)

### Neutral

- **Event Enhancement**: The existing `EventTypeToolCallStart` event is enhanced with optional tool name metadata
- **UI Adaptation**: TUI needs minor update to check for tool name in `EventTypeToolCallStart` metadata
- **Documentation**: Need to update event documentation to explain enhanced behavior

---

## Implementation

### Phase 1: Core Changes ✅ COMPLETED

1. ✅ Added `extractToolNameFromPartial()` function in `pkg/agent/core/stream.go`
   - Regex-based extraction: `<tool_name>\s*([^<>\s][^<>]*?)\s*</tool_name>`
   - Handles whitespace, incomplete tags, and edge cases
   - Returns empty string for malformed/incomplete XML (graceful degradation)

2. ✅ Modified `handleToolCallContent()` in `pkg/agent/core/stream.go`
   - Added `toolNameDetected` flag to `streamState` to prevent duplicate emissions
   - Accumulates tool call content and checks for tool name on each chunk
   - Emits enhanced `EventTypeToolCallStart` with tool name in `Metadata["tool_name"]`

3. ✅ Updated TUI handler in `pkg/executor/tui/executor.go`
   - Added handler for `EventTypeToolCallStart` event
   - Checks `event.Metadata["tool_name"]` for early tool name
   - Displays tool name immediately if available, falls back to `EventTypeToolCall` otherwise

### Phase 2: Testing ✅ COMPLETED

1. ✅ Comprehensive unit tests in `pkg/agent/core/stream_test.go`
   - 17 test cases covering normal operation and edge cases
   - Tests for complete/incomplete XML, whitespace handling, special characters
   - All tests passing (0.537s)

2. ⏳ Integration tests (recommended for future work)
   - End-to-end streaming tests with mock LLM responses
   - Verify event emission timing and order

### Phase 3: Documentation

1. ✅ Architecture Decision Record (this document)
2. ✅ Code comments in `stream.go` explaining the two-phase parsing approach
3. ⏳ Event documentation update (recommended)

### Migration Path

This is a backward-compatible enhancement:
- Existing code that doesn't check `Metadata` continues to work unchanged
- UI components can optionally check for `Metadata["tool_name"]` to display early feedback
- Graceful degradation: if regex fails or XML is malformed, falls back to existing behavior

### Implementation Summary

**Files Modified:**
- `pkg/agent/core/stream.go` - Core streaming logic with early detection
- `pkg/executor/tui/executor.go` - TUI event handler for early tool name display
- `pkg/agent/core/stream_test.go` - Comprehensive unit tests

**Key Design Decisions:**
- Used existing `EventTypeToolCallStart` event (no new event type)
- Tool name stored in `Metadata` map (no schema changes)
- Regex pattern is strict to minimize false positives
- State tracking prevents duplicate tool name emissions

---

## Validation

### Success Metrics

1. **Latency Reduction**: Time from first tool call chunk to UI feedback < 100ms (vs ~500ms currently)
2. **Detection Rate**: Tool name detected early in > 95% of tool calls
3. **Error Rate**: False positives < 1% (incorrect tool name shown)
4. **User Feedback**: Perceived responsiveness improvement in user testing

### Monitoring

- Log detection success/failure rates in development mode
- Track timing between `tool_call_start` and full XML parse
- Monitor error reports related to incorrect tool names
- A/B test with users to measure perceived performance improvement

---

## Related Decisions

- [ADR-0004](0004-agent-content-processing.md) - Agent Content Processing
- [ADR-0005](0005-channel-based-agent-communication.md) - Channel-Based Agent Communication
- [ADR-0019](0019-xml-cdata-tool-call-format.md) - XML CDATA Tool Call Format

---

## References

- Tool Call Parser: `pkg/llm/parser/toolcall.go`
- Stream Processor: `pkg/agent/core/stream.go`
- TUI Event Handler: `pkg/executor/tui/executor.go`
- Event Type Definitions: `pkg/types/event.go`

---

## Notes

**Implementation Considerations:**

The regex pattern for early detection should be strict to avoid false positives. The tool_name element always appears near the start of the XML, making early detection practical. If detection fails, graceful degradation ensures the full tool call event will still fire after complete XML parsing.

**Last Updated:** 2024-01-09
