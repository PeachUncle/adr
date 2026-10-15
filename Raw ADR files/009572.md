# ADR-0002: Component Composition Pattern (H1-H6 Delegation)

## Status

Accepted

## Date

2025-11-09

## Context

The project uses semantic HTML headings (H1-H6) extensively throughout the site. Requirements include:
- Consistent styling across all heading levels
- Accessibility features (ARIA labels, semantic HTML)
- Multiple variants (default, accent, subtle)
- Type-safe props validation
- Maintainable codebase

Initial approaches considered:
1. **Duplicate components** (H1.astro, H2.astro, H3.astro, etc.) - Each with identical logic
2. **Single dynamic component** - Takes level as prop
3. **Hybrid composition pattern** - Individual components delegating to shared base

Option 1 would violate DRY principle. Option 2 loses type safety and autocomplete for specific heading levels. Option 3 provides best of both worlds.

## Decision

Implemented a **component composition pattern** where:

1. **Base component** `H.astro` contains all shared logic:
   - Dynamic heading tag generation (`h${level}`)
   - ARIA attributes handling
   - Variant styling system
   - Accessibility validation script
   - Centralized CSS styles

2. **Specific heading components** (H1.astro, H2.astro, etc.) are thin wrappers:
   ```astro
   ---
   import H from "./H.astro";
   export interface Props {
     // ... specific props for H1
   }
   ---
   <H level={1} {...Astro.props}>
     <slot />
   </H>
   ```

3. **Type safety** maintained through:
   - Each wrapper has its own Props interface
   - Compile-time validation of heading level
   - IDE autocomplete for specific heading components

## Consequences

### Positive

- **Single source of truth** for heading styles and behavior
- **Zero code duplication** - all logic in H.astro
- **Type-safe API** - Each H1-H6 component has proper TypeScript types
- **Better developer experience** - Autocomplete works with `<H1>`, `<H2>`, etc.
- **Maintainable** - Styling/behavior changes only need to be made in H.astro
- **Extensible** - Easy to add new variants or features
- **Consistent accessibility** - Runtime validation ensures all headings have accessible names

### Negative

- **Additional indirection** - Two-component chain (H1 → H)
- **Slightly more complex** to understand initially
- **Small performance overhead** - Extra component in render tree (negligible in practice)

### Neutral

- Requires developers to understand delegation pattern
- Total lines of code similar to duplicate approach, but organized better

## Implementation Details

### Base Component (H.astro)
```astro
---
interface Props {
  level: 1 | 2 | 3 | 4 | 5 | 6;
  id?: string;
  ariaLabel?: string;
  variant?: "default" | "accent" | "subtle";
}

const HeadingTag = `h${level}` as keyof HTMLElementTagNameMap;
---

<HeadingTag class:list={[...]} {...ariaProps}>
  <slot />
</HeadingTag>
```

### Wrapper Component (H1.astro)
```astro
---
import H from "./H.astro";
export interface Props {
  id?: string;
  // ... H1-specific props
}
---
<H level={1} {...Astro.props}>
  <slot />
</H>
```

## Alternatives Considered

### 1. Complete Duplication
**Rejected** - Violates DRY principle, ~500+ lines of duplicate code

### 2. Single Dynamic Component Only
```astro
<H level={1}>Title</H>
```
**Rejected** - Loses autocomplete, requires passing level every time, less semantic

### 3. CSS-only Approach
Use single `<Heading>` with level prop, rely only on CSS classes
**Rejected** - Doesn't solve semantic HTML issue, loses accessibility benefits

## Pattern Extension

This pattern has been successfully applied to other element families and should be used for:
- List components (ordered/unordered)
- Button variants
- Link types
- Any component family with shared behavior but type-specific APIs

## Related Decisions

- Component size guidelines (CLAUDE.md) - Composition helps keep files under 300 lines
- TypeScript best practices - Interfaces used for component props

## Notes

This is an excellent example of the **Open/Closed Principle** from SOLID:
- Open for extension (easy to add new heading levels or variants)
- Closed for modification (changes to base logic don't require touching wrappers)

The pattern demonstrates proper abstraction: complexity hidden in H.astro, simple API exposed through H1-H6.

## References

- `src/components/elements/H.astro`
- `src/components/elements/H1.astro` through `H6.astro`
- CLAUDE.md: Development Principles - SOLID Principles
