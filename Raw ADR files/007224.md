# ADR-005: Enum Complexity is Constant Regardless of Size

## Status

**Accepted** - October 24, 2025

## Context

The `getSchemaComplexity` function calculates a complexity score for OpenAPI schemas to determine whether they should be inlined or extracted to a named variable. During Phase 1c, we encountered a regression where enum complexity was being calculated as `2 + enum.length`, causing large enums to be extracted when they should have been inlined.

### The Problem

**Original behavior** (correct):

```typescript
// Small enum: complexity = 2 (inlined)
{ type: "string", enum: ["a", "b"] }

// Large enum: complexity = 2 (inlined)
{ type: "string", enum: [/* 100 values */] }
```

**Regression** (incorrect):

```typescript
// Small enum: complexity = 2 + 2 = 4 (extracted!)
{ type: "string", enum: ["a", "b"] }

// Large enum: complexity = 2 + 100 = 102 (extracted!)
{ type: "string", enum: [/* 100 values */] }
```

### Forces at Play

**For variable complexity (based on enum size):**

- Intuitive: more values → more complex
- Reflects code generation size
- Penalizes very large enums

**Against variable complexity:**

- **Enum is an enum** whether it has 2 or 100 values
- Generated Zod code size doesn't grow linearly with enum values
- Breaks existing snapshot tests
- Changes inlining behavior unexpectedly

### Why Constant Complexity is Correct

1. **Conceptual simplicity**: An enum is one concept, not N concepts
2. **Zod generation**: `z.enum(["a", "b"])` vs `z.enum([...100 items])` - both are one line
3. **Consistent threshold**: Small enums should inline, size doesn't change that
4. **Spec alignment**: OpenAPI doesn't consider enum size for complexity

## Decision

**Enum complexity is constant (2 total) regardless of the number of values.**

### Formula

```typescript
// For enum with type
complexity = complexityByType(type) + complexityByComposite("enum")
           = 1 (type) + 1 (enum) = 2

// For enum without type
complexity = 1 (base enum) + 1 (enum composite) = 2
```

### Implementation

```typescript
if (isPrimitiveSchemaType(schema.type)) {
  if (schema.enum) {
    return (
      current +
      complexityByType(schema as SchemaObject & { type: PrimitiveSchemaType }) +
      complexityByComposite('enum')
      // NOTE: We intentionally do NOT add enum.length here
      // Rationale: An enum is an enum whether it has 2 or 100 values
      // The base complexity remains constant to ensure inlining behavior
    );
  }
  return current + complexityByType(schema as SchemaObject & { type: PrimitiveSchemaType });
}

// Handle enum without explicit type
if (schema.enum && !schema.type) {
  return current + complexityByComposite('enum') + 1;
  // 1 for base enum declaration + 1 for enum composite = 2 total
}
```

## Test-Driven Development Approach

We used TDD to define and validate the correct behavior:

### 1. Created 21 unit tests

```typescript
describe('schema-complexity: enum calculations', () => {
  describe('base enum complexity (without type)', () => {
    test('enum with 2 values should have complexity 2', () => {
      expect(getComplexity({ enum: ['a', 'b'] })).toBe(2);
    });

    test('enum with 10 values should have complexity 2', () => {
      expect(getComplexity({ enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] })).toBe(2);
    });

    test('enum with 100 values should have complexity 2', () => {
      const values = Array.from({ length: 100 }, (_, i) => `val${i}`);
      expect(getComplexity({ type: 'string', enum: values })).toBe(2);
    });
  });

  // ... 18 more tests covering edge cases
});
```

### 2. Verified against existing snapshots

All 283 existing tests continued to pass, proving backward compatibility.

### 3. Confirmed inlining behavior

```typescript
test('simple enum should inline (complexity < 4)', () => {
  const complexity = getComplexity({ type: 'string', enum: ['a', 'b', 'c'] });
  expect(complexity).toBeLessThan(4); // Will be inlined
});

test('enum with 100 values should still inline', () => {
  const values = Array.from({ length: 100 }, (_, i) => `val${i}`);
  const complexity = getComplexity({ type: 'string', enum: values });
  expect(complexity).toBeLessThan(4); // Even large enums inline
});
```

## Consequences

### Positive

✅ **Consistent behavior**: Enum size doesn't affect extraction decisions  
✅ **Simpler mental model**: "Enum = 2, always"  
✅ **Predictable inlining**: Small enums always inline  
✅ **Test coverage**: 21 unit tests document the behavior  
✅ **Backward compatible**: All existing snapshots pass  
✅ **Spec aligned**: Matches OpenAPI conceptual model

### Negative

⚠️ **Very large enums**: 1000-value enums still inline (but this is rare)  
⚠️ **Generated code size**: Large enums create long arrays (but still readable)

### Mitigation

If extremely large enums become a problem:

- Add a **separate threshold** for enum value count (e.g., > 50 values → always extract)
- Make it **opt-in** via configuration
- Document as a **known limitation** with workaround

## Edge Cases Covered

1. **Single-value enum**: Complexity = 2
2. **Empty enum** (invalid but handled): Complexity = 2
3. **Enum with null**: Complexity = 2
4. **Mixed type enum** (invalid but handled): Complexity = 2
5. **Enum in object properties**: Correctly adds to object complexity
6. **Enum in array items**: Correctly adds to array complexity
7. **Multiple enums in object**: Each adds 2 to complexity

## Before & After

### Before (Regression)

```typescript
// ❌ Adding enum.length
if (schema.enum) {
  return (
    current +
    complexityByType(schema as SchemaObject & { type: PrimitiveSchemaType }) +
    complexityByComposite('enum') +
    schema.enum.length // ❌ WRONG!
  );
}
```

Result: Enum with 3 values = 2 + 3 = 5 → **extracted** ❌

### After (Correct)

```typescript
// ✅ Constant complexity
if (schema.enum) {
  return (
    current +
    complexityByType(schema as SchemaObject & { type: PrimitiveSchemaType }) +
    complexityByComposite('enum')
    // NOTE: We intentionally do NOT add enum.length here
  );
}
```

Result: Enum with any number of values = 2 → **inlined** ✅ (if < 4)

## Related Decisions

- [ADR-004: Pure Functions and Single Responsibility](./ADR-004-pure-functions-single-responsibility.md) - Complexity calculation uses pure helpers

## References

- Implementation: `lib/src/schema-complexity.ts:40-52`
- Tests: `lib/src/schema-complexity.enum.test.ts` (21 tests)
- Session context: `.agent/SESSION_SUMMARY.md`

## Commits

- `f2445d2` feat(validation): fix enum complexity calculation using TDD
