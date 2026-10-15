# ADR 002: Rich, Actionable Error Reporting

**Status:** Approved
**Date:** 2025-11-05
**Reviewers:** Development Team, Session 023
**Context:** Session 021-023 - Error Handling Improvements

---

## 1. Context

The current error handling system, based on a simple `Issue` structure (`{ code, message }`), is insufficient. It lacks the necessary detail to enable developers to quickly diagnose and fix problems.

- **For CSS Parsing:** Errors lack source context. A message like "Invalid angle value" is not actionable without knowing _where_ in the source CSS the invalid angle is located.
- **For IR Generation:** Errors are often cryptic. When Zod validation fails on an IR object, a message like "Expected string, received undefined" doesn't pinpoint the _cause_ of the error (e.g., a misspelled property name in the input IR).

This ADR proposes a phased enhancement of the `Issue` structure and error reporting mechanisms to provide rich, actionable context for both parsing and generation failures.

---

## 2. Decision

We will evolve our `Issue` structure and error reporting pipelines to provide developers with precise, contextual, and actionable feedback.

### The Unified `Issue` Structure

The core of this decision is to unify around a more expressive `Issue` interface. All new fields will be optional to maintain backward compatibility.

```typescript
// Proposed structure in packages/b_types/src/result/issue.ts
export interface Issue {
  code: IssueCode;
  severity: "error" | "warning" | "info";
  message: string;

  // --- Context Fields ---

  /** The CSS property associated with this issue, if applicable. */
  property?: string;

  /** A structured path to the problematic field within the IR. */
  path?: (string | number)[];

  /** A developer-friendly hint on how to resolve the issue. */
  suggestion?: string;

  /**
   * For CSS parsing errors, a pre-formatted string containing the source line,
   * context, and a pointer (^^^) to the error location.
   */
  sourceContext?: string;

  /** For type-related errors, the expected type or value. */
  expected?: string;

  /** For type-related errors, the actual type or value received. */
  received?: string;

  // --- Internal Fields (not exposed to users) ---

  /** Internal: location in source for error formatting */
  _location?: { offset: number; length: number };
}
```

### Phase 1: Rich Parser Errors (High Priority)

**Goal:** Integrate rich error formatting directly into the parsing pipeline with source-aware parsers.

**Refined Strategy:** The current `validate()` function is excellent for linting a whole stylesheet, but calling it for every single property value is inefficient. A better approach is to enhance our core parsers to be **source-aware**.

1. **Thread Source Context:** When `parseDeclaration` is called with a string, it should pass both the **value string** and track the **offset** in the original declaration string down to property-specific parsers.

2. **Report Errors with Location:** If a lower-level parser fails, it should include the offset and length of the problematic substring in the error's internal `_location` field.

3. **Format at the Top:** The top-level `parseDeclaration` function catches these errors and uses a utility (derived from `validate.ts`) to generate the `sourceContext` string just before returning the final `ParseResult`.

This avoids parsing the same string multiple times and keeps the source formatting logic contained at the API entry point.

**Example:**

```typescript
{
  code: "invalid-syntax",
  message: "Invalid hex color: must be 3, 4, 6, or 8 hex characters.",
  property: "color",
  sourceContext:
    "  1 | .my-class {\n" +
    "  2 |   color: #gg0000;\n" +
    "    |          ^^^^^^^\n" +
    "  3 | }"
}
```

### Phase 2: Rich Generator Errors (HIGHEST Priority)

**Goal:** Translate Zod `SafeParseError` objects into our rich `Issue` format. This has the highest ROI for improving the generator DX.

**Strategy:**

1. **Centralize Translation:** We use and enhance the `zodErrorToIssues` function in `b_utils`. This function is the single source of truth for converting a `ZodError` into an `Issue[]` array.

2. **Enforce Strictness:** All IR object schemas in `b_types` **must** use `.strict()`. ✅ **Complete (Session 023)**. This is non-negotiable as it's the primary mechanism for catching typos (e.g., `names` instead of `name`).

3. **Generator Implementation:** All `generate` functions begin with a `safeParse` call and use `zodErrorToIssues` to create the error result if validation fails. ✅ **Pattern established (Session 022)**.

**`zodErrorToIssues` Enhancement:**
This utility will be enhanced to populate the new `Issue` fields:

- `path` from `zodIssue.path`
- `expected`/`received` for `invalid_type` errors
- `suggestion` for `unrecognized_keys` errors (e.g., "Unrecognized key(s): 'names'. Did you mean 'name'?"), with Levenshtein distance for typo detection.

**Example:**

```typescript
{
  code: "unrecognized_keys",
  message: "Unrecognized key(s) in object: 'positon'",
  property: "background-image",
  path: [ "ir", "positon" ],
  suggestion: "Did you mean 'position'?",
  severity: "error"
}
```

### Phase 3: Path Propagation in Nested Calls (Medium Priority)

**Goal:** Ensure that error paths are correctly composed when parsers or generators call each other.

**Example Scenario:** `generateDeclaration` calls `generateBackgroundImage`, which calls `Generators.Gradient.generate`, which calls `Generators.Color.generate`. If the color is invalid, the path needs to be correctly assembled.

**Strategy:**

1. **Pass Down a `parentPath`:** Functions in the call chain accept an optional `GenerateContext` parameter containing `parentPath: (string | number)[]`.

2. **Prepend the Path:** When an error is created or a Zod error is translated, the `parentPath` is prepended to the `path` field of the resulting `Issue`.

**Example:**

