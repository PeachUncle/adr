# ADR-003: Type Predicates Over Boolean Filters

## Status

**Accepted** - October 23, 2025

## Context

TypeScript supports type narrowing through type predicates (functions that return `value is Type`). However, it's easy to create functions that _look_ like type guards but don't actually narrow types.

### The Problem

The original codebase had "boolean filters" that looked like type guards but provided no type narrowing:

```typescript
// ❌ Boolean filter - provides NO type narrowing
function isPrimitiveType(type: SchemaObject["type"]): boolean {
    return type === "string" || type === "number" || ...;
}

// Usage: TypeScript doesn't know the type is narrowed!
if (isPrimitiveType(schema.type)) {
    // schema.type is still SchemaObject["type"], not narrowed
}
```

### The Forces

**For boolean filters:**

- Simpler to write (no `is` keyword)
- Works at runtime
- Familiar pattern

**Against boolean filters:**

- No compile-time type narrowing
- Misleading function name (`is*` implies type guard)
- Loses TypeScript's type safety benefits
- Requires type assertions elsewhere

## Decision

**We will use proper type predicates with the `is` keyword that narrow from `unknown` to a specific type.**

### Requirements for Type Predicates

1. **Use `is` keyword**: `value is Type`
2. **Accept `unknown` input**: Real type narrowing starts from `unknown`
3. **Tie to library types**: Use `Extract<>` to validate against source types
4. **Runtime validation**: Actually check the value at runtime

### Pattern

```typescript
// 1. Extract the subset from library type (compiler validates)
type MySubset = Extract<LibraryType, 'foo' | 'bar'>;

// 2. Define literals tied to that type
const MY_VALUES: readonly MySubset[] = ['foo', 'bar'] as const;

// 3. Create type predicate that narrows from unknown
export function isMySubset(value: unknown): value is MySubset {
  if (typeof value !== 'string') return false;
  return (MY_VALUES as readonly string[]).includes(value);
}
```

### Examples

#### Good: Proper Type Predicates

```typescript
import type { SchemaObject } from 'openapi3-ts';

// ✅ Proper type guard - tied to library type with Extract
type PrimitiveSchemaType = Extract<
  NonNullable<SchemaObject['type']>,
  'string' | 'number' | 'integer' | 'boolean' | 'null'
>;

const PRIMITIVE_SCHEMA_TYPES: readonly PrimitiveSchemaType[] = [
  'string',
  'number',
  'integer',
  'boolean',
  'null',
] as const;

export function isPrimitiveSchemaType(value: unknown): value is PrimitiveSchemaType {
  if (typeof value !== 'string') return false;
  const typeStrings: readonly string[] = PRIMITIVE_SCHEMA_TYPES;
  return typeStrings.includes(value);
}

// Usage: TypeScript knows the type is narrowed!
if (isPrimitiveSchemaType(schema.type)) {
  // schema.type is now PrimitiveSchemaType
  // "string" | "number" | "integer" | "boolean" | "null"
}
```

```typescript
// ✅ Type guard from existing library
import { isReferenceObject } from 'openapi3-ts';

if (isReferenceObject(obj)) {
  // obj is now ReferenceObject
  console.log(obj.$ref);
}
```

#### Bad: Boolean Filters

```typescript
// ❌ Boolean filter - no type narrowing
function isPrimitiveType(type: SchemaObject["type"]): boolean {
    // Input is already typed! This provides NO type narrowing
    return type === "string" || type === "number" || ...;
}

// ❌ Performative type predicate - not meaningful
function isObject(obj: unknown): obj is Record<string, unknown> {
    return typeof obj === "object" && obj !== null;
    // Record<string, unknown> is basically 'any' - not useful
}

// ❌ Type predicate with already-typed input
function isString(value: string | number): value is string {
    return typeof value === "string";
    // Should accept `unknown`, not pre-narrowed union
}
```

## Consequences

### Positive

✅ **Type safety**: TypeScript can narrow types automatically  
✅ **Fewer assertions**: Don't need `as` casts after checks  
✅ **Compile-time validation**: Literals validated against library types  
✅ **Refactoring safety**: Type changes break code visibly  
✅ **Intent clarity**: Function signature declares its purpose  
✅ **Reusability**: Can use in different contexts safely

### Negative

⚠️ **More verbose**: Requires `is` keyword and careful typing  
⚠️ **Learning curve**: Team must understand type predicates  
⚠️ **Runtime overhead**: Still need runtime checks

### Mitigation

- **Document pattern** in RULES.md
- **Provide examples** in ADRs
- **Code reviews** catch boolean filters
- **Lint rules** can help detect missing type predicates

## Why `unknown` Input?

Type predicates that accept already-narrowed inputs defeat the purpose:

```typescript
// ❌ BAD: Input is already narrowed
function isString(value: string | number): value is string {
  return typeof value === 'string';
}

// ✅ GOOD: Input is unknown, provides real narrowing
function isString(value: unknown): value is string {
  return typeof value === 'string';
}
```

**Exceptions:**

- **Public API type guards** where the input type is part of the contract
- **Discriminated union narrowing** where you're narrowing within a known set

## Before & After

### Before

```typescript
// Boolean filter
const primitiveTypeList: readonly string[] = ['string', 'number', 'integer', 'boolean', 'null'];

function isPrimitiveType(type: SchemaObject['type']): boolean {
  return primitiveTypeList.includes(type as any);
}

// Usage requires type assertion
if (isPrimitiveType(schema.type)) {
  const narrowed = schema.type as PrimitiveType; // ❌ Manual assertion!
}
```

### After

```typescript
// Proper type predicate
import type { SchemaObject } from 'openapi3-ts';

type PrimitiveSchemaType = Extract<
  NonNullable<SchemaObject['type']>,
  'string' | 'number' | 'integer' | 'boolean' | 'null'
>;

const PRIMITIVE_SCHEMA_TYPES: readonly PrimitiveSchemaType[] = [
  'string',
  'number',
  'integer',
  'boolean',
  'null',
] as const;

export function isPrimitiveSchemaType(value: unknown): value is PrimitiveSchemaType {
  if (typeof value !== 'string') return false;
  const typeStrings: readonly string[] = PRIMITIVE_SCHEMA_TYPES;
  return typeStrings.includes(value);
}

// Usage: TypeScript automatically narrows!
if (isPrimitiveSchemaType(schema.type)) {
  // schema.type is now PrimitiveSchemaType - no assertion needed!
}
```

## Related Decisions

- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Provides the library types to tie to
- [ADR-004: Pure Functions and Single Responsibility](./ADR-004-pure-functions-single-responsibility.md) - Type predicates are pure functions

## References

- RULES.md Section: "Type Guards Over Assertions"
- Implementation: `lib/src/utils.ts:60-76`
- Tests: `lib/src/utils.test.ts:12-49`
- TypeScript Handbook: [Narrowing - Type Predicates](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates)

## Commit

- `ac70bdc` refactor: use library types, proper type guards
