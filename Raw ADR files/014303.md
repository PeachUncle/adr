# ADR-003: UI Kit Choice

**Status** Accepted

**Date** December 2025

**Last Review Date** January 2026

## Context

Building interactive components for this application requires proper focus management, keyboard navigation, and accessibility support. Initially, I attempted to build a custom UI kit from scratch without third-party libraries, but quickly realized that implementing these features correctly is complex and time-consuming.

Key requirements:

-   Proper focus management for complex components (autocomplete, select with multiple selection, inline-edit)
-   Keyboard navigation support
-   Customizability to match a custom Figma design system (colors, fonts, sizes)
-   Learning experience — understanding the challenges of building UI component libraries

While full screen reader support isn't a current priority, having a solid foundation for accessibility benefits keyboard users and future extensibility.

## Decision

Build a custom UI kit on top of **React Aria Components** (from Adobe Spectrum) with:

-   **React Aria** — behavior hooks with focus management and keyboard support
-   **React Stately** — state management hooks for complex components
-   **React Aria Components** — pre-built accessible components as a foundation
-   **Tailwind CSS 4** — utility-first styling
-   **Class Variance Authority (CVA)** — variant-based styling patterns
-   **Tailwind Merge** — className conflict resolution

## Options Considered

### 1. Custom UI Kit (No Libraries)

**Pros:**

-   Full control over implementation
-   No external dependencies

**Cons:**

-   Significant effort to implement proper focus management
-   Keyboard navigation is complex to get right
-   Accessibility requires deep expertise
-   Time-consuming for complex components

**Verdict:** Disqualified — too much effort for correct accessibility implementation

### 2. React Aria + React Stately (Selected)

**Pros:**

-   Headless/unstyled — complete control over appearance
-   Best-in-class accessibility from Adobe's team
-   Composable behavior and state hooks with clear separation of concerns
-   Architecture pattern: state hooks (logic) + behavior hooks (interactions/ARIA) + component (UI)
-   Can build complex components (autocomplete, multi-select, inline-edit) easily
-   Well-maintained with excellent documentation

**Cons:**

-   Steeper learning curve than ready-made component libraries
-   More boilerplate than drop-in solutions
-   Bundle size includes accessibility primitives

**Verdict:** Selected — best balance of flexibility and accessibility

### 3. shadcn/ui

**Pros:**

-   Beautiful default styling
-   Copy-paste components (owns the code)
-   Popular in the community

**Cons:**

-   Less flexibility for complex custom components
-   Built on Radix — less composable than React Aria hooks
-   Harder to customize deeply without fighting defaults

**Verdict:** Not selected — insufficient flexibility for custom requirements

### 4. Radix UI

**Pros:**

-   Headless primitives
-   Good accessibility
-   Popular choice

**Cons:**

-   Less composable than React Aria's hook-based approach
-   Harder to build custom complex components
-   Limited state management hooks compared to React Stately

**Verdict:** Not selected — React Aria's composability is superior for custom needs

### 5. Hero UI (formerly NextUI)

**Pros:**

-   Nice default styles
-   Built for Next.js

**Cons:**

-   Less customizable than headless solutions
-   Opinionated styling harder to override

**Verdict:** Not selected — too opinionated for custom design system

## Consequences

### Positive

-   **Full design control** — can implement exact Figma designs without fighting library defaults
-   **Excellent accessibility foundation** — React Aria handles focus management, keyboard navigation, ARIA attributes
-   **Composable architecture** — behavior hooks can be combined for complex custom components
-   **Learning value** — gained deep understanding of UI component library development challenges
-   **Keyboard users benefit** — even without full screen reader support, keyboard navigation works well
-   **Future-proof** — can add full a11y support later without architectural changes

### Negative

-   **Higher initial effort** — building custom components takes more time than using ready-made libraries
-   **Bundle size for landing page** — React Aria components are used on landing page where full accessibility isn't needed, bloating bundle size
-   **React Aria dependency spread** — currently React Aria is used in both `shared/ui` and `app` folders (ideally should be contained to shared layer)

## Mitigations

-   **Landing page bundle size** — consider creating "light" components with same styles but without React Aria for landing page
-   **React Aria containment** — consider extracting UI kit to separate package to enforce boundaries
-   **Documentation** — added conventions guide and this ADR to help future contributors

## Technical Details

### Stack

| Library                  | Purpose                         | Version |
| ------------------------ | ------------------------------- | ------- |
| react-aria-components    | Pre-built accessible components | ^1.11.0 |
| react-aria               | Behavior hooks                  | ^3.42.0 |
| react-stately            | State management hooks          | ^3.40.0 |
| tailwindcss              | Utility-first CSS               | ^4.0.9  |
| class-variance-authority | Variant-based styles            | ^0.7.0  |
| tailwind-merge           | Class conflict resolution       | ^2.5.3  |

### Component Structure

```
component-name/
├── component-name.tsx      # Main component
├── component-name.test.tsx # Tests (colocated)
├── index.ts                # Barrel export
└── components/             # Sub-components (if needed)
```

### Documentation

-   **Storybook** — visual documentation and interaction testing
-   **Convention Guide** — `docs/guides/ui-kit-conventions.md`

## Notes

-   Layout components not included — using Tailwind directly for layout (acceptable trade-off)
-   No component prop documentation (JSDoc) — could be improved
-   Consider lazy loading React Aria components for landing page optimization

## Related ADRs

-   [ADR-001: Frontend Framework Choice](./001-frontend-framework-choice.md)
-   [ADR-002: Frontend Architecture Design Choice](./002-frontend-architecture-design-choice.md)
