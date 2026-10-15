# ADR-003: Styling Approach (Mobile-First)

## Status

Accepted

## Context

Rule Bound must be:

- **Mobile-friendly**: Work seamlessly on phones and tablets
- **Accessible**: WCAG 2.1 AA compliant with proper contrast, sizing, etc.
- **Beautiful**: Modern, well-designed interface
- **Performant**: Fast loading and rendering
- **Maintainable**: Easy to update and extend styles

The app will be used both as a reference (quick lookups on mobile) and learning tool (potentially longer sessions on desktop). We need a styling solution that supports:

- Responsive, mobile-first design
- Design system/theming for consistency
- Accessibility features (contrast, focus states, etc.)
- TypeScript integration
- Component-scoped styling
- Dynamic theming (potentially dark mode)

## Options Considered

### 1. CSS Modules + PostCSS

- **Pros:**
  - Component-scoped styles
  - Standard CSS syntax
  - Build-time processing
  - Good Vite support
  - TypeScript declarations available
- **Cons:**
  - No built-in theming system
  - Requires custom setup for design tokens
  - More manual work for responsive design
  - Limited dynamic styling

### 2. Tailwind CSS

- **Pros:**
  - Utility-first approach
  - Mobile-first responsive design built-in
  - Excellent accessibility utilities
  - Highly performant (PurgeCSS)
  - Great TypeScript support
  - Easy to maintain consistency
  - Design tokens via config
  - Large ecosystem
- **Cons:**
  - Learning curve for utility-first approach
  - Can lead to long className strings
  - Some developers find it less "semantic"

### 3. Styled Components / Emotion

- **Pros:**
  - CSS-in-JS with full JavaScript power
  - Dynamic styling easy
  - TypeScript support
  - Theming built-in
- **Cons:**
  - Runtime overhead
  - Larger bundle size
  - Can impact performance
  - More complex build setup

### 4. Vanilla Extract

- **Pros:**
  - Zero-runtime CSS-in-TS
  - Type-safe styling
  - Great performance
- **Cons:**
  - Less mature ecosystem
  - Smaller community
  - Learning curve

## Decision

We will use **Tailwind CSS** as the primary styling solution.

**Key reasons:**

1. **Mobile-First**: Responsive utilities are mobile-first by default
2. **Accessibility**: Built-in utilities for focus rings, sr-only, contrast
3. **Performance**: PurgeCSS removes unused styles, minimal runtime cost
4. **Consistency**: Design tokens in `tailwind.config.ts` ensure consistency
5. **Productivity**: Rapid development with utility classes
6. **TypeScript**: Excellent editor support with IntelliSense
7. **Customization**: Easy to extend with custom utilities and plugins
8. **Documentation**: Comprehensive docs and large community

## Consequences

### Positive

- Fast development with utility classes
- Automatic responsive design with mobile-first breakpoints
- Built-in accessibility utilities (focus-visible, sr-only, etc.)
- Very small production bundle (only used classes)
- Consistent spacing, colors, typography via design tokens
- Easy to implement dark mode if needed
- Excellent editor support with autocomplete

### Negative

- Developers unfamiliar with Tailwind need to learn utility-first approach
- className strings can get long (mitigated with components)
- Need to configure design tokens properly upfront

### Neutral

- Will use `@tailwindcss/forms` plugin for accessible form styling
- Will use `@tailwindcss/typography` plugin for rich text content
- May use `tailwind-merge` and `clsx` for conditional classes

### Implementation Notes

#### Configuration

- Define design tokens in `tailwind.config.ts`:
  - Color palette (with WCAG AA compliant contrast)
  - Typography scale
  - Spacing scale
  - Breakpoints (mobile, tablet, desktop)
  - Focus ring styles

#### Mobile-First Breakpoints

```
sm: 640px   - Small tablets
md: 768px   - Tablets
lg: 1024px  - Small laptops
xl: 1280px  - Desktops
2xl: 1536px - Large screens
```

#### Accessibility Considerations

- Use Tailwind's contrast utilities
- Implement focus-visible for keyboard navigation
- Use sr-only for screen reader text
- Ensure touch targets meet 44x44px minimum on mobile
- Use semantic HTML with Tailwind classes

#### Component Organization

- Create reusable components to avoid className duplication
- Use composition for variant styling
- Extract common patterns into custom utilities if needed
