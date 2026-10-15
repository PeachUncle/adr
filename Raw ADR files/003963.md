# Continuous Input

## Premise

In a CLI workflow, commands often produce intermediate results that subsequent commands need to build upon. For example, a user might run a command to filter data, then run another command to sort that filtered data, then a third command to format and display it. Rather than requiring users to re-enter context with each command or forcing commands to persist state externally, the system needs a way to maintain command execution context across multiple sequential inputs.

The system needs to:
- Preserve command execution context (workflow runs) across multiple user inputs
- Allow commands to produce reusable outcomes that persist for subsequent commands
- Enable commands to access outcomes from prior commands in the session
- Automatically clean up context when commands produce final (non-reusable) outcomes
- Support command chaining without explicit state management by command authors

## Problem

Managing stateful command sequences in a CLI presents several challenges:

1. **Context Continuity** - Users expect to build upon previous command results without re-entering parameters or re-running queries. The system needs to preserve command context between inputs while allowing commands to remain stateless.

2. **Automatic Cleanup** - The system must know when to create a new context versus reusing an existing one. Reusable outcomes should persist, while final outcomes should trigger cleanup.

3. **Property Propagation** - Subsequent commands need type-safe access to outcomes from previous commands. This requires converting outcomes to properties and passing them through the workflow.

4. **State Machine Complexity** - The workflow run state machine needs additional states to track reusable outcomes, requiring careful state transition management to avoid invalid states.

5. **Run Lifecycle** - Traditional command execution follows a create → run → finish → destroy lifecycle. Reusable commands need a create → run → pause → resume → run → finish lifecycle.

6. **Backward Compatibility** - Commands that don't produce reusable outcomes should continue working unchanged. The reusability mechanism must be opt-in.

## Solution

The Continuous Input concept extends the workflow run lifecycle to support command context persistence. When a command produces a reusable outcome, its workflow run remains active and is returned by subsequent `NextRun()` calls, allowing the next command to build upon the previous context.

### Architecture Overview

```
User Input #1 → CliWorkflow.NextRun() → New CliWorkflowRun
                                            ↓
                                    Execute Command A
                                            ↓
                                    Produces Reusable Outcome
                                            ↓
                                    State: ReachedReusableOutcome
                                            ↓
User Input #2 → CliWorkflow.NextRun() → Same CliWorkflowRun (reused!)
                                            ↓
                                    Execute Command B (with Command A's outcomes)
                                            ↓
                                    Produces Final Outcome
                                            ↓
                                    State: Finished
                                            ↓
User Input #3 → CliWorkflow.NextRun() → New CliWorkflowRun
```

### 1. Reusable vs Final Outcomes

Command outcomes are classified into two categories based on their `CliCommandOutcomeKind`:

**Reusable Outcomes** (`CliCommandOutcomeKind.Reusable`)
- Represent intermediate results meant to be consumed by subsequent commands
- Examples:
  - `CliCommandAggregatorOutcome<T>` - Contains filtered/aggregated data
  - `CliCommandListAggregatorOutcome<T>` - Contains collections of data
  - `CliCommandMessageOutcome` - Contains messages that can be appended to
- When returned, the workflow run transitions to `ReachedReusableOutcome` state
- The run remains active and is returned by the next `NextRun()` call

**Final Outcomes** (`CliCommandOutcomeKind.Final`)
- Represent completed operations with no further processing needed
- Examples:
  - `CliCommandTableOutcome` - Formatted table for display
  - `CliCommandNothingOutcome` - No output (invalid input, help text)
  - `CliCommandExceptionOutcome` - Error occurred
- When returned, the workflow run transitions to `ReachedFinalOutcome` then `Finished`
- The run is complete and a new run is created for the next input

### 2. Extended State Machine

The workflow run state machine includes additional states for reusability:

```csharp
public enum ClIWorkflowRunStateStatus
{
    NotInitialized,
    Running,
    InvalidAsk,
    ReachedReusableOutcome,  // NEW: Command produced reusable output
    ReachedFinalOutcome,     // NEW: Command produced final output
    Exceptional,
    Finished
}
```

