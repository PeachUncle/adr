# ADR-011: Package Manager

## Status

Accepted

## Context

The project requires a reliable and efficient package manager for managing
dependencies. The chosen tool must ensure consistent and fast installs, good
performance, and support for modern development workflows.

## Decision

We decided to use Yarn as the package manager for the project.

## Reasons

1. **Performance**:
   Yarn offers faster dependency installation compared to npm due to its
   parallelized installation process, reducing wait times during development.

2. **Consistency with Lock Files**:
   Yarn’s lockfile (`yarn.lock`) ensures that dependency versions are consistent
   across different environments, minimizing “it works on my machine” issues.

3. **Workspaces Support**:
   Yarn natively supports workspaces, which is useful for managing monorepos or
   projects with multiple packages, providing better organization and dependency
   sharing.

4. **Deterministic Installs**:
   Yarn ensures deterministic installs by strictly adhering to the `yarn.lock`
   file, reducing unexpected dependency changes.

5. **Offline Mode**:
   Yarn’s offline mode allows packages to be installed from the local cache
   without requiring internet access, which can be beneficial in restricted
   environments.

6. **Compatibility**:
   Yarn is fully compatible with the npm registry, allowing seamless access to
   the vast ecosystem of JavaScript packages.

## Consequences

1. Developers must use Yarn-specific commands, which may differ slightly from
   npm, requiring minimal adjustments.

2. Dependency management processes will rely on the Yarn ecosystem, so any
   significant changes in Yarn’s future development could impact the project.

3. The `yarn.lock` file will need to be committed to version control and
   maintained to ensure consistent dependency versions.

## Alternatives Considered

### npm:

- **Pros**: Comes pre-installed with Node.js, requires no additional setup.
- **Cons**: Historically slower and less consistent than Yarn, though recent
  updates have improved performance.

### pnpm:

- **Pros**: Excellent performance and disk space optimization through a
  unique symlink-based approach.
- **Cons**: Smaller community and less adoption compared to Yarn and npm.
