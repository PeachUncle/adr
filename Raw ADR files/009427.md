# 3. Provider Abstraction Layer

**Status:** Accepted
**Date:** 2025-10-29
**Deciders:** Forge Core Team
**Technical Story:** Designing a provider abstraction that enables multiple LLM integrations while maintaining simplicity and performance

---

## Context

Forge needs to support multiple LLM providers (OpenAI, Anthropic Claude, Google Gemini, local models, etc.) without tying the agent framework to any specific vendor. Each provider has different APIs, authentication methods, and response formats.

### Problem Statement

How do we design a provider interface that:
1. Works consistently across different LLM vendors
2. Remains simple to implement for new providers
3. Provides good developer experience for both provider implementers and agent builders
4. Handles streaming efficiently
5. Separates provider concerns from agent orchestration logic

### Background

LLM providers vary significantly:
- **OpenAI**: Chat completions API, streaming SSE, function calling
- **Anthropic**: Messages API, streaming, tool use
- **Google Gemini**: GenerativeLanguage API, different auth
- **Local models**: Various formats (Ollama, vLLM, etc.)

We needed an abstraction that works for all of them without becoming a "lowest common denominator" that loses important features.

### Goals

- Support multiple LLM providers with a single interface
- Enable streaming as a first-class feature
- Keep provider implementation simple (minimize boilerplate)
- Separate content transformation from agent logic
- Make providers testable in isolation
- Support both streaming and non-streaming use cases

### Non-Goals

- Support every possible LLM feature (focus on core capabilities)
- Create a universal LLM abstraction library (Forge-specific is fine)
- Optimize for non-streaming use cases (streaming is primary)

---

## Decision Drivers

* **Multi-provider support**: Must work with OpenAI, Anthropic, Gemini, local models
* **Simplicity**: Provider implementers shouldn't need to understand agent concepts
* **Streaming performance**: Efficient real-time content delivery
* **Separation of concerns**: Provider = LLM communication, Agent = orchestration
* **Developer experience**: Easy to add new providers
* **Testability**: Providers can be tested without full agent infrastructure

---

## Considered Options

### Option 1: Provider Returns Raw API Response

**Description:** Provider interface returns native API response objects (OpenAI's ChatCompletion, Anthropic's Message, etc.)

**Pros:**
- Maximum flexibility
- No translation needed
- Access to all provider-specific features

**Cons:**
- **Agent coupled to provider types**: Would need to handle OpenAI vs Anthropic types differently
- **No abstraction**: Defeats the purpose
- **Complex agent code**: Every agent needs provider-specific logic
- **Hard to test**: Mocking requires knowing all provider response formats

**Verdict:** ❌ Rejected - No abstraction, tight coupling

### Option 2: Provider Returns Structured Messages

**Description:** Provider returns complete, structured message objects with all metadata

```go
type CompletionResponse struct {
    Content    string
    Role       string
    ToolCalls  []ToolCall
    Thinking   string
    Usage      TokenUsage
    Metadata   map[string]interface{}
}
```

**Pros:**
- Complete information in one object
- Type-safe
- Easy to work with in non-streaming contexts

**Cons:**
- **Poor streaming experience**: Have to buffer entire response
- **Over-engineered**: Too much structure for simple use cases
- **Provider complexity**: Providers must parse and categorize everything
- **Agent coupling**: Agent knows about provider's categorization decisions

**Verdict:** ❌ Rejected - Sacrifices streaming, too complex

### Option 3: Provider Returns Simple StreamChunks (Chosen)

**Description:** Provider emits lightweight `StreamChunk` objects during streaming with minimal structure:

```go
type StreamChunk struct {
    Content  string      // Text content
    Role     string      // Optional: message role
    Type     ContentType // "thinking" or "message"
    Finished bool        // Last chunk indicator
    Error    error       // Error if occurred
}
```

