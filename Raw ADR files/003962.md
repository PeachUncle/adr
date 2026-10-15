# CLI Workflow Concept

## Premise

A command-line interface needs a robust system to manage the execution of individual commands. Each time a user enters a command, the system must parse the input, find and execute the appropriate command handler, manage the command's lifecycle, handle errors, and track execution state.

The system needs to:
- Parse text input into structured command objects
- Route commands to their appropriate handlers
- Manage command execution state (running, finished, failed)
- Handle exceptions and invalid input gracefully
- Track command execution history
- Coordinate with the outer CLI loop for session management

## Problem

Managing command execution in a CLI presents several challenges:

1. **State Management** - Each command execution needs to track its own state (created, running, finished, exceptional) with proper state transitions.

2. **Command Routing** - The system needs to map parsed instructions to concrete command implementations without tight coupling.

3. **Separation of Concerns** - Session-level concerns (workflow) should be separate from command-level concerns (individual runs).

4. **Error Handling** - Different types of errors (invalid input, command not found, execution exceptions) need consistent handling.

5. **Asynchronous Execution** - Commands may perform I/O or long-running operations and should execute asynchronously without blocking the CLI.

6. **Dependency Injection** - Commands need access to services and dependencies without the workflow knowing implementation details.

7. **History Tracking** - The system should maintain a record of executed commands for debugging and auditing purposes.

## Solution

The CLI Workflow Concept implements a two-level state machine architecture:

1. **CliWorkflow** - Session-level state machine managing the overall CLI lifecycle
2. **CliWorkflowRun** - Command-level state machine managing individual command executions

This separation creates clear boundaries between session management and command execution.

### Architecture Overview

```
CliWorkflow (Session State Machine)
    ├── Status: Started | Stopped
    └── Creates → CliWorkflowRun (Command State Machine)
                      ├── State: NotInitialized → Created → Running → Finished
                      ├── Uses → CliInstructionParser
                      ├── Uses → CliWorkflowCommandProvider
                      └── Uses → IMediator
```

### 1. CliWorkflow - The Session State Machine

```csharp
public class CliWorkflow
{
    private readonly IServiceProvider _serviceProvider;
    private List<CliWorkflowRun> _runs = [];
    
    public CliWorkflowStatus Status = CliWorkflowStatus.Started;

    public CliWorkflow(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public CliWorkflowRun CreateRun()
    {
        var state = new CliWorkflowRunState();
        var instructionParser = _serviceProvider.GetRequiredService<CliInstructionParser>();
        var commandProvider = _serviceProvider.GetRequiredService<CliWorkflowCommandProvider>();
        var mediator = _serviceProvider.GetRequiredService<IMediator>();
        
        var run = new CliWorkflowRun(state, instructionParser, commandProvider, mediator);
        _runs.Add(run);
        return run;
    }

    public void Stop()
    {
        Status = CliWorkflowStatus.Stopped;
    }
}
```

**Key Design Decision**: The workflow acts as a factory for runs, resolving dependencies from the service provider. This keeps dependency management centralized while allowing runs to remain focused on execution.

**Responsibilities**:
- Maintain session status (Started/Stopped)
- Create new command runs with proper dependencies
- Store run history for potential debugging/auditing
- Control session lifecycle via `Stop()`

### 2. CliWorkflowStatus - Session States

```csharp
public enum CliWorkflowStatus
{
    Started,
    Stopped
}
```

**Key Design Decision**: Simple two-state enum rather than complex state machine. Sessions are either active or terminated. Additional states (Paused, Suspended) can be added if needed.

### 3. CliWorkflowRun - The Command State Machine

```csharp
public class CliWorkflowRun
{
    private readonly CliWorkflowRunState _state;
    private readonly CliInstructionParser _cliInstructionParser;
    private readonly CliWorkflowCommandProvider _workflowCommandProvider;
    private readonly IMediator _mediator;

    public async Task<CliCommandOutcome> RespondToAsk(string? ask)
    {
        _state.ChangeTo(ClIWorkflowRunStateType.Created);
        
        if (!IsValidAsk(ask))
        {
            _state.ChangeTo(ClIWorkflowRunStateType.InvalidAsk);
            return new CliCommandNothingOutcome();
        }

        try
        {
            _state.ChangeTo(ClIWorkflowRunStateType.Running);
            
            var instruction = _cliInstructionParser.Parse(ask!);
            var command = _workflowCommandProvider.GetCommand(instruction);
            return await _mediator.Send(command);
        }
        catch (ArgumentNullException)
        {
            _state.ChangeTo(ClIWorkflowRunStateType.InvalidAsk);
            return new CliCommandNothingOutcome();
        }
        catch (NoInstructionException)
        {
            _state.ChangeTo(ClIWorkflowRunStateType.InvalidAsk);
            return new CliCommandNothingOutcome();
        }
        catch (NoCommandGeneratorException)
        {
            _state.ChangeTo(ClIWorkflowRunStateType.InvalidAsk);
            return new CliCommandNothingOutcome();
        }
        catch (Exception exception)
        {
            _state.ChangeTo(ClIWorkflowRunStateType.Exceptional);
            return new CliCommandExceptionOutcome(exception);
        }
        finally
        {
            _state.ChangeTo(ClIWorkflowRunStateType.Finished);
        }
    }
}
```

