# TALL Stack UI Libraries Comparison

**Document Type:** Architecture Specification
**Purpose:** Comprehensive analysis of open-source UI component libraries for TALL Stack applications
**Related:** [Livewire Volt Architecture](./livewire-volt.md), [Flux Replacement Strategy](./flux-replacement.md)
**Last Updated:** 2025-12-02

---

## Executive Summary

This document analyzes five UI libraries for TALL Stack applications, evaluating their suitability for AGPL-3.0-only open-source projects. All libraries reviewed are fully open-source (MIT license), making them compatible with Belimbing's licensing requirements.

---

## Libraries Analyzed

### Primary UI Component Libraries

1. **TallStackUI** - Suite of Blade components for TALL Stack apps
2. **MaryUI** - Laravel Blade components built on DaisyUI for Livewire
3. **WireUI** - Comprehensive component library for Laravel and Livewire

### Complementary Libraries

4. **Pines** - Alpine.js UI component library (works with any TALL UI lib)
5. **Blade Icons Set** - Icon library for Laravel (works with any TALL UI lib)

---

## Detailed Analysis

### 1. TallStackUI

**Repository:** [github.com/tallstackui/tallstackui](https://github.com/tallstackui/tallstackui)
**License:** MIT
**Stars:** 682 (as of 2025)
**Last Updated:** September 2025

#### Overview

TallStackUI is a powerful suite of Blade components specifically designed for TALL Stack applications. It provides over 30 ready-to-use components that elevate the workflow of Livewire applications.

#### Key Features

- **30+ Components** - Comprehensive set including forms, navigation, modals, tables, and more
- **Easy Installation** - Components can be set up in less than 5 minutes
- **Customization** - Unique personalization approaches (soft and deep customization)
- **Active Maintenance** - Regular updates and continuous development
- **Livewire-Native** - Built specifically for Livewire applications
- **TailwindCSS Integration** - Styled with TailwindCSS utilities

#### Components Available

- Form components (inputs, selects, checkboxes, radios)
- Navigation (sidebar, breadcrumbs, navlists)
- Overlays (modals, dropdowns, tooltips)
- Data display (tables, cards, badges)
- Feedback (alerts, notifications, progress)
- And more...

#### Pros

- ✅ **100% Open Source** - MIT license, fully compatible with AGPL-3.0
- ✅ **Mature Library** - Well-established with active community
- ✅ **Comprehensive** - Large component set covering most use cases
- ✅ **Customizable** - Multiple customization approaches
- ✅ **Good Documentation** - Well-documented with examples
- ✅ **Active Development** - Regular updates (latest: September 2025)

#### Cons

- ⚠️ **Component API** - Some components may have different API than Flux
- ⚠️ **Migration Effort** - May require refactoring when migrating from Flux
- ⚠️ **Dependency on TailwindCSS** - Requires TailwindCSS setup

#### Installation

```bash
composer require tallstackui/tallstackui
php artisan tallstackui:install
```

#### Example Usage

```blade
<x-ts::button>Click me</x-ts::button>
<x-ts::input label="Name" wire:model="name" />
<x-ts::modal title="Example Modal">
    Modal content
</x-ts::modal>
```

#### Compatibility with AGPL-3.0

✅ **Fully Compatible** - MIT license allows use in AGPL-3.0 projects

---

### 2. MaryUI ⭐

**Repository:** [github.com/robsontenorio/mary](https://github.com/robsontenorio/mary)
**License:** MIT
**Stars:** 1.4k (as of 2025)
**Last Updated:** December 2025

#### Overview

MaryUI provides gorgeous UI components for Livewire applications, powered by DaisyUI and TailwindCSS. It offers a comprehensive set of Blade components with a modern, accessible design.

#### Key Features

- **DaisyUI Foundation** - Built on mature DaisyUI component library
- **Livewire Integration** - Native support for Livewire wire:model, wire:click, etc.
- **Complete Component Set** - Forms, navigation, modals, tables, and more
- **Accessibility** - Built-in ARIA attributes and keyboard navigation
- **Dark Mode** - Automatic dark mode support
- **Active Development** - Very active with regular updates (latest: December 2025)

#### Components Available

- Form components (input, select, textarea, checkbox, radio, file upload)
- Buttons and links
- Modals and dialogs
- Navigation (menu, breadcrumbs, tabs)
- Data display (table, card, badge, avatar)
- Feedback (alert, toast, progress, skeleton)
- Layout (spacer, separator, container)
- And more...

#### Pros

- ✅ **100% Open Source** - MIT license, fully compatible with AGPL-3.0
- ✅ **Highly Popular** - 1.4k stars, active community
- ✅ **DaisyUI Foundation** - Built on proven, mature DaisyUI library
- ✅ **Livewire-Native** - Excellent Livewire integration
- ✅ **Active Development** - Very recent updates (December 2025)
- ✅ **Well Documented** - Comprehensive documentation
- ✅ **Accessibility** - Built-in accessibility features
- ✅ **Dark Mode** - Automatic theme switching

#### Cons

- ⚠️ **DaisyUI Dependency** - Requires DaisyUI as dependency
- ⚠️ **Learning Curve** - Different API than Flux components
- ⚠️ **Component Naming** - Uses `<x-mary-*>` prefix instead of `<flux:*>`

#### Installation

```bash
composer require robsontenorio/mary
php artisan mary:install
```

#### Example Usage

```blade
<x-mary-input label="Name" wire:model="name" />
<x-mary-button wire:click="save">Save</x-mary-button>
<x-mary-modal wire:model="showModal">
    Modal content
</x-mary-modal>
```

#### Compatibility with AGPL-3.0

✅ **Fully Compatible** - MIT license allows use in AGPL-3.0 projects

---

### 3. WireUI

**Repository:** [github.com/wireui/wireui](https://github.com/wireui/wireui)
**License:** MIT
**Stars:** ~500+ (estimated)
**Last Updated:** Active development

#### Overview

WireUI is a comprehensive library of components and resources designed to empower Laravel and Livewire application development. It provides form components, UI elements, notifications, and icon libraries.

#### Key Features

- **Comprehensive Components** - Wide range of form and UI components
- **Built-in Icons** - Includes Heroicons and Phosphor icons
- **Notifications** - Built-in notification system
- **Confirmation Dialogs** - Alert and confirmation components
- **TALL Stack Integration** - Works seamlessly with Alpine.js, TailwindCSS, Livewire
- **Active Development** - Actively maintained

#### Components Available

- Form components (input, select, textarea, checkbox, radio)
- UI components (card, modal, avatar, button, badge)
- Navigation (dropdown, menu)
- Feedback (notifications, alerts, confirmations)
- Icon integration (Heroicons, Phosphor)

#### Pros

- ✅ **100% Open Source** - MIT license, fully compatible with AGPL-3.0
- ✅ **Icon Integration** - Includes major icon libraries
- ✅ **Notification System** - Built-in notification/alert system
- ✅ **TALL Stack Native** - Designed for TALL stack
- ✅ **Comprehensive** - Good component coverage

#### Cons

- ⚠️ **Smaller Community** - Less popular than MaryUI or TallStackUI
- ⚠️ **Less Documentation** - May have less comprehensive documentation
- ⚠️ **Migration Effort** - Different API requires refactoring

#### Installation

```bash
composer require wireui/wireui
php artisan wireui:install
```

#### Example Usage

```blade
<x-input label="Name" wire:model="name" />
<x-button wire:click="save">Save</x-button>
<x-modal wire:model="showModal">
    Modal content
</x-modal>
```

#### Compatibility with AGPL-3.0

✅ **Fully Compatible** - MIT license allows use in AGPL-3.0 projects

---

### 4. Pines (Alpine.js UI Components)

**Repository:** [github.com/thedevdojo/pines](https://github.com/thedevdojo/pines)
**License:** MIT
**Type:** Alpine.js component library (complementary)

#### Overview

Pines is a free, impressive UI library built on Alpine.js. It provides Alpine.js components that work seamlessly with any TALL Stack UI library, adding interactive components like modals, dropdowns, tooltips, and more.

#### Key Features

- **Alpine.js Based** - Pure Alpine.js components, no framework dependency
- **Complementary** - Works alongside any UI library (TallStackUI, MaryUI, WireUI)
- **Interactive Components** - Modals, dropdowns, tooltips, popovers
- **Lightweight** - Minimal JavaScript overhead
- **Framework Agnostic** - Can be used in any Alpine.js project

#### Components Available

- Modals and dialogs
- Dropdowns and menus
- Tooltips and popovers
- Overlays and drawers
- And more Alpine.js components

#### Pros

- ✅ **100% Open Source** - MIT license
- ✅ **Lightweight** - Minimal overhead
- ✅ **Universal** - Works with any TALL UI library
- ✅ **Alpine.js Native** - Pure Alpine.js implementation
- ✅ **Complementary** - Enhances any UI library

#### Cons

- ⚠️ **Limited Scope** - Focuses on interactive components, not full UI suite
- ⚠️ **JavaScript Required** - Requires Alpine.js knowledge
- ⚠️ **Not Standalone** - Needs to be paired with other UI libraries

#### Installation

```bash
npm install @alpine-collective/pines
# or
composer require thedevdojo/pines
```

#### Example Usage

```blade
<button @click="$pines.open('my-modal')">Open Modal</button>

<div x-data @pines:open="my-modal" class="hidden">
    Modal content
</div>
```

#### Compatibility with AGPL-3.0

✅ **Fully Compatible** - MIT license allows use in AGPL-3.0 projects

**Use Case:** Use alongside TallStackUI, MaryUI, or WireUI to add interactive Alpine.js components.

---

### 5. Blade Icons Set

**Repository:** [github.com/driesvints/blade-icons](https://github.com/driesvints/blade-icons)
**License:** MIT
**Type:** Icon library (complementary)

#### Overview

Blade Icons Set is a package to easily make use of SVG icons in your Laravel Blade views. It supports multiple icon sets and works seamlessly with any UI library.

#### Key Features

- **SVG Icons** - Renders SVG icons as inline SVG
- **Multiple Icon Sets** - Supports Heroicons, Font Awesome, and more
- **Blade Components** - Simple `<x-icon>` component usage
- **Customizable** - Easy to customize size, color, and classes
- **Universal** - Works with any Laravel Blade project

#### Icon Sets Supported

- Heroicons
- Font Awesome
- Custom icon sets
- And more via packages

#### Pros

- ✅ **100% Open Source** - MIT license
- ✅ **Universal** - Works with any UI library
- ✅ **Flexible** - Supports multiple icon sets
- ✅ **Simple API** - Easy to use `<x-icon>` syntax
- ✅ **Customizable** - Full control over styling
- ✅ **Popular** - Widely used in Laravel community

#### Cons

- ⚠️ **Icon Focus Only** - Only provides icons, not UI components
- ⚠️ **Setup Required** - Need to install icon sets separately

#### Installation

```bash
composer require blade-ui-kit/blade-icons
php artisan blade-icons:install
```

#### Example Usage

```blade
<x-icon name="heroicon-o-user" class="w-6 h-6" />
<x-icon name="heroicon-s-home" class="w-5 h-5 text-blue-500" />
```

#### Compatibility with AGPL-3.0

✅ **Fully Compatible** - MIT license allows use in AGPL-3.0 projects

**Use Case:** Use with any TALL UI library to add icon support. Many UI libraries have built-in icon support, but Blade Icons provides a unified way to use icons across all libraries.

---

## Alternative Approach: HTMX

**Repository:** [htmx.org](https://htmx.org)
**License:** BSD
**Type:** HTML enhancement library (alternative to Livewire)

### Overview

**HTMX** is an alternative approach that extends HTML with attributes to create dynamic behavior without JavaScript frameworks. It focuses on enhancing HTML with AJAX, CSS Transitions, WebSockets, and Server-Sent Events through declarative attributes.

### HTMX Approach

```html
<button hx-post="/api/update-profile"
        hx-target="#profile"
        hx-swap="outerHTML">
    Update Profile
</button>
```

HTMX works by:
1. Listening for user interactions (clicks, form submits, etc.)
2. Making AJAX requests to server endpoints
3. Receiving HTML fragments from the server
4. Updating the DOM with the received HTML

### Comparison with Livewire Volt + MaryUI

| Feature | Livewire Volt + MaryUI | HTMX |
|---------|---------------------|------|
| **Learning curve** | Requires PHP/Laravel knowledge | HTML attributes, works with any backend |
| **State management** | Automatic reactivity, component state | Manual DOM manipulation |
| **UI components** | Pre-built MaryUI components | Build your own or use other libraries |
| **Framework coupling** | Laravel-specific | Framework-agnostic |
| **Complex interactions** | Easy with PHP logic | Requires backend endpoints |
| **Developer experience** | Integrated Laravel workflow | Requires API endpoints |
| **Type safety** | PHP type system | No type checking |
| **Validation** | Laravel validation rules | Server-side validation only |
| **Component reusability** | High (Volt components) | Low (HTML fragments) |
| **Licensing** | 100% open source (MIT) | 100% open source (BSD) |

### When to Use HTMX

HTMX is a better choice when:

- **Building simple, server-driven applications** with minimal interactivity
- **Preferring a framework-agnostic approach** (works with Python, Ruby, PHP, etc.)
- **Working with non-Laravel backends** (Django, Rails, etc.)
- **Wanting maximum simplicity** with HTML-first approach
- **Need for lightweight solution** without framework overhead
- **Existing backend APIs** that return HTML fragments

### Why Livewire Volt + MaryUI Was Chosen Over HTMX

1. **Tight Laravel integration** - Direct access to Eloquent, validation, authentication without creating separate API endpoints
2. **Component reusability** - Volt components can be easily shared, tested, and reused across the application
3. **Rich UI library** - MaryUI provides production-ready components out of the box with accessibility built-in
4. **Type safety** - PHP's type system helps catch errors at development time, not runtime
5. **Laravel ecosystem** - Works seamlessly with Laravel's features (middleware, policies, events, queues, etc.)
6. **Less API surface** - No need to create separate API endpoints; logic lives with the component
7. **Better developer experience** - Integrated debugging, testing, and tooling within Laravel
8. **State management** - Automatic reactivity without manual DOM manipulation
9. **Open source** - Both Volt and MaryUI are fully open source (MIT license)

### Can HTMX and Livewire Work Together?

While technically possible, they serve similar purposes and using both would add unnecessary complexity:

- **Overlapping functionality** - Both handle dynamic content updates
- **Increased complexity** - Two different paradigms for the same task
- **Maintenance burden** - Two systems to learn, debug, and maintain
- **Team confusion** - Unclear when to use which approach

**Recommendation:** Choose one approach that fits your project's needs and stick with it for consistency.

### Compatibility with AGPL-3.0

✅ **Fully Compatible** - BSD license allows use in AGPL-3.0 projects

---

## Comparison Matrix

| Feature | TallStackUI | MaryUI | WireUI | Pines | Blade Icons |
|---------|------------|--------|--------|-------|-------------|
| **License** | MIT | MIT | MIT | MIT | MIT |
| **AGPL Compatible** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Component Count** | 30+ | 40+ | 30+ | 10+ | N/A (icons) |
| **Livewire Native** | ✅ | ✅ | ✅ | ⚠️ (Alpine) | ✅ |
| **Dark Mode** | ✅ | ✅ | ✅ | N/A | N/A |
| **Accessibility** | ✅ | ✅ | ✅ | ⚠️ | N/A |
| **Community Size** | Medium | Large | Small | Medium | Large |
| **Last Updated** | Sep 2025 | Dec 2025 | Active | Active | Active |
| **Documentation** | Good | Excellent | Good | Good | Excellent |
| **Dependencies** | TailwindCSS | DaisyUI + TailwindCSS | TailwindCSS | Alpine.js | None |

---

## Recommendation Matrix

### For AGPL-3.0 Projects

All libraries are compatible with AGPL-3.0 (MIT license). The choice depends on specific needs:

#### Best Overall: MaryUI ⭐

**Recommended for:**
- Projects needing comprehensive component set
- Teams familiar with DaisyUI
- Applications requiring active support
- Projects needing dark mode and accessibility

**Reasons:**
- Largest community (1.4k stars)
- Most recent updates (December 2025)
- Built on proven DaisyUI foundation
- Excellent Livewire integration
- Comprehensive documentation

#### Alternative: TallStackUI

**Recommended for:**
- Projects preferring TALL Stack-specific library
- Teams wanting unique customization options
- Applications needing 30+ components
- Projects preferring established library

**Reasons:**
- Mature and stable
- Good component coverage
- Unique customization approaches
- Active maintenance

#### Lightweight Option: WireUI

**Recommended for:**
- Projects needing notification system
- Applications requiring built-in icons
- Teams wanting comprehensive but smaller library

**Reasons:**
- Built-in notification system
- Icon integration
- Good TALL stack integration

### Complementary Libraries

#### Pines (Alpine.js Components)

**Use When:**
- You need additional Alpine.js interactive components
- Working with any primary UI library
- Need modals, dropdowns, tooltips
- Want pure Alpine.js solutions

**Best Paired With:** Any primary UI library (TallStackUI, MaryUI, or WireUI)

#### Blade Icons Set

**Use When:**
- Need unified icon system across project
- Want flexibility in icon choice
- Working with multiple icon sets
- Need simple icon component syntax

**Best Paired With:** Any primary UI library (all UI libraries can benefit from unified icon system)

---

## Migration Considerations

### From Flux to Alternative

All three primary libraries (TallStackUI, MaryUI, WireUI) require component refactoring:

1. **Component Syntax Changes**
   - Flux: `<flux:input>`
   - TallStackUI: `<x-ts::input>`
   - MaryUI: `<x-mary-input>`
   - WireUI: `<x-input>`

2. **API Differences**
   - Property names may differ
   - Slot names may change
   - Event handling may vary

3. **Styling Adjustments**
   - Different default styles
   - May need TailwindCSS class adjustments
   - Dark mode implementation may differ

### Migration Effort Estimate

- **MaryUI:** Medium (similar structure to Flux)
- **TallStackUI:** Medium-High (different component API)
- **WireUI:** Medium (different API structure)

---

## Recommended Stack Combination

### Option 1: MaryUI + Blade Icons (Recommended) ⭐

```json
{
    "require": {
        "robsontenorio/mary": "^2.4",
        "blade-ui-kit/blade-icons": "^1.0"
    }
}
```

**Rationale:**
- MaryUI provides comprehensive component set
- Blade Icons provides unified icon system
- Both are MIT licensed
- Active development and large community
- Excellent documentation

### Option 2: TallStackUI + Pines + Blade Icons

```json
{
    "require": {
        "tallstackui/tallstackui": "^2.0",
        "thedevdojo/pines": "^1.0",
        "blade-ui-kit/blade-icons": "^1.0"
    }
}
```

**Rationale:**
- TallStackUI for core components
- Pines for additional Alpine.js interactions
- Blade Icons for icon system
- All MIT licensed

### Option 3: WireUI + Blade Icons

```json
{
    "require": {
        "wireui/wireui": "^2.0",
        "blade-ui-kit/blade-icons": "^1.0"
    }
}
```

**Rationale:**
- WireUI includes built-in icons but Blade Icons provides flexibility
- Good for projects needing notification system
- All MIT licensed

---

## Feature Comparison

### Component Coverage

| Component Type | TallStackUI | MaryUI | WireUI |
|----------------|------------|--------|--------|
| Form Inputs | ✅ | ✅ | ✅ |
| Buttons | ✅ | ✅ | ✅ |
| Modals | ✅ | ✅ | ✅ |
| Dropdowns | ✅ | ✅ | ✅ |
| Navigation | ✅ | ✅ | ⚠️ |
| Tables | ✅ | ✅ | ⚠️ |
| Cards | ✅ | ✅ | ✅ |
| Alerts | ✅ | ✅ | ✅ |
| Notifications | ⚠️ | ⚠️ | ✅ |
| Sidebar | ✅ | ✅ | ⚠️ |
| Date Picker | ❌ | ⚠️ | ⚠️ |
| Calendar | ❌ | ❌ | ❌ |

### Developer Experience

| Aspect | TallStackUI | MaryUI | WireUI |
|--------|------------|--------|--------|
| Installation | Easy | Easy | Easy |
| Documentation | Good | Excellent | Good |
| Examples | Good | Excellent | Good |
| Customization | High | High | Medium |
| Learning Curve | Medium | Low | Medium |
| Community Support | Medium | High | Low |

---

## Licensing Summary

All libraries analyzed are **fully compatible** with AGPL-3.0-only projects:

| Library | License | AGPL Compatible | Notes |
|---------|---------|----------------|-------|
| TallStackUI | MIT | ✅ | Fully open source |
| MaryUI | MIT | ✅ | Fully open source |
| WireUI | MIT | ✅ | Fully open source |
| Pines | MIT | ✅ | Fully open source |
| Blade Icons | MIT | ✅ | Fully open source |

**Conclusion:** All five libraries can be used in AGPL-3.0-only projects without licensing concerns.

---

## Decision Framework

### Choose MaryUI If:
- ✅ You want the most popular and actively maintained library
- ✅ You need comprehensive component set with excellent Livewire integration
- ✅ You prefer DaisyUI-based components
- ✅ You want excellent documentation and community support
- ✅ You need dark mode and accessibility out of the box

### Choose TallStackUI If:
- ✅ You want a TALL Stack-specific library
- ✅ You prefer unique customization approaches
- ✅ You want established, stable library
- ✅ You need 30+ components

### Choose WireUI If:
- ✅ You need built-in notification system
- ✅ You want icon integration included
- ✅ You prefer comprehensive but smaller library

### Use Pines If:
- ✅ You need additional Alpine.js interactive components
- ✅ Working with any primary UI library
- ✅ Want pure Alpine.js solutions

### Use Blade Icons If:
- ✅ You want unified icon system
- ✅ Need flexibility across multiple icon sets
- ✅ Want simple icon component syntax
- ✅ Working with any UI library

---

## Final Recommendation

### For Belimbing Project

**Recommended Stack:**
1. **MaryUI** - Primary UI component library
2. **Blade Icons Set** - Unified icon system
3. **Pines** (optional) - Additional Alpine.js components if needed

**Rationale:**
- ✅ All 100% open source (MIT licenses)
- ✅ Fully compatible with AGPL-3.0
- ✅ MaryUI has largest community and most recent updates
- ✅ Excellent Livewire integration
- ✅ Comprehensive component set
- ✅ Active development (December 2025)
- ✅ Blade Icons provides unified icon system
- ✅ Pines can add interactive components if needed

This combination provides:
- Complete UI component coverage
- Unified icon system
- Optional interactive enhancements
- 100% open-source licensing
- Active community support

---

## Implementation Timeline

### Phase 1: Research & Decision (Week 1)
- Review all libraries
- Test components in development environment
- Evaluate component coverage vs. current Flux usage
- Make final decision

### Phase 2: Installation & Setup (Week 1-2)
- Install chosen library (MaryUI recommended)
- Install Blade Icons Set
- Configure TailwindCSS/DaisyUI
- Set up dark mode

### Phase 3: Custom Components (Week 2-3)
- Build custom sidebar component (if needed)
- Build profile widget
- Build theme switcher
- Test all custom components

### Phase 4: Migration (Weeks 3-6)
- Migrate components file by file
- Test after each migration
- Refine styling and behavior
- Update documentation

---

## Resources

### Official Documentation

- [TallStackUI Documentation](https://tallstackui.com)
- [MaryUI Documentation](https://mary-ui.com)
- [WireUI Documentation](https://wireui.dev)
- [Pines Documentation](https://pinesui.com)
- [Blade Icons Documentation](https://github.com/blade-ui-kit/blade-icons)

### GitHub Repositories

- [TallStackUI](https://github.com/tallstackui/tallstackui)
- [MaryUI](https://github.com/robsontenorio/mary)
- [WireUI](https://github.com/wireui/wireui)
- [Pines](https://github.com/thedevdojo/pines)
- [Blade Icons](https://github.com/blade-ui-kit/blade-icons)

---

## Conclusion

All five libraries analyzed are **fully open-source** and **compatible with AGPL-3.0-only** projects. The recommended combination for Belimbing is:

- **MaryUI** as the primary UI component library
- **Blade Icons Set** for unified icon system
- **Pines** (optional) for additional Alpine.js components

This stack provides comprehensive UI coverage while maintaining 100% open-source licensing, active community support, and excellent developer experience.

---

**Document Status:** Analysis Complete
**Next Steps:**
1. Review recommendations with team
2. Install and test MaryUI in development
3. Begin migration planning
4. Create component mapping document

