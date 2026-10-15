# 5. Channel-Based Agent Communication

**Status:** Accepted
**Date:** 2025-10-30
**Deciders:** Forge Core Team
**Technical Story:** Designing a robust, asynchronous communication mechanism between agents and their executors

---

## Context

Forge agents run as long-lived, concurrent processes. We need a communication pattern that allows an external "executor" (like a CLI, API server, or GUI) to interact with an agent without blocking, enabling true asynchronous and event-driven behavior.

### Problem Statement

How should an executor and an agent communicate? The solution must support:
1. Sending user input to the agent
2. Receiving a stream of rich events (thinking, tool calls, messages) from the agent
3. Handling graceful shutdown and cancellation
4. Decoupling the agent's internal event loop from the executor's logic
5. Concurrency safety and idiomatic Go design

### Background

An agent's lifecycle is asynchronous. It processes input, makes LLM calls, and runs tools in the background. A simple request-response model wouldn't work because the agent needs to emit a stream of events over time for a single input. We need a pattern that embraces this asynchronicity.

### Goals

- Decouple agent and executor lifecycles
- Enable non-blocking, asynchronous communication
- Provide a rich, real-time event stream to the executor
- Ensure concurrency safety and prevent race conditions
- Use an idiomatic Go concurrency pattern
- Support graceful shutdown and in-flight request cancellation

### Non-Goals

- Support for non-Go executors (the pattern is Go-specific, but the *concept* is portable)
- A single, universal communication bus for all agents
- The simplest possible interface (some complexity is acceptable for robustness)

---

## Decision Drivers

* **Asynchronous Nature**: Agents are inherently async; the communication pattern must reflect this
* **Go Idiom**: Leverage Go's core concurrency primitives (goroutines and channels)
* **Decoupling**: The agent should run independently of how its inputs are provided or outputs are consumed
* **Observability**: Executors need real-time insight into the agent's state (thinking, using tools, etc.)
* **Lifecycle Management**: Must handle startup, shutdown, and cancellation gracefully
* **Concurrency Safety**: The pattern must be safe for concurrent access from multiple goroutines

---

## Considered Options

### Option 1: Callback-Based API

**Description:** The executor passes callback functions to the agent for different events (e.g., `OnMessage(func...)`, `OnToolCall(func...)`).

**Pros:**
- Familiar pattern from other languages (e.g., JavaScript event listeners)
- Explicitly defines event handlers

**Cons:**
- **"Callback Hell"**: Can lead to deeply nested and hard-to-read code
- **State management**: The executor becomes responsible for managing state across multiple callbacks
- **Concurrency issues**: Requires manual locking within callbacks to safely update shared state
- **Not idiomatic Go**: While possible, channels are the preferred concurrency pattern in Go

**Verdict:** ❌ Rejected - Leads to complex state management and is not idiomatic Go.

### Option 2: Synchronous Request-Response

**Description:** The executor makes a single blocking call to the agent and receives a complete `TurnResult` object after the entire turn is finished.

**Pros:**
- Simple to understand
- No concurrency management needed for the caller

**Cons:**
- **Blocks the caller**: The executor is frozen until the agent completes its full turn
- **No real-time feedback**: Can't show thinking, tool calls, or streaming message content
- **Poor UX**: Users see a long delay with no feedback
- **Doesn't fit the model**: Ignores the streaming, event-driven nature of LLM agents

**Verdict:** ❌ Rejected - Fails to meet the core requirement for real-time, asynchronous feedback.

### Option 3: A Single, Bidirectional Channel

**Description:** Use a single channel of an `interface{}` or a generic `Message` struct for all communication in both directions.

**Pros:**
- Simple infrastructure (just one channel)
- Flexible message types

**Cons:**
- **Type safety issues**: Requires type assertions and switches on every received message
- **Directionality is unclear**: Who is allowed to send what? It's easy to create deadlocks
- **No clear ownership**: Who closes the channel? Leads to complex lifecycle management
- **Mixed concerns**: Input, output, and control signals are all mixed, making logic complex