**Key Design Decision**: The run encapsulates the entire command execution pipeline: validation, parsing, routing, and execution. Each step has explicit error handling with appropriate state transitions.

**Execution Flow**:
1. **Created** - Run is initialized
2. **Validate** - Check if input is valid (not null/empty)
3. **Running** - Input is being processed
4. **Parse** - Convert text to structured instruction
5. **Route** - Find command handler for instruction
6. **Execute** - Send command via MediatR to handler
7. **Handle Errors** - Catch and convert exceptions to outcomes
8. **Finished** - Mark run as complete (always executes via finally)

This kind of validation is an important step. For example, you could try to recall `.RespondToAsk()` in one of the life cyle hooks such as `OnRunCompletezd` and if the state is not valid for that operation, an exception would be thrown. This helps avoid having runs represent any more than one command execution.

### 4. ClIWorkflowRunStateType - Command Execution States

```csharp
public enum ClIWorkflowRunStateType
{
    NotInitialized,
    Created,
    Running,
    InvalidAsk,
    Exceptional,
    Finished,
}
```

**State Transitions**:
- `NotInitialized` → `Created` (run created)
- `Created` → `Running` (valid input, processing started)
- `Running` → `InvalidAsk` → `Finished` (invalid input detected)
- `Running` → `Exceptional` → `Finished` (exception thrown)
- `Running` → `Finished` (successful completion)

**Key Design Decision**: Separate states for different failure modes (`InvalidAsk` vs `Exceptional`) enable better error reporting and debugging.

### 5. CliWorkflowRunState - State Management

```csharp
public class CliWorkflowRunState
{
    private readonly Stopwatch _stopwatch = new Stopwatch();
    private readonly List<RecordedCliWorkflowRunStateChange> _recordedStateChanges = [];

    public void ChangeTo(ClIWorkflowRunStateType stateTypeToChangeTo)
    {
        var currentState = CanChangeTo(stateTypeToChangeTo);
        UpdateStopwatch(stateTypeToChangeTo);
        
        var stateChange = new RecordedCliWorkflowRunStateChange(
            _stopwatch.ElapsedTicks,
            currentState, 
            stateTypeToChangeTo);
        
        _recordedStateChanges.Add(stateChange);
    }

    private ClIWorkflowRunStateType CanChangeTo(ClIWorkflowRunStateType stateTypeToChangeTo)
    {
        // Validates state transition is legal, throws ImpossibleStateChangeException if not
    }
}
```

**Key Design Decision**: State changes are validated against a predefined set of legal transitions. Illegal transitions throw exceptions, preventing invalid state sequences.

**Features**:
- **State Validation** - Ensures only valid transitions occur
- **History Recording** - Tracks all state changes with timestamps
- **Timing** - Uses Stopwatch to measure execution time
- **Immutable History** - State changes are recorded, not modified

### 6. CliWorkflowCommandProvider - Command Routing

```csharp
public class CliWorkflowCommandProvider(IServiceProvider serviceProvider)
{
    public CliCommand GetCommand(CliInstruction instruction)
    {
        if (string.IsNullOrEmpty(instruction.Name))
        {
            throw new NoInstructionException("No instruction entered.");
        }
        
        var generator = serviceProvider.GetKeyedService<IGenericCommandGenerator>(instruction.Name);
        if (generator == null)
        {
            throw new NoCommandGeneratorException("Did not find generator for " + instruction.Name);
        }

        return generator.Generate(instruction);
    }
}
```

**Key Design Decision**: Uses keyed service registration to map instruction names to command generators. This provides loose coupling between the workflow and command implementations.

**Command Generation Pattern**:
1. Instruction name (e.g., "spare-money") acts as key
2. Service provider returns registered `IGenericCommandGenerator`
3. Generator creates `CliCommand` from instruction
4. Command is sent to MediatR for handling

