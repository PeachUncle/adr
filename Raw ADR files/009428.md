# 4. Agent-Level Content Processing

**Status:** Accepted
**Date:** 2025-10-29
**Deciders:** Forge Core Team
**Technical Story:** Defining the boundary between provider content delivery and agent content processing/orchestration

---

## Context

With the Provider abstraction layer established ([ADR-0003](0003-provider-abstraction-layer.md)), we needed to decide what content processing happens at the agent layer. Providers emit `StreamChunks` with thinking/message separation, but agents need to handle tool calls, convert chunks to events, and orchestrate the agent loop.

### Problem Statement

How should agents process streaming content from providers?
1. What parsing happens at agent level vs provider level?
2. How do we handle tool extraction and execution?
3. How do we convert provider StreamChunks into agent events?
4. What's the right boundary between provider and agent responsibilities?

### Background

Agents need to:
- Extract tool calls from LLM responses
- Execute tools with proper error handling
- Emit rich events (ThinkingStart, ToolCall, MessageContent, etc.)
- Control the agent loop (loop-breaking tools, error recovery)
- Manage conversation memory

Providers emit StreamChunks with `.Type` (thinking vs message), but tool calls are embedded in message content as XML: `<tool>JSON</tool>`.

### Goals

- Clear separation between provider (content delivery) and agent (orchestration)
- Efficient streaming processing without re-parsing
- Reusable stream processing across different agent implementations
- Support for tool extraction, validation, and execution
- Rich event system for observability

### Non-Goals

- Move all parsing to provider (tools require agent context)
- Create agent-specific parsing that duplicates provider work
- Support every possible agent architecture (focus on core DefaultAgent)

---

## Decision Drivers

* **Separation of concerns**: Provider delivers content, agent orchestrates
* **Tool context**: Tool execution needs agent state (registry, memory, loop control)
* **Efficiency**: Process during streaming, not after buffering
* **Simplicity**: Agent implementers use core utilities, don't rewrite parsing
* **Consistency**: Both `<thinking>` and `<tool>` are Forge-wide XML standards
* **Developer experience**: Building custom agents should be straightforward

---

## Considered Options

### Option 1: Move All Parsing to Provider

**Description:** Providers parse both `<thinking>` and `<tool>` tags, emit fully-structured chunks with parsed tool calls

**Pros:**
- Single parsing pass
- Consistent location for all XML parsing
- Agents get completely structured data

**Cons:**
- **Provider complexity**: Providers need to know about tools
- **Tight coupling**: Providers coupled to agent-specific formats
- **Lost abstraction**: Defeats provider as "dumb pipe"
- **Reusability**: Can't use provider in non-tool contexts
- **Tool execution context**: Provider doesn't have tool registry, error recovery, etc.

**Verdict:** ❌ Rejected - Violates provider/agent separation, increases provider complexity

### Option 2: Agent Buffers and Re-Parses Everything

**Description:** Agents buffer all provider chunks, then parse for thinking AND tools after stream completes

**Pros:**
- Clear separation: provider streams, agent parses
- All agent logic in one place

**Cons:**
- **Performance**: Loses streaming benefits, must wait for complete response
- **Duplicate work**: Re-parsing thinking that provider already separated
- **Poor UX**: Can't show real-time thinking or tool progress
- **Complexity**: Agent implements all parsing logic

**Verdict:** ❌ Rejected - Sacrifices streaming performance, duplicates work

### Option 3: Hybrid Approach with Shared Utilities (Chosen)

**Description:** 
- Provider uses ThinkingParser (content categorization during streaming)
- Agent uses ToolCallParser (action extraction from message chunks)
- Shared `pkg/llm/parser/` package for utilities
- Agent layer: ProcessStream() handles chunk → event conversion

**Pros:**
- **Streaming efficiency**: Both parsers work on live streams
- **Clear boundaries**: Provider = content transformation, Agent = action extraction
- **Shared utilities**: Parsers in `pkg/llm/parser/` reusable
- **Agent simplicity**: ProcessStream() provides reusable logic
- **Right context**: Tools parsed where they're executed (agent has registry, memory)

**Cons:**
- **Perceived inconsistency**: Thinking at provider, tools at agent (but justified)
- **Two parsing locations**: Not immediately obvious why they differ

**Verdict:** ✅ Accepted - Best balance of performance, separation, and simplicity

---

## Decision

**Chosen Option:** Option 3 - Hybrid Parsing with Shared Utilities

### Architecture

