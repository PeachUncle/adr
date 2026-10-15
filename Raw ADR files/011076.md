# Deno for Tooling, Node for Runtime Split

## Purpose
This document records the decision to use a dual-runtime architecture with Deno for all development tooling and Node.js for application runtime.

## Classification
- **Domain:** Architecture
- **Stability:** Static
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context

When building a TypeScript development environment for agentic coding, we needed to choose runtime environments for:
1. Development tools (AST analysis, database operations, CLI commands)
2. Application code (the actual TypeScript projects being analyzed)

Key factors influencing this decision:
- **Developer Experience**: Tools should be fast and easy to use
- **Security**: Development tools need access to file systems and databases
- **Ecosystem Compatibility**: Application code needs Node.js ecosystem
- **AI Agent Clarity**: LLM agents need clear boundaries about what goes where
- **Maintenance Burden**: Minimize complexity and context switching

### Decision

**We will use a dual-runtime architecture:**
- **Deno for all tooling scripts** (`scripts/` directory)
- **Node.js for application runtime** (`src/` directory and user code being analyzed)

This creates a clear boundary: if it's analyzing code, it runs in Deno. If it's the code being analyzed, it runs in Node.

### Status
Accepted (2025-09-28)

### Consequences

**Positive Consequences:**
- Clear separation of concerns reduces confusion for developers and AI agents
- Deno's built-in TypeScript support eliminates transpilation for tools
- Deno's security model protects against accidental file system damage
- Deno's modern import system (URL imports) works better for tool development
- Node.js ecosystem remains fully available for application code
- Fast tool startup times with Deno's performance characteristics

**Negative Consequences:**
- Requires maintaining two runtime environments
- Developers need to understand which runtime context they're in
- Cannot share code directly between Deno and Node contexts without careful design
- Need to manage two sets of dependencies (Deno imports vs npm packages)

**Risks Introduced:**
- Confusion if developers mix Deno and Node imports
- Tooling may need updates if Deno or Node introduce breaking changes
- AI agents might try to use Node patterns in Deno scripts or vice versa

**Trade-offs Made:**
- Increased complexity of dual runtimes vs. clarity of separation
- Learning curve for Deno vs. familiarity of Node-only approach

### Alternatives Considered

#### Alternative 1: Node.js Only
Use Node.js with ts-node for all code, both tools and applications.

**Pros:**
- Single runtime to learn and maintain
- Familiar to all TypeScript developers
- No confusion about which runtime to use
- Can share code freely between tools and app

**Cons:**
- Requires transpilation (ts-node) for all scripts
- Slower startup times for CLI tools
- No built-in security model
- Less modern TypeScript/ES module support
- AI agents may be less clear about boundaries

#### Alternative 2: Deno Only
Use Deno for everything, including application code analysis via Deno-compatible versions.

**Pros:**
- Single runtime to learn and maintain
- Modern TypeScript support everywhere
- Fast and secure throughout
- Consistent import patterns

**Cons:**
- Cannot analyze Node.js-specific projects properly
- Incompatible with npm ecosystem for apps
- Would require Deno-specific versions of many Node packages
- Limits the types of projects we can analyze

#### Alternative 3: Bun for Everything
Use Bun as a unified fast runtime for both tools and apps.

**Pros:**
- Single fast runtime
- Node.js compatibility
- Built-in TypeScript support
- Modern package management

**Cons:**
- Bun is less mature than Deno or Node
- Less stable API surface
- Smaller ecosystem and community
- May have compatibility issues with existing tooling

### Implementation Notes

**Directory Structure:**
```
scripts/          # All Deno scripts (--allow-all)
  commands/       # CLI commands
  lib/           # Reusable libraries
  utils/         # Utilities
src/             # Node.js application code
  index.ts       # Application entry points
tests/           # Node.js tests (Vitest)
bench/           # Deno benchmarks
```

**Import Patterns:**
- Deno scripts use: `import { x } from "https://..."` or `import { x } from "npm:..."`
- Node code uses: `import { x } from "package"` or `import { x } from "./file"`

**VS Code Configuration:**
- Deno LSP enabled for `scripts/` and `bench/` only
- Node TypeScript LSP for `src/` and `tests/`
- File associations help determine correct context

**Key Rules:**
1. NEVER mix Deno and Node import styles
2. Tools that analyze Node code do so via AST parsing, not execution
3. Database operations (Kuzu, DuckDB) happen in Deno scripts only
4. All CLI commands are Deno scripts in `scripts/commands/`

## Relationships
- **Parent Nodes:**
  - [foundation/project_definition.md] - implements - Fulfills project goals for clear tooling
  - [adr_001_devcontainer_architecture.md] - builds_on - DevContainer supports dual runtime
- **Child Nodes:**
  - [architecture/directory_structure.md] - implements - Physical layout implements this split
  - [architecture/tooling_architecture.md] - implements - Tool design follows this pattern
- **Related Nodes:**
  - [adr_003_no_python_policy.md] - complements - Both create clear boundaries
  - [cross_cutting/import_patterns.md] - implements - Import patterns enforce this split

## Navigation Guidance
- **Access Context:** Reference when unclear about which runtime to use for new code
- **Common Next Steps:** Review directory structure and import patterns
- **Related Tasks:** Creating new tools, setting up development environment, onboarding
- **Update Patterns:** Only revisit if Deno or Node fundamentally change

## Metadata
- **Decision Number:** ADR-002
- **Created:** 2025-09-30
- **Last Updated:** 2025-09-30
- **Updated By:** Claude (AI Agent)
- **Deciders:** Development team, based on implementation guide analysis

## Change History
- 2025-09-30: Initial creation based on implementation guide documentation