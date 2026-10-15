---
status: accepted
date: 2025-08-14
decision-makers:
  - voder-dev-team
consulted:
  - platform-team
  - tooling-experts
informed:
  - contributors
  - consumer-packages
packages: '@voder/dev-config'
---

# ADR-0002: Require peer dependencies for consumer tools

## Context and Problem Statement

The `@voder/dev-config` package exports configuration presets for ESLint, Prettier, TypeScript, and Vitest that consumers import and use in their projects. All required tools (eslint, prettier, typescript, eslint plugins, etc.) are listed only as `devDependencies` in this package.

However, consumers need these tools installed in their own projects to actually use our configurations. For example:

- ESLint configurations require consumers to have `eslint` and specific plugins installed
- Prettier configurations require consumers to have `prettier` installed
- TypeScript configurations require consumers to have `typescript` installed

Without explicit `peerDependencies`, consumers get unclear error messages about missing modules, and there's a risk of version conflicts if multiple versions of the same tool are installed in the dependency tree.

## Decision Drivers

- **Clear consumer requirements**: Consumers should know exactly what tools they need to install
- **Version compatibility**: Prevent version conflicts and ensure compatible tool versions
- **Better error messages**: npm/pnpm should warn clearly about missing peer dependencies
- **Standard package pattern**: Configuration packages typically use peerDependencies for required tools
- **Avoid bundling**: Don't bundle development tools that consumers should control versions of
- **Policy compliance**: All packages are required to use Vitest with coverage requirements

## Considered Options

1. **Add peerDependencies for all consumer-required tools** (recommended)
2. **Keep everything in devDependencies only** (status quo)
3. **Move tools to regular dependencies** (bundles tools with package)

## Decision Outcome

Chosen option: "Add peerDependencies for all consumer-required tools", because it follows standard npm patterns for configuration packages, provides clear requirements to consumers, prevents version conflicts, and gives better error messages when tools are missing.

### Consequences

- **Good**: Clear consumer requirements with explicit version ranges
- **Good**: Prevents version conflicts between this package and consumer projects
- **Good**: Better error messages when consumers are missing required tools
- **Good**: Follows standard npm patterns for shareable configs
- **Good**: Consumers control their own tool versions within compatible ranges
- **Bad**: Consumers must explicitly install more dependencies
- **Bad**: Slightly more complex package.json structure

### Confirmation

- `package.json` includes `peerDependencies` section with all consumer-required tools
- `peerDependenciesMeta` marks optional tools (like vitest for non-testing configs)
- Documentation clearly explains what consumers need to install
- Consumer projects get clear warnings when peer dependencies are missing
- ESLint configs work when consumers have required plugins installed

## Pros and Cons of the Options

### Add peerDependencies for all consumer-required tools

This approach moves tools that consumers need from `devDependencies` to `peerDependencies`.

- **Good**: Follows npm standards for shareable configuration packages
- **Good**: Explicit version compatibility ranges prevent conflicts
- **Good**: Clear error messages when tools are missing
- **Good**: Consumers control their dependency versions
- **Good**: No duplicate installations of the same tools
- **Good**: Package managers warn about missing peer dependencies
- **Neutral**: Requires consumers to install dependencies explicitly
- **Bad**: More complex initial setup for consumers

### Keep everything in devDependencies only

Status quo approach where all tools are only in `devDependencies`.

- **Good**: Simple package.json structure
- **Good**: No additional requirements for consumers
- **Bad**: Unclear what consumers actually need to install
- **Bad**: Confusing error messages about missing modules
- **Bad**: Risk of version conflicts
- **Bad**: Doesn't follow npm patterns for configuration packages
- **Bad**: May bundle or require tools that consumers should control

### Move tools to regular dependencies

Bundle all tools as regular dependencies of this package.

- **Good**: Consumers don't need to install tools separately
- **Good**: Guaranteed compatible versions
- **Bad**: Violates principle that consumers should control their tool versions
- **Bad**: Increases package size unnecessarily
- **Bad**: May cause conflicts with consumer's preferred versions
- **Bad**: Development tools shouldn't be runtime dependencies

## Implementation Details

### Tools Moving to peerDependencies

**Core tools** (required for any usage):

- `eslint` - Required for ESLint configurations
- `prettier` - Required for Prettier configurations
- `typescript` - Required for TypeScript configurations

**ESLint ecosystem** (required for ESLint configs):

- `@typescript-eslint/eslint-plugin` - TypeScript linting rules
- `@typescript-eslint/parser` - TypeScript parser for ESLint
- `eslint-config-prettier` - Disables conflicting ESLint rules
- `eslint-import-resolver-typescript` - Resolves TypeScript imports
- `eslint-plugin-import` - Import/export linting
- `eslint-plugin-simple-import-sort` - Import sorting
- `eslint-plugin-unicorn` - Additional code quality rules

**Testing tools** (required by policy):

- `vitest` - Required for all packages (policy mandate)
- `@vitest/coverage-v8` - Required for coverage requirements (policy mandate)

### Tools Staying in devDependencies

**Development-only** (for developing this package):

- `@types/node` - Type definitions for development
- `jiti` - TypeScript config loading for development

Plus duplicate entries of peer dependencies needed for developing this package itself.

### Version Ranges

Use caret ranges (^) for peer dependencies to allow compatible updates:

- `eslint: "^9.0.0"` - ESLint v9 flat config support
- `prettier: "^3.0.0"` - Modern Prettier versions
- `typescript: "^5.0.0"` - Modern TypeScript with NodeNext support
- `vitest: "^3.2.0"` - Modern Vitest with Node.js testing support
- `@vitest/coverage-v8: "^3.2.0"` - Version-aligned with Vitest for coverage

## More Information

This decision complements ADR-0001 (Select development dependencies for @voder/dev-config) by clarifying the distinction between tools needed to develop this package (devDependencies) vs. tools that consumers need to use this package (peerDependencies).

Related documentation:

- Package exports in package.json define what consumers can import
- Consumer README should list all peer dependencies with installation instructions
- ESLint flat config examples should mention required peer dependencies
