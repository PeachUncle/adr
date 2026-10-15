# ADR 006 - Runtime Exit

### Status: Accepted

### Josh Holbrook

## Context

Matanuska supports an `exit` command, which exits the interpreter.

Currently, Matanuska's architecture supports exiting in the CLI through an exit handler configured in the `Cli` class, and a special exception called `Exit`. Currently, the `Exit` exception only supports successful exits.

While implementing the `exit` command in Matanuska, I first opted to emit an event on `Runtime` (which would now be an `EventEmitter`), listened to that event in the `Commander`, and implemented a `Host#exit` method to actually call `process.exit`.

These two mechanisms are redundant and inconsistent. We would like to find one mechanism for exiting the application in a non-error context.

### Why an Error? Why in Cli?

Exiting has to be implemented in `Cli` because it contains the top-level error handling code. This is where we decide how to report on various Errors which may be thrown by other parts of the application, and how to exit.

The motivation for the exit handler override is entirely testing. When testing the `Cli` abstraction, I want it to "exit" without actually ending the process. In the relevant tests, I override the exit handler that asserts the expected exit code and throws a test-only Error to stop execution and signal the exit.

The motivation for an `Exit` Error type is that it allows for error handling to implement graceful shutdown - that is, error handling in the rest of the application can call its "finally" blocks to cleanly spin down resources before an exit. It's also inspired by [click](https://click.palletsprojects.com/en/8.1.x/)'s API - the actual needs were unknown, but given I was implementing a CLI framework, following click's lead seemed reasonable.

A behavior to keep in mind is that the `Exit` error type's message is written to output. This is so that `Exit` can be used to share help text (and similar use cases) when doing options parsing in the `Config` class.

### Why Host#exit?

As Matanuska has evolved, it's become clear that the `Host` abstraction owns much more than just logging - in fact, it owns all "os-level" actions. This includes things like getting the current UNIX user and the current working directory. Through this lens, it's appropriate for it to handle exits as well.

This also offers a clear, consistent mechanism for overriding exit behavior - that is, overriding the Host. The `Cli` class already supports a custom `Host`, and the tests include a `MockConsoleHost` used for these purposes. It would be natural to extend `MockConsoleHost` to implement a test-only behavior for exits as well.

### Why an EventEmitter?

The event emitter interface is largely motivated by an interest in delegating exit behavior to the `Commander`.

Given you _are_ going to delegate to the `Commander`, the alternative to an event is injecting it as a dependency to the `Runtime`. Events allow the runtime to be unaware of the commander, at the cost of the commander being unable to "yield" data back to the runtime.

Unfortunately, there are already reasons to inject the commander into the runtime. In particular, the commander handles prompting, because it handles the `readline` interface. This decision was made because readline requires asynchronous initialization, and because it's higher level than what the host provides. That decision isn't set in stone, but it _is_ really convenient.

While it hasn't been implemented yet, the runtime will need to request input from the commander _eventually_ - so we might as well inject it now and avoid two interfaces.

But we could also inject the host into the runtime, and have it call `Host#exit` directly. In fact, the host is already injected, just not used.

The alternative to this is implementing proxy methods on the commander whenever the runtime needs to access anything from the host. But the host contains a _lot_ of functionality, and effectively adding all of the host's functionality to the commander muddies its interface.

## Decision

1. The `Host` will be injected into the `Runtime`, where its `exit` method will be called directly. This will follow a pattern which should become more common over time.
2. The `Runtime` will _not_ inherit from `EventEmitter`, instead preferring to call methods on an injected `Commander` instance. This will create one consistent way to call back to the `Commander` that supports "yielding".
3. `ConsoleHost#exit` will throw an `Exit` error. This will allow for graceful shutdown behavior, while using the host as the common path for exits within the interpreter. 4. The `Exit` error will be extended to take an exit code. This will allow for its use with intentional non-zero exits.
4. `Cli` will continue to handle actual exit behavior. This will include overriding the `exit` handler in tests.
5. `MockConsoleHost#exit` will throw a `MockExit` error, maintaining the current structure of the tests.

In other words, when the runtime handles an `OpCode.Exit`, the following will occur:

1. The runtime will call `Host#exit` with the exit code.
2. The host will throw an `Exit` error with the exit code.
3. The error will be caught and handled in the `Cli` class.

Note a subtlety in testing: both `Host#exit` and the CLI exit handler _should_ throw an error to stop execution. This is to ensure that they short-circuit execution in tests as they do in practice. The code has been factored to include a return after the relevant calls, which _should_ protect against that, but it's an easy footgun. This could be addressed through the typing system by returning `never` instead of `void`, but this is unimplemented in the interest of maximizing flexibility.

Therefore, both `MockConsoleHost#exit` and the test exit handler throw a `MockExit`. A consequence of this is that it's not possible to distinguish between a triggered exit and a "clean exit" - but the tests don't cover that distinction, instead simply asserting the exit code as 0.
