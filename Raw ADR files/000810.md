---
docid: ADR-102
title: ADR_DAISYUI_FRAMEWORK
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# Architecture Decision Record: DaisyUI Component Framework

**Date:** December 30, 2025  
**Author:** @Architect  
**Status:** Accepted  
**Scope:** Frontend Component Architecture  

---

## Decision

**Adopt DaisyUI v5 as the official component framework** for B2X frontend applications. DaisyUI provides production-ready, accessible, and customizable components built on Tailwind CSS.

---

## Context

### Current Situation
- Store frontend has Tailwind CSS v4 installed
- DaisyUI v5 is already imported via CSS (`@import "daisyui"`)
- Components currently use mixed DaisyUI classes and custom Tailwind
- Team was considering building custom Tailwind components from scratch

### Problem
- **Redundant work:** Building custom components when DaisyUI exists
- **Inconsistency:** Mix of DaisyUI and custom implementations
- **Accessibility risk:** Custom components may not meet WCAG 2.1 AA
- **Maintenance overhead:** More code to maintain long-term

### Goals
1. Use battle-tested, accessible components (DaisyUI)
2. Reduce custom component code
3. Maintain visual consistency across apps
4. Simplify developer experience

---

## Decision

### Use DaisyUI v5 as Primary Component Framework

```
┌─────────────────────────────────────────────────┐
│        B2X Component Stack                │
├─────────────────────────────────────────────────┤
│                                                  │
│  Application Layer (Vue 3 Components)           │
│           ↓                                      │
│  DaisyUI Components (Accessible, Pre-Built)     │
│           ↓                                      │
│  Tailwind CSS Utilities (Styling)               │
│           ↓                                      │
│  Custom Themes (B2X Branding)             │
│           ↓                                      │
│  Browser APIs                                   │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Component Coverage

### DaisyUI Provides (Use These)

| Component | Status | Usage |
|-----------|--------|-------|
| Button | ✅ Adopt | All action buttons (primary, secondary, outline) |
| Input | ✅ Adopt | Text, email, password, number fields |
| Select | ✅ Adopt | Dropdown selections |
| Checkbox | ✅ Adopt | Boolean inputs |
| Radio | ✅ Adopt | Single-choice selections |
| Textarea | ✅ Adopt | Multi-line text input |
| Label | ✅ Adopt | Form labels |
| Form Control | ✅ Adopt | Form field grouping |
| Card | ✅ Adopt | Content containers |
| Alert | ✅ Adopt | Notifications and messages |
| Badge | ✅ Adopt | Status indicators |
| Divider | ✅ Adopt | Visual separators |
| Loading | ✅ Adopt | Progress and loading states |
| Navbar | ✅ Adopt | Navigation header |
| Footer | ✅ Adopt | Footer section |
| Breadcrumb | ✅ Adopt | Navigation path |
| Pagination | ✅ Adopt | Page navigation |
| Tabs | ✅ Adopt | Tab navigation |
| Modal | ✅ Adopt | Dialogs and overlays |
| Tooltip | ✅ Adopt | Contextual hints |
| Dropdown | ✅ Adopt | Dropdown menus |

### Extend with Custom When Needed

- **Complex layouts:** Build with Tailwind flex/grid
- **Domain-specific components:** Create custom Vue components using DaisyUI building blocks
- **Unique interactions:** Layer custom Vue logic over DaisyUI structure

### Never Duplicate

- ❌ Don't build custom buttons when DaisyUI button exists
- ❌ Don't create form fields from scratch
- ❌ Don't replicate alert/modal functionality

---

## DaisyUI Best Practices

### Naming Convention
```vue
<!-- DaisyUI component classes -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-ghost">Ghost</button>

<!-- DaisyUI sizes -->
<button class="btn btn-xs">Extra Small</button>
<button class="btn btn-sm">Small</button>
<button class="btn btn-md">Medium (default)</button>
<button class="btn btn-lg">Large</button>

<!-- DaisyUI states -->
<button class="btn btn-disabled">Disabled</button>
<button class="btn loading">Loading</button>
```

### Form Structure
```vue
<div class="form-control">
  <label class="label">
    <span class="label-text">Email</span>
  </label>
  <input type="email" placeholder="your@email.com" class="input input-bordered" />
  <label class="label">
    <span class="label-text-alt">We'll never share your email</span>
  </label>
</div>
```

### Card Component
```vue
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content here</p>
    <div class="card-actions justify-end">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

---

## Color System

### DaisyUI Theme Colors (Pre-defined)
```
- primary: Main brand color (blue)
- secondary: Secondary actions (purple)
- accent: Accent highlights
- neutral: Neutral backgrounds
- base-100: Background color
- base-200: Lighter background
- base-300: Even lighter background
- info: Information messages (blue)
- success: Success messages (green)
- warning: Warning messages (amber)
- error: Error messages (red)
```

### Usage Pattern
```vue
<!-- Button variants -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>

<!-- Text colors -->
<p class="text-primary">Primary text</p>
<p class="text-success">Success text</p>
<p class="text-error">Error text</p>

<!-- Backgrounds -->
<div class="bg-base-100">Base background</div>
<div class="bg-primary text-primary-content">Primary background</div>
```

