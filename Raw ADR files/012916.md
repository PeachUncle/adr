---
status: accepted
date: 2024-04-24
---

# Git Repository Structure

## Context and Problem Statement

Since OnionSeed will include many projects and packages,
a strategy for Git repository structure must be decided upon.

## Decision Drivers

- Ease of managing project dependencies
- Ease of publishing new releases
- Ease of versioning packages
- Ease of developing features and fixing bugs
- Ease of use for consumers

## Considered Options

- [Repository per package](#repository-per-package) (MongoDB, SqlServer, Serilog, NLog, etc.)
- [Repository per subset of packages](#repository-per-subset-of-packages) (Storage, Logging, etc.)
- [Single repository for all packages](#single-repository-for-all-packages) (monorepo)
  - [Wikipedia](https://en.wikipedia.org/wiki/Monorepo)
  - [Monorepo.tools](https://monorepo.tools/)
  - [What is a monorepo? (and should you use it?)](https://semaphoreci.com/blog/what-is-monorepo)

## Decision Outcome

**Chosen option:**
[Single repository for all packages](#single-repository-for-all-packages) (monorepo),
because it eliminates the truly problematic issues around dependencies,
versioning, and repetition, while only sacrificing repo size and a slight
non-standard structure—which can both be mitigated easily enough.

## Pros and Cons of the Options

### Repository per package

- 🟢 **Good:** small repos
- 🟢 **Good:** independent versioning
- 🟢 **Good:** standard .NET project stucture
- 🔴 **Bad:** most context switching
- 🔴 **Bad:** difficult to manage dependencies
- 🔴 **Bad:** lots of work to keep up-to-date with each other
- 🔴 **Bad:** more difficult for consumers to manage versions
- 🔴 **Bad:** much repetition between repos (CI/CD, etc.)
- 🔴 **Bad:** allows circular dependencies

### Repository per subset of packages

- 🟢 **Good:** good balance between repo size and context switching
- 🟢 **Good:** standard .NET project stucture
- 🔴 **Bad:** still some difficulting in managing dependencies
- 🔴 **Bad:** still some difficulties in versioning
- 🔴 **Bad:** still some repetition between repos (CI/CD, etc.)
- 🔴 **Bad:** still allows some circular dependencies

### Single repository for all packages

- 🟢 **Good:** dependencies are simple to manage
- 🟢 **Good:** single version number across all packages
- 🟢 **Good:** easy for consumers to manage versions
- 🟢 **Good:** no repetition between repos (CI/CD, etc.)
- 🟢 **Good:** circular dependencies not possible
- 🔴 **Bad:** huge project
  - Can be mitigated by providing subset `.sln` files
- 🔴 **Bad:** non-standard .NET project structure
  - Can be mitigated by tooling
