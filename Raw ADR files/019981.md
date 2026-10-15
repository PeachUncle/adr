---
status: accepted
date: 2025-08-18
decision-makers: LLM Agent
consulted: Universal Development Guide, existing package requirements
informed: dev-config package consumers
---

# Select markdownlint-cli2 for markdown linting implementation

## Context and Problem Statement

The `@voder/dev-config` package currently has a stub implementation for markdown linting that requires concrete tool selection and implementation. Consumers need a working markdown linting solution with both CLI and programmatic access, strict enforcement capabilities, and flexible override mechanisms. The implementation must abstract tool-specific details while providing comprehensive linting for documentation quality.

## Decision Drivers

- **Active maintenance requirement**: Tool must be actively maintained with recent releases
- **JSON configuration preference**: Simple JSON config format for wide tooling support
- **Dual access patterns**: Both CLI commands and programmatic API access required
- **Strict enforcement with overrides**: Error-level enforcement with ability to customize rules
- **Tool abstraction**: Consumers should import configuration, not tool directly
- **Integration compatibility**: Must work well with ESLint, Prettier, and Vitest
- **Performance needs**: Fast execution suitable for CI/CD pipelines

## Considered Options

- markdownlint-cli2
- markdownlint (original CLI)
- remark-lint
- textlint

## Decision Outcome

Chosen option: "markdownlint-cli2", because it is the only option that meets all requirements: active maintenance with Microsoft backing, native JSON configuration support, robust CLI with programmatic API, flexible override mechanisms, and excellent performance for CI/CD pipelines.

### Consequences

- Good, because provides simple JSON configuration with wide editor support
- Good, because offers multiple override mechanisms for different consumer needs
- Good, because delivers fast linting performance suitable for CI/CD pipelines
- Good, because actively maintained tool reduces long-term maintenance burden
- Good, because abstraction layer protects consumers from tool-specific details
- Bad, because adds markdownlint-cli2 as package dependency
- Bad, because creates tool lock-in (mitigated by abstraction layer)
- Bad, because requires maintainers to understand markdownlint-cli2 specifics

### Confirmation

Implementation compliance will be confirmed through:

- Comprehensive test suite validating configuration and override mechanisms
- Integration tests verifying CLI commands and programmatic API access
- Consumer documentation validation with usage pattern examples
- Build process integration testing with existing toolchain (ESLint, Prettier, Vitest)

## Pros and Cons of the Options

### markdownlint-cli2

Active, modern markdown linter with comprehensive CLI and API support.

- Good, because actively maintained with regular releases and Microsoft backing
- Good, because native `.markdownlint.json` config files with simple, readable format
- Good, because provides both robust CLI tool and programmatic API access
- Good, because supports flexible override mechanisms (function parameters and config files)
- Good, because offers fine-grained rule control with ability to disable/modify individual rules
- Good, because delivers fast execution performance for CI/CD pipelines
- Good, because has comprehensive documentation and examples
- Good, because supports config composition and extension patterns
- Neutral, because requires learning tool-specific rule names and configuration
- Bad, because adds external dependency to package

### markdownlint (original CLI)

Original markdown linting CLI tool.

- Good, because established tool with proven track record
- Good, because basic JSON configuration support
- Neutral, because still maintained but less actively developed
- Bad, because limited TypeScript/JavaScript config support
- Bad, because older architecture with fewer configuration options
- Bad, because less flexible API compared to markdownlint-cli2
- Bad, because fewer advanced features for enterprise use

### remark-lint

Plugin-based markdown linting as part of the unified ecosystem.

- Good, because part of larger unified/remark ecosystem
- Good, because highly extensible through plugin architecture
- Good, because supports custom rule development
- Neutral, because requires understanding of unified/remark ecosystem
- Bad, because more complex setup requiring multiple plugins
- Bad, because steeper learning curve for configuration
- Bad, because more configuration overhead for basic use cases
- Bad, because overkill for straightforward markdown linting needs

### textlint

Extensible text linting framework supporting multiple formats.

- Good, because supports multiple text formats beyond markdown
- Good, because highly extensible plugin system
- Good, because active development and community
- Neutral, because broader scope than markdown-specific needs
- Bad, because plugin complexity for markdown-only requirements
- Bad, because overkill for markdown-specific linting
- Bad, because more complex configuration setup
- Bad, because additional learning overhead for markdown-focused use case

## More Information

**Implementation approach**: Create abstraction layer in `linters/markdown/index.ts` that exports `getConfig()` function with override support and `createCLICommand()` helper for consumer package.json scripts. Base configuration will enforce strict rules for documentation quality while allowing consumer customization through both function parameters and config file extension patterns.

**Rule configuration strategy**: Enable heading order enforcement, fenced code language specification, and no bare HTML. Disable line length limits since Prettier handles formatting. Strict enforcement for relative link prohibition in public documentation with configurable overrides for project-specific needs.

**Consumer integration**: Package exports will include markdown linting path. Consumers can import configuration programmatically or use CLI commands through npm scripts. Both `.markdownlint.json` config file extension and function parameter override patterns supported.
