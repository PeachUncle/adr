# ADR-014: Migrate from tanu to ts-morph for AST Manipulation

## Status

**Accepted** - October 26, 2025  
**Implementation:** Phase 2 of Architecture Rewrite

## Context

We currently use `tanu` (v0.2.0) for TypeScript AST manipulation and code generation. During the Architecture Rewrite planning (ADR-013), we identified that tanu has API composition issues and limited ecosystem support.

### The Problem with tanu

1. **API Confusion**
   - Both `t` and `ts` exports from same library
   - They don't compose well together
   - Suggests we're using the API incorrectly
   - ~15-20 type assertions at tanu boundaries

2. **Limited Ecosystem**
   - Small package (last updated 2+ years ago)
   - Limited documentation
   - No active community
   - Uncertain maintenance status

3. **Type Safety Issues**
   - `t.TypeDefinition` vs `ts.Node` incompatibility
   - Requires assertions to bridge these types
   - No clear conversion path
   - Type flow is unclear

4. **Integration with CodeMeta**
   - CodeMeta wraps tanu types
   - Adds unnecessary abstraction layer
   - Makes code harder to understand
   - Analysis: `.agent/analysis/CODEMETA_ANALYSIS.md`

### Alternatives Considered

**Option 1: Fix tanu Usage (Rejected)**

- Investigate correct tanu API patterns
- Attempt to use `t` or `ts` exclusively
- **Rejected:** Even if fixable, ecosystem concerns remain

**Option 2: Template Literals (Rejected)**

- Generate code via string concatenation
- Use template literals for structure
- **Rejected:** Fragile, no type safety, hard to maintain
- Reference: `.agent/analysis/HANDLEBARS_EVALUATION.md`

**Option 3: ts-morph (Accepted)**

- Wrapper around TypeScript Compiler API
- Excellent documentation and ecosystem
- Type-safe AST manipulation
- Active maintenance
- **Accepted:** Best long-term choice

**Option 4: TypeScript Compiler API Directly (Rejected)**

- Use `ts.factory` directly
- Maximum control and flexibility
- **Rejected:** Too low-level, ts-morph provides better DX

## Decision

**We will migrate from tanu to ts-morph for all TypeScript code generation.**

### Why ts-morph

**Advantages:**

- ✅ **Mature ecosystem** - Actively maintained, 2M+ weekly downloads
- ✅ **Excellent documentation** - Comprehensive guides and examples
- ✅ **Type-safe** - Full TypeScript compiler type safety
- ✅ **Higher-level API** - Easier than raw compiler API
- ✅ **Better debugging** - Clear error messages
- ✅ **Future-proof** - Backed by TypeScript compiler itself

**Type Safety Example:**

```typescript
// Before (tanu with assertions)
const param = t.param(name, t.fromString(type) as any); // ❌ Assertion needed

// After (ts-morph, type-safe)
const param = sourceFile.addParameter({
  name: name,
  type: type, // ✅ No assertion, type-safe
});
```

### Migration Strategy

**Phase 2 of Architecture Rewrite: Migrate tanu → ts-morph (6-8 hours)**

**Step 1: Create ast-builder.ts (2-3 hours)**

- New module wrapping ts-morph
- Pure functions for building AST nodes
- Type-safe, testable
- Comprehensive TSDoc

**Step 2: Rewrite openApiToTypescript.ts (3-4 hours)**

- Replace tanu with ast-builder
- Remove CodeMeta (already eliminated in Phase 1)
- Use ts-morph source file manipulation
- Add tests for each function

**Step 3: Update Tests (1 hour)**

- Verify all 430+ tests still pass
- Update snapshot tests if needed
- Add new tests for ast-builder

### Implementation Principles

1. **Build ast-builder as separate module** - Testable, reusable
2. **Pure functions** - Each function builds one AST construct
3. **Comprehensive tests** - Test each builder function independently
4. **Incremental migration** - One function at a time, tests always passing
5. **TDD approach** - Write failing tests first for each builder

### Example Migration

**Before (tanu):**

```typescript
import { t } from 'tanu';
import { CodeMeta } from './CodeMeta.js';

function generateInterface(name: string, props: Property[]): CodeMeta {
  const properties = props.map(
    (p) => t.prop(p.name, t.fromString(p.type) as any), // ❌ Type assertion
  );
  return new CodeMeta(
    name,
    t.inter(name, properties), // Wrapped in CodeMeta
  );
}
```

