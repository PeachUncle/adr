# ADR-0001: Use Go for CLI and TUI

## Status

Accepted

Date: 2024-11-01

## Context

We need to build a command-line orchestration tool with a terminal user interface (TUI) that manages multiple background processes. The tool needs to:

- Provide a responsive, interactive TUI
- Manage process lifecycles reliably
- Parse configuration files
- Handle concurrent operations
- Be easily distributable as a single binary
- Work cross-platform (Linux, macOS)

Language options considered: Go, Python, Rust, Node.js

## Decision

We will use Go (1.21+) for implementing the CLI and TUI components of the Agent Stack Controller.

## Consequences

### Positive

- **Single binary distribution**: Go compiles to a single static binary with no runtime dependencies
- **Excellent concurrency**: Goroutines and channels make concurrent operations natural
- **Strong ecosystem**: Mature libraries for CLI (cobra), TUI (bubbletea), and configuration (viper)
- **Fast compilation**: Quick build times improve developer experience
- **Cross-compilation**: Easy to build for multiple platforms
- **Memory safety**: Garbage collection prevents memory leaks
- **Strong typing**: Catches errors at compile time
- **Good performance**: Fast enough for our use case without optimization

### Negative

- **Learning curve**: Team needs to learn Go if not familiar
- **Verbose error handling**: Explicit error checking can be repetitive
- **No generics** (in Go 1.21): Some code duplication for type-specific operations
- **Garbage collection pauses**: Could affect real-time responsiveness (unlikely to be an issue)

### Neutral

- **Different from agent code**: Agents are in Python, creating a polyglot codebase
- **Opinionated formatting**: gofmt enforces style (generally positive)

## Alternatives Considered

### Alternative 1: Python

**Description:** Use Python for the entire stack (CLI, TUI, and agents)

**Pros:**
- Single language for entire project
- Rich ecosystem for CLI tools
- Team likely already knows Python
- Easy to prototype quickly

**Cons:**
- Distribution requires Python runtime
- TUI libraries less mature (textual, urwid)
- Process management more complex
- Slower startup time
- Packaging complexity (pip, venv, etc.)

**Why not chosen:** Distribution complexity and less mature TUI ecosystem

### Alternative 2: Rust

**Description:** Use Rust for maximum performance and safety

**Pros:**
- Excellent performance
- Memory safety without GC
- Strong type system
- Growing ecosystem

**Cons:**
- Steep learning curve
- Longer compilation times
- Smaller ecosystem for TUI
- Overkill for our performance needs
- Slower development velocity

**Why not chosen:** Complexity outweighs benefits for this use case

### Alternative 3: Node.js

**Description:** Use Node.js with TypeScript

**Pros:**
- JavaScript/TypeScript widely known
- Good CLI libraries (commander, inquirer)
- Decent TUI options (blessed, ink)
- Fast development

**Cons:**
- Requires Node.js runtime
- Distribution complexity (npm, node_modules)
- Process management less robust
- Memory usage concerns
- Callback/async complexity

**Why not chosen:** Runtime dependency and distribution complexity

## Implementation Notes

- Use Go modules for dependency management
- Follow standard Go project layout
- Use cobra for CLI framework
- Use bubbletea for TUI framework
- Use viper for configuration parsing
- Target Go 1.21+ for latest features

## References

- [Cobra CLI Framework](https://github.com/spf13/cobra)
- [Bubbletea TUI Framework](https://github.com/charmbracelet/bubbletea)
- [Go Project Layout](https://github.com/golang-standards/project-layout)
- [Design Document](../../.kiro/specs/agent-stack-controller/design.md)

## Revision History

- 2024-11-01: Initial version
