# Decision: Telemetry and Debugging Approach

## Status
**Proposed** - Awaiting review and approval

## Context
Building agent systems introduces multiple layers of potential failure:
- Tool implementation bugs
- LLM formatting errors (tool calls, data formats)
- Workflow sequencing issues
- Context window limitations for debugging

Traditional "build everything then debug" approaches make it nearly impossible to isolate which layer is failing. Additionally, standard telemetry formats (large JSON logs, OpenTelemetry spans) often exceed LLM context windows, preventing AI-assisted debugging.

## Decision
Adopt a **progressive development approach** with **dual-format telemetry**:

1. **Build in phases**: Tools → Workflows → Agents
2. **Verify each layer** independently before integration
3. **Dual telemetry format**: Full detail for systems, compact for LLMs
4. **Hierarchical storage** with selective loading
5. **Built-in debugging interfaces** at each layer

## Rationale

### Why Progressive Development?
- **Isolation**: Each layer can be tested independently
- **Confidence**: Know tools work before adding LLM complexity
- **Debugging**: Clear which layer failed when issues occur
- **Velocity**: Faster to fix issues when you know where they are

### Why Dual-Format Telemetry?
- **LLM Analysis**: Compact format fits in context windows
- **Human Debugging**: Full detail available when needed
- **Retrospectives**: Can analyze patterns across executions
- **Progressive Detail**: Load only what's needed for the task

### Why This Order (Tools → Workflows → Agents)?
Based on production experience:
1. **Tools first**: Foundation must be solid
2. **Workflows second**: Sequencing logic without LLM unpredictability
3. **Agents last**: Add LLM only after deterministic parts work

## Implementation Approach

### Phase 1: Tool Development
```rust
// Every tool implements verification interface
pub trait VerifiableTool {
    fn verify_input(&self, input: &ToolInput) -> ValidationResult;
    fn verify_output(&self, output: &ToolOutput) -> ValidationResult;
    async fn execute_debug(&self, input: ToolInput) -> DebugResult;
}
```

### Phase 2: Workflow Development
```rust
// Test workflows with deterministic paths
pub struct WorkflowTestHarness {
    pub async fn execute_path(&mut self, path: Vec<Step>) -> TestResult;
}
```

### Phase 3: Agent Integration
```rust
// Separate validation of each failure mode
pub struct AgentDebugger {
    pub async fn verify_tool_call_format(&self, response: &LLMResponse) -> ValidationResult;
    pub async fn verify_data_format(&self, response: &LLMResponse) -> ValidationResult;
}
```

### Telemetry Format Strategy
```rust
// Compact format for LLMs
pub struct CompactTrace {
    summary: String,           // < 100 tokens
    key_events: Vec<KeyEvent>, // < 500 tokens
    error_chain: Option<ErrorChain>, // < 300 tokens
}

// Smart truncation
pub trait TelemetryFormatter {
    fn format_for_context_window(&self, max_tokens: usize) -> String;
}
```

## Consequences

### Positive
- **Faster debugging**: Clear isolation of failures
- **Better testing**: Each layer fully tested before integration
- **LLM-assisted debugging**: Telemetry fits in context windows
- **Learning curve**: Easier to understand one layer at a time
- **Maintainability**: Clear separation of concerns

### Negative
- **Initial overhead**: More setup for verification interfaces
- **Storage complexity**: Dual-format requires more design
- **Development discipline**: Must resist jumping to agent layer

### Neutral
- Changes typical development workflow
- Requires explicit phase transitions
- More upfront design of interfaces

## Alternatives Considered

### Alternative 1: Traditional All-at-Once
Build complete agent system, debug holistically.
- **Rejected because**: Too hard to isolate failures

### Alternative 2: Standard Telemetry Only
Use only OpenTelemetry/JSON logs.
- **Rejected because**: Exceeds LLM context windows

### Alternative 3: Minimal Telemetry
Log only errors and key events.
- **Rejected because**: Insufficient for debugging complex flows

## Implementation Priority
**High** - This is foundational for development velocity

## Open Questions
1. What specific detail levels for telemetry? (Summary/Key/Diagnostic/Full sufficient?)
2. How long to retain detailed telemetry? (Storage vs debugging needs)
3. Should we auto-generate verification tests from tool schemas?
4. Format for LLM-consumable telemetry? (Markdown vs structured text)

## References
- [elements/progressive_telemetry_strategy.md] - Detailed implementation strategy
- [elements/monitoring_strategy.md] - Existing monitoring approach
- [elements/failure_recovery_strategies.md] - Related failure handling

## Decision History
- 2025-01-18: Initial proposal based on production experience
- [Awaiting review and approval]