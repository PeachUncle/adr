# ADR-0003: Module System Policy

## Status
Accepted

## Context
The repository currently has mixed CommonJS (CJS) and ES Module (ESM) usage across different packages and scripts. This has led to several issues:

- **Root-level `"type": "module"` risk**: Setting this at the repository root flips all `.js` files to ESM, causing `require()` and `module.exports` to break unless files are converted or renamed
- **CI/runtime breakages**: Mixed module systems cause build failures, dependency resolution issues, and inconsistent behavior across environments
- **Developer confusion**: Unclear which files use which module system, leading to accidental mixing of syntaxes
- **Toolchain complexity**: Different tools expect different module systems, requiring careful configuration

Recent incidents include:
- ES module configuration causing CommonJS scripts to fail (`require is not defined in ES module scope`)
- Build failures due to module resolution mismatches
- CI failures from mixed syntax usage

## Decision
We will establish a clear module system policy with the following rules:

### Default Module System
- **Node.js helper scripts**: Default to CommonJS via `.cjs` extension and `require`/`module.exports` syntax
- **TypeScript execution**: Use `tsx` for running TypeScript files that need ES module support
- **Package-level ESM**: Use `package.json#type: "module"` only for packages that are fully ESM
- **File-level ESM**: Use `.mjs` extension for individual files that need ESM syntax

### Avoid Repository-Wide ESM
- **No root-level `"type": "module"`**: Unless the entire repository is converted to ESM
- **Per-package configuration**: Each package/service should declare its module system explicitly
- **Clear boundaries**: Maintain clear separation between CJS and ESM code

### File Extension Rules
- `.js` files: CommonJS (unless package has `"type": "module"`)
- `.cjs` files: CommonJS (explicit)
- `.mjs` files: ES Modules (explicit)
- `.ts` files: TypeScript (executed via `tsx`)

## Consequences

### Positive
- **Consistent semantics**: Clear rules for which files use which module system
- **Fewer collisions**: Reduced accidental mixing of CJS/ESM syntax
- **Clear migration path**: Explicit steps for converting between module systems
- **Better tooling support**: Tools can make correct assumptions about module systems
- **Reduced CI failures**: Fewer module resolution and syntax errors

### Negative
- **Migration effort**: Existing mixed files need to be converted or renamed
- **Learning curve**: Developers need to understand the policy
- **Toolchain complexity**: May need different tools for different module systems

### Risks
- **Inconsistent application**: Policy must be enforced consistently
- **Legacy code**: Existing mixed files may cause issues until converted
- **Tool compatibility**: Some tools may not handle mixed module systems well

## Implementation

### Immediate Actions
1. **Audit existing files**:
   ```bash
   # Find CommonJS usage
   rg -n "module.exports|require(" scripts/ packages/ services/
   
   # Find ES Module usage
   rg -n "import .* from" scripts/ packages/ services/
   ```

2. **Convert Node.js helpers**:
   - Rename `.js` files using CommonJS to `.cjs`
   - Update script references in `package.json`
   - Ensure `require()` and `module.exports` work correctly

3. **Package-level ESM**:
   - Add `"type": "module"` only to packages that are fully ESM
   - Use `.mjs` for individual ESM files in CJS packages

### Guardrails

#### CI Enforcement
- **Conflict marker detection**: Fail CI if merge conflict markers are present
- **Module system linting**: Flag `require()` in `.mjs` files and `import` in `.cjs` files
- **Toolchain pins**: Enforce Node 20.18.x and npm 10.x versions

#### Development Guidelines
- **File naming**: Use appropriate extensions (`.cjs`, `.mjs`, `.ts`)
- **Import/export consistency**: Don't mix `require()` and `import` in the same file
- **Package boundaries**: Keep module systems consistent within packages

### Migration Strategy
1. **Phase 1**: Establish policy and convert critical scripts
2. **Phase 2**: Add CI enforcement and linting rules
3. **Phase 3**: Migrate remaining mixed files
4. **Phase 4**: Consider full ESM migration for specific packages

## Examples

### Correct Usage
```javascript
// scripts/check-node-version.cjs (CommonJS)
const fs = require('fs');
const path = require('path');

function checkNodeVersion() {
  // ... implementation
}

module.exports = { checkNodeVersion };
```

```javascript
// packages/shared/index.mjs (ES Module)
import { readFile } from 'fs/promises';
import path from 'path';

export async function loadConfig() {
  // ... implementation
}
```

### Incorrect Usage
```javascript
// ❌ Mixed syntax in same file
const fs = require('fs');
import path from 'path';

// ❌ Wrong extension for syntax
// file.js with ES module syntax
import { something } from './other.js';
```

## References
- [Node.js ES Modules Documentation](https://nodejs.org/api/esm.html)
- [CommonJS vs ES Modules](https://nodejs.org/api/modules.html)
- [TypeScript Module Resolution](https://www.typescriptlang.org/docs/handbook/module-resolution.html)



