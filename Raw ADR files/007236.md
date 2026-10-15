# ADR-001: OpenAPI 3.1-First Internal Type System

**Date:** November 4, 2025  
**Status:** Accepted  
**Deciders:** Architecture Team  
**Related:** ADR-002 (Scalar Pipeline), ADR-003 (Intersection Types)

---

## Context

The library generates Zod validation schemas and TypeScript clients from OpenAPI specifications. Historically, the codebase supported both OpenAPI 3.0.x and 3.1.x specifications, maintaining parallel type systems and conditional logic to handle version-specific differences.

### Key Differences Between OpenAPI 3.0 and 3.1

1. **Nullable Types:**
   - 3.0: `{ type: 'string', nullable: true }`
   - 3.1: `{ type: ['string', 'null'] }`

2. **Exclusive Bounds:**
   - 3.0: `{ minimum: 5, exclusiveMinimum: true }` (boolean)
   - 3.1: `{ exclusiveMinimum: 5 }` (number)

3. **JSON Schema Alignment:**
   - 3.1 aligns with JSON Schema Draft 2020-12
   - 3.0 uses a custom schema dialect

4. **New Features in 3.1:**
   - Webhooks
   - Enhanced discriminator mapping
   - `const` keyword support
   - Better oneOf/anyOf handling

### Problem Statement

Maintaining dual type systems created:

- **Code complexity:** Conditional logic throughout conversion/template layers
- **Type safety issues:** Version-specific type guards and assertions
- **Testing burden:** Duplicate test fixtures for 3.0 and 3.1
- **Future limitations:** Inability to leverage 3.1-specific features
- **Maintenance overhead:** Every new feature required version branching

---

## Decision

**We will normalize all OpenAPI documents to version 3.1 immediately after bundling, regardless of input version.**

All internal code (conversion logic, templates, type definitions) will exclusively use OpenAPI 3.1 types from `openapi3-ts/oas31`. The upgrade happens transparently via `@scalar/openapi-parser/upgrade` as part of the document loading pipeline.

### Pipeline Flow

```
Input (3.0 or 3.1 spec: file, URL, or object)
    ↓
bundle() via @scalar/json-magic
    ↓ (resolves $refs, adds x-ext metadata)
upgrade() via @scalar/openapi-parser/upgrade
    ↓ (normalizes to OpenAPI 3.1)
Validate & type as intersection
    ↓ (runtime boundary: loose → strict types)
BundledOpenApiDocument (OpenAPIV3_1.Document & OpenAPIObject)
    ↓ (strict openapi3-ts/oas31 + Scalar extensions)
Downstream code (conversion, templates, etc.)
```

### Implementation Principles

1. **Single Internal Type System:** All code uses `openapi3-ts/oas31` types exclusively
2. **Automatic Upgrades:** 3.0 specs transparently upgraded to 3.1 during load
3. **No Version Branching:** Conversion/template logic assumes 3.1 semantics
4. **Strict Typing:** Type guards at boundaries, no escape hatches
5. **Backward Compatible:** Users can still provide 3.0 specs as input

### Critical Architectural Boundary

**After `loadOpenApiDocument()` returns, ALL downstream code operates exclusively on OpenAPI 3.1 documents with `openapi3-ts/oas31` types.**

This means:

- ❌ **No checks for OpenAPI 3.0 structures** (e.g., `nullable: true`, `exclusiveMinimum: boolean`)
- ❌ **No conditional logic based on spec version** (always 3.1.x)
- ❌ **No fallbacks to 3.0 patterns** (e.g., `example` vs `examples`)
- ✅ **All code assumes 3.1 semantics** (type arrays, numeric exclusive bounds, examples as objects)
- ✅ **Import only from `openapi3-ts/oas31`** (never `oas30` or `oas2`)

The upgrade happens at the document loading boundary. Once a document is loaded, it is guaranteed to be OpenAPI 3.1.

---

## Consequences

### Positive

