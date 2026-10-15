# ADR-004: CSS Validation Pattern - Check Warnings, Not Parse Success

**Status:** Accepted
**Date:** 2025-11-06
**Context:** Session 037

---

## Problem

When validating CSS using `csstree`, we cannot rely on parse success (`ok: true/false`) to determine if CSS is valid. This leads to false positives in both directions:

**False Positive (accepts invalid CSS):**

```typescript
const css = "conic-gradient(red, blue"; // missing closing )
const ast = csstree.parse(css, { context: "value" });
// Parses successfully! But CSS is incomplete/malformed
```

**False Negative (rejects valid CSS):**

```typescript
// Some valid CSS might fail to parse in certain contexts
// but would be valid in the full document
```

The issue: **css-tree is lenient** - it successfully parses partial/incomplete CSS because it's designed for resilient parsing (useful for editors, formatters, etc).

---

## Decision

**DO NOT key off `ok: true/false` status for validation.**

Instead, use this pattern:

1. Parse the CSS
2. Run validation (e.g., `csstree.lexer.matchProperty()`)
3. Check for `formattedWarning` or validation errors
4. Merge warnings into `issues` array
5. Return result with issues

### Implementation Pattern

```typescript
export function validateProperty(css: string, property: string) {
  const issues: Issue[] = [];

  try {
    const ast = csstree.parse(css, { context: "value" });
    const result = csstree.lexer.matchProperty(property, ast);

    // Don't check result.error directly
    // Instead, check for formattedWarning
    if (result.error?.formattedWarning) {
      issues.push({
        severity: "warning",
        code: "invalid-value",
        message: result.error.formattedWarning,
        prop: property,
      });
    }
  } catch (error) {
    // Catch actual parse failures
    issues.push({
      severity: "fatal",
      code: "syntax-error",
      message: extractMessage(error),
    });
  }

  return { issues };
}
```

### Key Points

1. **Parse success ≠ Valid CSS**
   - css-tree can parse incomplete syntax
   - We need semantic validation, not just syntactic

2. **Check `formattedWarning`**
   - This contains the actual validation errors
   - Merge these into your issues array

3. **Don't rely on boolean flags**
   - `ok: true/false` has false positives in both directions
   - Use the presence of warnings/errors instead

---

## Rationale

### Why css-tree is lenient

css-tree is designed for tools like:

- **Code editors** - need to parse incomplete code as you type
- **Formatters** - need to handle malformed input gracefully
- **Error recovery** - parser continues after errors

This is correct behavior for these use cases, but wrong for validation.

### Why we need semantic validation

```typescript
// Syntactically valid (parses), semantically invalid (incomplete)
"conic-gradient(red, blue"; // missing )
"conic-gradient(from, red, blue)"; // from without angle
"background: rgb(300, 0, 0)"; // out of range values
```

These all parse successfully, but are invalid CSS.

---

## Consequences

### Positive

✅ Catch incomplete syntax (missing parentheses, etc.)
✅ Catch semantic errors (invalid values, missing required parts)
✅ Clear separation: parse for structure, validate for correctness
✅ Consistent error handling across all parsers

### Negative

⚠️ More verbose validation code
⚠️ Need to understand css-tree validation API
⚠️ Different pattern than typical parser usage

---

## Related

- See `packages/b_parsers/src/color/color.ts` - hex color validation
- See `packages/b_parsers/src/gradient/conic.ts` - keyword validation
- See `src/lib/css/core/issues.ts` (b_style project) - `issuesFromValidationWarnings()`

---

## Examples

### Bad (before)

```typescript
function parse(css: string) {
  try {
    const ast = csstree.parse(css, { context: "value" });
    return { ok: true, value: ast }; // ❌ Assumes valid if parsed
  } catch (error) {
    return { ok: false, error };
  }
}
```

### Good (after)

```typescript
function parse(css: string) {
  const issues: Issue[] = [];

  try {
    const ast = csstree.parse(css, { context: "value" });
    const result = csstree.lexer.matchProperty(property, ast);

    // Check for validation warnings
    if (result.error?.formattedWarning) {
      issues.push(warning("invalid-value", result.error.formattedWarning));
    }

    // Can still return parsed result even with warnings
    return { value: ast, issues };
  } catch (error) {
    issues.push(fatal("syntax-error", extractMessage(error)));
    return { value: null, issues };
  }
}
```

---

## Implementation Checklist

When validating CSS:

- [ ] Parse with css-tree
- [ ] Run semantic validation (`lexer.matchProperty`, `lexer.matchType`, etc.)
- [ ] Check for `formattedWarning` in validation result
- [ ] Merge warnings into issues array
- [ ] Return result with issues
- [ ] **DO NOT** check `ok` boolean or `result.error` directly

---

## Notes

This pattern was discovered during Session 037 while fixing validation bugs. The "missing closing parenthesis" test failure revealed that parse success does not guarantee valid CSS.

**Key insight:** We cannot represent incomplete CSS without making assumptions, therefore we must reject it during validation, not just parsing.
