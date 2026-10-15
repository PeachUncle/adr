# ADR-003: Use Separate Repositories with Git Subtree for Shared Specifications and Language-Specific Implementations

## Status
Accepted

## Context

The BlueZone project follows the **"Ports and Adapters" architecture pattern**, which encourages clean separation between application core and external systems. This architectural style naturally supports **Set-Based Engineering (SBE)**—a product development approach that delays premature decisions by evaluating multiple competing options in parallel.

As discussed in the [publication on architectural flexibility](https://medium.com/@asher-sterkin/focus-on-core-value-and-keep-cloud-infrastructure-flexible-with-ports-adapters-af79c5fa1e56), this approach is especially useful in early-stage or evolving systems, where technology choices (e.g., programming language, infrastructure, deployment model) are uncertain or may need to change over time.

To operationalize this principle, the BlueZone project distinguishes between:

- **Language-neutral specifications and assets** (core domain intent),
- And **language-specific implementations** (technology realization of that intent).

## Decision

We will adopt a **split-repository model** structured as follows:

### 1. `bluezone-app` (shared core)

A centralized repository that contains **programming language-neutral specifications**, including:

- Use case documentation
- Acceptance tests specification
- Common UML diagrams
- Glossary and terminology definitions
- Architecture Decision Records (ADRs)

This repository reflects the stable **intent layer** of the system, independent of any specific technology stack.

### 2. `bluezone-app-<language>` (implementation-specific repos)

Each implementation lives in a separate repository named according to its target language or stack. Examples:

- `bluezone-app-py` – Python implementation
- `bluezone-app-ts` – TypeScript implementation

Each implementation:

- Includes the `bluezone-app` repo as a **Git subtree** mounted at `common/`
- Builds adapters, configuration, and tests specific to that language and platform
- Can evolve independently, compete, or be replaced without altering the shared intent

### 3. Git Subtree Strategy

Language-specific repositories incorporate the shared repo using [GitHub subtree](https://docs.github.com/en/get-started/using-git/about-git-subtree-merges).

This strategy:

- Allows seamless inclusion of shared specs without requiring nested Git metadata
- Enables stable integration across autonomous repositories
- Is preferable to submodules due to better toolchain and developer experience

## Benefits

- **Encourages multiple implementations** without prematurely committing to any single one
- **Supports language-agnostic and technology-neutral architecture**
- **Minimizes duplication** of core specifications
- **Improves flexibility** for client teams with different stacks or deployment models
- **Aligns with SBE** by treating core specifications as stable contracts, while allowing competing realizations

## Consequences

- Requires coordination to keep subtree references updated in implementation repos
- Introduces slight complexity in contributor workflows (e.g., subtree pull vs. regular pull)
- Tooling differences between languages must be addressed in their respective repos

## Out of Scope

- The precise mapping of use cases to driving ports or services is not addressed here and will be defined in separate ADRs.
- Naming conventions and packaging structure for ports and adapters are language-specific and deferred to future ADRs.

## References

- [Focus on Core Value and Keep Cloud Infrastructure Flexible (Sterkin, 2025)](https://medium.com/@asher-sterkin/focus-on-core-value-and-keep-cloud-infrastructure-flexible-with-ports-adapters-af79c5fa1e56)
- [Hexagonal Architecture (Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Git Subtree Documentation (GitHub)](https://docs.github.com/en/get-started/using-git/about-git-subtree-merges)