✅ **Simplified Codebase:** Eliminated all version-specific conditional logic  
✅ **Type Safety:** Single type system reduces casting and assertions  
✅ **Future-Proof:** Ready for 3.1-specific features (webhooks, enhanced discriminators)  
✅ **Better Testing:** Single set of test fixtures using 3.1 syntax  
✅ **Reduced Maintenance:** New features only need 3.1 implementation  
✅ **Standards Alignment:** JSON Schema Draft 2020-12 compatibility  
✅ **Cleaner Conversions:** Nullable checks use standard type arrays

### Negative

⚠️ **Migration Effort:** All existing code/tests needed updating to 3.1 patterns  
⚠️ **Dependency on Scalar:** Relies on `@scalar/openapi-parser/upgrade` correctness  
⚠️ **Breaking Change:** Internal APIs changed (mitigated by public API stability)

### Neutral

ℹ️ **User Impact:** Transparent to end users (both 3.0 and 3.1 inputs still accepted)  
ℹ️ **Performance:** Negligible overhead from upgrade step  
ℹ️ **Debugging:** Scalar adds `x-ext` metadata for traceability

---

## Implementation Notes

### Type Migration

All imports changed from `openapi3-ts/oas30` to `openapi3-ts/oas31`:

```typescript
// Before
import type { OpenAPIObject } from 'openapi3-ts/oas30';

// After
import type { OpenAPIObject } from 'openapi3-ts/oas31';
```

### Nullable Type Handling

```typescript
// Helper function for 3.1 nullable checks
function isNullableType(schema: SchemaObject): boolean {
  const types = Array.isArray(schema.type) ? schema.type : schema.type ? [schema.type] : [];
  return types.includes('null');
}

// Before (3.0 style)
if (schema.nullable) {
  /* ... */
}

// After (3.1 style)
if (isNullableType(schema)) {
  /* ... */
}
```

### Exclusive Bounds

```typescript
// Before (3.0 style)
if (schema.minimum !== undefined) {
  if (schema.exclusiveMinimum === true) {
    validations.push(`gt(${schema.minimum})`);
  } else {
    validations.push(`gte(${schema.minimum})`);
  }
}

// After (3.1 style)
if (schema.minimum !== undefined) {
  validations.push(`gte(${schema.minimum})`);
} else if (typeof schema.exclusiveMinimum === 'number') {
  validations.push(`gt(${schema.exclusiveMinimum})`);
}
```

### Test Fixtures

```typescript
// Before (3.0 fixtures)
const schema = {
  type: 'string',
  nullable: true,
  minimum: 5,
  exclusiveMinimum: true,
};

// After (3.1 fixtures)
const schema = {
  type: ['string', 'null'],
  exclusiveMinimum: 5,
};
```

---

## Alternatives Considered

### Alternative 1: Maintain Dual Type Systems

**Rejected:** Complexity and maintenance burden outweighed any benefits. Version branching throughout the codebase made features harder to implement and test.

### Alternative 2: Normalize to 3.0

**Rejected:** Would prevent leveraging 3.1 features and JSON Schema alignment. OpenAPI 3.1 is the current standard and future direction.

### Alternative 3: Runtime Version Detection

**Rejected:** Would still require conditional logic throughout. Normalization at the boundary is cleaner and more maintainable.

---

## References

- [OpenAPI 3.1.0 Specification](https://spec.openapis.org/oas/v3.1.0)
- [OpenAPI 3.0.3 Specification](https://spec.openapis.org/oas/v3.0.3)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html)
- [@scalar/openapi-parser Documentation](https://github.com/scalar/scalar/tree/main/packages/openapi-parser)
- [openapi3-ts Library](https://github.com/metadevpro/openapi3-ts)

---

## Related Decisions

- **ADR-002:** Scalar Pipeline Adoption (provides the upgrade mechanism)
- **ADR-003:** Intersection Type Strategy (handles type boundary validation)
- **ADR-004:** Legacy Dependency Removal (removes `openapi-types` and SwaggerParser)

---

## Revision History

| Date       | Version | Changes                     |
| ---------- | ------- | --------------------------- |
| 2025-11-04 | 1.0     | Initial decision documented |
