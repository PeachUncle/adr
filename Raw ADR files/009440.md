# 20. Context Information Overlay

**Status:** Accepted
**Date:** 2025-11-17
**Deciders:** Engineering Team
**Technical Story:** Implementation of comprehensive context visibility in the TUI executor

---

## Context

As Forge evolved into a sophisticated agent system with complex token management, memory handling, and tool orchestration, users needed visibility into the agent's internal state. Without this visibility, users couldn't understand:
- Why the agent was running out of context space
- How much of their conversation history was being retained
- What tools were available and their token overhead
- Whether they were approaching model context limits

### Background

The Forge agent maintains several components that consume context tokens:
1. **System Prompt**: Base instructions and agent identity
2. **Custom Instructions**: User-provided additional context
3. **Tool Schemas**: XML-formatted tool definitions
4. **Conversation Memory**: Message history with role markers
5. **Current Context**: Combined total of all components

Each component has token overhead that accumulates toward the model's maximum context window (typically 128K tokens for GPT-4). When context limits are approached, the agent must make decisions about what to trim or summarize, affecting conversation quality.

### Problem Statement

Users had no way to inspect the agent's context state during a conversation session. This created several issues:
- Users couldn't diagnose why responses degraded as conversations lengthened
- No visibility into token consumption patterns across different components
- Difficult to understand the trade-offs between adding tools vs. conversation length
- No feedback on cumulative API token usage across the session

### Goals

- Provide comprehensive visibility into all context components and their token usage
- Display real-time context consumption as percentage and absolute values
- Show cumulative API token usage across all requests in the session
- Present information in a clear, scannable format within the TUI
- Enable users to make informed decisions about context management

### Non-Goals

- Automatic context management or optimization suggestions
- Historical tracking of context usage across multiple sessions
- Export or logging of context statistics
- Integration with external monitoring tools

---

## Decision Drivers

* **User Experience**: Users need immediate, clear feedback about context state
* **Performance**: Context calculation must not introduce noticeable latency
* **Accuracy**: Token counts must match actual LLM provider calculations
* **Maintainability**: Solution must align with existing agent architecture
* **Extensibility**: Design should accommodate future context components

---

## Considered Options

### Option 1: Status Bar Context Display

**Description:** Add condensed context information to the existing TUI status bar

**Pros:**
- Always visible without user action
- Minimal UI changes required
- Integrates with existing status bar infrastructure

**Cons:**
- Limited space for detailed information
- Would clutter an already information-dense status bar
- Cannot show all context components simultaneously
- Poor user experience for scanning detailed statistics

### Option 2: Dedicated Context Panel

**Description:** Add a permanent split-screen panel showing context information

**Pros:**
- Always visible and comprehensive
- Can show real-time updates as context changes
- Familiar pattern from other development tools

**Cons:**
- Reduces space for conversation display (primary UI purpose)
- Information may not be needed constantly
- Increases visual complexity of the interface
- Wastes screen real estate when not actively needed

### Option 3: Modal Overlay Dialog (Chosen)

**Description:** Implement a command-triggered modal overlay that displays comprehensive context information

**Pros:**
- Full control over information density and organization
- Doesn't consume permanent screen space
- Can be dismissed when not needed
- Allows for scrollable content if statistics expand
- Fits existing TUI modal pattern (slash commands)

**Cons:**
- Requires user action to view (not always-on visibility)
- Adds another slash command to learn
- Information shown is a snapshot, not live-updating

---

## Decision

**Chosen Option:** Option 3 - Modal Overlay Dialog

### Rationale

The modal overlay approach provides the best balance of comprehensive information display and user control. Context information is critical but not constantly needed—users typically check it when:
1. Diagnosing performance issues
2. Planning to add more context (tools, instructions)
3. Understanding why context trimming occurred
4. Monitoring API token consumption for cost tracking

By using a slash command (`/context`) to trigger the overlay, we maintain the TUI's clean primary interface while making detailed statistics instantly available on demand. The modal pattern is already familiar to users through other TUI interactions.

---

## Consequences

### Positive

- Users can now inspect all context components and their token consumption
- Clear visibility into context window utilization (used/available/percentage)
- Visual progress bar provides at-a-glance context health status
- Cumulative token tracking helps users understand API costs
- Separate sections (System, Tools, History, Context, Usage) create scannable organization
- Color-coded progress bar (green/yellow/red) provides immediate status feedback
- Implementation follows existing TUI architectural patterns

