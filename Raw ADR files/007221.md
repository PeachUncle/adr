# ADR-002: Defer Type Definitions to Source Libraries

## Status

**Accepted** - October 23, 2025

## Context

When working with OpenAPI specifications in TypeScript, we need runtime and compile-time type information for schemas, parameters, responses, and other OpenAPI constructs.

We had a choice:

1. **Define our own types**: Create custom type definitions that mirror OpenAPI concepts
2. **Extract from library types**: Use `Pick<>`, `Extract<>`, `Exclude<>` to derive types from library definitions
3. **Use library types directly**: Import and use types from `openapi3-ts` as-is

### The Problem

The original codebase had custom type definitions that duplicated library types:

```typescript
// ❌ BAD: Custom type definitions
type PrimitiveType = 'string' | 'number' | 'integer' | 'boolean' | 'null';
type SingleType = Exclude<SchemaObject['type'], unknown[] | undefined>;

function handleItems(items: SchemaObject): Result {
  // ❌ Actually receives SchemaObject | ReferenceObject!
}
```

This led to several issues:

- **Type mismatches**: Our types diverged from actual library types
- **Maintenance burden**: Had to keep custom types in sync with library updates
- **Complexity**: Unnecessary type gymnastics with `Exclude<>`, `Extract<>`, etc.
- **Incorrectness**: Claimed narrower types than reality (e.g., `SchemaObject` when it's actually `SchemaObject | ReferenceObject`)

## Decision

**We will use library types directly from `openapi3-ts` and other source libraries.**

### Principles

1. **Import types directly** from `openapi3-ts`, `zod`, `tanu`, etc.
2. **Avoid complex type extractions** - no `Exclude<>`, `Extract<>`, `Pick<>` gymnastics on library types
3. **Don't redefine library concepts** - if the library has it, use it
4. **Accept union types** - if the spec allows `SchemaObject | ReferenceObject`, accept both
5. **Use type guards** from libraries when available

### When Custom Types Are Acceptable

Custom types are OK when:

- Representing **domain-specific concepts** not in libraries
- **Aggregating multiple library concepts** meaningfully (with justification)
- Creating **helper types** that genuinely simplify (must document why)

### Pattern: Type Guards Tied to Library Types

When we need runtime validation of library types, use this pattern:

```typescript
// 1. Extract the subset from library type (compiler validates)
import type { SchemaObject } from 'openapi3-ts';

type PrimitiveSchemaType = Extract<
  NonNullable<SchemaObject['type']>,
  'string' | 'number' | 'integer' | 'boolean' | 'null'
>;

// 2. Define literals tied to that type
const PRIMITIVE_SCHEMA_TYPES: readonly PrimitiveSchemaType[] = [
  'string',
  'number',
  'integer',
  'boolean',
  'null',
] as const;

// 3. Create type predicate that narrows from unknown
export function isPrimitiveSchemaType(value: unknown): value is PrimitiveSchemaType {
  if (typeof value !== 'string') return false;
  const typeStrings: readonly string[] = PRIMITIVE_SCHEMA_TYPES;
  return typeStrings.includes(value);
}
```

This pattern ensures:

- ✅ Compiler validates literals match library types at compile time
- ✅ Type guard actually narrows from `unknown` (real type narrowing)
- ✅ Refactoring safety: library type changes break our code visibly
- ✅ No boolean filters pretending to be type guards

### Examples

#### Good: Use Library Types Directly

```typescript
import type { SchemaObject, ReferenceObject, SchemaObjectType } from 'openapi3-ts';
import { isReferenceObject, isSchemaObject } from 'openapi3-ts';

// ✅ Accept union types as defined by the library
function processSchema(schema: SchemaObject | ReferenceObject): Result {
  if (isReferenceObject(schema)) {
    return handleRef(schema);
  }
  return handleSchema(schema);
}

// ✅ Use library's exact types
function getSchemaType(schema: SchemaObject): SchemaObjectType | SchemaObjectType[] | undefined {
  return schema.type; // Type matches library definition
}

// ✅ Use library's type guards
if (isSchemaObject(obj)) {
  // TypeScript now knows obj is SchemaObject
}
```

#### Bad: Custom Type Definitions

```typescript
// ❌ Redefining library enums
type PrimitiveType = 'string' | 'number' | 'integer' | 'boolean' | 'null';

// ❌ Complex extractions
type SingleType = Exclude<SchemaObject['type'], unknown[] | undefined>;

// ❌ Claiming narrower types than reality
function handleItems(items: SchemaObject): Result {
  // Actually receives SchemaObject | ReferenceObject!
}

// ❌ Boolean filter pretending to be a type guard
function isPrimitive(type: SchemaObject['type']): boolean {
  // Input is already typed! This provides NO type narrowing
  return type === 'string' || type === 'number';
}
```

## Consequences

### Positive

✅ **Accuracy**: Types match the actual library definitions  
✅ **Maintenance**: Library updates automatically propagate to our code  
✅ **Simplicity**: Less code, less complexity  
✅ **Correctness**: Can't claim narrower types than reality  
✅ **Refactoring safety**: Type changes in libraries cause visible breaks  
✅ **Team alignment**: Everyone uses the same type definitions

### Negative

⚠️ **Union types**: May need to handle `SchemaObject | ReferenceObject` in more places  
⚠️ **Less control**: Can't "fix" library type issues without upstream changes  
⚠️ **Learning curve**: Team must learn library type structures

### Mitigation

- **Use type guards** (`isReferenceObject`, `isSchemaObject`) to narrow unions
- **Document patterns** in RULES.md for team reference
- **Report issues** to upstream libraries when types are incorrect
- **Helper functions** can wrap complex type handling

## Before & After

### Before

```typescript
// Custom types
type PrimitiveType = "string" | "number" | "integer" | "boolean" | "null";
const primitiveTypeList: readonly PrimitiveType[] = [...];

// Boolean filter (not a real type guard)
function isPrimitiveType(type: SchemaObject["type"]): boolean {
    return primitiveTypeList.includes(type as any);
}

// Claimed narrower types than reality
function resolveAdditionalPropertiesType(
    additionalProperties: SchemaObject["additionalProperties"],
    convertSchema: (schema: SchemaObject) => unknown // ❌ Actually SchemaObject | ReferenceObject
): ...
```

### After

```typescript
// Use library types with Extract
import type { SchemaObject } from "openapi3-ts";

type PrimitiveSchemaType = Extract<
    NonNullable<SchemaObject["type"]>,
    "string" | "number" | "integer" | "boolean" | "null"
>;

const PRIMITIVE_SCHEMA_TYPES: readonly PrimitiveSchemaType[] = [...] as const;

// Proper type guard from unknown
export function isPrimitiveSchemaType(value: unknown): value is PrimitiveSchemaType {
    if (typeof value !== "string") return false;
    const typeStrings: readonly string[] = PRIMITIVE_SCHEMA_TYPES;
    return typeStrings.includes(value);
}

// Accept union types as defined by library
function resolveAdditionalPropertiesType(
    additionalProperties: SchemaObject["additionalProperties"],
    convertSchema: (schema: SchemaObject | ReferenceObject) => unknown // ✅ Accurate
): ...
```

## Related Decisions

- [ADR-003: Type Predicates Over Boolean Filters](./ADR-003-type-predicates-over-boolean-filters.md) - How to create type guards
- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Validates against spec

## References

- RULES.md Section: "Defer Type Definitions to Source Libraries"
- Implementation: `lib/src/utils.ts:60-76`
- Implementation: `lib/src/openApiToTypescript.helpers.ts`
- Tests: `lib/src/utils.test.ts`
- Tests: `lib/src/openApiToTypescript.helpers.test.ts`

## Commit

- `ac70bdc` refactor: use library types, proper type guards
