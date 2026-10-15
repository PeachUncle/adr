# ADR-007: ESM with NodeNext Module Resolution

## Status

**Accepted** - October 22, 2025

## Context

The project needed to modernize from mixed CommonJS/ESM to pure ESM with proper module resolution. Node.js has evolved its module system significantly, and TypeScript 4.7+ supports new `moduleResolution` options that align with Node.js ESM behavior.

### The Problem

**Before:**

- Mixed ESM/CJS code
- Incomplete ESM migration
- Import paths without `.js` extensions
- `moduleResolution: "node"` (outdated)
- Inconsistent module handling

### Module Resolution Options

1. **`node`** (Classic): Legacy Node.js resolution, doesn't match modern behavior
2. **`node16/nodenext`**: Matches Node.js ESM behavior exactly, requires `.js` extensions
3. **`bundler`**: For bundler environments, allows extensionless imports

## Decision

**We will use pure ESM with `moduleResolution: "nodenext"` and explicit `.js` extensions for all relative imports.**

### Configuration

```json
// tsconfig.json (lib workspace)
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "NodeNext",
    "target": "ES2022",
    "outDir": "./dist",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true
  }
}
```

### Import Rules

```typescript
// ✅ CORRECT: Relative imports with .js extension
import { getZodSchema } from './openApiToZod.js';
import type { TemplateContext } from './template-context.js';

// ✅ CORRECT: Package imports without extension
import type { OpenAPIObject } from 'openapi3-ts';
import { z } from 'zod';

// ❌ WRONG: Relative import without extension
import { getZodSchema } from './openApiToZod';

// ❌ WRONG: Using .ts extension
import { getZodSchema } from './openApiToZod.ts';
```

### Why `.js` Extensions?

Node.js ESM requires explicit file extensions. TypeScript compiles `.ts` to `.js`, so imports must reference the **output** file extension (`.js`), not the source extension (`.ts`).

**Compile-time:**

```typescript
// src/index.ts
import { helper } from './helper.js'; // ✅ References future output file
```

**Runtime (after compilation):**

```javascript
// dist/index.js
import { helper } from './helper.js'; // ✅ File exists as helper.js
```

### Dual Package Output

We output both ESM and CJS for maximum compatibility:

```javascript
// tsup.config.ts
export default defineConfig({
  entry: ['src/index.ts', 'src/cli.ts'],
  format: ['cjs', 'esm'], // Dual output
  dts: true, // Generate .d.ts
  sourcemap: true,
  clean: true,
  splitting: false,
  treeshake: true,
});
```

**Output structure:**

```
dist/
  ├── index.js          # ESM
  ├── index.cjs         # CJS
  ├── index.d.ts        # Types
  ├── cli.js            # ESM
  ├── cli.cjs           # CJS
  └── cli.d.ts          # Types
```

## Consequences

### Positive

✅ **Standards compliant**: Matches Node.js ESM exactly  
✅ **Dual output**: Supports both ESM and CJS consumers  
✅ **Future-proof**: Aligned with ecosystem direction  
✅ **Type safety**: TypeScript validates module resolution  
✅ **Clear imports**: `.js` extension makes intent obvious  
✅ **IDE support**: Better autocomplete and navigation  
✅ **No runtime surprises**: Compile-time === runtime

### Negative

⚠️ **Extension requirement**: Must add `.js` to all relative imports (475 files updated)  
⚠️ **Mental shift**: Writing `.js` for `.ts` files feels odd initially  
⚠️ **Tooling compatibility**: Some older tools don't understand this pattern

### Mitigation

- **Migration script**: Could automate adding `.js` extensions (we did it manually for precision)
- **Lint rules**: ESLint validates correct extensions
- **Team education**: Document why `.js` is used for `.ts` imports
- **IDE configuration**: Configure to suggest `.js` extensions

## Migration Process

1. **Update `tsconfig.json`**: Set `moduleResolution: "NodeNext"`
2. **Add `.js` to all relative imports**: 475 import statements updated
3. **Update tests**: Test files also need `.js` extensions
4. **Verify build**: Ensure ESM and CJS outputs work
5. **Test quality gates**: Confirm `format`, `type-check`, `lint`, `test` all pass

### Example Migration

**Before:**

```typescript
// src/index.ts
import { getZodSchema } from './openApiToZod';
import { TemplateContext } from './template-context';
```

**After:**

```typescript
// src/index.ts
import { getZodSchema } from './openApiToZod.js';
import type { TemplateContext } from './template-context.js';
```

## Alternative Considered: `bundler` Resolution

**Option**: Use `moduleResolution: "bundler"` to allow extensionless imports.

**Pros**:

- No `.js` extensions needed
- Simpler migration
- Feels more natural

**Cons**:

- **Not standards compliant**: Doesn't match Node.js behavior
- **Bundler-specific**: Only works with bundlers, not raw Node.js
- **Runtime mismatch**: Different behavior in Node.js vs bundled

**Decision**: Rejected because we want **maximum compatibility** and **standards compliance**, not bundler-specific behavior.

## Future: TypeScript 5.7+ `rewriteRelativeImportExtensions`

TypeScript 5.7+ will support `rewriteRelativeImportExtensions` which allows writing `.ts` extensions that get rewritten to `.js` in output:

```typescript
// Source
import { helper } from './helper.ts';

// Output (with rewriteRelativeImportExtensions: true)
import { helper } from './helper.js';
```

When TypeScript 5.7+ is stable, we may consider this option. However, the current `.js` pattern is more explicit and works today.

## Quality Gates Impact

All quality gates pass with this configuration:

```bash
✅ pnpm format       # Prettier handles .js imports
✅ pnpm build        # tsup generates ESM + CJS + DTS
✅ pnpm type-check   # TypeScript validates NodeNext resolution
✅ pnpm lint         # ESLint validates import paths
✅ pnpm test         # Vitest runs ESM tests
```

## Related Decisions

- [ADR-009: Replace Preconstruct with tsup](./ADR-009-replace-preconstruct-with-tsup.md) - Build tool for dual output
- [ADR-010: Use Turborepo for Monorepo Orchestration](./ADR-010-use-turborepo.md) - Orchestrates workspaces

## References

- TypeScript 4.7 Release Notes: [Node.js ESM Support](https://devblogs.microsoft.com/typescript/announcing-typescript-4-7/#ecmascript-module-support-in-node-js)
- Node.js ESM Documentation: https://nodejs.org/api/esm.html
- Implementation: 475 files updated across `lib/src` and `lib/tests`
- Configuration: `lib/tsconfig.json`, `lib/tsup.config.ts`

## Commits

- Multiple commits during Phase 1a ESM migration