**Valid State Transitions**:
```
NotInitialized
    ↓
Running → ReachedReusableOutcome → Running → ReachedFinalOutcome → Finished
       ↓                        ↓
       ↓→ ReachedFinalOutcome → Finished
       ↓
       ↓→ InvalidAsk → Finished
       ↓
       ↓→ Exceptional → Finished
```

**Key Design Decision**: `ReachedReusableOutcome` can transition back to `Running`, creating a loop. This is the only state that doesn't immediately progress to `Finished`, enabling run reuse.

### 3. CliWorkflow.NextRun() - Run Reuse Logic

The workflow's `NextRun()` method implements run reuse:

```csharp
public CliWorkflowRun NextRun()
{
    var lastRunToAchieveReusableOutcome = Runs.LastOrDefault(run =>
        run.State.WasChangedTo(ClIWorkflowRunStateStatus.ReachedReusableOutcome));

    return lastRunToAchieveReusableOutcome ?? CreateNewRun();
}
```

**Execution Logic**:
1. Search backwards through all runs for one in `ReachedReusableOutcome` state
2. If found, return that run (it will be reused)
3. If not found, create and return a new run

**Key Design Decision**: Only the *last* run that achieved reusable outcome is reused. Earlier runs are abandoned. This prevents memory leaks and ensures users are always building on their most recent context.

### 4. CliWorkflowRun - Outcome Processing

The workflow run determines whether an outcome is reusable:

```csharp
private void UpdateStateAfterOutcome(CliCommandOutcome[] outcomes)
{
    var reusableOutcome = outcomes.LastOrDefault(x => x.IsReusable);
    
    var nextState = reusableOutcome != null
        ? ClIWorkflowRunStateStatus.ReachedReusableOutcome
        : ClIWorkflowRunStateStatus.ReachedFinalOutcome;

    State.ChangeTo(nextState, outcomes);
}

private void UpdateStateWhenFinished()
{
    if (!State.WasChangedTo(ClIWorkflowRunStateStatus.ReachedReusableOutcome))
    {
        State.ChangeTo(ClIWorkflowRunStateStatus.Finished);
    }
}
```

**Key Design Decision**: If *any* outcome in the array is reusable, the run is kept alive. This allows commands to return multiple outcomes where some are reusable and some are informational.

**Lifecycle Flow**:
1. Command executes and returns outcome array
2. `UpdateStateAfterOutcome()` checks for reusable outcomes
3. If reusable: State → `ReachedReusableOutcome`, run remains active
4. If final: State → `ReachedFinalOutcome` → `Finished`, run completes
5. `UpdateStateWhenFinished()` ensures final state is set unless outcome was reusable

### 5. Prior Outcome Propagation

Reused runs provide prior outcomes to subsequent commands:

```csharp
private CliCommand GetCommandFromInstruction(CliInstruction instruction)
{
    var priorOutcomes = State
        .AllOutcomeStateChanges()
        .SelectMany(outcomeChange => outcomeChange.Outcomes)
        .ToList();
    
    return _workflowCommandProvider.GetCommand(instruction, priorOutcomes);
}
```

**Key Design Decision**: All outcomes from all state changes in the run's history are passed to the command provider. This allows commands to access not just the immediate prior outcome, but the entire chain of outcomes in the current run.

The command provider converts these outcomes to typed properties (see ADR10 - Command Properties) that command generators can access:

```csharp
// Example: TableCommand generator accessing prior aggregator
public CliCommand Generate(CliInstruction instruction, List<CliCommandProperty> properties)
{
    var aggregatorProperty = properties
        .OfType<AggregatorCliCommandProperty<MyAggregate>>()
        .FirstOrDefault();
    
    if (aggregatorProperty != null)
    {
        // Use the aggregator from the previous command
        return new TableCommand(aggregatorProperty.Value);
    }
    
    // No prior aggregator, create default command
    return new TableCommand();
}
```

