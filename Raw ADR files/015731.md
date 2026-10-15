# ADR-0006: Tailwind CSS + Shadcn/ui Design System

## Status
Accepted

## Date
2024-12-30

## Context

The application needs a consistent, maintainable design system that:

1. Supports custom branding (Verity green palette)
2. Provides accessible, production-ready components
3. Enables rapid UI development
4. Works well with Next.js and React
5. Supports dark mode (future consideration)

Options evaluated:
- **Material UI**: Heavy bundle, opinionated styling
- **Chakra UI**: Good DX, but vendor lock-in
- **Tailwind + Headless UI**: Low-level, need to build components
- **Tailwind + Shadcn/ui**: Copy-paste components, full ownership

## Decision

Adopt Tailwind CSS with Shadcn/ui component library and custom Verity design tokens.

### Tailwind Configuration

Custom color palette in `tailwind.config.ts`:

```typescript
colors: {
  // Verity Green Spectrum
  verity: {
    950: '#05110D',  // Darkest
    900: '#0D211A',  // Dark
    800: '#1A3C30',  // Brand Primary
    700: '#2A4D3E',  // Button Hover
    600: '#5C6D63',  // Text Muted
    500: '#426154',  // Medium
    400: '#5C8070',  // Light Text
    300: '#7A9F8F',  // Accent
    200: '#A3C2B5',  // Light Accent
    100: '#D1E7DD',  // Minty
    50: '#E8F3EE'    // Minty Light
  },

  // Sand Spectrum (Warm Backgrounds)
  sand: {
    400: '#E5E5E5',
    300: '#EBE9E1',
    200: '#F3F1EB',
    100: '#F9F8F6',  // Main BG
    50: '#FDFCFB'
  },

  // Ouro (Gold for currency)
  ouro: {
    600: '#C9922A',
    500: '#D4A034',
    400: '#E0B14E'
  }
}
```

### Shadcn/ui Integration

Components copied to `src/components/ui/`:

```
src/components/ui/
├── button.tsx
├── card.tsx
├── dialog.tsx
├── dropdown-menu.tsx
├── input.tsx
├── select.tsx
├── skeleton.tsx
├── toast.tsx
└── ...
```

CSS Variables in `globals.css`:

```css
:root {
  --background: 40 33% 98%;      /* sand-100 */
  --foreground: 150 35% 10%;     /* verity-900 */
  --primary: 150 35% 17%;        /* verity-800 */
  --primary-foreground: 0 0% 100%;
  --muted: 40 20% 94%;           /* sand-200 */
  --muted-foreground: 150 10% 40%;
  /* ... */
}
```

### Typography

Custom fonts via `next/font`:

```typescript
// src/app/layout.tsx
const inter = Inter({ variable: '--font-inter' })
const crimson = Crimson_Text({ variable: '--font-crimson' })
```

Font classes in Tailwind:
- `font-sans`: Inter (body text)
- `font-display`: Crimson Text (headings)

### Component Patterns

Custom components extend Shadcn base:

```typescript
// src/components/ui/button.tsx (Shadcn)
const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md...',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        // ...
      }
    }
  }
)

// src/components/v2/Button/Button.tsx (Custom extension)
export function Button({ children, ...props }) {
  return (
    <ShadcnButton className="font-medium" {...props}>
      {children}
    </ShadcnButton>
  )
}
```

## Consequences

### Positive

1. **Full Ownership**: Components are in our codebase, not a dependency
2. **Radix Primitives**: Accessible by default (keyboard, screen reader)
3. **Customizable**: Easy to modify any component
4. **Type-Safe**: TypeScript support with `class-variance-authority`
5. **Tree-Shakeable**: Only imported components in bundle
6. **Consistent Styling**: Design tokens in one place

### Negative

1. **Manual Updates**: No automatic updates from Shadcn
2. **Initial Setup**: Need to copy and configure each component
3. **Learning Curve**: Need to understand Radix primitives
4. **CSS Variables**: Require understanding of HSL color format

### Design Tokens Summary

| Token | Usage |
|-------|-------|
| `verity-800` | Primary buttons, links |
| `verity-700` | Hover states |
| `verity-600` | Muted text |
| `verity-100/50` | Backgrounds, cards |
| `sand-100` | Page background |
| `ouro-500` | Currency highlights |

## References

- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Shadcn/ui](https://ui.shadcn.com)
- [Radix UI Primitives](https://www.radix-ui.com/primitives)
- `tailwind.config.ts` - Full configuration
- `src/app/globals.css` - CSS variables
