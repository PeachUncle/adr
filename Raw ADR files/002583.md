# ADR-003: Styling Approach

## Status
Accepted

## Date
2024-07-29

## Context

We needed to choose a styling approach for our Angular application that would:
- Provide consistent design across components
- Enable rapid UI development
- Support responsive design
- Be maintainable by team members with varying CSS skills
- Work well with Angular's component architecture
- Support theming and customization

## Decision

We decided to use **Tailwind CSS** as our primary styling solution with the following approach:
- Tailwind CSS for utility-first styling
- Custom CSS classes using Tailwind's `@apply` directive when needed
- BEM methodology for custom component styles
- CSS custom properties for theming

## Consequences

### Positive
- **Rapid development**: Utility classes enable fast UI prototyping
- **Consistent design**: Built-in design system with spacing, colors, typography
- **Responsive by default**: Mobile-first responsive utilities
- **Small production bundles**: Unused styles are purged automatically
- **Team productivity**: Reduces CSS decision fatigue
- **Customizable**: Extensive configuration options via tailwind.config.js
- **Documentation**: Excellent documentation and community resources

### Negative
- **Learning curve**: Team needs to learn utility class names
- **HTML verbosity**: Many utility classes can make HTML look cluttered
- **Debugging complexity**: Harder to debug styles compared to semantic class names
- **IDE support needed**: Requires proper IDE extensions for autocomplete

## Alternatives Considered

### CSS Modules
- **Pros**: Scoped styles, no naming conflicts
- **Cons**: Requires build configuration, less design consistency

### Styled Components
- **Pros**: Component-scoped styles, dynamic styling
- **Cons**: Not commonly used in Angular, runtime performance impact

### Angular Material
- **Pros**: Complete component library, accessibility built-in
- **Cons**: Opinionated design, harder to customize, larger bundle size

### Bootstrap
- **Pros**: Familiar to many developers, comprehensive components
- **Cons**: Less modern approach, harder to customize, jQuery dependencies

## Implementation Details

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8'
        }
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
}
```

### Global Styles Setup
```css
/* src/styles.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom component styles */
@layer components {
  .btn {
    @apply px-4 py-2 rounded font-medium transition-colors duration-200;
  }
  
  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700;
  }
}
```

### Component Styling Approach
```typescript
// Prefer utility classes in templates
@Component({
  template: `
    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">
        {{ title }}
      </h2>
      <p class="text-gray-600 leading-relaxed">
        {{ description }}
      </p>
    </div>
  `
})
export class CardComponent {}
```

## Guidelines

### Utility Class Organization
```html
<!-- Group utilities logically for readability -->
<div class="
  flex items-center justify-between
  bg-white rounded-lg shadow-md
  p-6 mb-4
  hover:shadow-lg transition-shadow
">
  <!-- Content -->
</div>
```

### When to Use Custom CSS
1. **Complex animations** that require keyframes
2. **Component-specific styles** that don't fit utility patterns
3. **Pseudo-selectors** beyond Tailwind's built-in support
4. **Print styles** and other media queries

### Custom Component Classes
```css
/* Use BEM for custom styles */
.user-card {
  @apply bg-white rounded-lg shadow-md p-6;
}

.user-card__header {
  @apply flex items-center justify-between mb-4;
}

.user-card__title {
  @apply text-xl font-semibold text-gray-900;
}

.user-card--featured {
  @apply ring-2 ring-blue-500;
}
```

### Responsive Design
```html
<!-- Mobile-first responsive design -->
<div class="
  grid grid-cols-1 gap-4
  md:grid-cols-2 md:gap-6
  lg:grid-cols-3 lg:gap-8
">
  <!-- Grid items -->
</div>
```

### Dark Mode Support
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ... other config
}
```

```html
<!-- Dark mode utilities -->
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  <!-- Content -->
</div>
```

## Development Workflow

### IDE Setup
- Install Tailwind CSS IntelliSense extension
- Configure Prettier with Tailwind plugin for class sorting
- Use Tailwind Play for quick prototyping

### Build Process
- PostCSS processes Tailwind directives
- PurgeCSS removes unused styles in production
- Automatic vendor prefixing

### Design System Integration
- Define custom colors in tailwind.config.js
- Create component variants using @apply
- Document design patterns in style guide

## Performance Considerations

### Bundle Size Optimization
- Unused utilities are purged in production
- Only import needed Tailwind plugins
- Use dynamic imports for large component libraries

### Runtime Performance
- No JavaScript runtime for styles
- CSS-only animations when possible
- Efficient selector specificity

## Team Guidelines

### Code Review Checklist
- [ ] Utility classes are organized logically
- [ ] Responsive breakpoints are used appropriately
- [ ] Custom CSS follows BEM methodology
- [ ] No unused utility classes
- [ ] Accessibility considerations addressed

### Learning Resources
- Tailwind CSS Documentation
- Component examples repository
- Internal style guide and patterns
- Regular team knowledge sharing sessions

## Migration Strategy

If we need to migrate away from Tailwind in the future:
1. **Gradual migration**: Convert components one at a time
2. **CSS extraction**: Use @apply to extract utilities to semantic classes
3. **Design token export**: Extract design tokens to CSS custom properties
4. **Component library**: Build semantic component library as abstraction layer

## Related Decisions
- ADR-001: Frontend Framework Selection (Angular component architecture)
- Component library design using shared components

## Review Date
This decision should be reviewed in 12 months (July 2025) or when:
- Team feedback indicates significant productivity issues
- Performance problems are attributed to styling approach
- Design requirements change significantly