### 6. Example: Multi-Step Data Pipeline

Consider a user building a report through multiple commands:

**Step 1: Filter Data**
```
User: /transactions --category Food
Command: Executes query, returns CliCommandAggregatorOutcome<Transaction>
State: ReachedReusableOutcome
Run: Remains active with transactions in memory
```

**Step 2: Sort Results**
```
User: /sort --by Date
Command: Receives transactions from prior outcome, sorts them
         Returns new CliCommandAggregatorOutcome<Transaction>
State: ReachedReusableOutcome → Running → ReachedReusableOutcome
Run: Same run, now contains both filter and sort outcomes
```

**Step 3: Display Table**
```
User: /table
Command: Receives sorted transactions, formats as table
         Returns CliCommandTableOutcome (final)
State: Running → ReachedFinalOutcome → Finished
Run: Completes, table displayed
```

**Step 4: New Query**
```
User: /transactions --category Rent
Command: No reusable run available, creates new run
State: Fresh execution context
Run: New run created, previous context abandoned
```

### 7. Reusable Outcome Types

The system provides several reusable outcome types:

**CliCommandAggregatorOutcome<TAggregate>**
```csharp
public class CliCommandAggregatorOutcome<TAggregate>(CliAggregator<TAggregate> aggregator)
    : CliCommandOutcome(CliCommandOutcomeKind.Reusable)
{
    public CliAggregator<TAggregate> Aggregator { get; } = aggregator;
}
```
- Carries typed aggregators (filtered data collections)
- Converted to `AggregatorCliCommandProperty<T>` for consumption
- Used for data transformation pipelines

**CliCommandListAggregatorOutcome<TAggregate>**
- Carries lists of aggregators
- Useful for operations producing multiple data sets
- Enables commands that work with aggregator collections

**CliCommandMessageOutcome**
```csharp
public class CliCommandMessageOutcome(string message)
    : CliCommandOutcome(CliCommandOutcomeKind.Reusable)
{
    public string Message { get; } = message;
}
```
- Carries string messages
- Converted to `MessageCliCommandProperty` for consumption
- Can be appended to or modified by subsequent commands

## Constraints

### Single Active Reusable Run

Only one reusable run is kept active at a time (the most recent). Earlier reusable runs are not garbage collected but are also not returned by `NextRun()`. This prevents:
- Memory leaks from accumulating runs
- Confusion about which context is active
- Complex run selection logic

However, it also means:
- Users cannot return to earlier contexts without re-running commands
- No "undo" or "branch" operations on run context
- Run history is linear, not tree-structured

### Reusable State Cannot Be Cancelled

Once a run reaches `ReachedReusableOutcome`, it can only be exited by:
1. Producing a final outcome (completes run)
2. Producing another reusable outcome (continues in reusable state)
3. Exception or invalid input (completes run)

There's no way to explicitly "cancel" or "clear" a reusable run. Users must complete the operation or start a new session.

### Outcomes Are Immutable After Creation

Outcomes stored in the run state cannot be modified. Subsequent commands receive copies of outcome data, not references. This ensures:
- Commands cannot corrupt prior context
- State transitions remain traceable
- Debugging is simpler

However, it also means:
- Large datasets are copied, consuming memory
- Commands cannot "update" prior outcomes, only replace them
- No in-place data transformations

### No Run Persistence

Reusable runs exist only in memory for the current session. When the CLI exits:
- All run context is lost
- Reusable outcomes are not saved
- Users cannot resume sessions

Adding persistence would require:
- Serialization of outcome types
- Session management infrastructure
- Coordination between process restarts

### Command Coupling via Property Types

Commands become coupled through shared property types. If Command A produces `AggregatorCliCommandProperty<Transaction>` and Command B consumes it, they're coupled through the `Transaction` type. Changes to `Transaction` impact both commands.

This is intentional for type safety but creates dependencies that must be managed carefully.

