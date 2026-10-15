# ADR 0005: Use pnpm with Root-level node_modules for Monorepo

## Status
Accepted

## Date
2025-05-01

## Context
We are using a monorepo architecture with multiple microservices (written in Node.js and Rust). As the number of services grows, managing dependencies across services becomes challenging. We need a way to streamline dependency management and optimize disk space usage.

Using npm or Yarn would lead to duplicate `node_modules/` folders for each service, resulting in slower installs and wasted disk space.

## Decision
We will use **pnpm** as the package manager for the entire monorepo. pnpm will use a **single root-level `node_modules/`** and **workspaces** to manage dependencies for each service.

- All Node.js services will share the same `node_modules/` store.
- Services will be placed in the `services/` folder and use individual `package.json` files.
- pnpm will handle dependency resolution across the entire monorepo.

## Consequences
### Pros
- **Disk efficiency**: Dependencies are stored in a centralized location and symlinked into each service, avoiding duplication.
- **Faster installs**: pnpm's disk structure improves installation speed by using symlinks and caching.
- **Consistency**: pnpm ensures that all services use the same versions of shared dependencies.
- **Scalable**: As the number of services grows, pnpm’s efficient dependency management helps maintain performance.

### Cons
- **Learning curve**: pnpm may require a bit of learning, especially for developers unfamiliar with it.
- **pnpm-specific tooling**: Switching from npm or Yarn means some tools (like CI/CD pipelines) may need minor adjustments for compatibility with pnpm.
  
## Alternatives Considered
- **Yarn Workspaces**: Similar to pnpm but has slower install times and less efficient disk usage due to duplicated dependencies.
- **npm Workspaces**: Built-in workspace support, but pnpm provides better performance and disk space management.
  
## Notes
- pnpm requires the use of a `pnpm-lock.yaml` file, ensuring reproducible installs.
- Docker Compose will be used for orchestrating services in local development and production.
