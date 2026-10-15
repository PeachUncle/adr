# ADR 0001: Use Nx Monorepo for Workspace Management

**Status**: Accepted

**Date**: 2025-11-08 (Documented retroactively)

**Deciders**: AI Agent (with user approval)

## Context

The playground workspace needed a structure to manage multiple Angular applications with shared tooling, dependencies, and potential future shared libraries.

### Options Considered

1. **Separate Repositories** - Individual repos for each app
2. **Nx Monorepo** - Single repository with Nx orchestration
3. **Manual Monorepo** - Single repository without Nx

## Decision

Use **Nx Monorepo (v22.0.2)** for workspace management.

## Rationale

### Chosen: Nx Monorepo

**Advantages**:
- ✅ **Build Caching**: Intelligent caching prevents rebuilding unchanged code
- ✅ **Affected Commands**: Only test/lint/build what changed
- ✅ **Code Sharing**: Easy to create shared libraries (e.g., `libs/tailwind-preset`)
- ✅ **Consistent Tooling**: Unified ESLint, Jest, Playwright configuration
- ✅ **Task Orchestration**: Parallel execution with dependency awareness
- ✅ **Angular Integration**: First-class Angular support with generators
- ✅ **Nx Cloud**: Optional CI optimization with task distribution
- ✅ **Scalability**: Can add more apps/libs without restructuring

**Disadvantages**:
- ⚠️ Learning curve for Nx-specific concepts
- ⚠️ Additional dependency (though minimal overhead)

### Rejected: Separate Repositories

**Why Rejected**:
- Code duplication for shared configurations
- Harder to maintain consistent tooling versions
- No shared libraries without npm publishing
- More complex CI/CD setup

### Rejected: Manual Monorepo

**Why Rejected**:
- No intelligent caching or affected detection
- Manual task orchestration
- Missing Nx generators for code scaffolding
- No visualization of project dependencies

## Consequences

### Positive

- **Fast Builds**: CI runs only affected tests/builds
- **Easy Sharing**: Created `libs/tailwind-preset` for shared design system
- **Nx Console**: IDE integration for generators and task running
- **Project Graph**: Visual understanding of dependencies (`npx nx graph`)

### Negative

- **Nx-Specific Commands**: Must use `npx nx` instead of `npm run`
- **Configuration**: Additional `nx.json` and `project.json` files to maintain

### Neutral

- **Nx Cloud Integration**: Available but optional (currently enabled for caching)

## Implementation

**Files Created**:
- `nx.json` - Workspace configuration with caching rules
- `apps/*/project.json` - Per-project target definitions
- `.github/workflows/ci.yml` - CI using `nx run-many` commands

**Current Structure**:
```
apps/
  family-calendar/
  family-calendar-e2e/
  reward-chart/
  reward-chart-e2e/
libs/
  tailwind-preset/
```

## Follow-up

- ✅ Successfully used for both apps
- ✅ Created first shared library (Tailwind preset)
- 🔮 Future: Consider Nx Cloud task distribution for larger CI pipelines
- 🔮 Future: Extract shared Supabase service into library

## References

- [Nx Documentation](https://nx.dev/)
- [Nx Angular Tutorial](https://nx.dev/getting-started/tutorials/angular-monorepo-tutorial)
- Repository: nmck91/playground
