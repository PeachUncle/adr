# ADR 006: Use Tailwind CSS Instead of CSS-in-JS

**Status:** Accepted

**Date:** 2025-10-18

**Context:**

WCAG Explorer needs a styling solution that:
- Provides consistent design system
- Supports theming (light/dark/high-contrast)
- Works well with React components
- Has good performance
- Is maintainable and scalable
- Supports accessibility patterns
- Enables rapid development

Modern React applications have several styling approaches:
1. **CSS-in-JS** (styled-components, Emotion, Styled-jsx)
2. **Utility-first CSS** (Tailwind CSS)
3. **CSS Modules**
4. **Plain CSS/SCSS**
5. **Hybrid approaches** (Tailwind + CSS custom properties)

**Decision:**

We will use **Tailwind CSS** with **CSS custom properties** for theming, and **NO CSS-in-JS libraries**.

Our styling stack:
- **Tailwind CSS 3.x** - Utility-first framework
- **CSS Custom Properties** - Theme variables
- **PostCSS** - Build-time processing
- **Plain CSS** - Global styles and theme definitions (index.css)

**Consequences:**

### Positive

1. **Performance:**
   - No runtime style injection
   - No JavaScript overhead for styling
   - Smaller bundle size (no styled-components ~15KB)
   - Styles are pure CSS, optimized by browsers

2. **Development Velocity:**
   - Rapid prototyping with utility classes
   - No context switching between files
   - IntelliSense autocomplete for classes
   - Consistent spacing/sizing out of the box

3. **Consistency:**
   - Design system enforced by default classes
   - Hard to create one-off custom values
   - Standardized colors, spacing, typography
   - Team writes similar-looking code

4. **Build-Time Optimization:**
   - PurgeCSS removes unused styles
   - Small production CSS bundle
   - Predictable cache behavior
   - No critical CSS extraction needed

5. **No Runtime Theme Switching Overhead:**
   - Themes use CSS custom properties
   - Class toggle changes all styles instantly
   - No recalculation of styled components
   - Theme JS is minimal (~2KB)

6. **Accessibility:**
   - Plain CSS makes focus states explicit
   - Dark mode variants are built-in
   - Screen readers aren't affected by styling approach
   - Can audit generated CSS easily

7. **Debugging:**
   - Browser DevTools show normal CSS
   - No cryptic generated class names
   - Can override styles in DevTools
   - Performance profiling is straightforward

8. **Serverless-Friendly:**
   - Could add SSR without hydration issues
   - No dynamic style calculation
   - Static CSS can be cached aggressively

### Negative

1. **Verbose JSX:**
   - Long className strings in components
   - Can be harder to read complex components
   - Repeated patterns not automatically DRY

```tsx
// Can become verbose
<div className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow">
```

2. **Component Coupling:**
   - Styles tightly coupled to markup
   - Moving/refactoring components requires updating classNames
   - No automatic style scope like styled-components

3. **No Props-Based Styling:**
   - Can't dynamically generate styles from props easily
   - Need conditional className logic instead

```tsx
// CSS-in-JS
const Button = styled.button`
  background: ${props => props.primary ? 'blue' : 'gray'};
`;

// Tailwind - more verbose
<button className={primary ? 'bg-blue-600' : 'bg-gray-600'}>
```

4. **Learning Curve:**
   - Team must learn Tailwind class names
   - Need to remember utilities vs reading CSS
   - Arbitrary values syntax for edge cases

5. **Customization Overhead:**
   - Complex custom designs require configuration
   - Extending Tailwind can be verbose
   - Some designs need custom CSS classes anyway

6. **Responsive Design Verbosity:**
```tsx
<div className="text-sm md:text-base lg:text-lg xl:text-xl">
  // Many breakpoint variants
</div>
```

7. **Lack of Co-location:**
   - Styles aren't "owned" by components
   - Global utility classes vs component styles
   - No automatic dead code elimination for CSS

8. **Conditional Logic:**
```tsx
// More complex than styled-components
const classes = `
  ${base}
  ${isActive ? 'text-blue-600' : 'text-gray-600'}
  ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}
`;
```

### Implementation Details

**Theme System:**
```css
/* index.css - CSS custom properties for themes */
:root {
  --color-bg-primary: 255 255 255;
  --color-text-primary: 17 24 39;
}

.theme-dark {
  --color-bg-primary: 17 24 39;
  --color-text-primary: 243 244 246;
}

/* Tailwind uses these variables */
@layer base {
  body {
    background-color: rgb(var(--color-bg-primary));
    color: rgb(var(--color-text-primary));
  }
}
```

