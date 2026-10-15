# ADR 005: Property Field Precedence in Results and Issues

**Status:** Accepted
**Date:** 2025-11-15
**Context:** Session audit of feedback items

---

## Context

Both `ParseResult`/`GenerateResult` and individual `Issue` objects have an optional `property` field:

```typescript
type ParseResult<T> = {
  ok: boolean;
  property?: string; // Top-level property name
  value?: T;
  issues: Issue[]; // Each issue may have its own property field
};

interface Issue {
  property?: string; // Issue-specific property name
  // ...
}
```

This dual presence creates ambiguity: when both are set, which one should consumers trust?

## Decision

**Issue.property takes precedence over Result.property.**

### Rules

1. **Issue.property (if set)** - Use this value. It's the most specific context.
   - Example: Nested color parser sets `issue.property = "color"` when parsing a gradient color stop
2. **Result.property (if set)** - Fallback for issues without specific property.
   - Example: Top-level `"background-image"` stamps all issues from nested parsers that don't set property
3. **Neither set** - Generic/reusable parser with no property context (rare)

### Implementation Pattern

The `stampIssues()` utility in `b_declarations/src/generator.ts` already implements this correctly:

```typescript
function stampIssues(issues: Issue[], property: string): Issue[] {
  return issues.map((issue) => (issue.property ? issue : { ...issue, property }));
}
```

**Key insight:** Only stamp issues that DON'T already have a property field.

## Rationale

### Why Issue.property wins

1. **Specificity** - Closer to the actual error source
2. **Nested parsers** - Color parser inside gradient inside background-image should report "color" error, not "background-image" error
3. **Debuggability** - More precise property name helps developers locate the issue faster

### Why Result.property exists

1. **Fallback stamping** - Declarative layer can annotate all issues from generic parsers
2. **Context propagation** - Multi-value parsers can tag results with property name
3. **Error aggregation** - When combining multiple parse results, top-level property provides context

## Examples

### Example 1: Nested Color Error

```typescript
// User input: background-image: linear-gradient(notacolor, blue)
const result = parseBackgroundImage("linear-gradient(notacolor, blue)");

// Gradient parser calls Color.parse("notacolor")
// Color.parse() returns: { property: "color", issues: [...] }
// Top-level sets: { property: "background-image", issues: [...] }

// Final issue should report:
{
  property: "color",  // More specific - helps user fix "notacolor"
  message: "Unknown named color 'notacolor'"
}
```

### Example 2: Generic Parser Without Context

```typescript
// Reusable angle parser has no property knowledge
const result = Angle.parse("invalid");
// Returns: { property: undefined, issues: [{ property: undefined, ... }] }

// Declaration layer stamps it:
stampIssues(result.issues, "transform");
// Result: [{ property: "transform", ... }]
```

### Example 3: Multi-Value Parser

```typescript
createMultiValueParser({
  propertyName: "background-size", // Stamps result.property
  itemParser: (ast) => parseBackgroundSize(ast), // May set issue.property
});

// Result.property = "background-size" (fallback)
// Issue.property = "background-size" OR more specific nested property
```

## Consequences

### Positive

- Clear precedence rule prevents ambiguity
- Enables precise error reporting in nested contexts
- Backward compatible with existing code

### Negative

- Two sources of truth for property name (unavoidable with nested parsers)
- Developers must understand stamping pattern

### Neutral

- No code changes required - pattern already implemented correctly
- Documentation clarifies existing behavior

## See Also

- `packages/b_types/src/result/parse.ts` - ParseResult definition
- `packages/b_types/src/result/issue.ts` - Issue definition
- `packages/b_declarations/src/generator.ts` - stampIssues() implementation
- ADR 002: Rich Error Messaging - Original issue system design
