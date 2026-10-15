# ADR-015: Eliminate makeSchemaResolver in Favor of Direct Component Access

## Status

**Accepted** - October 26, 2025  
**Implementation:** Phase 1 of Architecture Rewrite

## Context

The codebase uses `makeSchemaResolver` as a factory function to create schema resolution closures. During the Architecture Rewrite planning (ADR-013), we discovered that this abstraction is fundamentally dishonest about types and creates an anti-pattern.

### The Problem with makeSchemaResolver

**1. Type Dishonesty**

```typescript
// ❌ Claims to return SchemaObject
export function makeSchemaResolver(openApiDoc: OpenAPIObject) {
  return function resolver($ref: string): SchemaObject {
    // Actually returns: SchemaObject | ResponseObject | ParameterObject | any component!
    return get(openApiDoc.components, $ref.split('/').slice(2));
  };
}
```

The resolver **lies**:

- Claims return type: `SchemaObject`
- Actual return type: `any component type`
- Result: ~20-25 type assertions throughout codebase to "fix" this lie

**2. Masked Architectural Issue**

The resolver exists because we thought we needed custom `$ref` resolution. However:

```typescript
// We already use SwaggerParser.bundle()!
const bundledSpec = await SwaggerParser.bundle(spec);
```

`SwaggerParser.bundle()` **already resolves all operation-level $refs**:

- Resolves `$ref` in paths/operations
- Resolves `$ref` in parameters, request bodies, responses
- Does NOT resolve component-level $refs (intentionally - those should stay as refs)

**We don't need custom resolution - we need direct component access.**

**3. Unnecessary Abstraction**

```typescript
// Making a resolver for each function
const resolver = makeSchemaResolver(openApiDoc);

// Then passing it around
function processSchema(schema: SchemaObject, resolver: Resolver) {
  const resolved = resolver(schema.$ref); // Type assertion needed
}
```

This pattern:

- Hides the components object
- Makes type flow unclear
- Requires closures and function passing
- Adds cognitive overhead

**Better approach: Pass components directly**

```typescript
// Direct, honest access
function processSchema(schema: SchemaObject | ReferenceObject, components: ComponentsObject) {
  if (isReferenceObject(schema)) {
    const resolved = getSchemaFromComponents(components, schema.$ref);
    // Type is honest: SchemaObject | undefined
  }
}
```

### Discovery Process

Analysis documented in:

- `.agent/analysis/SWAGGER_PARSER_INTEGRATION.md` - SwaggerParser.bundle() guarantees
- `.agent/docs/type-assertion-elimination-analysis.md` - Type flow analysis
- `.agent/plans/archive/COMPLETED_WORK.md` - Task 2.3 analysis

## Decision

**We will eliminate `makeSchemaResolver` and use direct component access with honest types.**

### New Pattern: Direct Component Access

**Create `component-access.ts` module:**

````typescript
import type { ComponentsObject, SchemaObject, ReferenceObject } from 'openapi3-ts/oas31';

/**
 * Gets a schema from components by $ref path.
 *
 * @param components - The components object from OpenAPI spec
 * @param $ref - The reference path (e.g., "#/components/schemas/User")
 * @returns The schema object, or undefined if not found
 *
 * @throws {Error} If $ref format is invalid or schema is not a SchemaObject
 *
 * @example
 * ```typescript
 * const schema = getSchemaFromComponents(components, "#/components/schemas/User");
 * if (!schema) {
 *   throw new Error("Schema not found");
 * }
 * ```
 */
export function getSchemaFromComponents(
  components: ComponentsObject | undefined,
  $ref: string,
): SchemaObject | undefined {
  if (!components?.schemas) return undefined;

  // Parse $ref path
  const parts = $ref.split('/');
  if (parts[0] !== '#' || parts[1] !== 'components' || parts[2] !== 'schemas') {
    throw new Error(`Invalid $ref format: ${$ref}. Expected #/components/schemas/...`);
  }

  const schemaName = parts[3];
  const schema = components.schemas[schemaName];

  if (!schema) return undefined;

  // Ensure it's not a reference (SwaggerParser.bundle() should have resolved these)
  if (isReferenceObject(schema)) {
    throw new Error(
      `Unexpected $ref in components: ${$ref}. ` +
        `Ensure SwaggerParser.bundle() is called before processing.`,
    );
  }

  return schema;
}

/**
 * Resolves a SchemaObject | ReferenceObject to SchemaObject.
 *
 * @param schema - Schema or reference to resolve
 * @param components - The components object
 * @returns Resolved SchemaObject
 *
 * @throws {Error} If reference cannot be resolved
 */
export function resolveSchemaRef(
  schema: SchemaObject | ReferenceObject,
  components: ComponentsObject | undefined,
): SchemaObject {
  if (isReferenceObject(schema)) {
    const resolved = getSchemaFromComponents(components, schema.$ref);
    if (!resolved) {
      throw new Error(`Cannot resolve $ref: ${schema.$ref}`);
    }
    return resolved;
  }
  return schema;
}

/**
 * Type guard to assert a value is not a ReferenceObject.
 * Useful for fail-fast validation.
 */
