# 8. Agent-Controlled Loop Termination

**Status:** Accepted  
**Date:** 2025-10-29  
**Deciders:** Forge Core Team  
**Technical Story:** Enabling autonomous agent operation with agent-controlled exit conditions

---

## Context

Traditional programming loops use deterministic exit conditions (counter limits, boolean flags, explicit breaks). Agent loops present a unique challenge: the agent needs to run autonomously for as long as necessary to complete a task, but must eventually return control to the user or caller.

### Problem Statement

How do we design an agent loop that:
1. Runs autonomously without predetermined iteration limits
2. Allows the agent to work as long as needed (could be 1 iteration or 100)
3. Returns control to the user/caller when appropriate
4. Doesn't require the framework to determine "when the agent is done"
5. Prevents infinite loops while maintaining autonomy

The fundamental question: **Who decides when the agent loop should exit?**

### Goals

- **Agent Autonomy**: Let the agent decide when its work is complete
- **No Arbitrary Limits**: Avoid hardcoded max iteration counts
- **Flexible Duration**: Support both quick tasks (1-2 iterations) and complex tasks (many iterations)
- **Clear Exit Points**: Agent explicitly signals when to return control
- **Safety**: Prevent infinite loops through circuit breakers

### Non-Goals

- Predicting task complexity in advance
- Framework-level "task completion" detection
- Time-based or iteration-count-based termination as primary mechanism
- Supporting agents that never call tools

---

## Decision Drivers

* **Autonomy**: Agents should self-determine when work is complete
* **Flexibility**: Different tasks require different iteration counts
* **Clarity**: Exit conditions should be explicit, not inferred
* **Safety**: Must protect against infinite loops
* **Simplicity**: Easy to understand and reason about

---

## Considered Options

### Option 1: Max Iteration Count

**Description:** Set a maximum number of iterations (e.g., 10, 50, 100) and terminate when reached.

**Pros:**
- Simple to implement
- Guaranteed termination
- Predictable resource usage

**Cons:**
- **Arbitrary limit**: How do you choose the right number?
- **Wastes iterations**: Simple tasks forced to hit max
- **Insufficient for complex tasks**: Complex tasks may need more
- **Framework decides**: Takes control away from the agent
- **Poor UX**: Agent interrupted mid-task feels broken

**Verdict:** ❌ Rejected - Too rigid, undermines agent autonomy

### Option 2: Timeout-Based Termination

**Description:** Run agent loop until a time limit is reached.

**Pros:**
- Prevents infinite resource consumption
- Works with context deadlines

**Cons:**
- **Unrelated to task completion**: Time ≠ task done
- **Variable LLM latency**: Same task takes different time
- **Interrupts mid-task**: Agent cut off arbitrarily
- **Framework decides**: Not agent-controlled

**Verdict:** ❌ Rejected - Time is orthogonal to completion

### Option 3: Framework Heuristics (Completion Detection)

**Description:** Framework analyzes agent responses to infer completion (keywords, sentiment, etc.).

**Pros:**
- Agents don't need special tools
- Could work with any LLM

**Cons:**
- **Unreliable**: Natural language is ambiguous
- **False positives**: "I'm done thinking" ≠ "Task complete"
- **Complex logic**: Requires sophisticated NLP heuristics
- **Framework complexity**: Inference logic is brittle
- **No clear signal**: Agent can't explicitly control exit

**Verdict:** ❌ Rejected - Too unreliable, overly complex

### Option 4: Agent-Controlled Loop Termination (Chosen)

**Description:** Agent must execute a tool call every iteration. Loop terminates when agent calls a loop-breaking tool (e.g., `task_completion`, `ask_question`, `converse`).

**Pros:**
- **Agent autonomy**: Agent explicitly decides when to exit
- **Clear semantics**: Loop-breaking tools have obvious meaning
- **Flexible duration**: Works for any task length
- **No arbitrary limits**: Runs as long as needed
- **Explicit signal**: No ambiguity about exit intent
- **Type-safe**: `IsLoopBreaking()` interface method