**Verdict:** ❌ Rejected - Unsafe, complex to manage, and obscures communication flow.

### Option 4: A Struct of Unidirectional Channels (Chosen)

**Description:** Define a struct (`AgentChannels`) containing multiple, unidirectional channels, each with a specific purpose (input, events, control).

**Pros:**
- **Type Safe**: Each channel has a specific type (`*Input`, `*AgentEvent`).
- **Clear Directionality**: `chan<-` and `<-chan` semantics are clear. The `Input` channel is for writing to the agent, `Event` is for reading from it.
- **Separation of Concerns**: Data (`Input`, `Event`) is separate from control signals (`Shutdown`, `Done`).
- **Idiomatic Go**: This is the canonical way to structure concurrent Go programs.
- **Prevents Deadlocks**: By following clear ownership rules (the sender closes the channel), deadlocks are easier to avoid.
- **Structured Lifecycle**: The `Shutdown` and `Done` channels provide a clean, explicit mechanism for graceful shutdown.

**Cons:**
- **More complex setup**: Requires initializing and managing a struct of channels.
- **Requires understanding of Go concurrency**: Users need to be familiar with channels and the `select` statement.

**Verdict:** ✅ Accepted - The most robust, type-safe, and idiomatic solution for Go.

---

## Decision

**Chosen Option:** Option 4 - A Struct of Unidirectional Channels

### Channel and Lifecycle Design

We will use the `AgentChannels` struct to manage all communication between an agent and its executor. This struct is the "contract" for how to interact with a running agent.

#### `AgentChannels` Struct

Located in [`pkg/types/channels.go`](../../pkg/types/channels.go):

```go
type AgentChannels struct {
    // Executor -> Agent
    Input    chan *Input
    Shutdown chan struct{}

    // Agent -> Executor
    Event chan *AgentEvent
    Done  chan struct{}
}
```

**Channel Responsibilities:**

1.  **`Input` (`chan *Input`)**:
    *   **Direction**: Executor to Agent.
    *   **Purpose**: Sends user inputs, cancellation signals, or other commands to the agent.
    *   **Ownership**: The executor writes to this channel. The agent is the sole reader.

2.  **`Event` (`chan *AgentEvent`)**:
    *   **Direction**: Agent to Executor.
    *   **Purpose**: The agent emits a rich stream of events for real-time observability (thinking, messages, tool calls, errors, etc.).
    *   **Ownership**: The agent is the sole writer. The executor reads from this channel.

3.  **`Shutdown` (`chan struct{}`)**:
    *   **Direction**: Executor to Agent.
    *   **Purpose**: A signal-only channel. The executor closes this channel to request a graceful shutdown.
    *   **Ownership**: The executor closes this channel. The agent listens for the close event.

4.  **`Done` (`chan struct{}`)**:
    *   **Direction**: Agent to Executor.
    *   **Purpose**: A signal-only channel. The agent closes this channel to confirm that it has completed its shutdown process.
    - **Ownership**: The agent closes this channel. The executor can wait on this to ensure a clean exit.

#### Lifecycle Protocol:

1.  **Startup**:
    *   The executor creates an agent.
    *   The executor calls `agent.Start(ctx)`, which launches the agent's main `eventLoop` goroutine.
    *   The agent begins listening on its `Input` and `Shutdown` channels.

2.  **Interaction**:
    *   The executor reads user input and sends it to the `Input` channel.
    *   The executor continuously reads from the `Event` channel in a separate goroutine and updates the UI.

3.  **Graceful Shutdown**:
    *   The executor closes the `Shutdown` channel.
    *   The agent's `eventLoop` `select` statement detects the closed `Shutdown` channel and breaks its loop.
    *   Before returning, the agent's `eventLoop` `defer`s `channels.Close()`, which closes the `Event` and `Done` channels.
    *   The executor, waiting on the `Done` channel, unblocks and knows the agent has shut down cleanly.

---

## Consequences

### Positive