```
Provider Layer:
├── API communication
├── StreamChunk emission
└── ThinkingParser (content categorization)
    └── Emits: ContentTypeThinking vs ContentTypeMessage

Agent Layer:
├── ProcessStream() - Chunk → Event conversion
├── ToolCallParser - Extracts <tool>JSON</tool> from message chunks
├── Tool execution (with registry, error handling)
└── Agent loop control (loop-breaking, circuit breaker)
```

### Rationale

**Why Thinking at Provider:**
1. **Content categorization**: Thinking is about separating content types during streaming
2. **Performance**: Parse once as content streams in, emit typed chunks
3. **Universal standard**: `<thinking>` is Forge-wide, not agent-specific
4. **Streaming optimization**: Provider emits ContentTypeThinking/Message immediately
5. **No agent context needed**: Just categorize content, don't need to understand semantics

**Why Tools at Agent:**
1. **Action extraction**: Tools trigger agent behavior (execution, loop control)
2. **Agent context required**: Tools need registry, memory, error recovery
3. **Agent-specific semantics**: Tool execution = agent orchestration concern
4. **Different nature**: Tools are actions, thinking is content
5. **Loop control**: Loop-breaking tools need agent state

**Why Both Use Shared Utilities:**
- Both parsers handle XML tags (`<thinking>`, `<tool>`)
- Common parsing logic (state machine, buffering, tag matching)
- Located in `pkg/llm/parser/` as reusable utilities
- Usage location vs package location are separate concerns

---

## Consequences

### Positive

- **Streaming performance**: Both parsers work on live streams, no buffering
- **Clear separation**: Content transformation vs action orchestration
- **Reusable logic**: ProcessStream() used by all agent implementations
- **Simple agent authoring**: Call ProcessStream(), get events, execute tools
- **Testability**: Can test stream processing and tool execution separately
- **Flexibility**: Different agents can use same core processing utilities

### Negative

- **Learning curve**: Understanding why thinking≠tools requires explanation
- **Package vs usage**: Parser package location doesn't dictate usage layer
- **Two parse passes**: Technically two XML parsers running (but different purposes)

### Neutral

- **Shared utilities**: Both parsers in `pkg/llm/parser/` but used at different layers
- **Event conversion**: ProcessStream() adds overhead but provides rich observability

---

## Implementation

### Core Stream Processing

Located in [`pkg/agent/core/stream.go`](../../pkg/agent/core/stream.go):

```go
// ProcessStream converts provider StreamChunks into AgentEvents
func ProcessStream(
    stream <-chan *llm.StreamChunk,
    emitEvent func(*types.AgentEvent),
    onComplete func(assistantContent, thinkingContent, toolCallContent, role string),
) {
    state := &streamState{
        toolCallParser: parser.NewToolCallParser(), // Agent-level tool parsing
    }
    
    for chunk := range stream {
        if chunk.IsError() {
            handleError(chunk.Error, state, emitEvent)
            return
        }
        
        // Handle thinking vs message chunks from provider
        if chunk.IsThinking() {
            handleThinkingContent(chunk.Content, state, emitEvent)
        } else {
            handleMessageContent(chunk.Content, state, emitEvent)
        }
        
        if chunk.IsLast() {
            finalize(state, emitEvent, onComplete)
            return
        }
    }
}
```

### Tool Call Parsing

The agent uses ToolCallParser ([`pkg/llm/parser/toolcall.go`](../../pkg/llm/parser/toolcall.go)) to extract tool calls from message chunks:

```go
// In handleMessageContent
func handleMessageContent(content string, state *streamState, emitEvent func(*types.AgentEvent)) {
    // Parse message content for tool calls
    toolCallContent, regularContent := state.toolCallParser.Parse(content)
    
    if toolCallContent != nil {
        // Emit ToolCallStart, ToolCallContent events
        handleToolCallContent(toolCallContent.Content, state, emitEvent)
    }
    
    if regularContent != nil {
        // Emit MessageStart, MessageContent events
        handleRegularContent(regularContent.Content, state, emitEvent)
    }
}
```

### Event Emission

ProcessStream emits rich events for observability:

```go
// Event types emitted:
- ThinkingStartEvent    // First thinking chunk
- ThinkingContentEvent  // Thinking content delta
- ThinkingEndEvent      // Last thinking chunk
- ToolCallStartEvent    // Found <tool> tag
- ToolCallContentEvent  // Tool JSON delta
- ToolCallEndEvent      // Found </tool> tag
- MessageStartEvent     // First message chunk
- MessageContentEvent   // Message content delta
- MessageEndEvent       // Last message chunk
- ErrorEvent            // Error occurred
```

### Tool Execution

After ProcessStream completes, the agent executes tools ([`pkg/agent/default.go`](../../pkg/agent/default.go)):

