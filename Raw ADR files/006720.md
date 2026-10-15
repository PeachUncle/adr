# ADR-001: CSS Value Representation with Discriminated Unions

**Status:** Accepted
**Date:** 2025-11-04
**Deciders:** Session 008
**Context:** Building a spec-compliant CSS parser and generator system

---

## Context and Problem Statement

When designing the Intermediate Representation (IR) for CSS values, we face a fundamental question:

**How do we represent CSS values that can be literals, variables (`var()`), keywords (`none`), calc expressions, or future CSS syntax we don't know about yet?**

### The Challenge

CSS allows symbolic references and dynamic values in any position:

```css
/* All valid CSS */
lch(55 100 90)                           /* literals */
lch(55 var(--chroma) 90)                 /* variables */
lch(var(--l) var(--c) var(--h))          /* all variables */
lch(55 100 var(--hue, 270deg))           /* with fallback */
lch(none 100 90)                         /* keywords */
lch(calc(50% + 10) 100 90)               /* calc() */
```

Our initial schema approach failed:

```typescript
// ❌ WRONG - Can only hold computed values
export const lchColorSchema = z.object({
  kind: z.literal("lch"),
  l: z.number(), // Can't represent var(--l)!
  c: z.number(), // Can't represent none!
  h: z.number(), // Can't represent calc()!
  alpha: z.number().optional(),
});
```

### Core Insight

**A CSS parser's first job is to represent the _authored value_, not the _computed value_.**

We cannot and should not resolve `var(--value)` to a number at parse time because:

1. Custom property values are determined at **cascade time** by the browser
2. Values can change based on the element context
3. We're a **representation engine**, not a validation engine

---

## Decision Drivers

1. **Spec compliance** - Must represent all valid CSS Color Level 4 syntax
2. **Future-proof** - Must handle CSS features we don't know about yet (calc, future syntax)
3. **Type safety** - Maintain TypeScript safety without being restrictive
4. **Lossless** - Round-trip parse → generate should preserve authored values
5. **No validation** - Don't enforce value ranges (that's the browser's job)
6. **Developer experience** - Clear, intuitive API

---

## Considered Options

### Option 1: Single Type with Optional Fields ❌

```typescript
export const lchColorSchema = z.object({
  kind: z.literal("lch"),
  l: z.number().optional(),
  lVar: z.string().optional(),
  lKeyword: z.string().optional(),
  // ... repeat for c, h, alpha
});
```

**Rejected:** Confusing API, unclear which field to use, easy to create invalid states.

### Option 2: `data` Field Fallback ❌

```typescript
export const lchColorSchema = z.object({
  kind: z.literal("lch"),
  l: z.number(),
  c: z.number(),
  h: z.number(),
  data: z.string().optional(), // Raw CSS when we can't parse
});
```

**Rejected:** Loses all structure when any single value can't be parsed. Can't manipulate individual channels.

### Option 3: Discriminated Union (CssValue) ✅

```typescript
// Foundation type
type CssValue =
  | { kind: "literal"; value: number; unit?: string }
  | { kind: "variable"; name: string; fallback?: CssValue }
  | { kind: "keyword"; value: string };
// Extensible for future: calc, env(), etc.

// Color uses CssValue for all components
export const lchColorSchema = z.object({
  kind: z.literal("lch"),
  l: cssValueSchema,
  c: cssValueSchema,
  h: cssValueSchema,
  alpha: cssValueSchema.optional(),
});
```

**Accepted:** Best balance of flexibility, type safety, and clarity.

---

## Decision

**We will use discriminated unions (`CssValue`) as the foundation for representing all CSS values throughout the IR.**

### The `CssValue` Type

```typescript
// b_types/src/values/css-value.ts

export const literalValueSchema = z.object({
  kind: z.literal("literal"),
  value: z.number(),
  unit: z.string().optional(), // "deg", "%", "px", etc.
});

export const variableReferenceSchema = z.object({
  kind: z.literal("variable"),
  name: z.string(), // "--my-variable"
  fallback: z.lazy(() => cssValueSchema).optional(),
});

export const keywordValueSchema = z.object({
  kind: z.literal("keyword"),
  value: z.string(), // "none", "l", "c", etc.
});

export const cssValueSchema = z.union([literalValueSchema, variableReferenceSchema, keywordValueSchema]);

export type CssValue = z.infer<typeof cssValueSchema>;
```

### Updated Color Schema Example

```typescript
// All color components use CssValue
export const lchColorSchema = z.object({
  kind: z.literal("lch"),
  l: cssValueSchema,
  c: cssValueSchema,
  h: cssValueSchema,
  alpha: cssValueSchema.optional(),
});
```

### Generator Utility

```typescript
// b_utils/src/generate/css-value.ts

export function cssValueToCss(value: CssValue): string {
  switch (value.kind) {
    case "literal":
      return value.unit ? `${value.value}${value.unit}` : String(value.value);

    case "variable":
      if (value.fallback) {
        return `var(${value.name}, ${cssValueToCss(value.fallback)})`;
      }
      return `var(${value.name})`;

    case "keyword":
      return value.value;
  }
}
```

---

## Consequences

### Positive

✅ **Future-proof** - Can add new `CssValue` kinds (calc, env, etc.) without breaking existing code

✅ **Type-safe** - TypeScript enforces correct structure, impossible to create invalid IR

✅ **Flexible** - Handles literals, variables, keywords, nested fallbacks

