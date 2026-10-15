# ADR-001: Monorepo Structure

**Status**: Accepted  
**Date**: 2024-11-15  
**Author**: Technical Lead  

## Context

TypeB needs to support multiple client applications (web, iOS, Android) while sharing business logic, types, and state management code. The team is small and needs to maintain consistency across platforms.

## Decision

We will use a monorepo structure with pnpm workspaces to manage all TypeB applications and shared packages in a single repository.

## Consequences

### Positive
- **Code sharing**: Business logic, types, and validators shared across all platforms
- **Atomic commits**: Changes affecting multiple packages can be committed together
- **Simplified dependency management**: Single lockfile, consistent versions
- **Better refactoring**: IDE can update references across all packages
- **Unified CI/CD**: Single pipeline for all applications

### Negative
- **Larger repository size**: All code in one place
- **Longer clone times**: New developers download everything
- **Build complexity**: Need to manage inter-package dependencies
- **Potential for broader impact**: Mistakes can affect multiple apps

### Neutral
- Learning curve for developers new to monorepos
- Need for clear package boundaries
- Requires build tooling setup (Turborepo)

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Separate repos | Independent deployments, smaller repos | Code duplication, sync issues, multiple PRs for features | Too much overhead for small team |
| Git submodules | Some code sharing, independent repos | Complex to manage, easy to break, poor DX | Too complex, error-prone |
| npm packages | Clear versioning, standard approach | Publishing overhead, version sync issues, slower iteration | Too slow for rapid development |

## Implementation

```
tybeb_b/
├── apps/
│   ├── web/        # Next.js web application
│   └── mobile/     # React Native app (to be moved from typeb-family-app/)
├── packages/
│   ├── core/       # Business logic and utilities
│   ├── store/      # Redux store configuration
│   └── types/      # TypeScript type definitions
├── docs/           # Documentation
└── pnpm-workspace.yaml
```

### Migration Plan
1. Keep current structure initially
2. Gradually move `typeb-family-app/` to `apps/mobile/`
3. Extract shared code to packages
4. Update build scripts and CI/CD

## References

- [pnpm Workspaces Documentation](https://pnpm.io/workspaces)
- [Turborepo Documentation](https://turbo.build/repo/docs)
- [Monorepo Best Practices](https://monorepo.tools/)
