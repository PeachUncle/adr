# ADR 0013: Use CSS Modules and Global CSS in Next.js

## Status

Accepted

## Context

The Meatbag project requires a styling solution that is:

- Easy to use with **Next.js App Router**
- Scoped by default to prevent style collisions
- Compatible with server-rendered and client-rendered components
- Aligned with **vanilla CSS** practices (no Tailwind or CSS-in-JS)

We considered several options:

| Approach                           | Pros                                                      | Cons                               |
| ---------------------------------- | --------------------------------------------------------- | ---------------------------------- |
| **CSS Modules + Global CSS**       | Native to Next.js, scoped by default, simple mental model | Requires organizing multiple files |
| Tailwind CSS                       | Utility-first, fast prototyping                           | Verbose markup, additional tooling |
| CSS-in-JS (e.g. styled-components) | Co-located styles, good DX                                | Adds runtime overhead, less native |
| SCSS                               | Familiar to some, supports variables/nesting              | Adds build step, not yet needed    |

## Decision

We chose to use **CSS Modules** for component-level styling and a **single global CSS file** for resets, typography, and utility classes.

### ✅ Implementation Plan

- `globals.css`: contains site-wide styles (resets, body defaults, fonts, etc.)
  - Imported once in `app/layout.js`
- `[ComponentName].module.css`: scoped CSS files per component
  - Co-located with the component for maintainability

Example:

```
// app/layout.js
import './globals.css';

// app/components/Button.js
import styles from './Button.module.css';

export default function Button() {
  return <button className={styles.primary}>Click me</button>;
}
```

## Consequences

- Styles for each component are kept isolated, reducing risk of conflicts
- Global styles are managed in one place, making resets and typography easy
- Developers must remember to use `.module.css` for new components
- No Tailwind, CSS-in-JS, or SCSS complexity for MVP

## Future Considerations

- Consider adopting SCSS or CSS variables if design complexity increases
- Evaluate Tailwind or CSS-in-JS if requirements change
- Add Stylelint for CSS linting as part of CI/CD

---

_Created: 2025-06-20_
