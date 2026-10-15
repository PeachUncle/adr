# ADR-001: Fail Fast on OpenAPI Spec Violations

## Status

**Accepted** - October 24, 2025

## Context

When processing OpenAPI specifications, we encountered various malformed or spec-non-compliant documents. We had a choice:

1. **Be lenient**: Attempt to work around spec violations, apply heuristics, or silently ignore issues
2. **Fail fast**: Throw clear errors when specs don't conform to the standard

### The Problem

Real-world OpenAPI specs sometimes violate the official specification due to:

- Manual editing errors
- Tooling bugs
- Misunderstanding of the spec
- Copy-paste from incorrect examples

### Forces at Play

**For lenient handling:**

- Users might appreciate "it just works"
- Reduces friction in adoption
- Allows processing imperfect specs

**Against lenient handling:**

- Hides real problems in API specifications
- Creates unpredictable behavior
- Makes debugging harder
- Can lead to incorrect client generation
- Perpetuates bad practices

### Example Cases

1. **`MediaType.$ref` at wrong level:**

   ```typescript
   // ❌ WRONG (spec violation)
   parameter: {
     content: {
       "*/*": { $ref: "#/components/schemas/test2" }
     }
   }

   // ✅ CORRECT (per OAS spec lines 603-615)
   parameter: {
     content: {
       "*/*": {
         schema: { $ref: "#/components/schemas/test2" }
       }
     }
   }
   ```

2. **Schema as null:**

   ```typescript
   // ❌ WRONG
   { schema: null }

   // ✅ CORRECT
   { schema: { type: "string", nullable: true } }
   ```

3. **Parameter without schema or content:**

   ```typescript
   // ❌ WRONG (violates SchemaXORContent constraint)
   { name: "param1", in: "query" }

   // ✅ CORRECT
   { name: "param1", in: "query", schema: { type: "string" } }
   ```

## Decision

**We will fail fast with helpful error messages when encountering spec violations.**

### Implementation Principles

1. **Validate against the official OpenAPI specification**
2. **Throw errors immediately** when violations are detected
3. **Provide helpful error messages** that include:
   - What went wrong
   - Why it's a problem
   - Reference to the spec section
   - Example of correct usage

### Error Message Template

```typescript
throw new Error(
  `Invalid OpenAPI specification: [what's wrong]. ` +
    `[why it matters]. ` +
    `See: [spec URL]#[section]`,
);
```

### Example Implementation

```typescript
// In zodiosEndpoint.operation.helpers.ts
if (!paramSchema) {
  throw new Error(
    `Invalid OpenAPI specification: Could not resolve schema for parameter "${paramItem.name}" (in: ${paramItem.in}). ` +
      `This may indicate a missing or invalid $ref target.`,
  );
}

// In openApiToZod.ts
throw new Error(
  $schema === null
    ? "Invalid OpenAPI specification: Schema cannot be null. Use 'nullable: true' to indicate null values."
    : 'Schema is required',
);
```

## Consequences

### Positive

✅ **Clear boundaries**: Users know exactly what's supported  
✅ **Better error discovery**: Spec violations are caught early  
✅ **Predictable behavior**: No guesswork about how edge cases are handled  
✅ **Improved spec quality**: Users are motivated to fix their specs  
✅ **Easier maintenance**: No complex workaround logic  
✅ **Better documentation**: Error messages serve as inline documentation

### Negative

⚠️ **Strictness**: Users with malformed specs must fix them first  
⚠️ **Initial friction**: May require users to update their OpenAPI specs  
⚠️ **Support requests**: Users might ask for lenient handling

### Mitigation

- Provide **clear, actionable error messages** with spec references
- Offer **examples of correct patterns** in error messages
- Consider a **validation mode** that reports all errors without failing (future enhancement)
- Maintain **comprehensive compliance tests** to ensure our interpretation is correct

## Related Decisions

- [ADR-011: AJV for Runtime OpenAPI Validation](./ADR-011-ajv-runtime-validation.md) - Uses official schemas to validate
- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Ensures type accuracy

## References

- OpenAPI 3.0.3 Specification: https://spec.openapis.org/oas/v3.0.3
- OpenAPI 3.1.0 Specification: https://spec.openapis.org/oas/v3.1.0
- Implementation: `lib/src/zodiosEndpoint.operation.helpers.ts:73-83`
- Implementation: `lib/src/openApiToZod.ts:36-42`
- Tests: `lib/tests/param-invalid-spec.test.ts`
- Tests: `lib/tests/openapi-spec-compliance.test.ts`

## Commit

- `6d43201` feat(validation): enforce strict OpenAPI spec compliance
