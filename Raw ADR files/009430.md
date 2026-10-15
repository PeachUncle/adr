# 7. Memory System Design

**Status:** Accepted
**Date:** 2025-10-29
**Deciders:** Forge Core Team
**Technical Story:** Managing conversation history within LLM context window limits

---

## Context

Agent conversations can become very long, potentially exceeding LLM context windows (which range from 4K to 200K+ tokens depending on the provider). We needed a conversation history management system that:

1. Stores all messages in the conversation
2. Retrieves messages efficiently for LLM calls
3. Fits within token budget constraints
4. Preserves critical context (system instructions)
5. Remains simple and predictable

### Background

LLM agents maintain conversation history to provide context for multi-turn interactions. However:
- Context windows have hard limits (provider-dependent)
- Longer contexts increase API costs and latency
- Not all historical messages are equally important
- System messages (instructions) must always be preserved
- Concurrent access patterns require thread-safety

### Problem Statement

How do we manage conversation history in a way that:
- Fits within provider token limits
- Preserves the most relevant context
- Maintains system instructions
- Supports concurrent access patterns
- Remains simple and extensible

### Goals

- Simple, predictable pruning behavior
- Preserve system messages (critical instructions)
- Keep recent conversation history (most relevant)
- Thread-safe for concurrent access
- Extensible through interface abstraction

### Non-Goals

- Semantic importance analysis (too complex for v1)
- Persistent storage (can be added later)
- Multi-session management (out of scope)
- Provider-specific optimizations (keep generic)

---

## Decision Drivers

* **Simplicity**: Avoid complex heuristics that are hard to reason about
* **Predictability**: Users should understand what gets kept/pruned
* **Thread-Safety**: Agent loop runs concurrently with event emission
* **Extensibility**: Interface allows alternative implementations
* **Provider-Agnostic**: Work across all LLM providers

---

## Considered Options

### Option 1: Recency-Based Pruning with System Message Preservation

**Description:** Interface-based design with simple in-memory implementation that keeps system messages and most recent conversation messages.

**Pros:**
- Simple and predictable behavior
- Always preserves critical system instructions
- Recent context is most relevant for agents
- Easy to test and debug
- Thread-safe with RWMutex
- Interface allows future enhancements

**Cons:**
- May lose important context from middle of conversation
- Token estimation is approximate (1 token ≈ 4 chars)
- No persistence across restarts
- No semantic importance analysis

### Option 2: Semantic Importance Scoring

**Description:** Analyze messages for importance (decisions, key facts, tool results) and keep highest-scoring messages.

**Pros:**
- Could preserve more valuable context
- More intelligent pruning decisions

**Cons:**
- Complex to implement correctly
- Subjective importance criteria
- Computationally expensive (requires embeddings or analysis)
- Harder to predict what gets pruned
- May still lose recent context (which is often most important)

### Option 3: Turn-Based Pruning (Complete Exchanges)

**Description:** Prune complete user-assistant turn pairs to maintain coherent conversation structure.

**Pros:**
- Maintains conversational coherence
- Easier to understand pruned history

**Cons:**
- Wastes tokens if assistant response is large but user query small
- Doesn't account for system messages or tool results
- Less flexible than message-level pruning
- May not fit budget if turns are large

### Option 4: Sliding Window (Fixed Message Count)

**Description:** Keep only the last N messages regardless of token count.

**Pros:**
- Extremely simple implementation
- Predictable behavior

**Cons:**
- Ignores token budget constraints
- May exceed context window with large messages
- Doesn't preserve system messages specially
- Too rigid for variable message sizes

### Option 5: Exact Tokenization

**Description:** Use provider-specific tokenizers (like tiktoken for OpenAI) for accurate token counting.

**Pros:**
- Exact token counts
- No risk of exceeding context window

**Cons:**
- Requires provider-specific tokenizer dependencies
- Adds complexity and library dependencies
- Tokenizers may not be available for all providers
- Approximate estimation works well enough in practice

---

## Decision

**Chosen Option:** Option 1 - Recency-Based Pruning with System Message Preservation

### Rationale

We chose recency-based pruning for several key reasons:

1. **Simplicity**: The algorithm is straightforward - always keep system messages, then keep as many recent messages as fit within the token budget
2. **Predictability**: Users can easily understand what will be preserved and what will be pruned
3. **Recent = Relevant**: In agent conversations, recent context is typically most relevant for the current task
4. **System Message Preservation**: Critical instructions and agent capabilities must always be available
5. **Extensibility**: The Memory interface allows future implementations (persistent, semantic, etc.) without changing the agent core
6. **Thread-Safety**: RWMutex provides safe concurrent access for agent loop + event emission patterns
7. **Provider-Agnostic**: Approximate token counting works across all providers without dependencies