**After (ts-morph):**

````typescript
import { type SourceFile, type InterfaceDeclaration } from 'ts-morph';

/**
 * Generates a TypeScript interface declaration.
 *
 * @param sourceFile - The source file to add the interface to
 * @param name - The interface name
 * @param properties - Array of property definitions
 * @returns The created interface declaration
 *
 * @example
 * ```typescript
 * const iface = generateInterface(sourceFile, "User", [
 *   { name: "id", type: "string" },
 *   { name: "age", type: "number" }
 * ]);
 * // Generates: interface User { id: string; age: number; }
 * ```
 */
export function generateInterface(
  sourceFile: SourceFile,
  name: string,
  properties: Array<{ name: string; type: string }>,
): InterfaceDeclaration {
  return sourceFile.addInterface({
    name,
    properties: properties.map((p) => ({
      name: p.name,
      type: p.type, // ✅ Type-safe, no assertions
    })),
  });
}
````

## Consequences

### Positive

✅ **Type safety** - No assertions needed at AST boundaries  
✅ **Better maintainability** - Clear, well-documented API  
✅ **Ecosystem support** - Large community, many examples  
✅ **Future-proof** - Active maintenance, TypeScript compiler backing  
✅ **Better debugging** - Clear error messages from ts-morph  
✅ **Eliminates ~15-20 type assertions** - Naturally resolved  
✅ **Cleaner code** - No CodeMeta wrapper needed  
✅ **Easier testing** - Mock source files easily

### Negative

⚠️ **Learning curve** - Team must learn ts-morph API  
⚠️ **Dependency change** - Replace tanu in package.json  
⚠️ **Migration effort** - 6-8 hours to migrate existing code  
⚠️ **Bundle size** - ts-morph is larger than tanu (but tree-shakeable)

### Mitigation

**Learning Curve:**

- Comprehensive examples in ast-builder.ts
- TSDoc documentation for all functions
- Reference implementations in tests

**Migration Effort:**

- Incremental approach (one function at a time)
- Tests catch any behavioral changes
- Clear completion criteria per function

**Bundle Size:**

- Only affects CLI tool, not generated code
- Tree-shaking reduces actual impact
- Better type safety worth the trade-off

## Integration with Other Phases

**Depends On:**

- **Phase 0:** Comprehensive test suite protects during migration
- **Phase 1:** CodeMeta eliminated, simplifies migration

**Enables:**

- **Phase 3:** Clean foundation for Zodios removal
- **Future:** Easier multi-version OAS support (Phase 3E)
- **Future:** Plugin architecture for custom code generation

## Before & After

### Before (tanu + CodeMeta)

```typescript
// Complex type flow with assertions
const meta = makeCodeMeta(t.inter(name, props) as any);
const exported = exportCodeMeta(meta as any);
```

### After (ts-morph)

```typescript
// Clean, type-safe flow
const iface = sourceFile.addInterface({ name, properties: props });
sourceFile.addExportDeclaration({ namedExports: [name] });
```

## Related Decisions

- [ADR-013: Architecture Rewrite Decision](./ADR-013-architecture-rewrite-decision.md) - Parent decision
- [ADR-015: Eliminate makeSchemaResolver](./ADR-015-eliminate-make-schema-resolver.md) - Phase 1 (prerequisite)
- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Type safety principles

## References

**Dependencies:**

- ts-morph: <https://ts-morph.com/>
- npm: <https://www.npmjs.com/package/ts-morph> (2M+ weekly downloads)

## Timeline

- **October 26, 2025**: Decision accepted as part of Architecture Rewrite
- **November-December 2025**: Implementation completed
- **January 2026**: Verified and stable

## Success Criteria

✅ All tanu imports removed  
✅ CodeMeta completely eliminated  
✅ No type assertions in code generation  
✅ All 430+ tests passing  
✅ Generated code identical or improved  
✅ Quality gates pass (format, build, type-check, test)

## Commit

- Implementation will be committed as part of Phase 2 execution
- See: Phase 2 tasks in `01-CURRENT-IMPLEMENTATION.md`