### Negative

- Context information is snapshot-based, not live-updating during agent execution
- Adds another slash command for users to discover
- Token counting logic is duplicated between agent and tokenizer (potential consistency issues)
- Overlay blocks the main conversation view while displayed

### Neutral

- Requires users to learn the `/context` slash command
- Context statistics only reflect local session, not persisted across restarts
- Tool names list was removed to reduce clutter (count and token usage deemed sufficient)

---

## Implementation

### Architecture

The implementation spans three main components:

#### 1. Agent Layer (`pkg/agent/default.go`)

The `GetContextInfo()` method calculates all context statistics:

```go
func (a *DefaultAgent) GetContextInfo() *ContextInfo {
    // Calculate base system prompt tokens (without tools)
    baseSystemPrompt := prompts.NewPromptBuilder().
        WithCustomInstructions(a.customInstructions).
        Build()
    
    // Calculate tool section tokens separately
    toolsSection := "<available_tools>\n" + 
        prompts.FormatToolSchemas(a.getToolsList()) + 
        "</available_tools>\n\n"
    
    // Use tokenizer for accurate counts
    systemPromptTokens := a.tokenizer.CountTokens(baseSystemPrompt)
    toolTokens := a.tokenizer.CountTokens(toolsSection)
    
    // Calculate conversation memory tokens
    messages := a.memory.GetAll()
    conversationTokens := a.tokenizer.CountMessagesTokens(messages)
    
    // Build full context for total calculation
    fullSystemPrompt := prompts.NewPromptBuilder().
        WithTools(a.getToolsList()).
        WithCustomInstructions(a.customInstructions).
        Build()
    
    currentTokens := conversationTokens + a.tokenizer.CountTokens(fullSystemPrompt)
    
    return &ContextInfo{
        SystemPromptTokens:    systemPromptTokens,
        CustomInstructions:    a.customInstructions != "",
        ToolCount:             len(a.tools),
        ToolTokens:            toolTokens,
        ToolNames:             toolNames,
        MessageCount:          len(messages),
        ConversationTurns:     countUserMessages(messages),
        ConversationTokens:    conversationTokens,
        CurrentContextTokens:  currentTokens,
        MaxContextTokens:      a.contextManager.GetMaxTokens(),
        FreeTokens:            maxTokens - currentTokens,
        UsagePercent:          (currentTokens / maxTokens) * 100,
    }
}
```

**Design Decisions:**
- Separate calculation of system prompt and tool tokens allows visibility into each component
- Full context reconstruction ensures accurate total matches what's sent to LLM
- Tokenizer usage provides accurate counts matching provider calculations
- Fallback character-based estimation for cases where tokenizer unavailable

#### 2. TUI Executor Layer (`pkg/executor/tui/slash_commands.go`)

The `/context` slash command bridges agent and UI:

```go
func (m *Model) handleContextCommand() tea.Cmd {
    // Get context info from agent
    contextInfo := m.agent.GetContextInfo()
    
    // Augment with TUI-tracked cumulative usage
    overlayInfo := &ContextInfo{
        // Copy all agent-provided fields
        SystemPromptTokens:    contextInfo.SystemPromptTokens,
        // ... other fields ...
        
        // Add TUI session tracking
        TotalPromptTokens:     m.totalPromptTokens,
        TotalCompletionTokens: m.totalCompletionTokens,
        TotalTokens:           m.totalTokens,
    }
    
    // Create and activate overlay
    contextOverlay := NewContextOverlay(overlayInfo)
    m.overlay.activate(OverlayModeContext, contextOverlay)
    
    return nil
}
```

**Design Decisions:**
- TUI executor owns cumulative session token tracking (spans multiple agent calls)
- Agent owns current context state (single request snapshot)
- Separation of concerns: agent doesn't need to know about session totals

#### 3. Overlay Component (`pkg/executor/tui/context_overlay.go`)

The overlay renders context information with visual formatting:

```go
func buildContextContent(info *ContextInfo) string {
    // System Section
    System
      System Prompt:      12,450 tokens
      Custom Instructions: Yes

    // Tool System Section  
    Tool System
      Available Tools:    9 (8,234 tokens)
      Current Tool Call:  read_file (if pending)

    // Message History Section
    Message History
      Messages:           24
      Conversation Turns: 8
      Conversation:       15,678 tokens

    // Current Context Section
    Current Context
      Used:               36,362 / 128,000 tokens (28.4%)
      Free Space:         91,638 tokens
      [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

    // Cumulative Usage Section
    Cumulative Usage (All API Calls)
      Input Tokens:       145,234
      Output Tokens:      23,456
      Total:              168,690
}
```