```go
func (a *DefaultAgent) processToolCall(ctx context.Context, toolCallContent string) (bool, string) {
    // Parse tool call JSON (already extracted by ToolCallParser)
    var toolCall tools.ToolCall
    json.Unmarshal([]byte(toolCallContent), &toolCall)
    
    // Get tool from agent's registry
    tool, exists := a.getTool(toolCall.ToolName)
    if !exists {
        return true, buildUnknownToolError(toolCall.ToolName)
    }
    
    // Execute tool (agent has context: registry, memory, error tracking)
    result, err := tool.Execute(ctx, toolCall.Arguments)
    if err != nil {
        return true, buildToolExecutionError(err)
    }
    
    // Check if loop-breaking (needs agent state)
    if tool.IsLoopBreaking() {
        return false, "" // Exit agent loop
    }
    
    return true, "" // Continue loop
}
```

---

## Validation

### Success Metrics

- ✅ **Streaming performance**: Events emitted in real-time during streaming
- ✅ **Reusability**: ProcessStream used across different agent types
- ✅ **Tool execution**: Tools have access to agent context (registry, memory)
- ✅ **Event richness**: 9 different event types for observability
- ✅ **Error handling**: Circuit breaker, error recovery work correctly

### Monitoring

- Track event emission latency (chunk received → event emitted)
- Monitor tool execution success rates
- Measure stream processing overhead

---

## Related Decisions

- [ADR-0002](0002-xml-format-for-tool-calls.md) - XML format for tool calls
- [ADR-0003](0003-provider-abstraction-layer.md) - Provider abstraction
- Future: ADR on error recovery and circuit breaker patterns

---

## References

- [`pkg/agent/core/stream.go`](../../pkg/agent/core/stream.go) - ProcessStream implementation
- [`pkg/llm/parser/toolcall.go`](../../pkg/llm/parser/toolcall.go) - ToolCallParser
- [`pkg/llm/parser/thinking.go`](../../pkg/llm/parser/thinking.go) - ThinkingParser
- [`pkg/agent/default.go`](../../pkg/agent/default.go) - Tool execution
- [`pkg/types/event.go`](../../pkg/types/event.go) - Event definitions

---

## Notes

### Why Thinking and Tools Are Different

This is the most important concept to understand about Forge's architecture:

**Thinking = Content Categorization**
- Purpose: Separate reasoning from final answer during streaming
- Nature: Content-level concern (what type of content is this?)
- Context: Provider can categorize without understanding semantics
- Timing: Happens during content streaming
- Output: Typed chunks (ContentTypeThinking vs ContentTypeMessage)
- Analogy: Like separating metadata from content in HTTP headers

**Tools = Action Extraction**
- Purpose: Extract and execute agent actions
- Nature: Behavior-level concern (what should agent do?)
- Context: Requires agent state (tool registry, memory, loop control)
- Timing: Happens after content chunk is identified as message
- Output: Parsed tool calls ready for execution
- Analogy: Like route handling in web servers (needs app context)

**Key Insight:** Package location (`pkg/llm/parser/`) doesn't dictate usage layer. Both are parsing utilities, but used at different layers based on what context they need.

### Developer Experience

**For Provider Implementers:**
```go
// Simple: Use ThinkingParser, emit typed chunks
thinkingParser := parser.NewThinkingParser()
thinkingChunk, messageChunk := thinkingParser.Parse(apiContent)
// Don't worry about tools, agents, memory, etc.
```

**For Agent Implementers:**
```go
// Simple: Use ProcessStream, execute tools
core.ProcessStream(stream, agent.emitEvent, func(content, thinking, toolCall, role string) {
    // ProcessStream already extracted tool call
    agent.processToolCall(ctx, toolCall)
})
```

### Architectural Principles

1. **Provider = Dumb Pipe + Content Typing**
   - Transform API responses → StreamChunks
   - Categorize content (thinking vs message)
   - No understanding of agent semantics

2. **Agent = Smart Orchestrator**
   - Extract actions from content
   - Execute with proper context
   - Control loop, manage memory, handle errors

3. **Shared Utilities = Reusable Parsing**
   - XML parsing logic in one place
   - Used by both layers, but at appropriate times
   - Package organization vs layer responsibility are separate

### Future Enhancements

1. **Multiple Tool Calls**: Support multiple `<tool>` tags in single response
2. **Streaming Tool Execution**: Execute tools as they're extracted (before stream ends)
3. **Custom Event Types**: Allow agents to define custom events
4. **Parser Configuration**: Make parsers configurable (different tag formats)

**Last Updated:** 2025-11-02