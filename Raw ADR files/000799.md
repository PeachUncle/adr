---
docid: ADR-089
title: ADR 045 Unified Layout System
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

# ADR-045: Unified Layout System for Frontend Applications

**Status**: Proposed  
**Date**: 6. Januar 2026  
**Deciders**: @Architect, @Frontend, @UX, @TechLead  
**Technical Story**: Standardize inconsistent layout patterns across Admin frontend

---

## Context and Problem Statement

The Admin frontend has evolved organically, resulting in **multiple inconsistent patterns** for:
- Page headers and titles
- Form layouts and field groupings
- Container/card styling
- Button variants
- Dark mode implementation
- Internationalization coverage

This inconsistency leads to:
- Higher maintenance burden
- Inconsistent user experience
- Longer onboarding for new developers
- Difficulty implementing global UI changes

### Evidence of Inconsistency

| Pattern | Variations Found | Files Affected |
|---------|------------------|----------------|
| Page Headers | 4 different approaches | EmailTemplateCreate, Dashboard, UserForm, CMS Pages |
| Form Rows | 3 patterns (flex, grid, custom) | EmailTemplateEditor, UserForm, various |
| Dark Mode | 3 methods | `html.dark`, `dark:`, `@media prefers-color-scheme` |
| Buttons | 4+ custom classes | `.btn-primary`, `.btn-submit`, Tailwind inline |
| i18n | Inconsistent | UserForm (hardcoded DE), ProductForm (hardcoded EN) |

---

## Decision Drivers

1. **Consistency** — Users expect predictable UI patterns
2. **Maintainability** — Single source of truth for layouts
3. **Developer Experience** — Clear patterns to follow
4. **Dark Mode** — Unified approach required
5. **Accessibility** — Consistent focus states, spacing
6. **i18n Compliance** — All text must use translation keys

---

## Considered Options

### Option A: Shared Layout Components (Recommended)

Create a set of reusable Vue components for common layout patterns:

```
frontend/Admin/src/components/layout/
├── PageLayout.vue        # Full page wrapper with slots
├── PageHeader.vue        # Title + subtitle + actions
├── FormLayout.vue        # Form container with sections
├── FormSection.vue       # Grouped form fields with heading
├── FormRow.vue           # Responsive multi-column row
└── CardContainer.vue     # Standard card wrapper
```

**Pros:**
- Enforces consistency through component API
- Easy to update globally
- Self-documenting through props
- TypeScript-typed props

**Cons:**
- Migration effort required
- Slight abstraction overhead

### Option B: CSS Utility Classes Only

Define standardized Tailwind utility combinations:

```css
/* tailwind.config.js */
@layer components {
  .page-header { @apply flex justify-between items-center mb-6; }
  .form-row { @apply grid grid-cols-1 lg:grid-cols-2 gap-6; }
}
```

**Pros:**
- Lightweight, no component overhead
- Familiar to Tailwind users

**Cons:**
- No enforcement — developers can still use custom styles
- Less self-documenting
- Harder to add complex logic (slots, conditional rendering)

### Option C: Design Tokens + CSS Variables

Define design tokens as CSS custom properties:

```css
:root {
  --layout-page-padding: 2rem;
  --layout-form-gap: 1.5rem;
  --layout-section-gap: 2rem;
}
```

**Pros:**
- Framework-agnostic
- Easy theming

**Cons:**
- Still requires discipline to use
- Doesn't solve structural inconsistencies

---

## Decision

**Adopt Option A: Shared Layout Components** with CSS variables for spacing tokens.

### Component Specifications

#### 1. PageHeader.vue

```vue
<template>
  <div class="page-header">
    <div class="page-header__content">
      <h1 class="page-header__title">{{ title }}</h1>
      <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>
```

**Usage:**
```vue
<PageHeader 
  :title="$t('email.templates.create')" 
  :subtitle="$t('email.templates.subtitle')"
>
  <template #actions>
    <button class="btn-secondary">{{ $t('ui.cancel') }}</button>
    <button class="btn-primary">{{ $t('ui.save') }}</button>
  </template>
</PageHeader>
```

#### 2. FormRow.vue

