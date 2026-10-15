# Livewire Volt Architecture Decision

**Document Type:** Architecture Specification
**Purpose:** Explain the architectural decision to use Livewire Volt with MaryUI
**Related:** [File Structure](./file-structure.md), [Caddy Development Setup](./caddy-development-setup.md), [TALL Stack UI Libraries Comparison](./ui-libraries-comparison.md)
**Last Updated:** 2025-12-03

---

## Overview

This application uses **Livewire Volt** for reactive component development, combined with **MaryUI** for UI components. This document explains why Volt was chosen and how it works with MaryUI. For comparisons with alternative approaches, see the [TALL Stack UI Libraries Comparison](./ui-libraries-comparison.md) document.

---

## Livewire Volt: Minimal Boilerplate Components

**Role:** Volt enables creating reactive Livewire components using a single-file approach, combining PHP logic and Blade templates in one file.

### What It Provides

- **Single-file components** - PHP class and Blade view in the same file, reducing file navigation
- **Minimal boilerplate** - No need to create separate component classes; just use attributes and closures
- **Reactive state management** - Automatic UI updates when component properties change
- **Full Laravel integration** - Access to all Laravel features (validation, authentication, database) directly in components

### Example from This Codebase

```php
// resources/views/livewire/settings/profile.blade.php
new class extends Component {
    public string $name = '';

    public function updateProfileInformation(): void {
        // Validation, database operations, etc.
    }
}; ?>

<x-mary-input label="Name" wire:model="name" />
<x-mary-button wire:submit="updateProfileInformation">Save</x-mary-button>
```

### Why Volt?

Instead of creating separate component classes and view files, Volt lets you write everything in one place, making it ideal for small-to-medium components that need reactivity without the overhead of traditional Livewire class components.

**Traditional Livewire Approach:**
```php
// app/Livewire/Settings/Profile.php
class Profile extends Component {
    public string $name = '';

    public function updateProfileInformation(): void {
        // ...
    }

    public function render() {
        return view('livewire.settings.profile');
    }
}
```

**Volt Approach (Same Functionality):**
```php
// resources/views/livewire/settings/profile.blade.php
new class extends Component {
    public string $name = '';

    public function updateProfileInformation(): void {
        // ...
    }
}; ?>

<!-- Template continues here -->
```

This reduces boilerplate by ~50% while maintaining the same functionality.

---

## MaryUI: Open-Source UI Component Library

**Role:** MaryUI provides a comprehensive set of pre-built, accessible UI components built specifically for Livewire applications, powered by DaisyUI.

### What It Provides

- **Pre-built components** - Buttons, inputs, modals, navigation, dropdowns, and more
- **Accessibility built-in** - ARIA attributes, keyboard navigation, focus management
- **Consistent design system** - Cohesive look and feel across the entire application
- **Dark mode support** - Automatic theme switching without additional configuration
- **TailwindCSS integration** - Built on TailwindCSS 4.0 with DaisyUI, fully customizable
- **100% open source** - MIT license, no premium tiers or licensing concerns

### Example from This Codebase

```php
<x-mary-input wire:model="email" label="Email" type="email" required />
<x-mary-button variant="primary" type="submit">Submit</x-mary-button>
<x-mary-modal wire:model="showModal">
    <!-- Modal content -->
</x-mary-modal>
```

### Why MaryUI?

Building a complete UI component library from scratch is time-consuming and error-prone. MaryUI provides production-ready components with accessibility, theming, and responsive design already handled, allowing developers to focus on application logic rather than UI implementation details.

**Without MaryUI (Custom Components):**
- Build every component from scratch
- Implement accessibility features manually
- Handle keyboard navigation
- Manage focus states
- Test across browsers
- Maintain consistent styling

**With MaryUI:**
- Use pre-built, tested components
- Accessibility built-in
- Consistent design system
- Dark mode out of the box
- 100% open source (MIT license)

---

## Why Use Volt + MaryUI Together?

### Complementary Roles

1. **Volt provides reactivity** - Handles state management, form submissions, and server-side logic
2. **MaryUI provides the UI** - Supplies beautiful, accessible components ready to use
3. **Perfect separation of concerns** - Volt handles "what happens" (logic), MaryUI handles "how it looks" (presentation)
4. **Developer productivity** - Write less code, ship features faster
5. **Consistency** - MaryUI ensures all UI components follow the same design patterns
6. **Open source** - Both are fully open source, compatible with AGPL-3.0-only projects

### Real-World Example