-   **Decoupling**: The executor and agent are completely decoupled. The agent doesn't know or care if it's being driven by a CLI, an API, or a test harness.
-   **Concurrency Safety**: Channels provide a safe way to communicate between goroutines without needing manual locks.
-   **Clear Contract**: The `AgentChannels` struct is an explicit and type-safe API for agent interaction.
-   **Testability**: It's easy to write a test executor that drives the agent through its channels and asserts on the received events.
-   **Idiomatic**: Follows Go's core philosophy: *"Do not communicate by sharing memory; instead, share memory by communicating."*
-   **Robust Lifecycle Management**: The `Shutdown`/`Done` pattern is a standard and robust way to manage goroutine lifecycles.

### Negative

-   **Complexity Overhead**: Users must understand Go channels, goroutines, and the `select` statement. This is a reasonable expectation for a Go framework.
-   **Potential for Deadlocks**: If channel ownership rules are not respected (e.g., a reader tries to close a channel), it can lead to panics or deadlocks. The clear ownership defined in this ADR mitigates this.
-   **Buffered Channels**: The `Input` and `Event` channels are buffered (default size 10) to prevent temporary blocking. If the executor or agent can't keep up, these channels could fill up, causing the sender to block. This is a design choice that favors backpressure over unbounded memory growth.

### Neutral

-   The design is inherently Go-specific, which is appropriate for a Go framework.

---

## Implementation

### Channel Definition

Located in [`pkg/types/channels.go`](../../pkg/types/channels.go):
```go
func NewAgentChannels(bufferSize int) *AgentChannels {
    return &AgentChannels{
        Input:    make(chan *Input, bufferSize),
        Event:    make(chan *AgentEvent, bufferSize),
        Shutdown: make(chan struct{}),
        Done:     make(chan struct{}),
    }
}
```

### Agent's Event Loop

Located in [`pkg/agent/default.go`](../../pkg/agent/default.go):
```go
func (a *DefaultAgent) eventLoop(ctx context.Context) {
    defer a.channels.Close() // Guarantees Done and Event channels are closed on exit.

    for {
        select {
        case <-ctx.Done():
            // Application-level context was canceled.
            return
        case <-a.channels.Shutdown:
            // Graceful shutdown was requested.
            return
        case input := <-a.channels.Input:
            // A new input was received.
            a.processInput(ctx, input)
        }
    }
}
```

### Executor's Interaction Loop

Example from [`pkg/executor/cli/executor.go`](../../pkg/executor/cli/executor.go):
```go
// In a dedicated goroutine:
func (e *Executor) handleEvents(events <-chan *types.AgentEvent, ...) {
    for event := range events {
        // process event and update UI
    }
}

// In the main goroutine:
func (e *Executor) Run(ctx context.Context) error {
    // ... start agent and event handler ...

    for {
        // ... read user input ...

        // Send to agent
        channels.Input <- types.NewUserInput(input)

        // ... wait for turn to complete ...
    }
}
```

---

## Validation

-   **Success**: The CLI executor (`pkg/executor/cli`) and the `DefaultAgent` communicate effectively using this pattern without deadlocks or race conditions.
-   **Testability**: Unit and integration tests for the agent are able to drive it and assert on its behavior entirely through the channel interface.
-   **Performance**: The asynchronous nature allows the UI (even a simple CLI) to remain responsive while the agent is processing a turn.

---

## Related Decisions

-   [ADR-0004](0004-agent-content-processing.md): The event-driven nature of the channel-based communication is what allows the rich `AgentEvent` stream to be processed.

---

## References

-   [Go Concurrency Patterns: Channels](https://go.dev/blog/pipelines)
-   [`pkg/types/channels.go`](../../pkg/types/channels.go) - The `AgentChannels` struct definition.
-   [`pkg/agent/default.go`](../../pkg/agent/default.go) - The agent-side implementation of the event loop.
-   [`pkg/executor/cli/executor.go`](../../pkg/executor/cli/executor.go) - The executor-side implementation of the interaction loop.

**Last Updated:** 2025-11-02