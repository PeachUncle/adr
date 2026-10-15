# ADR-0005: Styling Approach

## Status
Accepted

## Context
We need a styling solution that provides:
- Consistency across the application
- Dark mode support
- Responsive design
- Customization and theming
- Developer productivity

## Decision
We will use Tailwind CSS with the following approach:

### 1. Tailwind CSS Utility-First
- Utility classes for styling
- Custom configuration in `tailwind.config.js`
- CSS variables for theming
- Dark mode via `class` strategy

### 2. shadcn/ui Component System
- Radix UI primitives styled with Tailwind
- Fully customizable components
- Copy-paste component library
- Type-safe component props

### 3. CSS Variables for Theming
- Defined in `index.css`
- HSL color system for easy manipulation
- Light and dark mode variants
- Semantic color tokens (primary, secondary, etc.)

### 4. Custom Utilities
- `.sr-only` for screen reader only content
- `.chat-scrollbar` for custom scrollbar styling
- Animation utilities in `index.css`

### Rationale

1. **Tailwind CSS**: 
   - Fast development with utility classes
   - Consistent design system
   - Excellent responsive design utilities
   - Small production bundle size (purge unused)

2. **shadcn/ui**:
   - Accessible components (Radix UI)
   - Full customization (not locked to library styles)
   - Copy-paste (not npm package dependency)
   - TypeScript support

3. **CSS Variables**:
   - Easy theme switching
   - Runtime theme changes
   - Consistent color system
   - Dark mode support

4. **HSL Colors**:
   - Easy to manipulate (lightness, saturation)
   - Better for theming than RGB
   - Intuitive for designers

## Consequences

### Positive
- Rapid development with utility classes
- Consistent design system
- Easy dark mode implementation
- Highly customizable components
- Small bundle size
- Excellent developer experience

### Negative
- Initial learning curve for Tailwind
- Need to maintain consistency with utility classes
- CSS variables can be tricky to debug
- Tailwind config needs maintenance

## File Structure

```
apps/web/
├── src/
│   ├── index.css          # Global styles, CSS variables, utilities
│   └── components/
│       └── ui/            # shadcn/ui components (styling)
├── tailwind.config.js     # Tailwind configuration
└── postcss.config.js      # PostCSS configuration
```

## Theme Customization

Theme colors are defined in `index.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --background: 240 33% 98.5%;
  /* ... */
}

.dark {
  --primary: 217.2 91.2% 59.8%;
  --background: 222.2 84% 4.9%;
  /* ... */
}
```

These are used in Tailwind config and components via `hsl(var(--primary))`.

## Alternatives Considered

1. **Styled Components**: Rejected - runtime overhead, larger bundle
2. **CSS Modules**: Rejected - less convenient than Tailwind
3. **Material UI**: Rejected - less customizable, larger bundle
4. **Emotion**: Rejected - runtime overhead
5. **Plain CSS**: Rejected - less productive, harder to maintain consistency

## Future Considerations

- Could add CSS-in-JS if needed for complex dynamic styling
- Consider CSS-in-JS libraries (Emotion, styled-components) if Tailwind becomes limiting
- Tailwind is likely sufficient for most use cases

