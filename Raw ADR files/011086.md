# ADR 002 - Architecture

### Status: Accepted

### Josh Holbrook

## Context

In `Writing Interactive Compilers & Interpreters` (WIC&I), PJ Brown outlines a general architecture for a BASIC-like interpreter. The architecture overall has aged well, and will be implemented in Matanuska BASIC with a few adjustments.

## Decision

The following architecture will be implemented.

### Host

WIC&I refers to this as the I/O module. I'm borrowing a page from PowerShell and calling it the Host.

This is the one component which varies based on environment or frontend - that is, `Host` is an interface, and `ConsoleHost` is the implementation for the console specifically.

Host has a lot of responsibilities:

- Prompting/reading input
- Writing simple output and/or logging - this it shares with a PowerShell host
- File reading/writing and tracking file handles
- Process spawning, stdio redirection and tracking child processes/PIDs
- Ports - both serial and networking, as well as HTTP
- If applicable, drawing procedures - ie, wrapping [ink](https://github.com/vadimdemedes/ink), [ratatui](https://github.com/ratatui-org/ratatui) [crossterm](https://crates.io/crates/crossterm), etc.

This is a larger surface area than most objects. However, I feel the division of responsibility is clear.

### Translator

This component contains the main REPL loop and feeds parsed lines to other components. The basic loop is:

1. Read source code input from the prompt
2. Use the scanner and parser to generate the AST for a line
3. If prefixed by a line number, feed to the Editor
4. If _not_ prefixed by a line number, feed to the command module as an immediate command

The Translator may also non-interactively read directly from a file.

### Compiler

Lines in BASIC are initially parsed without knowing the context of the rest of the program. This means that a second pass is needed to:

1. Check that blocks are closed properly
2. Resolve GOTOs
3. Resolve variables (refer to `Crafting Interpreters` for what this entails)

There may be other needs - this list is non-exhaustive.

In WIC&I, there is a corresponding component called the pre-run module. This module doesn't generate a bytecode from an AST - rather, it fills in context fields in the `Program` set to `null` on the first pass.

### Editor

In BASIC, editing programs is accomplished through the shell. If a command is prefixed with a line number, it is inserted into a program loaded in an editor.

The editor's responsibility is to take `Line`s and insert, update or remove them from a `Program`, and return the full `Program` when it's time to either RUN or LIST the program. Its interface is similar to a dictionary.

### Recreator

BASIC typically doesn't retain the original source code in the editor - rather, it contains parsed and compiled bytecode. This is largely to save space. In order to LIST the program, the source code has to be recreated from that bytecode. WIC&I calls this recreating.

Note that a recreator combined with a parser is effectively a formatter.

### AST and Bytecode

In WIC&I, a `Program` is the core abstraction for storing what it calls the "internal language". In a traditional BASIC, this is stored in a "reverse Polish" format - similar to a modern bytecode - but without stripping non-operating information from the source, such as comments.

The rationale for using the "reverse Polish" format over a tree is that executing it is faster - it can be done with a linear scan and stack operations, rather than doing pointer lookups through a visitor pattern. However, if non-operating information is stripped from this format, then the source code can't be recreated.

In Matanuska BASIC, I will be implementing both an AST and a bytecode. The `Program` will be the top-level node in an AST, and the output of the first pass executed in the Translator. The bytecode will be generated from a `Program` by the compiler when RUN is executed.

This means that there are _two_ intermediate representations, not just one. It also means that the compiler has to do more. However, it means that the bytecode can strip non-operating information from the AST, as well as implement optimizations and use a simplified instruction set.

### Commander

The commander - called the "command module" in WIC&I - has a few cross-cutting responsibilities.

#### Sessions

The commander is in charge of initializing and closing sessions. This includes:

- Initializing the Editor and Program
- Initializing the Host
- Managing `readline` functionality, including loading history
- Running any `autoexec.bas` (a feature of MSX BASIC, analogous to `~/.bashrc`)
- Printing any startup messages
- Gracefully closing resources on exit

#### Executing Commands

Most BASIC implementations have a number of commands which aren't implemented through the runtime. These include editor commands, as well as `RUN`. In these cases, the commander is in charge of taking the AST input and executing it directly.

But in the case of a runtime command, the commander is still in charge of delegating to the runtime. This makes the commander the common entry point for all command execution, such that the translator always passes parsed input to the commander.

#### Interrupts & Errors

In the case of interrupts, the commander is in charge of ensuring that the runtime is paused smoothly, and that execution is handed back to the translator.

In the case of interrupts caused by _errors_, the commander is in charge of reporting and recovery. Generally, the translator should not be doing error handling.

### Runtime

This component is straightforwardly a bytecode VM.
