# ADR 005: Use CSS Variables for Theming

## Status
Accepted

## Context
We needed to implement a dark mode feature and provide consistent theming across all Lit web components, which use shadow DOM for style encapsulation.

## Decision
We will use CSS custom properties (CSS variables) defined at the document level to enable dynamic theming that works across shadow DOM boundaries.

## Rationale
- **Shadow DOM compatible**: CSS variables pierce shadow DOM, unlike regular styles
- **Dynamic theming**: Change theme by toggling CSS class on `<body>`
- **DRY principle**: Define colors once, use everywhere
- **Performance**: Native CSS feature, no runtime overhead
- **Maintainability**: Single source of truth for all colors
- **Type safety**: Fallback values prevent broken styles

## Implementation

### Global variables in styles.css (27 variables):
```css
:root {
  --color-primary: #667eea;
  --color-text: #2d3748;
  --color-background: #ffffff;
  --color-btn-edit: #4CAF50;
  --color-btn-delete: #f44336;
  /* ... 22 more */
}

body.dark-mode {
  --color-text: #e2e8f0;
  --color-background: #1a202c;
  --color-btn-edit: #66BB6A;
  /* ... adjusted colors for dark theme */
}
```

### Usage in components:
```javascript
static styles = css`
  .todo-item {
    color: var(--color-text, #2d3748);
    background: var(--color-surface, #ffffff);
  }
`;
```

## What We Theme
- **Text colors**: Primary, muted, completed states
- **Surfaces**: Background, cards, inputs
- **Borders**: Default, focus, hover states
- **Buttons**: Edit, delete, save, cancel, warning, disabled
- **States**: Hover, active, focus indicators

## Consequences

### Positive
- Single class toggle (`body.dark-mode`) switches entire theme
- All 5 components get theming for free
- Easy to add new themes (e.g., high contrast, custom colors)
- Smooth transitions between themes via CSS
- Theme preference persists to localStorage
- No runtime JS color manipulation needed

### Negative
- No IE11 support (requires modern browser)
- Must remember to use `var()` instead of hardcoded colors
- Fallback values needed for robustness (adds verbosity)
- Can't scope variables easily (global namespace)

## Alternatives Considered
- **CSS-in-JS theming**: Runtime overhead, larger bundle size
- **Sass/Less variables**: Compile-time only, can't change dynamically
- **Class-based themes**: Doesn't work with shadow DOM
- **Inline styles from JS**: Violates separation of concerns, poor performance
- **CSS modules**: Doesn't solve shadow DOM theme propagation
