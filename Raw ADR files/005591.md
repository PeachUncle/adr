# ADR-001: Monorepo Architecture

## Status

Accepted

## Date

2024-01-15

## Context

The AI-BOS ERP platform requires a complex architecture with multiple applications and shared packages. We need to decide on the best approach for managing this codebase while ensuring:

- Efficient development workflow
- Code sharing between applications
- Consistent build and deployment processes
- Team collaboration and code organization
- Scalability for future growth

## Decision

Use **Turborepo with pnpm workspaces** for monorepo management.

### Key Components

1. **Turborepo**: High-performance build system with intelligent caching
2. **pnpm workspaces**: Fast, disk space efficient package manager
3. **TypeScript**: Type-safe development across all packages
4. **Shared packages**: Common UI components, utilities, and contracts

### Architecture Structure

```
aibos-erp/
├── apps/
│   ├── bff/          # Backend for Frontend (NestJS)
│   └── web/          # Next.js Web Application
├── packages/
│   ├── ui/           # UI Component Library
│   ├── contracts/    # Shared TypeScript Types
│   └── utils/        # Shared Utility Functions
├── scripts/          # Development & Deployment Scripts
├── turbo.json        # Turborepo configuration
├── pnpm-workspace.yaml # pnpm workspace configuration
└── package.json      # Root package configuration
```

## Consequences

### Positive

- **Performance**: Turborepo provides 97.7% build time improvement through intelligent caching
- **Efficiency**: pnpm reduces disk usage by 50% compared to npm/yarn
- **Code Sharing**: Easy sharing of components, utilities, and types across applications
- **Consistency**: Unified build, test, and deployment processes
- **Developer Experience**: Single repository for all related code
- **Dependency Management**: Centralized dependency management with workspace protocols
- **Type Safety**: Shared TypeScript types ensure consistency across applications
- **Scalability**: Easy to add new applications and packages

### Negative

- **Complexity**: Initial setup complexity compared to simple repositories
- **Learning Curve**: Team needs to understand monorepo concepts and tools
- **Build Dependencies**: Changes in shared packages can affect multiple applications
- **Repository Size**: Single repository grows larger over time
- **Tooling**: Requires specific tooling (Turborepo, pnpm) that team must learn

## Alternatives Considered

### 1. Multi-Repository Approach

- **Pros**: Simpler individual repositories, independent deployments
- **Cons**: Code duplication, complex dependency management, difficult cross-repository changes

### 2. Lerna + npm/yarn

- **Pros**: Mature tooling, wide adoption
- **Cons**: Slower builds, less efficient caching, higher disk usage

### 3. Nx Monorepo

- **Pros**: Comprehensive tooling, good caching
- **Cons**: Steeper learning curve, more complex configuration

## Implementation Details

### Turborepo Configuration (`turbo.json`)

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    }
  }
}
```

### pnpm Workspace Configuration (`pnpm-workspace.yaml`)

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### Package Dependencies

- **Workspace Protocol**: Use `workspace:^` for internal dependencies
- **Shared Dependencies**: Common dependencies hoisted to root
- **Version Management**: Centralized version management

## References

- [Turborepo Documentation](https://turbo.build/repo/docs)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Monorepo Best Practices](https://monorepo.tools/)
- [Turborepo Performance](https://turbo.build/repo/docs/core-concepts/monorepos/filtering)

## Related ADRs

- [ADR-002: Anti-Drift Guardrails](./002-anti-drift-guardrails.md)
- [ADR-003: Backend Architecture](./003-backend-architecture.md)
- [ADR-004: Frontend Architecture](./004-frontend-architecture.md)
