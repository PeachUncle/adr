# ADR-003: Use CSS Custom Properties for Theming

## Status

Accepted

## Context

We need a theming system that allows runtime theme switching, custom themes, and good performance. Options include CSS-in-JS, CSS modules, SASS variables, or CSS custom properties.

## Decision

We will use CSS custom properties (CSS variables) as the primary theming mechanism.

## Consequences

### Positive

- **Runtime Changes**: Switch themes without reloading
- **Performance**: Native browser feature, no JavaScript overhead
- **Inheritance**: Natural CSS cascade and inheritance
- **DevTools**: Easy to inspect and modify in browser
- **Framework Agnostic**: Works with any or no framework
- **Browser Support**: Excellent support in target browsers

### Negative

- **Limited Logic**: No complex calculations like SASS
- **IE11**: No support (acceptable for our targets)
- **Type Safety**: No TypeScript validation of values
- **Build Time**: Can't optimize unused variables

### Neutral

- **Naming**: Need consistent naming convention
- **Documentation**: Must document all variables

## Implementation

### Theme Structure

```typescript
interface Theme {
  name: string;
  colors: {
    primary: string;
    background: string;
    text: string;
    // ... more colors
  };
  fonts: {
    body: string;
    heading: string;
    code: string;
  };
  spacing: {
    unit: number;
    containerMaxWidth: string;
  };
  borderRadius: string;
}
```

### CSS Variable Mapping

```css
:root {
  --mdv-color-primary: #0066cc;
  --mdv-color-background: #ffffff;
  --mdv-color-text: #333333;
  --mdv-font-body: -apple-system, sans-serif;
  --mdv-spacing-unit: 8px;
  /* ... more variables */
}
```

### Theme Application

```javascript
function applyTheme(theme) {
  const root = document.documentElement;

  // Apply colors
  Object.entries(theme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--mdv-color-${key}`, value);
  });

  // Apply fonts, spacing, etc.
}
```

## Examples

### Using Variables in CSS

```css
.mdv-button {
  background-color: var(--mdv-color-primary);
  color: var(--mdv-color-background);
  font-family: var(--mdv-font-body);
  padding: var(--mdv-spacing-unit);
  border-radius: var(--mdv-border-radius);
}
```

### Dark Mode

```css
[data-theme='dark'] {
  --mdv-color-background: #1a1a1a;
  --mdv-color-text: #ffffff;
  /* Override only what changes */
}
```

## Trade-offs Considered

### CSS-in-JS

- ❌ Runtime overhead
- ❌ Larger bundle size
- ❌ Framework specific
- ✅ Type safety

### SASS Variables

- ❌ Compile-time only
- ❌ No runtime switching
- ✅ Advanced features
- ✅ Build optimization

### CSS Modules

- ❌ More complex setup
- ❌ No runtime theming
- ✅ Scoped styles
- ✅ Build optimization

## References

- [MDN CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [CSS Variables Performance](https://developers.google.com/web/updates/2016/02/css-variables-why-should-you-care)