```vue
<template>
  <div class="form-row" :class="[`form-row--cols-${cols}`]">
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  cols?: 1 | 2 | 3 | 4
}>(), {
  cols: 2
})
</script>

<style scoped>
.form-row {
  display: grid;
  gap: var(--form-gap, 1.5rem);
}
.form-row--cols-1 { grid-template-columns: 1fr; }
.form-row--cols-2 { grid-template-columns: repeat(2, 1fr); }
.form-row--cols-3 { grid-template-columns: repeat(3, 1fr); }
.form-row--cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 1024px) {
  .form-row--cols-2,
  .form-row--cols-3,
  .form-row--cols-4 {
    grid-template-columns: 1fr;
  }
}
</style>
```

#### 3. FormSection.vue

```vue
<template>
  <section class="form-section">
    <h2 v-if="title" class="form-section__title">{{ title }}</h2>
    <p v-if="description" class="form-section__description">{{ description }}</p>
    <div class="form-section__content">
      <slot />
    </div>
  </section>
</template>
```

---

## Standardization Rules

### Dark Mode

**Standard**: Use Tailwind `dark:` variant exclusively.

```vue
<!-- ✅ CORRECT -->
<div class="bg-white dark:bg-soft-800">

<!-- ❌ WRONG: html.dark selector -->
html.dark .my-component { background: #1e293b; }

<!-- ❌ WRONG: @media query -->
@media (prefers-color-scheme: dark) { }
```

### Button Classes

**Standard**: Use semantic button classes from Soft UI:

| Purpose | Class | Example |
|---------|-------|---------|
| Primary action | `btn-primary` | Save, Submit, Create |
| Secondary action | `btn-secondary` | Cancel, Back |
| Destructive | `btn-danger` | Delete, Remove |
| Ghost/Text | `btn-ghost` | Close, Dismiss |

### Spacing

**Standard**: Use Tailwind spacing scale with CSS variables for overrides:

```css
:root {
  --page-padding-x: 2rem;      /* px-8 */
  --page-padding-y: 1.5rem;    /* py-6 */
  --form-gap: 1.5rem;          /* gap-6 */
  --section-gap: 2rem;         /* space-y-8 */
}
```

### i18n

**Standard**: ALL user-facing text MUST use `$t()` or `t()` from vue-i18n.

```vue
<!-- ✅ CORRECT -->
<label>{{ $t('user.form.firstName') }} *</label>

<!-- ❌ WRONG: Hardcoded string -->
<label>Vorname *</label>
```

---

## Migration Plan

### Phase 1: Create Components (Week 1)
- [ ] Create `frontend/Admin/src/components/layout/` directory
- [ ] Implement PageHeader, FormRow, FormSection, CardContainer
- [ ] Add TypeScript types and props validation
- [ ] Document in Storybook (if available) or README

### Phase 2: Migrate High-Traffic Views (Week 2)
- [ ] Dashboard.vue
- [ ] EmailTemplateCreate.vue / EmailTemplateEditor.vue
- [ ] UserForm.vue (+ fix i18n)
- [ ] CMS Pages.vue

### Phase 3: Full Migration (Week 3-4)
- [ ] All remaining views in `/views/`
- [ ] Remove legacy custom styles
- [ ] Update component generation templates (CLI)

### Phase 4: Validation (Week 4)
- [ ] Visual regression testing
- [ ] Accessibility audit
- [ ] Dark mode verification
- [ ] i18n completeness check

---

## Files Requiring Immediate i18n Fixes

| File | Hardcoded Strings | Priority |
|------|-------------------|----------|
| `views/users/UserForm.vue` | German labels (Vorname, Nachname, etc.) | P1 |
| `views/catalog/ProductForm.vue` | English placeholders | P2 |
| `views/catalog/CategoryForm.vue` | TBD - needs audit | P2 |

---

## Consequences

### Positive
- Consistent user experience across all Admin views
- Reduced CSS duplication (estimated 30-40% reduction)
- Faster development of new views
- Easier global UI updates
- Improved accessibility through standardized patterns

### Negative
- Initial migration effort (~2-3 developer days)
- Slight learning curve for new component API
- Risk of regression during migration

### Neutral
- Requires code review attention during transition period

---

## Compliance

- [ ] @Architect approval
- [ ] @Frontend approval  
- [ ] @UX approval
- [ ] @TechLead approval

---

## References

- [UX_GUIDE.md](../../docs/guides/UX_GUIDE.md) — Design system documentation
- [GL-012] Frontend Quality Standards
- [ADR-044] Floating Labels Ruleset

---

**Next Steps**: 
1. Get approval from deciders
2. Create layout components (assign to @Frontend)
3. Begin Phase 2 migration with EmailTemplateEditor as pilot
