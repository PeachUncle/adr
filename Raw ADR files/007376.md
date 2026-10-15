# ADR-010: Theme and Styling Variables

## Status
Accepted

## Context
CharacterCraft Lite uses a consistent visual identity across all UI components. To make styling maintainable and customizable, we needed a strategy for managing theme colours, spacing, fonts, and UI tokens.

Originally, styles were defined inline or as one-off declarations in the CSS file. This made changes repetitive and error-prone. As the project evolved, we required:
- A central place to define core visual constants
- Ability to maintain consistent styling across components
- Flexibility to change themes in future or support dark/light modes

## Decision
We adopted a CSS custom properties approach (aka CSS variables) defined at the `:root` level in `style.css`.

### Example
```css
:root {
  --primary-color: #4a90e2;
  --accent-color: #f39c12;
  --background-color: #f9f9f9;
  --text-color: #333;
  --light-bg: #f0f4f8;
  --border-radius: 0.5rem;
  --transition: all 0.3s ease;
  --font-stack: 'Inter', sans-serif;
}
```

These variables are then used consistently throughout the stylesheet:
```css
button {
  background-color: var(--primary-color);
  border-radius: var(--border-radius);
  transition: var(--transition);
}
```

## Consequences
✅ Enables consistent visual language across components
✅ Makes theme updates easy (single point of change)
✅ Allows future support for light/dark mode with media queries or toggles
⚠️ Requires consistent discipline — avoid inline styles or hardcoded values

## Alternatives Considered
- SCSS/SASS variables (extra tooling for limited benefit in current scope)
- Utility-first frameworks like Tailwind (potentially too heavy for a small, self-contained tool)
- JavaScript-driven theming (unnecessary complexity)

## Future Considerations
- Define a second theme (e.g. dark mode) and switch via class or media query
- Extract theme into a separate file (`theme.css`) for reuse
- Allow user-defined overrides for whitelabeling or custom branding

---

*This decision prioritizes maintainability, clarity, and future-proof visual design.*