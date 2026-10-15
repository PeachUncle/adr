# ADR-001: CSS Styling Approach

**Status:** Accepted
**Date:** 2025-11-29
**Decision Makers:** Development Team
**Technical Story:** Evaluate CSS extraction alternatives for improved maintainability and developer experience

## Context and Problem Statement

The Twines and Straps codebase currently uses inline Tailwind CSS classes throughout all components. While functional, this approach has led to:

- **Significant duplication**: Common patterns repeated 40+ times across components
- **Long className strings**: Some components have 100+ character class strings
- **Inconsistent styling**: Similar components styled slightly differently
- **Difficult dark mode maintenance**: Every component needs `dark:` variants manually added
- **Hard to refactor**: Changing a pattern requires updating many files

### Current State Analysis

| Pattern | Occurrences | Example |
|---------|-------------|---------|
| Transition classes | 96 | `transition-colors`, `transition-all` |
| Dark mode backgrounds | 46+ | `bg-white dark:bg-secondary-800` |
| Button styles | 30+ | `px-4 py-2 rounded-lg...` |
| Input field styles | 20+ | `w-full px-4 py-2 border...` |
| Badge/status styles | 15+ | `px-2 py-0.5 text-xs font-medium...` |

## Decision Drivers

- **Maintainability**: Easier to update styles across the application
- **Consistency**: Enforce design system patterns
- **Developer Experience**: Reduce cognitive load when styling
- **Bundle Size**: Consider CSS output size impact
- **Type Safety**: Leverage TypeScript where possible
- **Learning Curve**: Team familiarity with chosen approach

## Considered Options

### Option 1: Keep Current Approach (Inline Tailwind)

**Description**: Continue using inline Tailwind classes as-is.

**Pros:**
- No migration effort
- Team already familiar
- Maximum flexibility per-component
- No additional dependencies

**Cons:**
- Growing duplication problem
- Inconsistent implementations
- Hard to maintain at scale
- Long, unreadable className strings

### Option 2: Tailwind @apply in CSS Modules

**Description**: Extract common patterns into CSS modules using `@apply` directive.

```css
/* components/Button.module.css */
.btn {
  @apply px-4 py-2 rounded-lg transition-colors font-medium;
}
.btnPrimary {
  @apply bg-primary-600 text-white hover:bg-primary-700;
}
.btnSecondary {
  @apply bg-gray-200 dark:bg-secondary-600 text-gray-800 dark:text-white;
}
```

**Pros:**
- Uses existing Tailwind infrastructure
- Scoped class names (no conflicts)
- Gradual migration possible
- Native CSS (no runtime)

**Cons:**
- Tailwind discourages `@apply` for this use case
- Loses some Tailwind tooling benefits
- Creates two styling paradigms
- CSS modules add complexity to imports

### Option 3: CVA (Class Variance Authority) + Tailwind

**Description**: Use CVA to create variant-based component styles with full TypeScript support.

```typescript
// src/styles/button.ts
import { cva, type VariantProps } from 'class-variance-authority';

export const button = cva(
  'px-4 py-2 rounded-lg font-medium transition-colors focus:ring-2 focus:ring-offset-2',
  {
    variants: {
      intent: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
        secondary: 'bg-gray-200 dark:bg-secondary-600 text-gray-800 dark:text-white hover:bg-gray-300',
        danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
        ghost: 'bg-transparent hover:bg-gray-100 dark:hover:bg-secondary-700',
      },
      size: {
        sm: 'text-sm px-3 py-1.5',
        md: 'text-base px-4 py-2',
        lg: 'text-lg px-6 py-3',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      intent: 'primary',
      size: 'md',
    },
  }
);

export type ButtonVariants = VariantProps<typeof button>;
```

```tsx
// Usage in component
import { button } from '@/styles/button';

<button className={button({ intent: 'primary', size: 'lg' })}>
  Click me
</button>
```

**Pros:**
- Full TypeScript support with autocomplete
- Variant-based design system
- Works seamlessly with Tailwind
- Small bundle (~1KB)
- Can use `cn()` / `clsx()` for merging
- Gradual adoption possible
- Industry best practice (used by shadcn/ui)