The approximate token estimation (1 token ≈ 4 characters) is good enough in practice. The 4:1 ratio is conservative and provides a safety margin to avoid exceeding context windows.

---

## Consequences

### Positive

- **Simple Mental Model**: Easy to understand and debug
- **System Messages Protected**: Critical instructions never pruned
- **Recent Context Preserved**: Most relevant messages kept
- **Thread-Safe**: Handles concurrent access correctly
- **No Dependencies**: No tokenizer libraries required
- **Extensible**: Interface allows alternative implementations
- **Provider-Agnostic**: Works with any LLM provider
- **Testing**: Easy to test with predictable behavior

### Negative

- **Approximate Tokens**: May under/overestimate actual token count
- **Context Loss**: Important information from middle of conversation may be pruned
- **No Persistence**: Messages lost on restart
- **No Semantic Analysis**: Can't identify and preserve important decisions/facts
- **Conservative Estimation**: 4:1 ratio may leave tokens unused

### Neutral

- **In-Memory Storage**: Fast access but no persistence (can add later via interface)
- **Message Copying**: Returns copies to prevent external modification (safe but uses more memory)
- **Fixed Strategy**: Recency-based only (alternatives can implement Memory interface)

---

## Implementation

### Memory Interface

Defined in [`pkg/agent/memory/memory.go`](../../pkg/agent/memory/memory.go):

```go
type Memory interface {
    Add(msg *types.Message)
    GetAll() []*types.Message
    GetRecent(n int) []*types.Message
    Clear()
    Prune(maxTokens int) error
    Count() int
}
```

### ConversationMemory Implementation

Implemented in [`pkg/agent/memory/conversation.go`](../../pkg/agent/memory/conversation.go):

```go
type ConversationMemory struct {
    messages []*types.Message
    mu       sync.RWMutex
}
```

### Pruning Algorithm

1. **Separate Messages**: Split into system messages and conversation messages
2. **Calculate System Token Budget**: Count tokens in all system messages
3. **Calculate Remaining Budget**: `remainingTokens = maxTokens - systemTokens`
4. **Keep Recent Messages**: Working backwards from newest message, keep messages until budget exhausted
5. **Rebuild**: Combine system messages + kept conversation messages

### Token Estimation

```go
estimateTokens := func(msg *types.Message) int {
    return len(msg.Content) / 4
}
```

Conservative 4:1 character-to-token ratio provides safety margin.

### Thread Safety

Uses `sync.RWMutex`:
- Read lock for `GetAll()`, `GetRecent()`, `Count()`, `GetByRole()`
- Write lock for `Add()`, `Clear()`, `Prune()`, `AddMultiple()`

---

## Validation

### Success Metrics

- Memory usage remains bounded
- No context window exceeded errors
- System messages always present in LLM calls
- Recent conversation context preserved
- No race conditions in concurrent access

### Testing

Tests in [`pkg/agent/memory/memory_test.go`](../../pkg/agent/memory/memory_test.go):
- Basic operations (Add, GetAll, GetRecent, Clear, Count)
- Pruning behavior with various token limits
- System message preservation during pruning
- Thread-safety under concurrent access
- Edge cases (empty memory, negative limits, etc.)

Run with:
```bash
go test ./pkg/agent/memory -v
```

---

## Related Decisions

- [ADR-0001: Record Architecture Decisions](0001-record-architecture-decisions.md) - Establishes ADR process
- [ADR-0003: Provider Abstraction Layer](0003-provider-abstraction-layer.md) - Provider-agnostic design philosophy
- [ADR-0004: Agent-Level Content Processing](0004-agent-content-processing.md) - Agent uses memory for conversation history

---

## References

- Implementation: [`pkg/agent/memory/`](../../pkg/agent/memory/)
- Message Types: [`pkg/types/message.go`](../../pkg/types/message.go)
- Usage in Agent: [`pkg/agent/default.go`](../../pkg/agent/default.go)

---

## Notes

### Future Enhancements

Potential improvements that could be added through new Memory implementations:

1. **Persistent Memory**: Store conversation to database/file system
2. **Semantic Pruning**: Use embeddings to identify important messages
3. **Hybrid Strategies**: Combine recency + importance scoring
4. **Exact Tokenization**: Use provider-specific tokenizers when available
5. **Multi-Session**: Manage multiple conversation sessions
6. **Message Search**: Filter/query historical messages
7. **Metadata/Tagging**: Tag messages for selective retrieval
8. **Summarization**: Summarize pruned context instead of discarding

These can be implemented as alternative Memory interface implementations without changing the agent core.

**Last Updated:** 2025-11-02