# ADR 004: Migration from npm to pnpm

## Status

Accepted

## Context

The Zaddies Game project currently uses npm workspaces to manage the monorepo structure (frontend, backend, shared packages). While npm workspaces provide basic monorepo functionality, several forces are pushing us to reconsider this choice:

### Performance Issues

- **Installation Speed**: npm can be slow when installing dependencies, particularly in CI/CD pipelines where fresh installations occur frequently
- **Disk Space**: npm creates duplicate copies of dependencies across workspaces, leading to bloated `node_modules` directories
- **CI/CD Time**: Longer installation times directly increase GitHub Actions costs and slow down the development feedback loop

### Monorepo Management Challenges

- **Phantom Dependencies**: npm's hoisting behavior allows packages to access dependencies they don't explicitly declare, creating hidden coupling
- **Version Conflicts**: npm's flat dependency structure can make resolving version conflicts between workspaces difficult
- **Peer Dependency Handling**: npm's peer dependency resolution is less strict, potentially allowing incompatible versions to coexist

### Developer Experience

- **Inconsistent Installations**: Different developers may get slightly different dependency trees due to npm's non-deterministic resolution
- **Lockfile Merge Conflicts**: `package-lock.json` frequently causes merge conflicts in team development
- **Workspace Commands**: npm workspace commands can be verbose and less intuitive than alternatives

### Industry Trends

- Modern monorepo tools (Turborepo, Nx) recommend or integrate better with pnpm
- Major projects (Vue.js, Microsoft, Prism) have migrated to pnpm for performance and reliability
- pnpm's strict mode prevents phantom dependencies, improving code quality

### Project-Specific Constraints

- **Cost Consciousness** (Constitution Principle V): We aim to minimize hosting and CI/CD costs
- **Performance-First** (Constitution Principle III): Installation performance impacts developer productivity
- **Modular Architecture** (Constitution Principle II): We need proper dependency isolation between modules

## Decision

We will migrate from npm to pnpm as our package manager.

**Migration Strategy**:

1. Install pnpm globally on development machines and CI/CD runners
2. Create `pnpm-workspace.yaml` to define workspace structure
3. Remove `package-lock.json` and `node_modules` directories
4. Run `pnpm install` to generate `pnpm-lock.yaml`
5. Update all documentation referencing npm commands
6. Update GitHub Actions workflows to use pnpm
7. Configure `.npmrc` to enforce strict peer dependency resolution
8. Update `package.json` engine requirements to specify pnpm version

**Configuration Choices**:

- Use pnpm's strict mode to prevent phantom dependencies
- Enable `auto-install-peers=true` to simplify peer dependency management
- Set `shamefully-hoist=false` to maintain proper dependency isolation
- Configure node-linker to use pnpm's default symlink strategy

## Consequences

### Positive

- **Faster Installations**: pnpm is typically 2-3x faster than npm due to content-addressable storage
- **Reduced Disk Usage**: Shared dependency store means packages are stored once globally, not duplicated per workspace
- **Strict Dependency Isolation**: Prevents phantom dependencies, improving code quality and maintainability
- **Better Monorepo Support**: First-class workspace support with intuitive commands (`pnpm --filter`)
- **Faster CI/CD**: Reduced installation times lower GitHub Actions costs and improve developer feedback loops
- **Deterministic Installs**: More reliable lockfile format reduces "works on my machine" issues
- **Smaller Lockfile Conflicts**: `pnpm-lock.yaml` has better merge conflict resolution than `package-lock.json`

### Negative

- **Learning Curve**: Team members need to learn pnpm-specific commands and concepts
- **Tooling Compatibility**: Some tools may expect npm/yarn and require configuration updates
- **Global Installation Required**: Developers must install pnpm globally (`npm install -g pnpm`)
- **Migration Effort**: One-time cost to update documentation, scripts, and CI/CD pipelines
- **Debugging Changes**: Different node_modules structure may require adjusting debugging workflows
- **Editor Support**: Some IDE integrations may work better with npm than pnpm (though modern editors support both)

### Neutral

- **Different Commands**: Similar but slightly different CLI syntax (e.g., `pnpm add` vs `npm install`)
- **Symlink Strategy**: pnpm uses symlinks which may behave differently on Windows vs Unix systems
- **Lockfile Format**: YAML-based lockfile instead of JSON (arguably more readable)

## Implementation Notes

**Prerequisites**:

- Node.js 20 LTS (already required by project)
- pnpm 8.x or later

**Migration Checklist**:

- [ ] Update README.md with pnpm installation instructions
- [ ] Create `pnpm-workspace.yaml` configuration
- [ ] Update all `npm` commands in documentation to `pnpm`
- [ ] Update GitHub Actions workflows (`.github/workflows/*.yml`)
- [ ] Configure `.npmrc` with pnpm settings
- [ ] Update `package.json` engines field to specify pnpm version
- [ ] Update developer onboarding documentation
- [ ] Remove old `package-lock.json` and `node_modules`
- [ ] Test all workspace commands (`build`, `test`, `lint`, `format`)
- [ ] Verify Firebase Functions deployment works with pnpm

**Rollback Plan**:
If critical issues arise, rollback by:

1. Reinstall dependencies with `npm install`
2. Restore `package-lock.json` from git history
3. Update workflows back to npm
4. Document issues encountered for future consideration

## Compliance

- ✅ **Constitution V (Observability & Debuggability)**: Cost conscious - reduces CI/CD costs through faster installations
- ✅ **Constitution III (Performance-First)**: Improves installation performance significantly
- ✅ **Constitution II (Modular Architecture)**: Strict mode prevents phantom dependencies, ensuring proper module isolation
- ✅ **Constitution VIII (ADR Documentation)**: This decision is documented per ADR 004

## References

- [pnpm Documentation](https://pnpm.io/)
- [pnpm Benchmarks](https://pnpm.io/benchmarks)
- [Why pnpm?](https://pnpm.io/motivation)
- [npm vs pnpm vs Yarn](https://pnpm.io/feature-comparison)