```php
// Volt handles the logic (validation, database updates)
public function updateProfileInformation(): void {
    $this->validate(['name' => 'required|string|max:255']);
    Auth::user()->update(['name' => $this->name]);
}

// MaryUI provides the UI (accessible form inputs, buttons)
<x-mary-input label="Name" wire:model="name" required />
<x-mary-button variant="primary" wire:submit="updateProfileInformation">
    {{ __('Save') }}
</x-mary-button>
```

**Without MaryUI:** You'd need to build all UI components from scratch (inputs, buttons, validation states, error messages, accessibility features).

**Without Volt:** You'd write more boilerplate code with separate component classes and view files.

**Together:** They provide a complete solution with minimal code and maximum productivity, all while maintaining 100% open-source licensing.

---

## Alternative Approaches

For a detailed comparison with alternative approaches like HTMX, see the [TALL Stack UI Libraries Comparison](./ui-libraries-comparison.md#alternative-approach-htmx) document.

---

## Modern Patterns (2024-2025)

### Trend Analysis

The trend in Laravel development is toward **Livewire Volt + Open-Source UI Libraries** for full-stack applications because:

1. **Reduced context switching** - No need to switch between frontend/backend code; everything is in one place
2. **Better developer experience** - Integrated Laravel tooling (tinker, testing, debugging)
3. **Complete solution** - Logic + UI in one ecosystem, reducing integration complexity
4. **Modern reactive patterns** - Supports reactive programming while staying server-rendered
5. **Performance** - Server-rendered HTML is fast, with minimal JavaScript overhead
6. **Accessibility** - Modern UI libraries include accessibility features by default
7. **Team productivity** - Faster development cycles with less code to write
8. **Open source** - Fully open-source stack aligns with AGPL-3.0-only projects

### Industry Adoption

- **Laravel's official recommendation** - Laravel promotes Livewire as the preferred way to build interactive UIs
- **Growing ecosystem** - Increasing number of Livewire packages and extensions
- **Community support** - Large, active community providing components and solutions
- **Enterprise adoption** - Used by companies building production applications
- **Open source focus** - Growing preference for fully open-source UI libraries

---

## Implementation Strategy

### Getting Started

1. **Install Livewire Volt** - Already included in Laravel 12 by default
2. **Install MaryUI** - `composer require robsontenorio/mary`
3. **Install DaisyUI** - `npm install -D daisyui@latest`
4. **Configure Volt** - Set up mount paths in `VoltServiceProvider`
5. **Configure MaryUI** - Run `php artisan mary:install`
6. **Use MaryUI components** - Start using `<x-mary-*>` components in Blade templates

### Best Practices

1. **Start with Volt** - Use Volt for component logic and state management
2. **Use MaryUI for UI** - Leverage MaryUI components for all UI elements
3. **Keep components focused** - Single responsibility per component
4. **Reuse MaryUI components** - Don't reinvent what MaryUI already provides
5. **Customize when needed** - MaryUI components are customizable via TailwindCSS
6. **Build custom components** - Create reusable components for complex UI patterns
7. **Maintain consistency** - Follow MaryUI design patterns for custom components

---

## Open Source Compatibility

### Licensing

Both Livewire Volt and MaryUI are fully open source:

- **Livewire Volt** - MIT license
- **MaryUI** - MIT license
- **DaisyUI** - MIT license

All are compatible with **AGPL-3.0-only** projects, making them ideal for Belimbing's open-source requirements.

### Benefits

1. **No licensing concerns** - Fully open source, no premium tiers
2. **Vendor independence** - No dependency on proprietary solutions
3. **Community-driven** - Active open-source community
4. **Freedom to modify** - Full control over components
5. **Distribution freedom** - Can be distributed with AGPL-3.0 projects

---

## Conclusion

**Livewire Volt + MaryUI** provides a powerful, productive stack for building modern Laravel applications:

- **Volt** handles reactivity and business logic with minimal boilerplate
- **MaryUI** provides professional, accessible UI components out of the box
- **Together** they offer a complete solution with excellent developer experience
- **100% open source** - MIT licenses ensure full compatibility with AGPL-3.0-only projects

For comparisons with alternative approaches, see the [TALL Stack UI Libraries Comparison](./ui-libraries-comparison.md) document. **Livewire Volt + MaryUI** is the recommended choice for AGPL-3.0 Laravel applications due to its tight integration, rich ecosystem, superior developer experience, and complete open-source licensing alignment.

---

**Related Documentation:**
- [Livewire Documentation](https://livewire.laravel.com)
- [Livewire Volt Documentation](https://livewire.laravel.com/docs/volt)
- [MaryUI Documentation](https://mary-ui.com)
- [DaisyUI Documentation](https://daisyui.com)
- [HTMX Documentation](https://htmx.org)
- [TALL Stack UI Libraries Comparison](./ui-libraries-comparison.md)