**Pros:**
- **Streaming-first**: Natural fit for real-time content
- **Simple interface**: Minimal fields, easy to implement
- **Performance**: Low overhead, immediate emission
- **Provider simplicity**: Just transform API chunks to StreamChunks
- **Type safety**: ContentType distinguishes thinking vs message
- **Error handling**: Inline error propagation

**Cons:**
- **Requires buffering for non-streaming**: Need wrapper for complete messages
- **Stateful processing**: Consumers need to accumulate chunks

**Verdict:** ✅ Accepted - Best balance of simplicity, performance, and abstraction

---

## Decision

**Chosen Option:** Option 3 - Simple StreamChunk-based Provider Interface

### Interface Design

```go
type Provider interface {
    // StreamCompletion streams response chunks
    StreamCompletion(ctx context.Context, messages []*Message) (<-chan *StreamChunk, error)
    
    // Complete returns full response (wrapper around streaming)
    Complete(ctx context.Context, messages []*Message) (*Message, error)
}
```

### Rationale

1. **Streaming is Primary**: Modern LLM UX demands real-time feedback. StreamCompletion is the core method, Complete() is a convenience wrapper.

2. **Minimal Interface**: Only two methods. Provider implementers focus on API communication, not agent concepts like tools, memory, or orchestration.

3. **Simple Data Model**: StreamChunk has just what's needed for incremental content delivery. Complex processing happens at agent layer.

4. **Content Type Separation**: The `Type` field (thinking vs message) enables efficient content categorization during streaming, handled by ThinkingParser at provider level.

5. **Provider Responsibility**: 
   - API communication (HTTP, auth, retries)
   - Streaming response transformation
   - Thinking content separation (via ThinkingParser utility)
   - Error handling and propagation

