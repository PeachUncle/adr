---
status: accepted
date: 2025-08-14
decision-makers:
  - voder-dev-team
consulted:
  - platform-team
informed:
  - contributors
  - consumer-packages
packages: '@voder/dev-config'
---

# ADR-0004: Use TypeScript format for Prettier configuration

## Context and Problem Statement

The `@voder/dev-config` package needs to provide a Prettier configuration that consumers can import. The package is configured as an ES module (`"type": "module"` in package.json), requiring a decision on the file format for the Prettier configuration file.

Prettier supports multiple configuration file formats:

- `prettier.config.js` (JavaScript)
- `prettier.config.mjs` (ES Module)
- `prettier.config.cjs` (CommonJS)
- `prettier.config.ts` (TypeScript)
- `.prettierrc.json` (JSON)

The configuration needs to be:

1. Consistent with the package's ES module nature
2. Importable by both the package's own tooling and consumer packages
3. Readable by Prettier's CLI tools
4. Maintainable and type-safe where possible
5. Supported by current Node.js versions

## Decision Drivers

- **ES Module Consistency**: Package has `"type": "module"`, so configurations should use ES module format
- **Tool Compatibility**: Prettier CLI must be able to read the configuration
- **Import Requirements**: Package tests and exports need to import the config
- **Developer Experience**: Configuration should be easy to maintain and understand
- **Type Safety**: Prefer typed configurations where feasible

## Considered Options

1. **Use prettier.config.ts (TypeScript)** - **CHOSEN**
2. **Use prettier.config.mjs (ES Module)**
3. **Use prettier.config.cjs (CommonJS)**
4. **Use prettier.config.js (JavaScript)**

## Decision Outcome

Chosen option: "Use prettier.config.ts (TypeScript)", because modern Node.js versions (22.6.0+) now support TypeScript configuration files natively with the `--experimental-strip-types` flag, providing the best balance of type safety, ES module consistency, and maintainability.

### Consequences

- **Good**: Full TypeScript type checking and IntelliSense support
- **Good**: Consistent with package's `"type": "module"` declaration
- **Good**: Native ES module syntax (`export default`)
- **Good**: Compile-time validation of configuration options
- **Good**: Can be imported by package tests and build processes
- **Good**: Works with Prettier CLI using `NODE_OPTIONS="--experimental-strip-types"`
- **Good**: No additional TypeScript loaders required
- **Neutral**: Requires Node.js 22.6.0+ for native TypeScript support
- **Neutral**: Requires experimental flag until Node.js stabilizes TypeScript support

### Confirmation

- Configuration file uses `.ts` extension with `export default` syntax
- Package exports point to `./prettier.config.ts`
- Format and format:check scripts use `NODE_OPTIONS="--experimental-strip-types"`
- Package tests successfully import and validate the configuration
- Full verification pipeline passes (type-check, test, lint, format:check)
- TypeScript project includes prettier.config.ts for ESLint integration

## Pros and Cons of the Options

### Use prettier.config.ts (TypeScript)

TypeScript configuration provides the best type safety and developer experience with modern Node.js support.

- **Good**: Full TypeScript type checking and IntelliSense
- **Good**: Consistent with other TypeScript files in the package
- **Good**: Can import types from `prettier` package
- **Good**: Compile-time validation of configuration options
- **Good**: Native Node.js support with `--experimental-strip-types` (22.6.0+)
- **Good**: Works with Prettier CLI using `NODE_OPTIONS` flag
- **Good**: No complex loader configuration required
- **Neutral**: Requires experimental flag until Node.js stabilizes support
- **Neutral**: Requires Node.js 22.6.0+ for native support

### Use prettier.config.mjs (ES Module)

Native ES module format that aligns with package module type.

- **Good**: Consistent with `"type": "module"` package configuration
- **Good**: Native ES module syntax (`export default`)
- **Good**: No additional tooling required
- **Good**: Prettier CLI reads it without configuration
- **Good**: Standard Node.js import resolution
- **Good**: Can be imported by tests and other tools
- **Bad**: No compile-time type validation
- **Bad**: Manual type checking required for configuration options

### Use prettier.config.cjs (CommonJS)

CommonJS format that explicitly declares module type.

- **Good**: Explicit CommonJS declaration avoids module resolution issues
- **Good**: Works reliably with all Node.js tooling
- **Good**: Prettier CLI support
- **Bad**: Inconsistent with package's ES module nature
- **Bad**: Mixing module systems in same package
- **Bad**: Uses `module.exports` syntax in an ES module package
- **Bad**: Conceptually confusing for package maintainers

### Use prettier.config.js (JavaScript)

Standard JavaScript format relying on package.json type declaration.

- **Good**: Simple file extension
- **Good**: Prettier CLI support
- **Bad**: Ambiguous module type (relies on package.json)
- **Bad**: Would use ES module syntax but with .js extension
- **Neutral**: Same functionality as .mjs but less explicit

## Implementation Instructions

Follow these step-by-step instructions to implement TypeScript Prettier configuration in your repository:

### Prerequisites

- **Node.js 22.6.0 or higher** (required for native TypeScript support)
- **Package configured as ES module** (`"type": "module"` in package.json)
- **Prettier installed** as a dependency

### Step 1: Create TypeScript Prettier Configuration

Create `prettier.config.ts` in your project root:

```typescript
// prettier.config.ts
import type { Config } from 'prettier';

const config: Config = {
  printWidth: 100,
  semi: true,
  singleQuote: true,
  trailingComma: 'all',
  arrowParens: 'always',
  bracketSpacing: true,
  endOfLine: 'lf',
  overrides: [
    {
      files: '*.md',
      options: {
        printWidth: 80,
      },
    },
  ],
};

export default config;
```

