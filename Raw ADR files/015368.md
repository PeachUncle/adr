# Scripting Language for Generic Tools and Scripts

* Status: accepted
* Deciders: Platform Team
* Date: 2025-12-05

## Context and Problem Statement

As the project grows, we need a consistent approach for writing generic tools, automation scripts, and CI orchestration. The codebase already has multiple scripting approaches in use: Node.js for CI orchestration, Bash for Docker/E2E operations, and Gradle for build tasks. With Nx adoption planned (per ADR 006), we need to standardize on a scripting language that integrates well with the Nx ecosystem while maintaining compatibility with our existing Gradle-based build.

The key question is: **What should be the primary language for writing generic tools and automation scripts that are not build tasks?**

## Decision Drivers

1. **Nx ecosystem compatibility** - ADR 006 establishes Nx as our monorepo tool; scripts should integrate naturally
2. **Developer familiarity** - Team members have varying expertise across languages
3. **Cross-platform support** - Scripts must work on macOS, Linux, and Windows CI runners
4. **Gradle minimization** - Gradle is powerful but slow to start; limit its use to true build tasks
5. **Dependency management** - Minimal runtime dependencies preferred for CI speed
6. **Ecosystem tooling** - Availability of libraries for common tasks (file ops, HTTP, YAML parsing)

## Considered Options

1. **Node.js (JavaScript/TypeScript)** - Continue and standardize current pattern (chosen)
2. **Bash** - Pure shell scripting for everything
3. **Python** - General-purpose scripting language
4. **Gradle-only** - Move all automation into Gradle tasks

## Decision Outcome

Chosen option: **Node.js (JavaScript/TypeScript)** as the primary and preferred language, with Bash for Docker/container orchestration. Gradle should only be used when the task cannot be reasonably accomplished with Node.js.

Node.js is the natural choice given our upcoming Nx adoption and existing investment. The `ci/` directory already contains a well-structured Node.js scripting infrastructure with ES modules, structured logging, and Gradle integration utilities. Node.js provides excellent cross-platform support, a rich ecosystem, and native integration with Nx. Bash is retained for Docker Compose orchestration where shell features are genuinely needed.

**Gradle is not a general-purpose scripting tool.** While Gradle excels at build tasks (compile, test, package), it should not be used for generic tooling or automation. Only use Gradle when the task is inherently build-related and cannot be reasonably accomplished with Node.js.

### Language Responsibilities

| Language | Use Cases |
|----------|-----------|
| **Node.js** (preferred) | CI orchestration, code generation, file manipulation, HTTP operations, Nx plugins, developer tooling, **default choice for any new script** |
| **Bash** | Docker Compose orchestration, container health checks, E2E test runners requiring shell features |
| **Gradle** (only when necessary) | Build tasks that require deep Gradle/JVM integration (e.g., compilation, dependency resolution, artifact publishing) - **only when Node.js cannot reasonably accomplish the task** |

### When Gradle is Acceptable

Gradle should only be used for tasks that meet **all** of these criteria:

1. The task is inherently build-related (compilation, testing, packaging, publishing)
2. The task requires deep integration with Gradle's dependency resolution or plugin ecosystem
3. Implementing in Node.js would require duplicating significant Gradle functionality

**Examples of acceptable Gradle use:**
- `./gradlew build` - compilation and unit tests
- `./gradlew bootJar` - creating Spring Boot JARs
- `./gradlew spotlessApply` - code formatting (Spotless plugin integration)
- Custom Gradle tasks in `buildSrc/` for build conventions

**Examples where Node.js should be used instead:**
- CI orchestration that calls `./gradlew` commands
- Code generation scripts
- File manipulation and scaffolding
- HTTP operations (API calls, health checks)
- Report aggregation and processing

### Positive Consequences

- Natural integration with Nx ecosystem and plugins
- Leverages existing `ci/` infrastructure (`ci/lib/gradle.js`, `ci/lib/logger.js`)
- Single runtime (Node.js 24.x) for most tooling
- TypeScript optional for type safety in complex tools
- pnpm workspace (per 020_NX_MONOREPO_IMPLEMENTATION.md) manages script dependencies

### Negative Consequences

- Requires Node.js runtime in CI environments (typically available)
- Some developers may prefer Python for certain tasks
- Bash scripts remain necessary for container orchestration (two languages to maintain)
- Gradle remains necessary for core build tasks, but this is a deliberate constraint not a workaround

## Pros and Cons of the Options

### 1. Node.js (JavaScript/TypeScript) (chosen)

**Good**
- Native Nx integration - Nx is built on Node.js; custom executors and generators use TypeScript
- Cross-platform - Works identically on macOS, Linux, Windows without shell compatibility issues
- Rich ecosystem - npm packages for HTTP, YAML, file operations, CLI building
- Existing investment - `ci/` scripts already use Node.js with established patterns
- Modern features - ES modules, async/await, structured error handling
- pnpm workspace integration - Dependencies managed alongside frontend packages

**Bad**
- Heavier than Bash for simple tasks
- Requires Node.js installation (though CI environments typically have it)
- Asynchronous patterns can be complex for simple sequential scripts

### 2. Bash

**Good**
- Zero dependencies on Unix systems
- Direct integration with Docker, git, and system commands
- Simple for linear command sequences

**Bad**
- Poor Windows support - requires WSL, Git Bash, or Cygwin
- Limited error handling - set -e is fragile
- No structured data types - YAML/JSON parsing requires external tools
- Complex string manipulation and logic
- No native HTTP client

### 3. Python

**Good**
- Excellent standard library for file operations and HTTP
- Good cross-platform support
- Readable syntax for non-programmers
- Strong YAML/JSON libraries

**Bad**
- Not aligned with Nx ecosystem (Node.js-based)
- Requires Python runtime and virtual environment management
- Version compatibility issues (2.x vs 3.x legacy)
- Additional dependency management system (pip) alongside npm/pnpm

### 4. Gradle-only

**Good**
- Single build tool for everything
- Kotlin DSL provides type safety
- Already configured in buildSrc

**Bad**
- Slow startup time for simple tasks
- Overkill for non-build operations
- Poor fit for code generation, HTTP operations, developer tools
- Creates build complexity mixing build and tooling concerns

## Implementation Notes and Next Steps

- **Default to Node.js** for any new script or tool - justify if using something else
- Continue using existing `ci/` Node.js infrastructure for CI orchestration
- New generic tools should be Node.js scripts in appropriate locations:
  - `ci/` for CI-specific scripts
  - `tools/` for developer utilities (migrate `tools/check-service-ports.sh` to Node.js)
  - `packages/tools/` or similar for Nx-integrated tooling (post Nx adoption)
- Retain Bash scripts in `ci/` for Docker Compose operations (`docker-up.sh`, `docker-down.sh`, E2E runners)
- Migrate embedded Python in `tools/check-service-ports.sh:1-50` to Node.js
- When Nx is implemented, use TypeScript for custom executors and generators
- Document Node.js version requirement (18+) in CLAUDE.md
- **Do not add new Gradle tasks** for non-build automation; use Node.js scripts that invoke `./gradlew` when build operations are needed

## References

- Current CI scripts: `ci/package.json`, `ci/verify.js`, `ci/lib/gradle.js`
- Bash Docker scripts: `ci/docker-up.sh`, `ci/docker-down.sh`
- Mixed-language tool: `tools/check-service-ports.sh` (Bash + embedded Python)
- Related ADR: `docs/ADRs/006_frontend_monorepo_strategy.md` (Nx decision)
- Nx implementation plan: `020_NX_MONOREPO_IMPLEMENTATION.md`
