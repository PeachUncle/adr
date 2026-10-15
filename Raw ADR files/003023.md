# ADR 001: Monorepo Structure

**Status**: Accepted  
**Date**: 2026-01-10  
**Deciders**: Architecture Team

## Context

MonoPod consists of multiple business domains (booking, e-commerce, inventory, CRM, etc.) plus shared platform services. We need to decide on the repository structure.

**Options**:

1. **Monorepo**: Single repository containing all modules
2. **Polyrepo**: Separate repository per module
3. **Hybrid**: Monorepo for platform, separate repos for modules

## Decision

**Use a monorepo structure** with modules organized under `/modules` directory.

## Consequences

### Positive

- **Atomic changes**: Single PR can update multiple modules (e.g., add event contract)
- **Simplified dependency management**: Shared libraries/tools across modules
- **Easier refactoring**: IDE support for cross-module refactoring
- **Consistent tooling**: Single CI/CD pipeline, linting, testing setup
- **Better discoverability**: All code in one place for developers

### Negative

- **Repository size**: Can become large over time
- **Build performance**: Need selective building (affected modules only)  
- **Access control**: Harder to restrict access to specific modules
- **Cognitive load**: Developers see all modules even if working on one

### Neutral

- **Requires tooling**: Need workspace managers (Nx, Turborepo, or custom scripts)
- **CI/CD complexity**: Must detect changed modules and run relevant tests

## Alternatives Considered

### Polyrepo

**Pros**:

- Independent versioning per module
- Smaller repositories
- Clear module boundaries

**Cons**:

- Cross-module changes require multiple PRs
- Dependency hell (versioning shared libs)
- Duplicated CI/CD config

**Why not chosen**: Complexity of coordinating changes across repositories outweighs benefits

### Hybrid

**Pros**:

- Platform services together, modules independent

**Cons**:

- Still requires polyrepo coordination for module-platform changes

**Why not chosen**: Doesn't solve cross-module coordination problem

## References

- [Monorepo.tools](https://monorepo.tools/)
- Google, Facebook, Microsoft all use monorepos
- [Minimum Compatibility Contract](../architecture/mcc-specification.md) (ensures consistency)

---

**Version**: 1.0
