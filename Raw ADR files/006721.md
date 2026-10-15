# ADR 001: Longhands Only - No Shorthand Support

**Status:** ✅ ACCEPTED  
**Date:** 2025-11-13  
**Deciders:** Core Team

---

## Decision

**We implement ONLY longhand CSS properties. We do NOT support shorthands. Ever.**

## Context

CSS has two types of properties:

- **Longhands:** Atomic properties (`background-color`, `padding-top`)
- **Shorthands:** Expand to multiple longhands (`background`, `padding`)

Other systems blur this boundary. We don't.

## The Principle

**We ONLY support what we register in `PROPERTY_DEFINITIONS`.**

If it's registered → we support it.  
If it's not registered → we don't support it.

**No exceptions. No special cases. No utilities for "maybe later."**

## Examples

```typescript
// ✅ WE SUPPORT (longhands)
background - color;
background - image;
padding - top;
padding - right;
border - top - width;
border - top - style;

// ❌ WE DON'T SUPPORT (shorthands)
background;
padding;
border;
border - top;
```

## Rationale

1. **Clarity:** What's registered is what exists
2. **Type Safety:** `PROPERTY_DEFINITIONS` is single source of truth
3. **Simplicity:** No expansion logic needed
4. **Focus:** ~50 critical longhands vs 200+ properties with shorthands

## Consequences

### Positive

- ✅ Type system matches runtime exactly
- ✅ Clear scope and boundaries
- ✅ Simpler implementation
- ✅ No ambiguity

### Constraints

- ⚠️ Users must use longhands
- ⚠️ No shorthand parsing/expansion

## Violations

**ANY of these violate this decision:**

- Directory named `utilities/` for shorthand parsing
- Documentation suggesting shorthand support
- Code parsing shorthand properties
- References to `b_short` package
- "Maybe we support shorthands later" comments

**Action:** Delete immediately. No discussion.

## Historical Context

`background-position` taught us this lesson. It's a shorthand that expands to `background-position-x` and `background-position-y`.

We learned: implement the longhands.

Later, a `utilities/` directory was created with 500+ lines suggesting we support shorthands.

**This was architectural debt.** It was deleted 2025-11-13.

## Enforcement

This decision is enforced by:

1. **Code:** Only longhands in `PROPERTY_DEFINITIONS`
2. **Tests:** Integrity tests verify no shorthand references
3. **Reviews:** Any shorthand suggestion is rejected
4. **Documentation:** AGENTS.md states principle clearly

## Related

- `AGENTS.md` - Core values and principles
- `docs/SESSION_HANDOVER.md` - We only support what we register

---

**This decision is permanent and non-negotiable.**