✅ **Lossless** - Preserves all information from authored CSS

✅ **No validation** - Doesn't enforce value ranges, just structure

✅ **Composable** - Same pattern works for lengths, angles, percentages, etc.

✅ **Clear semantics** - Discriminated union makes the type explicit

### Negative

⚠️ **Breaking change** - Requires updating all existing types and generators

⚠️ **More verbose** - Tests must use object syntax instead of bare numbers:

```typescript
// Old
{ kind: "lch", l: 55, c: 100, h: 90 }

// New
{
  kind: "lch",
  l: { kind: "literal", value: 55 },
  c: { kind: "literal", value: 100 },
  h: { kind: "literal", value: 90 }
}
```

⚠️ **Migration effort** - All 8 color types + lengths, angles, etc. need updating

### Neutral

🔵 **Test count increases** - More comprehensive tests for each value type combination

🔵 **Generator complexity** - Need `cssValueToCss()` utility, but it's reusable

---

## Implementation Notes

### Phase 1: Foundation ✅ (Complete)

- Created `CssValue` type in `b_types/src/values/`
- Added 15 tests covering all `CssValue` variants
- Created `cssValueToCss()` utility in `b_utils`

### Phase 2: Proof of Concept ✅ (Complete)

- Updated `LCHColor` schema to use `CssValue`
- Updated LCH generator with 17 comprehensive tests
- Verified: literals, variables, keywords, mixed types all work

### Phase 3: Rollout (Next)

- Update remaining 7 color types (RGB, HSL, HWB, LAB, OKLAB, OKLCH, ColorFunction)
- Update all color generators
- Update all color tests
- Target: Remove 43 failing validation tests, add comprehensive new tests

### Phase 4: Expand (Future)

- Apply pattern to `Length`, `Angle`, `Percentage`
- Add `calc` support to `CssValue`
- Add `env()` support
- Consider: `clamp()`, `min()`, `max()`

---

## Examples

### Literal Values

```typescript
// Input IR
{
  kind: "lch",
  l: { kind: "literal", value: 55, unit: "%" },
  c: { kind: "literal", value: 100 },
  h: { kind: "literal", value: 90, unit: "deg" }
}

// Output CSS
"lch(55% 100 90deg)"
```

### Variable References

```typescript
// Input IR
{
  kind: "lch",
  l: { kind: "literal", value: 55 },
  c: { kind: "variable", name: "--chroma" },
  h: {
    kind: "variable",
    name: "--hue",
    fallback: { kind: "literal", value: 270, unit: "deg" }
  }
}

// Output CSS
"lch(55 var(--chroma) var(--hue, 270deg))"
```

### Keywords (none)

```typescript
// Input IR
{
  kind: "lch",
  l: { kind: "keyword", value: "none" },
  c: { kind: "literal", value: 100 },
  h: { kind: "literal", value: 90 }
}

// Output CSS
"lch(none 100 90)"
```

### Relative Color Syntax

```typescript
// Input IR
{
  kind: "lch",
  l: { kind: "keyword", value: "l" },     // From source color
  c: { kind: "keyword", value: "c" },
  h: { kind: "literal", value: 180 }      // Override hue
}

// Output CSS (in context of "from <color>")
"lch(l c 180)"
```

### Out-of-Range Values (No Validation!)

```typescript
// Input IR - invalid ranges but valid structure
{
  kind: "lch",
  l: { kind: "literal", value: -50 },     // Out of range
  c: { kind: "literal", value: 999 },     // Out of range
  h: { kind: "literal", value: 420 },     // > 360
  alpha: { kind: "literal", value: 2 }    // > 1
}

// Output CSS - passed through as-is
"lch(-50 999 420 / 2)"
// Browser will handle invalid values
```

---

## Validation Philosophy

**Key principle: We are a representation engine, not a validation engine.**

### What We DO Validate

✅ **Structure** - IR must have correct shape and required fields
✅ **Types** - Values must be numbers, strings, objects as appropriate
✅ **Discriminated union** - `kind` field must be valid

### What We DON'T Validate

❌ **Value ranges** - No min/max on numbers
❌ **Unit correctness** - Accept any unit string
❌ **CSS validity** - Not our job to check if CSS is "correct"

### Rationale

1. **CSS is constantly evolving** - Hard to keep up with spec changes
2. **Browser handles it** - Invalid CSS is parsed and handled by browser
3. **Use cases vary** - What's "invalid" in one context may be valid in another
4. **Developer freedom** - Don't second-guess how people use CSS
5. **Future-proof** - New CSS features work automatically

---

## Related Decisions

- **ADR-002** (Future): No value range validation in schemas
- **ADR-003** (Future): Alpha channel always explicit if defined
- **ADR-004** (Future): Modern CSS syntax (space-separated, slash for alpha)

---

## References

- [CSS Values and Units Module Level 4](https://drafts.csswg.org/css-values-4/)
- [CSS Color Module Level 4](https://drafts.csswg.org/css-color/)
- [CSS Variables (Custom Properties)](https://drafts.csswg.org/css-variables/)
- [css-tree approach to value representation](https://github.com/csstree/csstree)

---

## Notes

- This decision fundamentally changes how we represent CSS values
- It's the correct long-term architecture even though it requires migration effort
- The pattern is proven (css-tree uses similar approach)
- Extensible to handle future CSS features we haven't seen yet
- Maintains type safety while being flexible

**This is the foundation for a world-class CSS parser/generator system.**