```typescript
{
  code: "invalid_ir",
  message: "ir.layers[0].gradient.colorStops[1].color.g: Required",
  path: [ "ir", "layers", 0, "gradient", "colorStops", 1, "color", "g" ],
  expected: "CssValue",
  received: "undefined",
  severity: "error"
}
```

---

## 3. Consequences

### Positive

1. **Superior Developer Experience:** Errors are no longer questions; they are answers that pinpoint the exact location and nature of a problem.
2. **Reduced Debugging Time:** Visual context for parsers and deep paths for generators eliminate guesswork.
3. **Improved Maintainability:** A single, robust `Issue` structure simplifies error handling logic throughout the codebase.
4. **Actionable Suggestions:** "Did you mean X?" suggestions catch common typos automatically.

### Risks & Mitigations

1. **Implementation Complexity (Parser Context):** Threading source context through parsers can be complex.
   - **Mitigation:** Focus on passing substring `offset` and `length` information at API boundaries only. The top-level function holds the full source and performs final formatting.

2. **Performance Overhead:** Error formatting could add latency.
   - **Mitigation:**
     - Format only on error path (success path unchanged)
     - Lightweight offset tracking during parsing
     - Zod validation is already fast and essential

3. **Breaking Changes:** New `Issue` fields change the structure.
   - **Mitigation:** All new fields are optional; existing code continues to work.

---

## 4. Implementation Plan

See detailed implementation plan: [`docs/sessions/023/ADR-002-IMPLEMENTATION-PLAN.md`](../../sessions/023/ADR-002-IMPLEMENTATION-PLAN.md)

### Immediate Actions

1. ✅ **Enhance `Issue` Type:** Update the interface in `b_types` with new optional fields
2. ✅ **Solidify Phase 2 Foundation (Session 022-023):**
   - Add `.strict()` to **all** Zod object schemas in `b_types`
   - Establish pattern: `safeParse` → `zodErrorToIssues` in generators

### Short-Term (Next 1-2 Sessions)

1. **Complete Phase 2:**
   - Enhance `zodErrorToIssues` with rich context (path, suggestion, expected/received)
   - Implement Levenshtein distance for "Did you mean" suggestions
   - Update all generators to use enhanced error translation

2. **Implement Phase 1:**
   - Create `formatSourceContext()` utility (derived from `validate.ts`)
   - Update `parseDeclaration` to be source-aware (track offsets)
   - Update property parsers to include location in errors
   - Format `sourceContext` at API boundary

### Medium-Term

1. **Implement Phase 3:**
   - Add `GenerateContext` parameter to generators
   - Thread `parentPath` through nested calls
   - Update error creation to prepend parent paths
   - Write integration tests for deeply nested errors

---

## 5. Timeline Estimate

- **Phase 1:** 3-4 hours (infrastructure + proof of concept + rollout)
- **Phase 2:** 2-3 hours (enhancement + Levenshtein + validation)
- **Phase 3:** 2-3 hours (interface updates + call site updates)

**Total:** 7-10 hours across 2-3 sessions

---

## 6. Success Criteria

### Quantitative

- ✅ All 944+ tests pass after each phase
- ✅ Zero performance regression on success path
- Error messages contain 2-5x more actionable detail

### Qualitative

- Errors show exact location in source (parsing)
- Errors show full path to problem (generation)
- Errors include "Did you mean X?" suggestions
- Users can fix errors without reading source code

---

## 7. References

- Existing validation: `packages/b_utils/src/parse/validate.ts`
- Issue structure: `packages/b_types/src/result/issue.ts`
- Zod documentation: https://zod.dev
- Implementation plan: `docs/sessions/023/ADR-002-IMPLEMENTATION-PLAN.md`
- Session 022: Multi-error collection + Zod standardization
- Session 023: Strict validation + structure cleanup

---

## 8. Appendix: Examples

### Parser Error (After Phase 1)

**Input:**

```typescript
parseDeclaration("color: #gg0000");
```

**Output:**

```typescript
{
  ok: false,
  issues: [{
    code: "invalid-syntax",
    message: "Invalid hex color: must be 3, 4, 6, or 8 hex characters",
    property: "color",
    sourceContext:
      "  1 | color: #gg0000;\n" +
      "    |        ^^^^^^^\n"
  }]
}
```

### Generator Error (After Phase 2)

**Input:**

```typescript
const color = { kind: "rgb", r: lit(255), positon: lit(128) };
RGB.generate(color);
```

**Output:**

```typescript
{
  ok: false,
  issues: [{
    code: "unrecognized_keys",
    message: "Unrecognized key(s) in object: 'positon'",
    path: ["positon"],
    suggestion: "Did you mean 'position'?",
    expected: "Valid keys: kind, r, g, b, alpha",
    severity: "error"
  }]
}
```

### Nested Error (After Phase 3)

**Input:**

```typescript
generateDeclaration({
  property: "background-image",
  value: {
    kind: "layers",
    layers: [
      {
        kind: "linear-gradient",
        colorStops: [
          { color: { kind: "rgb", r: lit(255) } }, // Missing g, b
        ],
      },
    ],
  },
});
```

**Output:**

```typescript
{
  ok: false,
  issues: [{
    code: "missing-required-field",
    message: "Missing required field at value.layers[0].colorStops[0].color.g",
    property: "background-image",
    path: ["value", "layers", 0, "colorStops", 0, "color", "g"],
    suggestion: "'g' is required in RGBColor",
    expected: "CssValue",
    received: "undefined"
  }]
}
```

---

**This ADR represents our commitment to exceptional developer experience through clear, actionable error messages.**