**Design Decisions:**
- Hierarchical section organization (System → Tools → History → Context → Usage)
- Consistent right-alignment for numbers improves scannability
- Progress bar uses color coding: green (<70%), yellow (70-90%), red (>90%)
- Token counts formatted with thousands separators for readability
- Viewport with scrolling accommodates future expansion

### Token Counting Implementation

A critical fix was required in the tokenizer to ensure accurate empty conversation handling:

```go
// pkg/llm/tokenizer/tokenizer.go
func (t *Tokenizer) CountMessagesTokens(messages []types.Message) int {
    total := 0
    for _, msg := range messages {
        // Count message overhead and content
        total += 4 // per-message overhead
        total += t.CountTokens(string(msg.Role))
        total += t.CountTokens(msg.Content)
    }
    
    // Only add reply priming tokens if messages exist
    if len(messages) > 0 {
        total += 3 // reply priming overhead
    }
    
    return total
}
```

**Problem:** The tokenizer was adding 3 tokens for "reply priming" even for empty message arrays, causing `TestEmptyMemoryTokenCounting` to fail (expected 0, got 3).

**Solution:** Conditionally add reply priming tokens only when messages exist. This ensures:
- Empty conversations correctly report 0 conversation tokens
- Non-empty conversations include appropriate LLM overhead
- Token counts match actual API consumption

### Data Flow

1. User triggers `/context` slash command
2. TUI executor calls `agent.GetContextInfo()`
3. Agent calculates:
   - System prompt tokens (base + custom instructions)
   - Tool tokens (XML schemas for all registered tools)
   - Conversation tokens (all messages in memory)
   - Current total context (sum of all components)
4. TUI augments with session cumulative totals
5. Overlay component renders formatted display
6. User views information, presses ESC to dismiss
7. TUI returns to normal conversation view

### Migration Path

No migration required—this is a new feature. Existing functionality unchanged.

---

## Validation

### Success Metrics

- **Accuracy**: Token counts match actual LLM provider consumption (validated via API response headers)
- **Performance**: Context calculation completes in <50ms (imperceptible to user)
- **Usability**: Users successfully interpret context information without documentation
- **Test Coverage**: All token counting logic covered by unit tests

### Test Results

```
✓ TestEmptyMemoryTokenCounting - Validates 0 tokens for empty conversations
✓ TestMemoryTokenCounting - Validates accurate counting with messages
✓ TestContextInfoCalculation - Validates all fields populated correctly
✓ All pkg/agent tests passing (8/8)
✓ All pkg/executor/tui tests passing
✓ Full project test suite passing (go test ./...)
```

### Monitoring

Context accuracy is monitored through:
1. Unit tests comparing expected vs. actual token counts
2. User feedback on context limit behavior
3. Comparison of context calculations vs. API response token headers

---

## Related Decisions

- [ADR-0014](0014-composable-context-management.md) - Composable Context Management (establishes context calculation patterns)
- [ADR-0007](0007-memory-system-design.md) - Memory System Design (message storage underlying conversation tokens)
- [ADR-0009](0009-tui-executor-design.md) - TUI Executor Design (overlay pattern foundation)
- [ADR-0012](0012-enhanced-tui-executor.md) - Enhanced TUI Executor (slash command infrastructure)

---

## References

- [OpenAI Tokenizer Documentation](https://platform.openai.com/docs/guides/tokens)
- [Bubble Tea Viewport Component](https://github.com/charmbracelet/bubbles/tree/master/viewport)
- Forge Agent Interface: `pkg/agent/core/agent.go`
- Tokenizer Implementation: `pkg/llm/tokenizer/tokenizer.go`

---

## Notes

**Tool Names Removal:** Initial implementation included a list of tool names in the overlay. This was removed because:
- Tool count and token usage provide sufficient quantitative information
- Tool names created visual clutter (9+ tools listed)
- Users primarily care about token overhead, not specific tool names
- Tool names can be discovered through help system if needed

**Future Enhancements:**
- Live-updating context display during agent execution
- Historical context usage graphs across conversation
- Warnings when approaching context limits
- Suggestions for context optimization (e.g., "Consider clearing history")

**Last Updated:** 2025-11-17