**Cons:**
- **Requires tool call**: Agent must call a tool every iteration
- **Learning curve**: Agents must understand loop-breaking concept
- **Potential for infinite loops**: Mitigated by circuit breaker

**Verdict:** ✅ Accepted - Best balance of autonomy, clarity, and safety

---

## Decision

**Chosen Option:** Option 4 - Agent-Controlled Loop Termination

### Rationale

We delegate loop control to the agent itself. The agent decides when to exit by calling a **loop-breaking tool**. This design treats the agent as an autonomous entity that knows when its work is complete.

**Core Principle**: The agent loop runs indefinitely until the agent explicitly signals termination via a loop-breaking tool.

### How It Works

1. **Iteration Requirement**: Agent must execute a tool call every iteration
   - If no tool call: Error recovery mechanism kicks in
   - Prevents agents from "talking in circles" without taking action

2. **Loop-Breaking Tools**: Tools with `IsLoopBreaking() == true`
   - `task_completion`: "I've finished the task, here's the result"
   - `ask_question`: "I need user input to proceed"
   - `converse`: "This is conversational, not a task"

3. **Loop Termination**: After executing a loop-breaking tool:
   ```go
   if tool.IsLoopBreaking() {
       return false, "" // Stop loop
   }
   ```

4. **Non-Breaking Tools**: Result added to memory, loop continues:
   ```go
   a.memory.Add(types.NewUserMessage(fmt.Sprintf("Tool '%s' result:\n%s", toolCall.ToolName, result)))
   return true, "" // Continue loop
   ```

5. **Safety Net**: Circuit breaker prevents infinite loops (see ADR-0006)

### Tool Interface Design

The `IsLoopBreaking()` method is part of the `Tool` interface:

```go
type Tool interface {
    Name() string
    Description() string
    Schema() map[string]interface{}
    Execute(ctx context.Context, arguments json.RawMessage) (string, error)
    IsLoopBreaking() bool  // Determines loop control
}
```

This makes loop control a first-class concern in tool design.

---

## Consequences

### Positive

- **True Autonomy**: Agent self-determines completion, no framework inference
- **Flexible Duration**: Works for 1-iteration or 100-iteration tasks equally well
- **Clear Semantics**: Loop-breaking tools have explicit, understandable purpose
- **No Arbitrary Limits**: No hardcoded max iterations or timeouts
- **Type-Safe**: `IsLoopBreaking()` enforced at compile time
- **Extensible**: New loop-breaking tools can be added (e.g., `delegate_task`, `escalate`)
- **Predictable**: Easy to reason about when loop will exit
- **Better UX**: Agent controls its own execution flow

### Negative

- **Tool Call Required**: Agent must call a tool every iteration (but this is also a feature - ensures progress)
- **Learning Curve**: Developers must understand loop-breaking vs non-breaking tools
- **Potential Confusion**: Agents might call wrong tool type if not well-prompted
- **Safety Depends on Circuit Breaker**: Infinite loops prevented by separate mechanism (ADR-0006)

### Neutral

- **Framework Simplicity**: Loop logic becomes simpler - just check `IsLoopBreaking()`
- **Prompting Responsibility**: System prompts must teach agents about loop-breaking tools
- **Tool Design Decisions**: Each custom tool must declare if it breaks the loop

---

## Implementation

### Agent Loop

Defined in [`pkg/agent/default.go`](../../pkg/agent/default.go:235):

```go
func (a *DefaultAgent) runAgentLoop(ctx context.Context) {
    var errorContext string
    
    for {
        // Execute one iteration with optional error context
        shouldContinue, nextErrorContext := a.executeIteration(ctx, errorContext)
        if !shouldContinue {
            // Loop-breaking tool was called or terminal error occurred
            return
        }
        
        // Update error context for next iteration
        errorContext = nextErrorContext
    }
}
```

**Key insight**: Infinite `for` loop with no predetermined exit condition. Only agent can terminate.

### Tool Execution

Defined in [`pkg/agent/default.go`](../../pkg/agent/default.go:510):