**Dark Mode Configuration:**
```javascript
// tailwind.config.js
export default {
  darkMode: ['variant', [
    '@media (prefers-color-scheme: dark) { :root:not(.theme-light) & }',
    ':root.theme-dark &',
  ]],
  // Enables dark: prefix for utilities
}
```

**Component Example:**
```tsx
export default function CriterionCard({ criterion }) {
  return (
    <div className="card bg-primary border-primary p-4">
      <h3 className="text-lg font-semibold text-primary mb-2">
        {criterion.title}
      </h3>
      <p className="text-secondary text-sm">
        {criterion.description}
      </p>
    </div>
  );
}
```

**Alternatives Considered:**

### Styled-Components
- **Pros:**
  - Component-scoped styles
  - Props-based styling
  - Automatic critical CSS
  - Strong community
- **Cons:**
  - Runtime overhead (~15KB + runtime cost)
  - Serialization of styles on each render
  - Bundle size increases with components
  - SSR complexity (hydration, style injection)
- **Reason for rejection:** Performance overhead not justified. Tailwind provides better DX and performance for utility-first patterns.

### Emotion
- **Pros:**
  - Similar to styled-components
  - Better performance than styled-components
  - Smaller bundle
  - Framework agnostic
- **Cons:**
  - Still has runtime overhead
  - CSS-in-JS paradigm less suitable for utility-first
  - Theme switching requires recalculation
- **Reason for rejection:** Same fundamental issues as styled-components. Tailwind is better fit.

### CSS Modules
- **Pros:**
  - Scoped styles
  - No runtime overhead
  - Standard CSS syntax
  - Good tooling support
- **Cons:**
  - File proliferation (one CSS file per component)
  - No design system enforcement
  - Manual responsive design
  - Theme switching more complex
- **Reason for rejection:** More files to manage, less velocity than Tailwind. Doesn't provide design system.

### Vanilla Extract
- **Pros:**
  - Zero-runtime CSS-in-TypeScript
  - Type-safe styles
  - Scoped styles
  - Good performance
- **Cons:**
  - Newer, smaller ecosystem
  - Build complexity
  - Not utility-first
  - More boilerplate
- **Reason for rejection:** More complex setup. Tailwind provides similar benefits with less configuration.

### Panda CSS
- **Pros:**
  - Zero-runtime
  - Type-safe
  - Utility-first like Tailwind
  - Props-based styling
- **Cons:**
  - Very new, experimental
  - Smaller community
  - Less documentation
  - Unknown long-term viability
- **Reason for rejection:** Too new for production. Tailwind is proven and stable.

### Tailwind + CSS-in-JS (Hybrid)
- **Pros:**
  - Best of both worlds
  - Use CSS-in-JS for complex components
  - Tailwind for rapid development
- **Cons:**
  - Two styling paradigms to maintain
  - Larger bundle size
  - Team confusion about which to use
  - Style conflicts possible
- **Reason for rejection:** Mixing paradigms creates inconsistency. Better to commit to one approach.

**Best Practices:**

### Extracting Repeated Patterns

When className strings get unwieldy:

```tsx
// 1. Extract to constants
const CARD_CLASSES = 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-4';

// 2. Use @apply in CSS for semantic classes
/* index.css */
@layer components {
  .card {
    @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-4;
  }
}

// 3. Use classnames/clsx utility
import clsx from 'clsx';

<button className={clsx(
  'btn',
  isPrimary && 'btn-primary',
  isDisabled && 'opacity-50'
)}>
```

### Conditional Styling

```tsx
const buttonClasses = clsx(
  'px-4 py-2 rounded font-medium transition-colors',
  variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
  variant === 'secondary' && 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  size === 'sm' && 'text-sm py-1 px-3',
  size === 'lg' && 'text-lg py-3 px-6',
  disabled && 'opacity-50 cursor-not-allowed'
);
```

### Responsive Design

```tsx
// Use Tailwind breakpoints consistently
<div className="
  grid
  grid-cols-1        /* mobile */
  md:grid-cols-2     /* tablet */
  lg:grid-cols-3     /* desktop */
  gap-4
">
```

**When to Use Custom CSS:**

Custom CSS is acceptable for:
1. **Global styles** (resets, base typography)
2. **Theme definitions** (CSS custom properties)
3. **Animations** (keyframes, complex transitions)
4. **Print styles** (@media print)
5. **Legacy browser support** (progressive enhancement)
6. **Accessibility** (focus states, screen reader only)

**Notes:**

- Tailwind + CSS custom properties gives us best of both worlds
- Performance is critical for accessibility (fast load times help everyone)
- Utility-first CSS encourages consistency without enforcing it
- We can always add component classes with @apply if needed
- The constraint of no CSS-in-JS pushes us toward simpler solutions
