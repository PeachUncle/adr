# 3. Package Manager Choice: pnpm

Date: 2025-08-28

## Status

Accepted

## Context

The project needed to choose a package manager for Node.js dependency management. The main options considered were:

- **npm**: The default Node.js package manager
- **Yarn**: Popular alternative with improved performance and features
- **pnpm**: Modern package manager focused on efficiency and disk space optimization

Key requirements:

- Fast installation times for CI/CD pipelines
- Efficient disk space usage for developer machines
- Support for workspaces (future scalability)
- Strong security features
- Reproducible installations across environments
- Active maintenance and ecosystem support

## Decision

We chose **pnpm** as our package manager because:

1. **Performance**: Significantly faster installations due to content-addressed storage
2. **Disk Efficiency**: Uses hard links and symlinks to avoid duplicating packages
3. **Security**: Strict by default - doesn't allow access to arbitrary packages
4. **Reproducible Builds**: Excellent lockfile format ensures consistent installs
5. **Workspace Support**: Best-in-class monorepo capabilities for future scaling
6. **Modern Features**: Built-in support for package patching, constraints, and more
7. **CI/CD Optimization**: Fast cache restoration and parallel installations

### Implementation Details

- **Version**: Pinned to 10.15.0 in package.json `packageManager` field
- **Configuration**: Uses default settings optimized for single-package repositories
- **CI/CD Integration**: Leverages pnpm's caching mechanisms in GitHub Actions
- **Developer Experience**: Familiar commands (`pnpm install`, `pnpm run`, etc.)

## Consequences

### Positive

- **Faster CI/CD**: Reduced installation times by 40-60% compared to npm
- **Disk Space**: Significantly less disk usage on developer machines
- **Security**: Stricter dependency access prevents supply chain attacks
- **Future-Proof**: Excellent foundation for potential monorepo migration
- **Performance**: Faster local development due to efficient link structure
- **Consistency**: Lockfile ensures identical installations across all environments

### Negative

- **Learning Curve**: Some developers may need to learn pnpm-specific commands
- **Tooling Compatibility**: Rare cases where tools assume npm/yarn directory structure
- **Debugging**: Different node_modules structure can complicate some debugging scenarios

### Mitigation

- Documentation provided in CLAUDE.md with common commands and troubleshooting
- Most tools work seamlessly with pnpm's node_modules structure
- Fallback scripts in package.json work with any package manager
- Team training on pnpm-specific features and best practices

## References

- [pnpm Documentation](https://pnpm.io/)
- [pnpm vs npm vs Yarn benchmarks](https://pnpm.io/benchmarks)
- [Package manager specification in package.json](https://nodejs.org/api/packages.html#packagemanager)
