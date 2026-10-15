# ADR-001: CSS Architecture - Tailwind CSS

## Status
Accepted

## Context
We need to choose a CSS architecture approach for the Fablecraft authentication pages and future UI development. The main options considered were:

1. **CSS-in-JS (styled-components/emotion)**
   - Pros: Dynamic theming, component scoping, JavaScript integration
   - Cons: Runtime overhead (3-10kb), bundle size increase, potential performance issues

2. **CSS Modules**
   - Pros: Build-time optimization, no runtime overhead, true CSS
   - Cons: Less dynamic, more boilerplate, separate files

3. **Tailwind CSS**
   - Pros: Utility-first, small production bundle, design system alignment
   - Cons: Verbose markup, learning curve for new developers

## Decision
We will use **Tailwind CSS** as our CSS architecture.

## Rationale

### 1. **Already Implemented**
- The existing landing page uses Tailwind CSS extensively
- Configuration is already optimized with custom theme values
- Team is already familiar with the utility classes

### 2. **Performance Benefits**
- Zero runtime overhead (all CSS is static)
- Extremely small production bundle (typically 5-15kb total CSS)
- PurgeCSS removes unused styles automatically
- No JavaScript execution for styling

### 3. **Design Token Integration**
- Our design tokens map perfectly to Tailwind's configuration
- CSS variables work seamlessly with Tailwind utilities
- Theme switching is handled via CSS variables, not JavaScript

### 4. **Developer Experience**
- Instant visual feedback while coding
- No context switching between files
- Excellent IDE support with Tailwind IntelliSense
- Consistent spacing, colors, and typography via utility classes

### 5. **Scalability**
- Component extraction pattern works well:
  ```tsx
  // Instead of inline utilities everywhere:
  <div className="bg-card/90 backdrop-blur-lg border border-border rounded-lg p-6">
  
  // We extract to components:
  <GlassCard variant="heavy">
  ```

### 6. **Production Optimization**
- Tailwind's JIT (Just-In-Time) compiler generates only used styles
- Automatic vendor prefixing
- Built-in responsive design system
- Tree-shaking of unused utilities

## Consequences

### Positive
- ✅ Consistent with existing codebase
- ✅ Optimal performance (no runtime overhead)
- ✅ Small bundle size
- ✅ Easy theme customization via config
- ✅ Built-in responsive utilities
- ✅ Design tokens integrate naturally

### Negative
- ❌ Verbose className strings (mitigated by component extraction)
- ❌ Learning curve for developers new to utility-first CSS
- ❌ Limited dynamic styling (must use CSS variables or inline styles)

### Mitigation Strategies

1. **Component Extraction**: Create reusable components for common patterns
2. **clsx/cn utility**: Use for conditional classes
3. **Documentation**: Maintain good documentation of custom utilities
4. **VS Code Extensions**: Mandate Tailwind IntelliSense for all developers

## Implementation

### Configuration Location
- `tailwind.config.js` - Main configuration
- `src/index.css` - Tailwind directives and custom CSS
- `postcss.config.js` - PostCSS processing

### Custom Utilities
We extend Tailwind with:
- Golden ratio typography scale
- Friendship-based spacing system
- Glass morphism utilities
- Theme-aware color system

### Example Usage
```tsx
// Component with Tailwind utilities
export function AuthCard({ children }: { children: React.ReactNode }) {
  return (
    <div className={cn(
      "bg-card/90 backdrop-blur-lg",
      "border border-border rounded-lg",
      "p-strangers shadow-lg",
      "transition-all duration-300"
    )}>
      {children}
    </div>
  );
}
```

## References
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS Performance](https://tailwindcss.com/docs/optimizing-for-production)
- [CSS Architecture Comparison](https://css-tricks.com/css-in-js-vs-css-modules/)

## Review Date
- Decision made: August 2024
- Next review: February 2025