---

## Customization Strategy

### DaisyUI Configuration (`tailwind.config.ts`)
```typescript
export default {
  daisyui: {
    themes: [
      {
        B2X: {
          "primary": "#0b98ff",      // B2X blue
          "secondary": "#8b5cf6",    // Purple
          "accent": "#f59e0b",       // Amber
          "neutral": "#3f3f46",      // Dark gray
          "base-100": "#ffffff",     // White
          "success": "#22c55e",      // Green
          "warning": "#f59e0b",      // Amber
          "error": "#ef4444",        // Red
        }
      }
    ],
  },
}
```

### Custom Component Overrides (CSS)
```css
/* Override DaisyUI button if needed */
.btn-custom {
  @apply btn btn-primary rounded-full;
}

/* Custom theme tweaks */
@layer components {
  .card-compact {
    @apply card gap-2;
  }
}
```

---

## Migration Path

### Phase 1 (Current - Component Cleanup)
✅ Identify all components using DaisyUI  
✅ Remove redundant custom CSS  
✅ Standardize on DaisyUI class names  

### Phase 2 (Component Migration)
⏳ Replace custom button implementations → `<button class="btn btn-primary">`  
⏳ Replace custom form fields → `<input class="input input-bordered">`  
⏳ Replace custom cards → `<div class="card">`  
⏳ Replace custom alerts → `<div class="alert">`  

### Phase 3 (Advanced Features)
⏳ Setup DaisyUI theming system  
⏳ Create component documentation  
⏳ Setup storybook for component showcase  
⏳ Create custom component wrappers (if needed)  

---

## Accessibility

### DaisyUI Compliance
✅ WCAG 2.1 AA compliant components  
✅ Semantic HTML structure  
✅ ARIA labels and roles included  
✅ Keyboard navigation built-in  
✅ Focus management handled  

### Custom Component Responsibility
- Maintain accessibility when extending DaisyUI
- Use DaisyUI semantic structure as base
- Test all custom interactive elements
- Document accessibility features

---

## Performance Implications

### Bundle Size
- DaisyUI adds ~5KB gzipped
- Trade-off: Eliminates custom component code
- Net benefit: Smaller overall bundle

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile: iOS 13+, Android 5+
- No IE 11 support (acceptable)

---

## Related Decisions

- ADR: Tailwind CSS as Utility Framework (foundational)
- ADR: Service Boundaries & Communication (independent)
- Decision: Vue 3 + TypeScript for Frontend (component language)

---

## Consequences

### Positive ✅
- Battle-tested accessible components
- Faster development (less custom code)
- Consistent UI across applications
- Easy customization via Tailwind
- Strong community support
- Excellent documentation
- Regular updates and bug fixes

### Negative ⚠️
- Dependency on external library
- Must work within DaisyUI constraints
- Some customizations may be complex
- Learning curve for new developers

### Mitigation
- Document DaisyUI usage in project
- Create component guidelines
- Setup linting rules to enforce DaisyUI usage
- Monitor DaisyUI releases for updates

---

## Implementation Checklist

### Immediate (Phase 1)
- ✅ DaisyUI v5 already imported
- ✅ Tailwind configured
- ⏳ Audit existing components for DaisyUI usage
- ⏳ Document DaisyUI patterns in project
- ⏳ Create component guidelines
- ⏳ Setup linting (no custom button components)

### Phase 2
- ⏳ Update component inventory to reference DaisyUI
- ⏳ Migrate components to pure DaisyUI
- ⏳ Setup component storybook
- ⏳ Create custom component wrapper layer (if needed)

### Phase 3
- ⏳ Theme customization system
- ⏳ Dark mode support
- ⏳ Custom theme variants
- ⏳ Component showcase website

---

## Documentation References

- DaisyUI Docs: https://daisyui.com/
- DaisyUI Components: https://daisyui.com/components/
- DaisyUI Colors: https://daisyui.com/docs/colors/
- DaisyUI Themes: https://daisyui.com/docs/themes/
- Tailwind CSS Docs: https://tailwindcss.com/

---

## Approval

| Role | Decision | Date |
|------|----------|------|
| @Architect | ✅ Decided | Dec 30, 2025 |
| @Frontend | ⏳ Acknowledging | Dec 30, 2025 |
| @TechLead | ⏳ Reviewing | Dec 30, 2025 |

---

## Next Steps

1. **Update COMPONENT_INVENTORY.md** to reference DaisyUI
2. **Update DESIGN_SYSTEM_SETUP.md** to use DaisyUI patterns
3. **Update MIGRATION_ROADMAP.md** to use DaisyUI components
4. **Revert custom Tailwind components** to DaisyUI equivalents
5. **Create DaisyUI Component Guidelines** for team

---

**Decision Made:** December 30, 2025  
**Implementation:** Phase 2 Component Migration  
**Authority:** @Architect  
**Next Review:** After Phase 2 completion
