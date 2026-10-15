# ADR-0001: Use Nx Monorepo

**Status:** Accepted  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-0

---

## Context

POC-0 requires a monorepo solution to manage multiple microfrontends (shell, remotes) and shared libraries. Requirements:
- Scalable monorepo management
- Build caching (only rebuild what changed)
- Task orchestration (parallel execution)
- Dependency graph visualization
- Code generation (scaffold new apps/libs)
- Affected projects (only test/build affected)
- Production-ready
- Excellent developer experience

**Note:** This is for MFE. For universal MFE (web + mobile), Yarn Workspaces was chosen due to Re.Pack compatibility issues with Nx (see `docs/nx-vs-yarn-workspaces-analysis.md`).

## Decision

Use Nx monorepo for MFE platform.

## Alternatives Considered

### Option 1: Yarn Workspaces

- **Pros:**
  - Simple, no additional tooling
  - Works with existing Yarn setup
  - Low learning curve
  - Proven for monorepos
- **Cons:**
  - No build caching
  - No task orchestration
  - No dependency graph visualization
  - No code generation
  - Manual affected project detection
- **Why Not:** Missing advanced features needed for scalable monorepo management. Better suited for simpler setups or when Nx is not compatible (e.g., React Native with Re.Pack).

### Option 2: pnpm Workspaces

- **Pros:**
  - Fast package installation
  - Disk space efficient
  - Works with Nx
  - Better dependency resolution
- **Cons:**
  - Still need Nx for build caching and task orchestration
  - Additional tooling complexity
- **Why Not:** pnpm is a package manager, not a monorepo tool. Can be used WITH Nx (and is recommended), but doesn't replace Nx's features.

### Option 3: Turborepo

- **Pros:**
  - Build caching
  - Task orchestration
  - Simpler than Nx
  - Good performance
- **Cons:**
  - Less features than Nx
  - Smaller ecosystem
  - Less code generation support
  - Less mature
- **Why Not:** Nx provides more comprehensive features (code generation, dependency graph, affected projects) that are valuable for enterprise-scale monorepos.

### Option 4: Nx (Chosen)

- **Pros:**
  - Comprehensive monorepo management
  - Build caching (only rebuild what changed)
  - Task orchestration (parallel execution)
  - Dependency graph visualization
  - Code generation (scaffold new apps/libs)
  - Affected projects (only test/build affected)
  - Production-ready
  - Excellent developer experience
  - Large ecosystem
  - Used by major companies
  - Active maintenance
- **Cons:**
  - Learning curve (moderate)
  - Additional tooling complexity
- **Why Chosen:** Best balance of features, maturity, and ecosystem. Provides all required features for scalable monorepo management.

## Trade-offs

- **Pros:**
  - Comprehensive monorepo features
  - Excellent developer experience
  - Production-ready
  - Scales to enterprise
- **Cons:**
  - Learning curve for team
  - Additional tooling complexity
- **Risks:**
  - Low risk - Nx is production-ready and widely used
  - Team needs to learn Nx concepts and commands

## Consequences

- **Positive:**
  - Faster builds (caching)
  - Better developer experience
  - Scalable to enterprise
  - Code generation speeds up development
  - Dependency graph helps understand architecture
- **Negative:**
  - Team needs to learn Nx
  - Additional configuration required
- **Neutral:**
  - Can migrate to other monorepo tools if needed (unlikely)

## Related Decisions

- `docs/mfe-poc0-architecture.md` - Section 3.1 Nx Workspace Structure
- `docs/mfe-poc0-tech-stack.md` - Nx details
- `docs/nx-vs-yarn-workspaces-analysis.md` - Analysis for universal MFE (different context)

---

**Last Updated:** 2026-01-XX