**Cons:**
- New dependency to learn
- Requires creating style definitions
- Initial setup time

### Option 4: Tailwind Plugin + Design Tokens

**Description**: Extend Tailwind config with custom component classes.

```javascript
// tailwind.config.ts
plugins: [
  plugin(({ addComponents }) => {
    addComponents({
      '.btn': {
        '@apply px-4 py-2 rounded-lg transition-colors font-medium': {},
      },
      '.btn-primary': {
        '@apply bg-primary-600 text-white hover:bg-primary-700': {},
      },
      '.input': {
        '@apply w-full px-4 py-2 border rounded-lg focus:ring-2': {},
      },
    });
  }),
],
```

**Pros:**
- Native Tailwind approach
- Global classes available everywhere
- No runtime overhead
- Integrates with Tailwind tooling

**Cons:**
- No TypeScript support
- Global namespace pollution
- Config file becomes large
- No variant system built-in

### Option 5: CSS-in-JS (Styled Components / Emotion)

**Description**: Use a CSS-in-JS library for component styling.

**Pros:**
- Full JavaScript integration
- Dynamic styling capabilities
- Scoped styles

**Cons:**
- Runtime overhead
- Conflicts with Tailwind approach
- Complete rewrite required
- Poor server component support (Next.js App Router)
- **Not recommended for this codebase**

## Decision Outcome

**Chosen Option: Option 3 - CVA (Class Variance Authority) + Tailwind**

### Rationale

1. **TypeScript Integration**: CVA provides excellent type safety and autocomplete, reducing errors and improving DX
2. **Industry Standard**: Used by shadcn/ui, Radix, and many modern React projects
3. **Gradual Migration**: Can be adopted component-by-component without breaking existing code
4. **Preserves Tailwind Benefits**: All Tailwind classes still work, including dark mode
5. **Variant System**: Built-in support for component variants (size, intent, state)
6. **Minimal Overhead**: ~1KB gzipped, no runtime CSS generation
7. **Compound Variants**: Can define complex conditional styling

### Implementation Plan

#### Phase 1: Foundation (Immediate)
1. Install CVA: `npm install class-variance-authority`
2. Install clsx for class merging: `npm install clsx tailwind-merge`
3. Create utility function:
   ```typescript
   // src/lib/utils.ts
   import { clsx, type ClassValue } from 'clsx';
   import { twMerge } from 'tailwind-merge';

   export function cn(...inputs: ClassValue[]) {
     return twMerge(clsx(inputs));
   }
   ```

#### Phase 2: Core Components
Create style definitions for most-used patterns:
- `src/styles/button.ts` - All button variants
- `src/styles/input.ts` - Form inputs
- `src/styles/badge.ts` - Status badges
- `src/styles/card.ts` - Card containers
- `src/styles/typography.ts` - Text styles

#### Phase 3: Component Migration
Migrate components in order of usage frequency:
1. ProductCard (most used)
2. Button components
3. Form inputs
4. Modal components
5. Admin UI components

#### Phase 4: Documentation
- Document all available variants
- Create Storybook stories for visual reference
- Update contribution guidelines

### Positive Consequences

- **Consistent styling** across all components
- **Type-safe variants** prevent invalid prop combinations
- **Easier onboarding** for new developers
- **Reduced bundle size** (fewer duplicate classes)
- **Better maintainability** for design system changes

### Negative Consequences

- **Learning curve** for CVA syntax
- **Migration effort** to update existing components
- **Additional abstraction layer** between styling intent and output

### Trade-offs Accepted

- Accept initial migration time for long-term maintainability
- Accept new dependency for significant DX improvement
- Accept abstraction cost for consistency benefits

## Links

- [CVA Documentation](https://cva.style/docs)
- [shadcn/ui (uses CVA)](https://ui.shadcn.com/)
- [Tailwind Merge](https://github.com/dcastil/tailwind-merge)
- [clsx](https://github.com/lukeed/clsx)

## Notes

- This ADR does not mandate immediate full migration
- Existing inline Tailwind remains valid during transition
- New components should use CVA patterns
- Existing components can be migrated opportunistically
