# ADR-001: Monorepo Structure

**Status**: Accepted
**Date**: 2026-01-03

## Context

QuizzMe requires code sharing between multiple packages while maintaining strict layer boundaries:
- Web app (Next.js)
- Domain logic (Trait Engine, Profile State)
- Storage implementations (LocalStorage, Supabase)
- API contracts (shared types/DTOs)
- UI components
- Cosmic bridge (Node orchestration)

We need to:
- Share code between packages without duplication
- Enforce dependency direction (UI -> Domain, not reverse)
- Enable fast incremental builds
- Support both static export and server deployment

## Decision

Use **pnpm workspaces** with **Turborepo** for build orchestration.

### Package Structure

```
/apps/web                 # Next.js App Router
/packages/domain          # Trait Engine, Profile State, Registry
/packages/storage         # Store interface + implementations
/packages/api-contracts   # Shared types/DTOs (prevents cycles)
/packages/ui              # Reusable UI components
/packages/cosmic-bridge   # Node Bridge / orchestration
/services/cloud-engine    # Python microservice (optional)
```

### Why pnpm + Turborepo

1. **pnpm**: Efficient disk usage via content-addressable storage, strict dependency resolution
2. **Turborepo**: Caching, parallel execution, dependency-aware task scheduling

## Consequences

### Positive

- **Faster builds**: Turborepo caches unchanged packages
- **Clear dependencies**: Workspace protocol (`workspace:*`) makes inter-package deps explicit
- **Layer enforcement**: ESLint rules can restrict imports between packages
- **Atomic changes**: Single commit can update API contract + all consumers

### Negative

- **Initial complexity**: More config files (turbo.json, per-package package.json)
- **Learning curve**: Team must understand workspace protocols
- **CI overhead**: Need to configure proper caching in CI

### Neutral

- Package boundaries force explicit API design upfront

## References

- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Turborepo Documentation](https://turbo.build/repo/docs)
