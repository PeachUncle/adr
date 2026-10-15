# Architectural Decision Record (ADR): Use of Lucide React for Icons

## Context

To ensure consistency, performance, and ease of use in icon management across the application, we decided to use the **lucide-react** library. Lucide is an open-source icon set that provides a modern, customizable, and lightweight alternative for rendering icons in React applications.

## Decision

**Date**: 24/03/2025

The application will use **lucide-react** as the primary library for handling icons. This decision is based on the following factors:

- **Lightweight & Optimized**: Lucide provides SVG-based icons, ensuring fast rendering and performance.
- **Customization**: The icons are easily customizable using standard properties such as `size`, `color`, and `strokeWidth`.
- **Consistency**: A single icon library helps maintain design consistency throughout the application.
- **Developer Experience**: The API is simple and integrates seamlessly into React components.

## Implementation

### Installation

To install the library, run the following command:

```sh
pnpm add lucide-react
```

or

```sh
yarn add lucide-react
```

### Usage

To use an icon, import it from `lucide-react` and include it as a component:

```tsx
import { Home } from 'lucide-react';

function MyComponent() {
  return <Home size={24} color='black' strokeWidth={2} />;
}
```

### Customization

Lucide icons accept several props for styling:

- **`size`**: Defines the size of the icon (default: `24` pixels)
- **`color`**: Sets the icon color (default: `currentColor`)
- **`strokeWidth`**: Adjusts the stroke thickness (default: `2`)

Example with customization:

```tsx
<Settings size={32} color='blue' strokeWidth={1.5} />
```

### Best Practices

- Use Lucide icons instead of other icon libraries to maintain consistency.
- Define reusable icon components when possible to centralize styling and avoid duplication.
- Avoid excessive inline styles and prefer CSS-in-JS or Tailwind classes when applicable.

## Status

**Accepted**

## Consequences

- All existing icon implementations should be migrated to **lucide-react** over time.
- Developers must adhere to the established guidelines for icon usage.
- Any future design changes should consider Lucide’s icon set first before introducing new libraries.
