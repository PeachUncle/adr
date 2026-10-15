# ADR-001: Monorepo Structure with Turborepo

## Status
Accepted

## Date
2024-01-15

## Context

NEURECTOMY consists of multiple interconnected components:
- Frontend application (React/TypeScript)
- Backend services (Rust, Python)
- Shared types and utilities
- Infrastructure configuration

We need a project structure that:
1. Enables code sharing between components
2. Provides efficient builds and caching
3. Maintains clear boundaries between modules
4. Supports independent deployment of services

## Decision

We will use a **monorepo structure** managed by **Turborepo** with **pnpm workspaces**.

### Structure
```
neurectomy/
├── apps/
│   └── spectrum-workspace/    # React frontend
├── services/
│   ├── rust-core/             # Rust backend
│   └── ml-service/            # Python ML service
├── packages/
│   └── types/                 # Shared TypeScript types
├── docker/                    # Docker configurations
├── docs/                      # Documentation
├── turbo.json                 # Turborepo configuration
├── pnpm-workspace.yaml        # pnpm workspace config
└── package.json               # Root package.json
```

### Key Choices
- **Turborepo**: Remote caching, parallel execution, intelligent scheduling
- **pnpm**: Fast, disk-efficient package manager with strict dependency resolution
- **Workspaces**: Each app/package is a separate workspace with its own dependencies

## Consequences

### Positive
- **Code Sharing**: Shared types package eliminates duplication
- **Atomic Changes**: Related changes across packages in single commits
- **Build Caching**: Turborepo caches build outputs, reducing CI time by 60%+
- **Dependency Management**: Single lockfile, consistent versions
- **Refactoring**: Easier to refactor across package boundaries

### Negative
- **Repository Size**: Larger clone size over time
- **Learning Curve**: Team must understand monorepo tooling
- **CI Complexity**: Need to configure per-package CI triggers
- **Build Times**: Initial builds take longer (mitigated by caching)

## Alternatives Considered

### 1. Polyrepo (Multiple Repositories)
- ❌ Complex dependency management between repos
- ❌ Difficult to make atomic cross-repo changes
- ❌ No shared build cache

### 2. Nx instead of Turborepo
- ✅ More features (generators, plugins)
- ❌ Heavier, more complex configuration
- ❌ Steeper learning curve

### 3. Lerna
- ❌ Less active development
- ❌ Slower than Turborepo
- ❌ Inferior caching capabilities

## References
- [Turborepo Documentation](https://turbo.build/repo/docs)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Monorepo.tools](https://monorepo.tools/)
