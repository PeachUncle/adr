# CLI Concept

## Premise

Cli is a terminal-based application that allows users to interact with their YNAB budget data through command-line instructions. Users need a consistent, interactive experience where they can enter commands, receive feedback, and continue working in a persistent session until they choose to exit.

The application needs to:
- Accept user input as text commands (extensible with sub-commands and multiple arguments)
- Parse and execute those commands
- Display results back to the user
- Maintain a continuous interaction loop
- Handle errors gracefully
- Allow the user to exit when desired

## Problem

Building a command-line interface presents several architectural challenges:

1. **Session Management** - The CLI needs to maintain state throughout a user's session while remaining responsive and allowing multiple commands to be executed sequentially.

2. **Input/Output Abstraction** - Direct coupling to Console I/O makes testing difficult and limits flexibility in how the CLI can be used (e.g., automated scripts, different terminals).

3. **Extensibility** - Different implementations of the CLI may need to customize behavior at various points in the command execution lifecycle without modifying core logic.

4. **Separation of Concerns** - The main CLI loop logic should be independent from specific command implementations and application-specific workflows.

5. **Lifecycle Hooks** - Implementations may need to perform actions at specific points (on startup, before command execution, etc.) without cluttering the core loop.

## Solution

The CLI Concept introduces an abstract base class `OriginalCli` that implements a standard command-line interface pattern with lifecycle hooks. This provides a reusable foundation for building terminal applications.

### Architecture Overview

The CLI is built on three core components:

1. **OriginalCli** - Abstract base class defining the CLI lifecycle
2. **CliWorkflow** - State machine managing command execution
3. **CliCommandOutcomeIo** - Abstraction for interaction with the Console program

### 1. The OriginalCli Base Class

`OriginalCli` is an abstract class that encapsulates the standard CLI loop pattern:

```csharp
public abstract class OriginalCli
{
    private readonly CliWorkflow _workflow;
    private readonly CliCommandOutcomeIo _io;

    protected OriginalCli(CliWorkflow workflow, CliCommandOutcomeIo io)
    {
        _workflow = workflow;
        _io = io;
    }
    
    public async Task Run()
    { 
        OnRun(_workflow, _io);
        
        while (_workflow.Status != CliWorkflowStatus.Stopped)
        {
            var cliWorkflowRun = _workflow.CreateRun();
            
            OnRunCreated(cliWorkflowRun, _io);
            
            var ask = _io.Ask();
            
            var cliWorkflowRunTask = cliWorkflowRun.RespondToAsk(ask);
            
            OnRunStarted(cliWorkflowRun, _io);

            var outcome = await cliWorkflowRunTask;
            
            _io.Say(outcome);
        }
    }

    protected virtual void OnRun(CliWorkflow workflow, CliIo io) { }
    protected virtual void OnRunCreated(CliWorkflowRun workflowRun, CliIo io) { }
    protected virtual void OnRunStarted(CliWorkflowRun workflowRun, CliIo io) { }
}
```

**Key Design Decision**: The class is abstract with virtual lifecycle hooks rather than a sealed implementation. This allows derived classes to inject custom behavior without modifying the core loop logic.

### 2. The Main Loop

The `Run()` method implements a standard REPL (Read-Eval-Print-Loop) pattern:

1. **OnRun Hook** - Called once at startup before entering the loop
2. **Loop Condition** - Continues while workflow status is not `Stopped`
3. **Create Run** - Creates a new workflow run for each command
4. **OnRunCreated Hook** - Called after run creation but before user input
5. **Ask** - Prompts user for input via the I/O abstraction
6. **Respond** - Starts asynchronous command processing
7. **OnRunStarted Hook** - Called after command processing begins
8. **Await** - Waits for command completion
9. **Say** - Displays the result to the user

**Key Design Decision**: Command processing is started before `OnRunStarted` is called, allowing the hook to execute while the command runs asynchronously. This enables implementations to show progress indicators or perform concurrent operations.

### 3. I/O Abstraction

The `CliCommandOutcomeIo` abstraction provides two methods:
- `Ask()` - Retrieves input from the user (returns `string?`)
- `Say(CliCommandOutcome)` - Displays output to the user

