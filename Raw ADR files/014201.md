# ADR 0005: Tailwind CSS with Shared Design System Preset

**Status**: Accepted (Enhanced in commit accf7f1)

**Date**: 2025-11-08 (Documented retroactively, refactored 2025-11-08)

**Deciders**: AI Agent (with user feedback)

## Context

Both applications needed a consistent styling solution with:
- Rapid UI development capabilities
- Shared design tokens (colors, spacing, typography)
- Easy customization per app
- Modern CSS tooling

### Options Considered

1. **Traditional CSS** - Separate CSS files per app
2. **CSS-in-JS** - styled-components, emotion
3. **Tailwind CSS** - Utility-first CSS framework
4. **Component Library Styles** - Rely on PrimeNG theming only

## Decision

Use **Tailwind CSS** with a **shared workspace preset** for design system tokens.

## Rationale

### Chosen: Tailwind CSS + Shared Preset

**Advantages**:
- ✅ **Utility-First**: Fast UI development with utility classes
- ✅ **Shared Design Tokens**: Centralized color/spacing/typography system
- ✅ **Type-Safe**: IntelliSense for class names
- ✅ **Tree-Shaking**: Unused utilities automatically removed
- ✅ **No Runtime Overhead**: Pure CSS, no JS overhead
- ✅ **Customization**: Easy to extend per app
- ✅ **Nx Integration**: Works well with Nx build system

**Disadvantages**:
- ⚠️ HTML can become verbose with many classes
- ⚠️ Initial learning curve for utility-first approach

### Rejected: Traditional CSS

**Why Rejected**:
- More maintenance overhead
- No shared design system out of the box
- Slower development velocity

### Rejected: CSS-in-JS

**Why Rejected**:
- Runtime overhead (JS parsing CSS)
- Larger bundle sizes
- Not as performant as static CSS

### Rejected: Component Library Only

**Why Rejected**:
- PrimeNG theming alone too restrictive
- Need custom spacing/layout utilities
- Want design system beyond components

## Consequences

### Positive

**Shared Design System**: Created `libs/tailwind-preset`
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        cream: { 50: '#FCFCF9', 100: '#FFFFFD' },
        teal: { 500: '#21808D' }, // Primary brand
        'child-1': '#87CEEB', // Domain-specific
        'child-2': '#90EE90',
        'child-3': '#DDA0DD',
        'parent': '#FFE55C',
      },
      fontFamily: {
        base: ['FKGroteskNeue', 'Geist', 'Inter'],
      },
      spacing: { /* 8px grid */ },
      borderRadius: { /* Custom radii */ },
    }
  }
};
```

**App-Specific Customization**:
```javascript
// apps/family-calendar/tailwind.config.js
module.exports = {
  presets: [require('../../libs/tailwind-preset/src/index.ts')],
  theme: {
    extend: {
      // App-specific overrides here
    }
  }
};
```

**Fast Development**:
```html
<div class="flex items-center gap-4 p-6 bg-cream-50 rounded-lg shadow-sm">
  <button class="px-4 py-2 bg-teal-500 text-white rounded-md hover:bg-teal-600">
    Click Me
  </button>
</div>
```

### Negative

**Build Step Required**: Must process Tailwind (acceptable with Angular build)

**Class Name Verbosity**: Some components have many classes
```html
<!-- Can be verbose -->
<div class="flex flex-col gap-2 p-4 bg-white rounded-lg shadow-md border border-gray-200">
```

**Solution**: Use component CSS for complex repeated patterns

### Evolution: From Root to Libs

**Original Implementation** (Commits before accf7f1):
- `tailwind-workspace-preset.js` at workspace root
- Apps referenced via `../../tailwind-workspace-preset.js`

**Refactored Implementation** (Commit accf7f1):
- Moved to `libs/tailwind-preset/src/index.ts`
- Better Nx dependency tracking
- Follows Nx best practices for shared code
- Apps reference via `../../libs/tailwind-preset/src/index.ts`

**Why Refactored**:
- ✅ Proper library in Nx project graph
- ✅ Clear dependency visualization
- ✅ Follows monorepo conventions
- ✅ Easier to version/test if needed

## Implementation

**Directory Structure**:
```
libs/
  tailwind-preset/
    src/
      index.ts          # Tailwind config export
    project.json        # Nx project config
    package.json        # Library metadata
    tsconfig.lib.json   # TypeScript config

apps/
  reward-chart/
    tailwind.config.js  # Uses preset
  family-calendar/
    tailwind.config.js  # Uses preset
```

**Preset Contents**:
- Color system (brand, semantic, domain-specific)
- Typography (fonts, sizes, weights, line-heights)
- Spacing (8px grid system)
- Border radius (custom design system)
- Box shadows (subtle, modern shadows)
- Animations (durations, timing functions)

**Current Usage**:
- Both apps use shared preset
- Minimal app-specific customization
- Consistent design tokens across workspace

## Follow-up

- ✅ Successfully refactored to libs/ folder
- ✅ Both apps using shared preset
- 🔮 Future: Consider adding more design tokens (animations, transitions)
- 🔮 Future: Extract common component patterns to Tailwind plugins
- 🔮 Future: Add PrimeNG integration with Tailwind (already using Aura theme)

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind Presets](https://tailwindcss.com/docs/presets)
- Implementation: `libs/tailwind-preset/src/index.ts`
- Configuration: `TAILWIND-CONFIG.md`
- Refactoring: Commit accf7f1