export function assertNotReference(
  value: SchemaObject | ReferenceObject,
  context: string,
): asserts value is SchemaObject {
  if (isReferenceObject(value)) {
    throw new Error(
      `Unexpected $ref in ${context}: ${value.$ref}. ` +
        `Ensure SwaggerParser.bundle() resolved all operation-level refs.`,
    );
  }
}
````

### Migration Strategy

**Phase 1 of Architecture Rewrite: Eliminate Resolver (8-10 hours)**

**Step 1: Create component-access.ts (1-2 hours)**

- Implement helper functions with proper types
- Write comprehensive tests
- Document fail-fast philosophy

**Step 2: Update Function Signatures (2-3 hours)**

- Change `resolver: Resolver` → `components: ComponentsObject`
- Update all call sites
- Fix type flows (no more assertions needed)

**Step 3: Remove makeSchemaResolver (1 hour)**

- Delete makeSchemaResolver.ts
- Update imports throughout codebase
- Verify all tests pass

**Step 4: Update Tests (1-2 hours)**

- Update test fixtures
- Verify component access patterns
- Add tests for new helper functions

**Step 5: Modernize topologicalSort (1-2 hours)**

- Add comprehensive TSDoc
- Optimize performance (`.includes()` → `Set.has()`)
- Add unit tests

### Implementation Principles

1. **Honest types** - Functions return what they claim
2. **Fail-fast** - Throw clear errors for invalid $refs
3. **Trust SwaggerParser.bundle()** - It resolves operation-level refs
4. **Direct access** - Pass components parameter, not closures
5. **Pure functions** - No hidden state in closures

## Consequences

### Positive

✅ **Type honesty** - Functions return actual types, not lies  
✅ **Eliminates ~20-25 type assertions** - No longer needed  
✅ **Clearer code** - Direct access is easier to understand  
✅ **Better debugging** - Type flow is transparent  
✅ **Fail-fast** - Invalid $refs caught immediately  
✅ **Simpler architecture** - No closure factory pattern  
✅ **Easier testing** - Pass components directly, no mocking closures  
✅ **Performance** - No closure creation overhead

### Negative

⚠️ **API change** - All functions accepting `resolver` must change  
⚠️ **More parameters** - Functions need `components` parameter  
⚠️ **Migration effort** - ~8-10 hours to update entire codebase

### Mitigation

**API Change:**

- Internal functions only (not public API)
- Phase 0 test suite catches any behavioral changes
- Migration done in small, testable steps

**More Parameters:**

- Actually simpler - no closure factory needed
- More explicit - clear where data comes from
- Standard pattern - same as passing `openApiDoc`

**Migration Effort:**

- Well-defined scope (Phase 1 of rewrite)
- Clear before/after examples
- TDD approach catches regressions

## Before & After

### Before (makeSchemaResolver)

```typescript
// Create resolver
const resolver = makeSchemaResolver(openApiDoc);

// Use resolver (type assertions needed)
function processParameter(param: ParameterObject, resolver: Resolver) {
  if (param.schema?.$ref) {
    const schema = resolver(param.schema.$ref) as SchemaObject; // ❌ Assertion
  }
}

// Pass resolver everywhere
processParameter(param, resolver);
```

### After (Direct Component Access)

```typescript
// Direct access
function processParameter(param: ParameterObject, components: ComponentsObject | undefined) {
  if (isReferenceObject(param.schema)) {
    const schema = resolveSchemaRef(param.schema, components); // ✅ No assertion
  }
}

// Pass components directly
processParameter(param, openApiDoc.components);
```

## Integration with Other Phases

**Enables:**

- **Phase 2:** Simpler ts-morph migration (no resolver to deal with)
- **Future:** Easier multi-version OAS support

**Prerequisites:**

- **Phase 0:** Test suite catches any behavioral changes

## Related Decisions

- [ADR-013: Architecture Rewrite Decision](./ADR-013-architecture-rewrite-decision.md) - Parent decision
- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Fail-fast principle
- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Honest types principle
- [ADR-003: Type Predicates Over Boolean Filters](./ADR-003-type-predicates-over-boolean-filters.md) - Type guard usage

## References

**Related ADRs:**

- [ADR-013: Architecture Rewrite Decision](./ADR-013-architecture-rewrite-decision.md) - Parent decision
- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Fail-fast principle
- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Honest types principle
- [ADR-003: Type Predicates Over Boolean Filters](./ADR-003-type-predicates-over-boolean-filters.md) - Type guard usage

## Timeline

- **October 26, 2025**: Decision accepted
- **November-December 2025**: Implementation completed
- **January 2026**: Verified and stable

## Success Criteria

✅ makeSchemaResolver.ts deleted  
✅ All functions use direct component access  
✅ ~20-25 type assertions eliminated  
✅ All 430+ tests passing  
✅ Quality gates pass  
✅ topologicalSort modernized with TSDoc and performance improvements

## Commit

- Implementation will be committed as part of Phase 1 execution
- See: Phase 1 tasks in `01-CURRENT-IMPLEMENTATION.md`
