# ADR-001: Keep CLI as Package

**Status**: Accepted  
**Date**: 2025-01-06  
**Deciders**: Outfitter monorepo maintainers

## Context

The `@outfitter/cli` currently resides in `packages/cli/` and provides the `outfitter` command for managing development configurations. As the monorepo evolves, we need to decide whether it should remain a package or move to an `apps/` directory.

This decision affects:

- How the CLI is versioned and published
- Whether it can be consumed as a library
- The overall monorepo structure pattern

## Decision

We will keep `@outfitter/cli` in the `packages/` directory for now, structured to support both CLI and potential programmatic usage.

The CLI will:

- Export its commands and API from the main entry point
- Have a separate CLI entry point for the executable
- Remain publishable to npm as a package
- Follow the same patterns as other packages

## Consequences

### Positive

- **Flexibility maintained**: Can be used programmatically if needed
- **Consistent patterns**: All npm packages live in `packages/`
- **Simple publishing**: Same process as other packages
- **Future options open**: Easy to migrate to `apps/` later if needed

### Negative

- **Slight complexity**: Must maintain both CLI and library interfaces
- **Unused exports**: Programmatic API might not be used initially
- **Pattern questions**: Other CLIs might follow this pattern unnecessarily

## Alternatives Considered

### Alternative 1: Move to apps/

Create `apps/cli/` for pure CLI applications.

**Pros**:

- Clear separation of apps vs libraries
- Simpler package without library concerns

**Cons**:

- Breaks established pattern
- Requires migration effort
- Limits future programmatic usage

### Alternative 2: Hybrid Approach

Keep library code in `packages/cli-core/` and CLI in `apps/cli/`.

**Pros**:

- Clear separation of concerns
- Each part focused on its role

**Cons**:

- Over-engineering for current needs
- Two packages to maintain
- Complex for a simple CLI

## Implementation

No changes required - this ADR documents the decision to maintain the current structure.

Future CLIs should evaluate their specific needs:

- Pure end-user tools → Consider `apps/`
- Potential library usage → Use `packages/`
- Complex tools → Consider splitting

## References

- [Original Proposal](/docs/proposals/cli-package-and-app.md)
- [Monorepo Standards](/packages/fieldguides/content/standards/monorepo-standards.md)
