# ADR-0005: No Barrel Exports Convention

**Status:** Accepted
**Date:** 2025-10-22
**Deciders:** Project maintainers

## Context

TypeScript/JavaScript projects often use "barrel exports" (index files that re-export everything) to simplify imports. However, barrel exports have significant performance and maintainability downsides.

**Barrel export example:**

```typescript
// components/index.ts (barrel export)
export * from './Button';
export * from './Input';
export * from './Select';
// ... 50 more components

// usage.tsx
import { Button } from './components'; // Imports ALL components
```

Requirements:

- Fast build times and bundling
- Tree-shaking effectiveness
- Clear import paths
- Maintainable code organization
- Good developer experience

The export convention affects:

- Component organization
- Build performance
- Bundle size
- Import patterns in generated code
- Developer mental model

## Decision

**Prohibit barrel exports (`export *`) in all generated code. Use explicit exports only.**

**Convention:**

```typescript
// ✅ Good: Explicit exports
// components/button/index.ts
export { Button } from './button';
export type { ButtonProps } from './button';

// usage.tsx
import { Button } from './components/button';

// ❌ Avoid: Barrel exports
// components/index.ts
export * from './button'; // NO!
export * from './input'; // NO!
```

**Rationale:**

- Explicit exports enable better tree-shaking
- Clearer import paths improve code navigation
- Faster build times (don't analyze unnecessary files)
- Prevents accidental circular dependencies
- Better type inference (TypeScript doesn't need to resolve `export *`)

## Alternatives Considered

### Option 1: Allow Barrel Exports

**Description:**
Use `export *` to re-export all module contents for convenient imports.

**Pros:**

- Shorter import paths (`from './components'` vs `from './components/button'`)
- Easier to add new exports (just add to barrel)
- Common pattern in React ecosystem
- Familiar to many developers

**Cons:**

- **Bundle size**: Bundlers must analyze all files (hurts tree-shaking)
- **Build performance**: Slower builds (more files to process)
- **Type performance**: TypeScript slower to resolve `export *`
- **Circular dependencies**: Easier to create unintentionally
- **Unclear exports**: Hard to know what's exported without reading barrel file
- **Maintenance**: Large barrel files become unwieldy

**Decision:** ❌ Rejected

**Rationale:** The performance costs and maintenance burden outweigh the convenience of shorter imports. Modern IDEs auto-complete full paths anyway.

### Option 2: Explicit Named Exports (Selected Approach)

**Description:**
Explicitly name each export in index files.

**Pros:**

- Better tree-shaking (bundlers know exactly what's used)
- Faster builds (only process needed files)
- Clearer code (explicit about what's public)
- Better TypeScript performance
- Prevents accidental exports
- Easier to maintain (see all exports at a glance)

**Cons:**

- Slightly longer import paths
- Must update index file when adding exports
- Less common pattern (though growing)

**Decision:** ✅ Selected

**Rationale:** Explicit exports provide better performance, maintainability, and clarity. The minor inconvenience of longer import paths is acceptable given the benefits.

### Option 3: No Index Files (Direct Imports Only)

**Description:**
Import directly from implementation files, no index files at all.

```typescript
// No index.ts at all
import { Button } from './components/button/button';
```

**Pros:**

- Maximum clarity (exact file is obvious)
- No indirection
- Fastest possible imports

**Cons:**

- Very verbose import paths
- Harder to refactor (file renames break imports)
- Less flexible (can't abstract implementation structure)

**Decision:** ❌ Rejected

**Rationale:** Too extreme. Index files with explicit exports provide a good balance of clarity and flexibility.

## Consequences

### Positive

- **Better bundling**: Smaller bundle sizes through effective tree-shaking
- **Faster builds**: Bundlers process fewer unnecessary files
- **Clearer exports**: Explicit list of public API
- **Better types**: Faster TypeScript compilation and better inference
- **Maintainability**: Easy to see what's exported from a module
- **Prevents bugs**: Harder to create circular dependencies accidentally

### Negative

- **Longer imports**: Import paths are more verbose (but IDEs auto-complete)
- **Index file maintenance**: Must explicitly add exports to index files
- **Less familiar**: Not the most common pattern in React ecosystem
- **Migration cost**: Existing barrel exports need refactoring

### Neutral

- **Convention enforcement**: Need linting to prevent barrel exports
- **Documentation**: Need to document the pattern for contributors
- **Code review**: Reviewers must check for barrel exports

## Implementation Notes

**How will this be enforced?**

- component-generator creates explicit export index files
- ESLint rule to prohibit `export *` (except for type-only re-exports)
- Code review checklist includes checking for barrel exports
- Documentation examples use explicit exports

**ESLint configuration:**

```javascript
// eslint.config.js
{
  rules: {
    'no-restricted-syntax': [
      'error',
      {
        selector: 'ExportAllDeclaration',
        message: 'Barrel exports (export *) are prohibited. Use explicit exports instead.',
      },
    ],
  },
}
```

**Exception: Type-only re-exports:**

```typescript
// Allowed: Type-only re-exports
export type * from './types';
```

**When does this take effect?**

- Immediately for all new code generation
- Existing code should be migrated opportunistically

**What needs to change to comply?**

- Component index files use explicit exports only
- Generated code follows explicit export pattern
- Documentation updated to show correct patterns
- ESLint configuration added to prevent barrel exports

**Correct pattern:**

```typescript
// components/button/button.tsx
export interface ButtonProps {
  // ...
}

export function Button(props: ButtonProps) {
  // ...
}

// components/button/index.ts
export { Button } from './button';
export type { ButtonProps } from './button';

// usage.tsx
import { Button } from '@/components/button';
```

## References

**Related ADRs:**

- ADR-0001: Adopt Base UI (Base UI uses explicit exports)

**OpenSpec Proposals:**

- [components-plugin](../../../openspec/changes/components-plugin/) - Component generation with explicit exports

**External Resources:**

- [Module Resolution Performance](https://github.com/microsoft/TypeScript/wiki/Performance#organizing-and-configuring-the-project)
- [Tree Shaking and Barrel Files](https://developers.google.com/web/fundamentals/performance/optimizing-javascript/tree-shaking)
- [TypeScript Performance Best Practices](https://github.com/microsoft/TypeScript/wiki/Performance)

## Notes

**Why this matters for code generation:**

Component-generator and other skills generate a lot of code. Barrel exports would compound:

- Build time (processing hundreds of components)
- Bundle size (larger apps = more unused exports)
- Type checking (TypeScript processing time)

By defaulting to explicit exports, generated code is performant by default.

**Migration path:**

For existing barrel exports:

```bash
# Before (barrel export)
export * from './button';
export * from './input';

# After (explicit export)
export { Button } from './button';
export type { ButtonProps } from './button';
export { Input } from './input';
export type { InputProps } from './input';
```

**Developer experience:**

Modern IDEs auto-complete full import paths, so longer paths aren't a significant burden:

```typescript
// Type "Button" and IDE suggests:
import { Button } from '@/components/button'; // Auto-completed
```

This decision prioritizes performance and maintainability over marginal convenience.