**Key Points:**

- Import the `Config` type from prettier for type safety
- Use `const config: Config` to ensure TypeScript validates your configuration
- Export as default using ES module syntax
- Customize the configuration options as needed for your project

### Step 2: Update Package.json Scripts

Add the `NODE_OPTIONS` flag to your Prettier scripts:

```json
{
  "scripts": {
    "format": "NODE_OPTIONS=\"--experimental-strip-types\" prettier \"**/*.{ts,tsx,js,jsx,json,md}\" --write",
    "format:check": "NODE_OPTIONS=\"--experimental-strip-types\" prettier \"**/*.{ts,tsx,js,jsx,json,md}\" --check"
  }
}
```

**Key Points:**

- `NODE_OPTIONS="--experimental-strip-types"` enables native TypeScript support
- Include file patterns that match your project structure
- Use double quotes around the NODE_OPTIONS value for cross-platform compatibility

### Step 3: Update Package Exports (For Shared Config Packages)

If you're creating a shared configuration package, add the export to `package.json`:

```json
{
  "exports": {
    "./prettier": "./prettier.config.ts"
  }
}
```

**Key Points:**

- Point directly to the `.ts` file (not compiled JavaScript)
- Consumers will also need Node.js 22.6.0+ to import this configuration

### Step 4: Update TypeScript Configuration

Include the Prettier config in your `tsconfig.json`:

```json
{
  "include": [
    "src",
    "prettier.config.ts",
    "eslint.config.ts",
    "vitest.config.ts"
  ]
}
```

**Key Points:**

- This allows ESLint to parse the file with type-aware rules
- Enables TypeScript to validate the configuration
- Include other config files that use TypeScript

### Step 5: Test the Configuration

Create a test to validate your configuration works:

```typescript
// src/prettier.test.ts (or similar)
import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const prettierConfigPath = path.resolve(currentDir, '../prettier.config.ts');

describe('prettier configuration', () => {
  it('should exist and be readable', () => {
    expect(fs.existsSync(prettierConfigPath)).toBe(true);

    const configContent = fs.readFileSync(prettierConfigPath, 'utf-8');
    expect(configContent).toContain('printWidth');
    expect(configContent).toContain('export default');
  });
});
```

**Key Points:**

- Use `import.meta.url` instead of `__dirname` in ES modules
- Test that the configuration file exists and contains expected content
- This validates that your configuration is accessible to your build process

### Step 6: Verify the Implementation

Run these commands to verify everything works:

```bash
# Check TypeScript compilation
npm run type-check

# Verify Prettier can read the config
npm run format:check

# Run tests to ensure config is accessible
npm test

# Run ESLint to ensure config is properly included
npm run lint
```

**Expected Results:**

- Type checking should pass without errors
- Prettier should successfully validate all files
- Tests should pass, confirming config accessibility
- ESLint should parse the TypeScript config without issues

### Step 7: Remove Old Configuration Files

If migrating from another format, remove the old files:

```bash
# Remove old configuration files
rm prettier.config.js   # if it exists
rm prettier.config.mjs  # if it exists
rm .prettierrc.json     # if it exists

# Remove any TypeScript declaration files for old configs
rm src/types/prettier-config.d.ts  # if it exists
```

**Key Points:**

- Only one Prettier configuration file should exist to avoid conflicts
- Remove any temporary type declarations that are no longer needed

### Common Issues and Solutions

#### Issue: "Cannot find module 'prettier.config.ts'"

- **Solution**: Ensure Node.js 22.6.0+ is installed and `NODE_OPTIONS="--experimental-strip-types"` is set

#### Issue: TypeScript compilation errors in config file

- **Solution**: Verify that `prettier.config.ts` is included in your `tsconfig.json` include array

#### Issue: ESLint parsing errors

- **Solution**: Make sure your ESLint configuration includes TypeScript parser and the config file is in the TypeScript project

#### Issue: Tests failing to import configuration

- **Solution**: Use `import.meta.url` for file path resolution in ES modules instead of `__dirname`

### Migration from .mjs Configuration

If migrating from `prettier.config.mjs`:

1. Replace the `.mjs` file with the TypeScript version above
2. Update package.json exports to point to `.ts` file
3. Add `NODE_OPTIONS` to your format scripts
4. Remove any `.mjs` type declarations from your TypeScript files
5. Update tests to import the new configuration location

### Package Dependencies

Ensure these are in your `package.json`:

```json
{
  "devDependencies": {
    "prettier": "^3.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=22.6.0"
  }
}
```

This implementation provides full type safety, excellent developer experience, and forward compatibility with future Node.js versions.

## More Information

This decision prioritizes type safety and developer experience over compatibility with older Node.js versions. The TypeScript configuration provides compile-time validation and excellent IDE support while working reliably with modern Node.js and Prettier CLI.

### Implementation Notes

With Node.js 22.6.0+, TypeScript configuration files are natively supported using the `--experimental-strip-types` flag. This eliminates the need for external loaders or complex build setups. The implementation requires:

- Adding `NODE_OPTIONS="--experimental-strip-types"` to format scripts
- Including `prettier.config.ts` in the TypeScript project configuration
- Using proper ES module imports in test files (import.meta.url instead of \_\_dirname)

The solution provides:

- Full type checking for the configuration
- IntelliSense support in IDEs
- Compile-time validation of options
- Seamless integration with the package's TypeScript codebase

### Future Considerations

When Node.js stabilizes TypeScript support (removes the experimental flag), the configuration will work without any changes. The solution is forward-compatible and provides immediate benefits while being ready for future Node.js versions.

Related:

- ADR-0002: Declare peer dependencies for consumer tools
- Package.json `"type": "module"` declaration
- ES module consistency across package configuration files
