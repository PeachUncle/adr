# ADR-0002: Interactive Menu-Driven CLI Pattern

- **Status:** Accepted
- **Date:** 2026-01-01
- **Feature:** 001-cli-task-crud
- **Context:** Phase I requires a command-line interface for task management. We need to decide how users will interact with the application - whether through command-line arguments, an interactive session, or a combination. This decision affects user experience, implementation complexity, and future extensibility.

## Decision

We will implement an interactive menu-driven CLI using Python's built-in `input()` function:

**Interaction Pattern:**
- Single long-running session with persistent menu loop
- Numbered menu options (1-6) for all operations
- Contextual prompts for required input (task ID, title, description)
- Clear confirmation messages after each operation
- Graceful exit on user request or Ctrl+C

**Visual Design:**
- ASCII-based menu display (no ANSI colors for portability)
- `[ ]` and `[x]` markers for task status (works in any terminal)
- Summary counts in task list view
- Consistent error message format

**Input Handling:**
- Built-in `input()` for all user prompts
- Immediate validation with clear error messages
- Empty input handling (skip optional fields, reject required fields)

## Consequences

### Positive

- **Zero Dependencies**: No external CLI libraries required (Click, Typer, argparse)
- **Universal Terminal Support**: Works in any terminal without ANSI color requirements
- **Single Session Workflow**: User can perform multiple operations without re-launching
- **Beginner Friendly**: Menu-driven interface is intuitive and discoverable
- **Simple Implementation**: Built-in input() is straightforward to use and test

### Negative

- **No Scripting Support**: Cannot pipe commands or use in shell scripts
- **No Tab Completion**: Users must type full input manually
- **Sequential Only**: One operation at a time, no batch operations
- **Terminal Session Required**: Cannot run headless or in background

## Alternatives Considered

**Alternative A: argparse Command-Line Arguments**
- Example: `python main.py add --title "Buy groceries"`
- Pros: Scriptable, composable, standard Python library
- Rejected: Requires multiple program invocations; less interactive feel; more complex for simple CRUD

**Alternative B: Click/Typer Library**
- Rich CLI framework with decorators and auto-help
- Pros: Professional CLI UX, colored output, auto-completion
- Rejected: Adds external dependency; overkill for Phase I scope; constitution emphasizes simplicity

**Alternative C: Hybrid (argparse + interactive fallback)**
- Support both command-line args and interactive mode
- Rejected: Increases complexity; not needed for Phase I single-user scope

**Alternative D: ANSI-Colored Output**
- Use colors for task status (green=complete, red=pending)
- Rejected: Not universally supported; ASCII markers achieve the same goal portably

## References

- Feature Spec: [specs/001-cli-task-crud/spec.md](../../specs/001-cli-task-crud/spec.md)
- Implementation Plan: [specs/001-cli-task-crud/plan.md](../../specs/001-cli-task-crud/plan.md)
- CLI Commands Contract: [specs/001-cli-task-crud/contracts/cli-commands.md](../../specs/001-cli-task-crud/contracts/cli-commands.md)
- Related ADRs: [ADR-0001](./0001-in-memory-data-architecture-with-modular-project-structure.md)
- Research: [specs/001-cli-task-crud/research.md](../../specs/001-cli-task-crud/research.md)
