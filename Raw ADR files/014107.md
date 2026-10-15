# ADR-001: Design System Structure

**Status:** Accepted
**Date:** 2025-01-13
**Phase:** Phase 1 - Foundation & Design System

## Context

The Quarterly Planner requires a consistent, maintainable design system that works across web and desktop platforms. We needed to decide on:

1. How to organize design tokens (colors, typography, spacing)
2. CSS architecture approach
3. Module structure for components
4. How to ensure design consistency across the application

## Decision

We adopted a **CSS Design Tokens** approach with the following structure:

### 1. Design Tokens via CSS Variables

All design tokens are defined as CSS custom properties in `/assets/styling/theme.css`:

```css
:root {
  --color-background-primary: #1a1a1a;
  --spacing-2: 8px;
  --font-size-base: 13px;
  /* etc. */
}
```

**Benefits:**
- Centralized theme definition
- Easy to override for future light mode support
- No build step required for theme changes
- Works natively in browsers and Dioxus desktop
- Can be dynamically modified at runtime if needed

### 2. Module Organization

Components are organized into three layers:

```
src/components/
├── ui/          # Atomic components (Button, Badge, Input, GridCell)
├── layout/      # Layout components (TopNav, ViewContainer)
└── views/       # Page-level views (RoadmapView, AllocationView)
```

**Rationale:**
- Clear separation of concerns
- UI components are reusable and framework-agnostic
- Views compose UI components and connect to state
- Layout components handle application shell

### 3. Apple-Inspired Dark Mode Design

We chose a dark-first design system inspired by Apple's design language:

- Dark backgrounds (#1a1a1a, #242424)
- Subtle borders and shadows
- High contrast text
- Consistent 4px spacing system
- System font stack prioritizing SF Pro

**Rationale:**
- Reduces eye strain for users working on planning for extended periods
- Professional appearance suitable for engineering management tools
- Clear visual hierarchy through subtle contrast
- Matches modern developer tool aesthetics

### 4. Component-First CSS

CSS is organized alongside components in a single `main.css` file during early phases, with clear section comments:

```css
/* ============================================
   BUTTON COMPONENT
   ============================================ */
```

**Rationale:**
- Single CSS file is easier to manage in early development
- Clear section boundaries make it easy to split later if needed
- No CSS-in-JS complexity or runtime overhead
- Better for performance (single CSS file, no JS parsing)

## Alternatives Considered

### 1. CSS-in-JS (Styled Components / Emotion)

**Rejected because:**
- Adds runtime overhead
- Requires additional dependencies
- More complex build setup
- Harder to override styles for theming
- Not idiomatic for Dioxus

### 2. Tailwind CSS

**Rejected because:**
- Verbose class names reduce readability
- Harder to maintain consistent design tokens
- Build step complexity
- Not as natural for component-based architecture
- Would make semantic class names harder

### 3. SCSS/SASS

**Rejected because:**
- Adds build step complexity
- CSS custom properties provide sufficient theming
- Not necessary with modern CSS features
- Additional tooling dependency

### 4. Light Mode First

**Rejected because:**
- Target users (engineering managers) often prefer dark interfaces
- Easier to add light mode later than to design for both simultaneously
- Dark mode is now expected in developer tools

## Consequences

### Positive

- **Fast development**: No build step for CSS changes
- **Maintainable**: Centralized design tokens make global changes easy
- **Flexible**: Easy to add light mode by providing alternate CSS variable values
- **Performant**: Single CSS file, no runtime CSS generation
- **Consistent**: Design tokens ensure visual consistency
- **Platform agnostic**: Works identically on web and desktop

### Negative

- **Single CSS file**: As application grows, main.css could become large (mitigated by clear section organization)
- **No scoped styles**: Need to be careful about class name collisions (mitigated by BEM-like naming)
- **Dark mode only**: Light mode will require additional work (acceptable for MVP)

### Neutral

- **Manual theme management**: No automatic theme generation, but provides full control
- **CSS expertise required**: Team needs to understand CSS custom properties and modern CSS

## Future Considerations

1. **Light Mode**: Add light mode by providing alternate CSS custom properties based on user preference
2. **CSS Splitting**: If `main.css` exceeds ~2000 lines, split into separate files (theme.css, components.css, views.css)
3. **Component Variants**: Consider CSS modules or styled components if component variants become too complex
4. **Design System Library**: If we extract components to a library, reconsider CSS architecture

## References

- Design specification: `docs/ui-design.md`
- CSS design tokens: `assets/styling/theme.css`
- Component reference: `docs/component-reference.md`
- Apple Human Interface Guidelines (inspiration for dark mode)