**Key Design Decision**: Using an abstraction instead of direct `Console.ReadLine()` and `Console.WriteLine()` calls enables:
- Unit testing without requiring actual console I/O
- Alternative I/O implementations (file-based, network-based, etc.)
- Mocking and stubbing in tests
- Consistent handling of null/empty input

### 4. Workflow Integration

The CLI delegates all command execution logic to a `CliWorkflow` instance (see ADR09). This separation ensures:
- The CLI focuses on user interaction loop
- The workflow focuses on command parsing and execution
- Each component has a single, well-defined responsibility

The workflow provides:
- Status management (`Started`/`Stopped`)
- Run creation and execution
- Command parsing and routing

### 5. Lifecycle Hooks

The three protected virtual methods allow derived classes to customize behavior:

- **OnRun(CliWorkflow, CliIo)** - Execute once at startup
  - Use case: Display welcome message, initialize resources, show help
  
- **OnRunCreated(CliWorkflowRun, CliIo)** - Execute before each command
  - Use case: Display prompt, log command start, reset state
  
- **OnRunStarted(CliWorkflowRun, CliIo)** - Execute after command starts
  - Use case: Show loading indicator, update UI, track execution time

**Key Design Decision**: Hooks are optional (empty default implementations) so derived classes only override what they need, following the principle of least surprise.

## Constraints

### Single-Threaded Loop
The main loop is synchronous and processes one command at a time. While individual commands execute asynchronously, the loop waits for each to complete before accepting new input. Concurrent command execution would require a more complex architecture.

### Workflow Coupling
The CLI is tightly coupled to the `CliWorkflow` abstraction. Changes to the workflow interface impact all CLI implementations. However, this coupling is intentional as they represent different layers of the same feature.

### I/O Abstraction Limitations
The I/O abstraction uses `CliCommandOutcome` for output, which must be converted to displayable text. Complex output formatting (colors, tables, progress bars) requires the `Say()` implementation to understand outcome types.

### No Built-in Command Discovery
The CLI doesn't provide any built-in command help or discovery mechanisms. Implementations must add commands like `/help` or `/list-commands` through the workflow's command provider.

### Exit Mechanism Dependency
The CLI only exits when `_workflow.Status` becomes `Stopped`. This requires a command (typically `/exit` or `/quit`) that calls `workflow.Stop()`. There's no built-in escape mechanism if a workflow never stops.

### Hook Execution Order
The hooks fire at specific points in the loop. Implementations cannot change this order or insert additional hooks without modifying the base class.

## Questions & Answers

### Why abstract base class instead of interface?

The base class provides the complete implementation of the main loop, which should be consistent across all CLI applications. An interface would force each implementation to duplicate this logic. The template method pattern (abstract class with virtual methods) is ideal for this use case.

### Why are hooks void instead of returning values?

Hooks are designed for side effects (display messages, log events) rather than affecting the flow. Returning values would suggest they can alter execution, which would make the main loop more complex and harder to reason about.

### Can a CLI implementation override the Run() method?

While technically possible (it's not sealed), this defeats the purpose of the base class. The Run() method is the core contract that all CLI implementations should follow. Override the hooks instead.

### How do you stop the CLI?

A command must call `workflow.Stop()` which sets the workflow status to `Stopped`, causing the loop to exit. Typically this is done through a `/exit` or `/quit` command.

### What happens if Ask() returns null or empty string?

The workflow's command processing should handle this gracefully. The `RespondToAsk()` method validates input and returns a `CliCommandNothingOutcome` for invalid input.

### Why pass workflow to OnRun hook?

This allows implementations to access workflow state or configuration at startup. For example, displaying available commands or checking workflow version.

### Can I add more hooks?

Not without modifying the base class. If you need additional extension points, consider:
- Using the existing hooks creatively
- Wrapping the I/O abstraction to intercept calls
- Extending the workflow instead of the CLI

### What about async hooks?

The current hooks are synchronous. Adding async support would complicate the loop logic. For async operations, consider doing them in the workflow's command handlers instead.

### How is this different from a command-line parser library?

This is not a parser—parsing is delegated to the `CliWorkflow` (which uses the Instruction Parser from ADR07). This is the outer shell that manages the interactive session and user interaction loop.

### Why have both a Run creation and Started hook?

`OnRunCreated` fires before user input, allowing UI preparation (like showing a prompt). `OnRunStarted` fires after command processing begins, allowing concurrent operations while the command runs (like showing a spinner).