```go
// Check if this is a loop-breaking tool
if tool.IsLoopBreaking() {
    return false, "" // Stop loop
}

// For non-breaking tools, add result to memory and continue loop
a.memory.Add(types.NewUserMessage(fmt.Sprintf("Tool '%s' result:\n%s", toolCall.ToolName, result)))
return true, "" // Continue with no error
```

### Built-In Loop-Breaking Tools

Forge provides three built-in loop-breaking tools:

1. **`task_completion`** ([`pkg/agent/tools/task_completion.go`](../../pkg/agent/tools/task_completion.go))
   - Signals task is complete
   - Returns final result to user
   - Most common exit path

2. **`ask_question`** ([`pkg/agent/tools/ask_question.go`](../../pkg/agent/tools/ask_question.go))
   - Requests user input for clarification
   - Pauses agent, waits for response
   - Used when agent lacks information

3. **`converse`** ([`pkg/agent/tools/converse.go`](../../pkg/agent/tools/converse.go))
   - Engages in conversation without completing task
   - Used for casual interactions
   - Returns conversational response

All implement `IsLoopBreaking() bool { return true }`.

### Example Flow

**Simple Task (3 iterations):**
```
Iteration 1: Agent calls file_reader tool (non-breaking) → continues
Iteration 2: Agent calls code_analyzer tool (non-breaking) → continues  
Iteration 3: Agent calls task_completion (breaking) → exits
```

**Task Requiring Input:**
```
Iteration 1: Agent calls list_files tool (non-breaking) → continues
Iteration 2: Agent realizes ambiguity, calls ask_question (breaking) → exits, waits for user
```

---

## Validation

### Success Metrics

- ✅ **Agents complete tasks without hitting iteration limits**
- ✅ **Simple tasks exit quickly (1-3 iterations typical)**
- ✅ **Complex tasks run as long as needed (seen 20+ iterations)**
- ✅ **No infinite loops in production** (circuit breaker catches pathological cases)
- ✅ **Clear exit semantics** (developers understand loop-breaking tools)

### Monitoring

- Track iterations per task (median, p95, p99)
- Monitor circuit breaker activation rate
- Analyze tool usage patterns (breaking vs non-breaking)
- User feedback on task completion accuracy

---

## Related Decisions

- [ADR-0002: XML Format for Tool Calls](0002-xml-format-for-tool-calls.md) - Tool call mechanism
- [ADR-0006: Self-Healing Error Recovery](0006-self-healing-error-recovery.md) - Circuit breaker prevents infinite loops
- [ADR-0007: Memory System Design](0007-memory-system-design.md) - Non-breaking tool results stored in memory

---

## References

- Tool Interface: [`pkg/agent/tools/tool.go`](../../pkg/agent/tools/tool.go:31-34)
- Agent Loop: [`pkg/agent/default.go`](../../pkg/agent/default.go:235-249)
- Loop-Breaking Tools: [`pkg/agent/tools/`](../../pkg/agent/tools/)

---

## Notes

### Design Philosophy

This decision embodies a core philosophy of Forge: **Trust the agent**. Rather than imposing external control structures, we give agents the tools to control their own execution. This mirrors how human workers operate - you don't limit how many steps someone can take to complete a task; you trust them to signal when they're done.

### Alternative Exit Points

While loop-breaking tools are the primary mechanism, the loop can also exit via:
- **Circuit breaker**: 5 identical consecutive errors (safety mechanism)
- **Context cancellation**: User interrupt or timeout (external control)
- **LLM API failure**: Terminal error (infrastructure failure)

These are fail-safes, not normal exit paths.

### Future Enhancements

Potential extensions to the loop control model:

1. **Parallel Tool Calls**: Agent calls multiple non-breaking tools simultaneously
2. **Subtask Delegation**: Loop-breaking `delegate_task` tool spawns child agent
3. **Pause/Resume**: `pause` tool saves state, `resume` continues later
4. **Conditional Breaking**: Tools that are breaking under certain conditions
5. **Loop Budget**: Soft limits that warn but don't terminate

**Last Updated:** 2025-11-02