This pattern enables:
- Dynamic command registration via DI
- Commands can be added without modifying workflow
- Commands can have their own dependencies injected
- Easy testing with mock generators

### 7. Integration with MediatR

The workflow uses MediatR to dispatch commands to handlers:

```csharp
var outcome = await _mediator.Send(command);
```

**Key Design Decision**: Using MediatR separates command routing from command handling. The workflow doesn't know about handler implementations, only that commands implement `IRequest<CliCommandOutcome>`.

**Benefits**:
- Handlers can be in separate assemblies
- Pipeline behaviors can be added (logging, validation, caching)
- Commands follow CQRS patterns
- Easy to test handlers in isolation

### 8. Outcome Pattern

All commands return `CliCommandOutcome` objects:
- `CliCommandNothingOutcome` - No output (invalid input)
- `CliCommandExceptionOutcome` - Error occurred
- `CliCommandTableOutcome` - Tabular data output
- `CliCommandOutputOutcome` - Text output
- Others as needed

**Key Design Decision**: Outcomes are value objects that encapsulate results. This allows the I/O layer to format output appropriately without commands needing to know about display logic.

## Constraints

### MediatR Dependency
The workflow is tightly coupled to MediatR. Changing to a different command dispatching mechanism would require significant refactoring. However, MediatR is a stable, well-tested library, so this risk is minimal.

### Synchronous State Transitions
State changes are synchronous and must complete before command execution continues. This is intentional for data integrity but could be a bottleneck if state recording becomes expensive.

### Single Command Execution
Each run executes exactly one command. There's no support for command chaining, pipes, or concurrent commands within a single run.

### Service Provider Coupling
The workflow depends on the service provider to resolve dependencies. This is pragmatic for a CLI application but makes testing more complex (need to mock/stub the service provider).

### State Transition Rigidity
Valid state transitions are hardcoded in `CliWorkflowRunState`. Adding new states requires updating the transition rules, which could break existing logic if not careful.

### Run History Memory
The workflow keeps all runs in memory (`_runs` list). For long-running sessions with many commands, this could consume significant memory. Currently not exposed or used beyond creation.

### No Cancellation Support
Commands cannot be cancelled once started. The workflow waits for completion or exception. Adding cancellation tokens would require threading them through the entire pipeline.

## Questions & Answers

### Why separate CliWorkflow and CliWorkflowRun?

This separation follows the Single Responsibility Principle. The workflow manages session lifecycle while runs manage command execution. This makes each component simpler to understand, test, and maintain.

### Why track runs in the workflow if they're not used?

The TODO comment suggests this is for future debugging/auditing features. It's a placeholder for potential features like command history, undo/redo, or execution analytics.

### What's the difference between InvalidAsk and Exceptional states?

`InvalidAsk` represents expected failures (empty input, unknown command) that don't indicate bugs. `Exceptional` represents unexpected failures (crashes, unhandled errors) that may indicate bugs. This distinction helps with debugging.

### Why use MediatR instead of direct handler invocation?

MediatR provides infrastructure for cross-cutting concerns (logging, validation, error handling) via pipeline behaviors. It also decouples the workflow from knowing about specific handlers.

### Can commands return custom outcome types?

Yes, as long as they inherit from `CliCommandOutcome`. The I/O layer needs to know how to display them, but the workflow treats all outcomes uniformly.

### Why validate state transitions?

State validation catches bugs where the code tries to perform illegal state changes (e.g., going from `Finished` back to `Running`). This makes the state machine more robust and easier to debug.

### How do you add new commands?

Register an `IGenericCommandGenerator` in the DI container with a key matching the instruction name. The workflow will automatically route instructions to your generator.

### What happens if a command takes a long time?

The run awaits the command's completion. The outer CLI loop can show progress via the `OnRunStarted` hook (see ADR08). For very long operations, consider implementing cancellation or progress reporting in the command itself.

### Can multiple workflows run simultaneously?

Each CLI instance has one workflow. For multiple simultaneous sessions, you'd need multiple CLI instances with separate workflows. Thread safety within a single workflow is not guaranteed.

### Why is the StopWatch logic in UpdateStopwatch backwards?

The stopwatch starts when transitioning to any state except `Running` and stops at `Finished`. This appears to be a bug or counterintuitive design. It likely needs review—expected behavior would be to start at `Running` and stop at `Finished`.

### How extensible is this for different CLI applications?

Very extensible. New commands just need generators and handlers. The core workflow logic remains unchanged. For significantly different workflows (e.g., batch processing, scripting), consider creating a new workflow implementation.