6. **NOT Provider Responsibility**:
   - Tool parsing or execution
   - Memory management
   - Agent loop control
   - Event emission (that's agent layer)

---

## Consequences

### Positive

- **Easy to add providers**: Implement two methods, transform API → StreamChunks
- **Provider simplicity**: No agent concepts, no complex types
- **Testable in isolation**: Mock StreamChunk emission, no agent needed
- **Streaming performance**: Chunks emitted immediately as received
- **Reusable**: Providers work in non-agent contexts (CLI tools, batch processing)
- **Clear separation**: Provider = LLM communication, Agent = orchestration
- **ThinkingParser integration**: Providers can use shared utility for content separation

### Negative

- **Accumulation needed**: Non-streaming use cases must buffer chunks (mitigated by Complete() wrapper)
- **Stateful consumption**: Consumers track chunks to build complete response
- **Limited metadata**: StreamChunk intentionally minimal, some provider metadata lost

### Neutral

- **Two-method interface**: StreamCompletion for streaming, Complete for convenience
- **Channel-based**: Go channels for async streaming (idiomatic but requires understanding)
- **Error in chunk**: Errors sent as StreamChunk.Error rather than separate channel

---

## Implementation

### Provider Interface

Located in [`pkg/llm/provider.go`](../../pkg/llm/provider.go):

```go
type Provider interface {
    StreamCompletion(ctx context.Context, messages []*types.Message) (<-chan *StreamChunk, error)
    Complete(ctx context.Context, messages []*types.Message) (*types.Message, error)
}
```

### StreamChunk Definition

Located in [`pkg/llm/types.go`](../../pkg/llm/types.go):

```go
type StreamChunk struct {
    Content  string
    Role     string
    Type     ContentType  // ContentTypeThinking or ContentTypeMessage
    Finished bool
    Error    error
}

func (c *StreamChunk) IsError() bool { return c.Error != nil }
func (c *StreamChunk) HasContent() bool { return c.Content != "" }
func (c *StreamChunk) IsThinking() bool { return c.Type == ContentTypeThinking }
func (c *StreamChunk) IsLast() bool { return c.Finished }
```

### Example Provider Implementation

OpenAI provider ([`pkg/llm/openai/openai.go`](../../pkg/llm/openai/openai.go)):

```go
func (p *Provider) StreamCompletion(ctx context.Context, messages []*types.Message) (<-chan *llm.StreamChunk, error) {
    chunks := make(chan *llm.StreamChunk, 10)
    
    // Use ThinkingParser for content separation
    thinkingParser := parser.NewThinkingParser()
    
    go func() {
        defer close(chunks)
        
        // Call OpenAI API streaming
        stream := p.callOpenAIStream(ctx, messages)
        
        for apiChunk := range stream {
            // Transform API chunk → StreamChunk
            // ThinkingParser separates <thinking> from message content
            thinkingChunk, messageChunk := thinkingParser.Parse(apiChunk.Content)
            
            if thinkingChunk != nil {
                chunks <- thinkingChunk
            }
            if messageChunk != nil {
                chunks <- messageChunk
            }
        }
        
        // Flush and emit final chunk
        chunks <- &llm.StreamChunk{Finished: true}
    }()
    
    return chunks, nil
}
```

### ThinkingParser Integration

Providers use the shared `ThinkingParser` utility ([`pkg/llm/parser/thinking.go`](../../pkg/llm/parser/thinking.go)) to separate `<thinking>` content from message content:

**Why at Provider Level:**
- **Streaming efficiency**: Parse once during streaming vs buffering and re-parsing
- **Content transformation**: Provider's job is transforming raw API text → typed chunks
- **Performance**: Thinking separation is content-level concern, not agent logic
- **Universal format**: `<thinking>` is Forge-wide standard, not agent-specific

The ThinkingParser enables providers to emit properly-typed StreamChunks (ContentTypeThinking vs ContentTypeMessage) without understanding agent semantics.

---

## Validation

### Success Metrics

- ✅ **Multiple providers implemented**: OpenAI, Anthropic, Gemini support
- ✅ **Simple implementation**: New provider in <200 lines of code
- ✅ **Performance**: Chunks emitted within milliseconds of API reception
- ✅ **Independence**: Providers testable without agent framework
- ✅ **Reusability**: Providers used in CLI tools, batch jobs, not just agents

### Monitoring

- Track provider implementation complexity (LOC, dependencies)
- Measure streaming latency (API chunk → emitted chunk)
- Monitor provider test coverage independence

---

## Related Decisions

- [ADR-0002](0002-xml-format-for-tool-calls.md) - XML format for tool calls (provider-agnostic)
- [ADR-0004](0004-agent-content-processing.md) - Agent layer handles tool extraction and execution

---

## References

- [`pkg/llm/provider.go`](../../pkg/llm/provider.go) - Provider interface
- [`pkg/llm/types.go`](../../pkg/llm/types.go) - StreamChunk definition  
- [`pkg/llm/openai/openai.go`](../../pkg/llm/openai/openai.go) - Reference implementation
- [`pkg/llm/parser/thinking.go`](../../pkg/llm/parser/thinking.go) - ThinkingParser utility

---

## Notes

### Design Philosophy

The provider abstraction follows the principle: **"Providers are dumb pipes with content separation, agents are smart orchestrators."**

Providers should:
- ✅ Handle API communication
- ✅ Transform API responses → StreamChunks
- ✅ Separate thinking from message content
- ✅ Propagate errors appropriately

Providers should NOT:
- ❌ Understand tools or execute them
- ❌ Manage conversation memory
- ❌ Emit agent events
- ❌ Control agent loop flow

This separation enables:
- **Provider reusability** across different contexts
- **Simple provider implementation** (new devs can add providers easily)
- **Agent flexibility** (agents control their own orchestration)
- **Independent evolution** (providers and agents change independently)

### Future Enhancements

1. **Provider Metadata**: May add optional metadata field to StreamChunk
2. **Function Calling**: Evaluate if native function calling should be provider concern
3. **Token Counting**: Consider adding usage/token info to final chunk
4. **Retry Logic**: Standardize provider-level retry patterns

**Last Updated:** 2025-11-02