### State Transition Validation Overhead

Every state change is validated against the legal transition matrix. This adds overhead to command execution. For high-frequency commands, this validation cost is multiplied by the number of state changes per command.

The benefit (catching invalid state transitions) outweighs the cost in typical CLI scenarios, but high-performance applications might need optimization.

## Questions & Answers

### Why is this called "Continuous Input" instead of "Command Chaining" or "Pipeline"?

"Continuous Input" emphasizes that the *user* continues providing input and the *workflow run* continues across those inputs. Unlike traditional command chaining (e.g., Unix pipes), this is interactive—users see results after each step and decide the next command dynamically.

### What happens if a command returns both reusable and final outcomes?

The last reusable outcome in the array determines run reusability. If any outcome is reusable, the run is kept alive. This allows commands to return status messages (final) alongside reusable data.

### Can a reused run access outcomes from before it was reused?

Yes. `AllOutcomeStateChanges()` returns all state changes with outcomes for the run's entire history, including outcomes from before the first reuse. This enables commands to access the full context chain.

### How do commands know if they're being called in a reused run?

Commands inspect the properties passed to their generator. If properties exist, the command is being called with prior context. The generator can check for specific property types to determine available context.

### What prevents infinite reusable loops?

Nothing in the architecture prevents it—if every command returns reusable outcomes, the run never finishes. This is intentional. Users must eventually run a command that produces final output (like displaying a table) to complete the run.

### Can multiple runs be reusable simultaneously?

No. `NextRun()` returns only the most recent reusable run. Earlier runs in `ReachedReusableOutcome` state are abandoned. This keeps the mental model simple: you're always building on your most recent work.

### Why not automatically create new runs when users switch topics?

The workflow cannot automatically detect "topic switches" without semantic understanding of commands. Forcing users to explicitly complete runs (via final outcomes) gives them control over when context resets.

### How does this interact with the CLI lifecycle hooks in CliApp?

`OnRunCreated` is called when `NextRun()` is called, even if returning a reused run. This is intentional—the hook signals "this run will handle the next input," not "a new run was created." Implementations can check run state to detect reuse.

### Can reusable outcomes be modified by subsequent commands?

Outcomes themselves are immutable, but commands can return new reusable outcomes based on prior ones. For example, a sort command receives an aggregator, creates a new sorted aggregator, and returns it as a new reusable outcome.

### What's the performance impact of accumulating outcomes in a long-running reusable run?

Each additional state change adds outcomes to the run's history. Commands that iterate through all prior outcomes will slow down as the history grows. For long pipelines, consider periodically producing final outcomes to reset context.

### How do I force a new run if I want to abandon reusable context?

Run a command that produces a final outcome (e.g., `/table`, `/help`, `/exit`). The run will complete and `NextRun()` will create a new run for the next input.

### Can I have different types of reusable outcomes in the same run?

Yes. A run can accumulate multiple reusable outcome types. For example, filtering might produce an aggregator, then a note command might add a message. Both are available to subsequent commands.

### Why doesn't the state machine support branches or parallel contexts?

Simplicity. A linear state machine is easier to reason about, test, and debug. Branching would require:
- Context selection UI
- Run garbage collection heuristics
- Complex state visualization

For a CLI, linear context is sufficient. Power users can open multiple terminals for parallel workflows.

### How does this relate to ADR10 - Command Properties?

ADR10 describes how outcomes are converted to properties. This ADR describes when runs are reused and how outcomes are accumulated. They work together: reusable outcomes (this ADR) are converted to properties (ADR10) for command consumption.

### What happens if a reused run encounters an exception?

The run transitions to `Exceptional` then `Finished`, ending its reusability. The next `NextRun()` creates a new run. The exception doesn't preserve context—reusability is lost.

### Can I inspect which run is currently active?

Yes, through workflow hooks. `CliWorkflow.Runs` contains all runs, and checking for `ReachedReusableOutcome` state identifies the active reusable run. However, this is primarily for debugging and testing.
