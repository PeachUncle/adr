# ADR 011: Choosing Nx for Monorepo Management

- **Date created**: 05/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

During the early planning stages of the `box-tracker` project, it became clear that managing multiple services in separate repositories would introduce unnecessary complexity. One of the key challenges we identified early on was sharing environment variables across projects, particularly between the `backend` (`FastAPI`) and `webapp` (`Next.js`) packages.

Additionally, we needed:

- A way to enforce consistent tooling and dependency management across projects.
- A unified build and execution system that allowed services to interact seamlessly.
- Support for task orchestration, so that commands like running the backend, frontend, and database could be handled from a central location.

Recognizing these needs, we determined that a monorepo management tool was required.

## Alternatives

### Nx (Chosen)

- Designed for monorepos with built-in support for dependency management and task execution.
- Provides environment variable management across multiple services.
- Supports multiple languages, including `Python` and `JavaScript`, making it suitable for our stack.
- Offers caching and incremental builds, improving CI/CD performance.

### Turborepo

- Similar to `Nx` but primarily optimized for `JavaScript/TypeScript`.
- Lacks built-in support for `Python`, requiring additional configuration.
- Simpler setup but not as feature-rich for mixed-language monorepos.

### Custom Scripts

- Could provide basic monorepo functionality through shell scripts.
- Requires significant manual setup and maintenance.
- Lacks the structured dependency graph and task management provided by dedicated tools.

## Decision

After evaluating the options, we decided to use `Nx` for monorepo management.

This decision was based on:

- The need for a structured monorepo with shared dependencies and environment variables.
- `Nx` providing first-class support for task execution and service orchestration.
- The ability to manage both `Python` and `JavaScript` projects in the same repository.

## Consequences

- Improved maintainability by having a single repository for all services.
- Simplified deployment and CI/CD with `Nx`'s task orchestration.
- Learning curve associated with `Nx`, but long-term benefits outweigh the initial complexity.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
