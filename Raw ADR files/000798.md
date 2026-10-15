---
docid: ADR-088
title: ADR 044 Floating Labels Ruleset
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-044: Floating Labels vs Traditional Labels - Ruleset

**Status**: Accepted  
**Date**: 6. Januar 2026  
**Authors**: @SARAH, @UX, @UI, @Frontend  
**Reviewers**: @TechLead, @Accessibility  
**Related**: [UX_GUIDE.md](../../docs/guides/UX_GUIDE.md)

---

## Context

B2X has three frontend applications (Store, Admin, Management) that require form input patterns. We need clear rules for when to use floating labels vs traditional labels to ensure consistency, accessibility, and optimal user experience.

Current state:
- Placeholder comments exist in `_forms.scss` for floating labels
- No implementation exists yet
- Mix of form patterns across applications
- Need standardized approach

---

## Decision

**Adopt a hybrid approach**: Provide both floating and traditional label components, with clear rules for when to use each pattern.

**Default**: Traditional labels (proven usability, better accessibility)  
**Opt-in**: Floating labels (space-constrained contexts, modern aesthetic)

---

## Ruleset

### 1. **ALWAYS Use Traditional Labels** (FormInput.vue)

✅ **Required for:**
- Forms with **5+ fields**
- Complex data entry (product management, user administration)
- Multi-step forms or wizards
- Forms requiring complex validation with multiple error types
- Accessibility-priority contexts (legal, healthcare, compliance)
- First-time user experiences (onboarding)
- Admin/Management applications (default)

✅ **Characteristics:**
```vue
<div class="form-control">
  <label class="label">
    <span class="label-text">Email Address</span>
  </label>
  <input type="email" class="input input-bordered" />
  <label class="label">
    <span class="label-text-alt text-error">Error message here</span>
  </label>
</div>
```

---

### 2. **MAY Use Floating Labels** (FloatingInput.vue)

✅ **Permitted for:**
- Simple forms (**1-4 fields**)
- Login/Registration pages
- Search bars and filters
- Quick-edit modals
- Mobile-optimized views (viewport < 768px)
- Store application (customer-facing)
- Profile/settings updates (familiar patterns)

✅ **Characteristics:**
```vue
<div class="relative">
  <input 
    type="email" 
    placeholder=" "
    class="input input-bordered peer"
    id="email"
  />
  <label 
    for="email"
    class="absolute left-3 -top-2.5 text-sm transition-all 
           peer-placeholder-shown:text-base 
           peer-placeholder-shown:top-2
           peer-focus:-top-2.5 peer-focus:text-sm
           peer-focus:text-primary"
  >
    Email Address
  </label>
</div>
```

---

### 3. **NEVER Use Floating Labels**

❌ **Prohibited for:**
- Password reset/recovery forms (security context)
- Payment/checkout forms (critical accuracy)
- Forms with dynamic field addition/removal
- Forms with autocomplete/suggestions
- Date/time pickers (label conflicts)
- File upload inputs
- Multi-select dropdowns
- Forms targeting users with cognitive disabilities

---

## Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                  FLOATING LABEL DECISION TREE                │
└─────────────────────────────────────────────────────────────┘

START: Need to design a form
  │
  ├─→ Is this a critical form (payment, security, admin)?
  │   └─→ YES → ❌ USE TRADITIONAL LABELS
  │
  ├─→ Does form have 5+ fields?
  │   └─→ YES → ❌ USE TRADITIONAL LABELS
  │
  ├─→ Does form have complex validation (multiple error types)?
  │   └─→ YES → ❌ USE TRADITIONAL LABELS
  │
  ├─→ Is this first-time user experience?
  │   └─→ YES → ❌ USE TRADITIONAL LABELS
  │
  ├─→ Are users unfamiliar with the pattern?
  │   └─→ YES → ❌ USE TRADITIONAL LABELS
  │
  ├─→ Simple form (1-4 fields) + familiar pattern?
  │   └─→ YES → ✅ MAY USE FLOATING LABELS
  │
  └─→ Mobile-first, space-constrained context?
      └─→ YES → ✅ MAY USE FLOATING LABELS

DEFAULT: When in doubt → USE TRADITIONAL LABELS
```

---

## Implementation Rules

### Rule 1: Component Structure

**Create two distinct components:**

```typescript
// frontend/[App]/src/components/forms/
├── FormInput.vue          // Traditional (DEFAULT)
├── FloatingInput.vue      // Floating (OPT-IN)
└── FormGroup.vue          // Wrapper with validation
```

**Import pattern:**
```vue
<script setup>
// Default import = traditional
import FormInput from '@/components/forms/FormInput.vue'

// Explicit opt-in for floating
import FloatingInput from '@/components/forms/FloatingInput.vue'
</script>
```

---

### Rule 2: Accessibility Requirements (MANDATORY)

**Both components MUST implement:**

```vue
<template>
  <div class="form-control">
    <!-- 1. Proper label association -->
    <label :for="id" class="label">
      <span class="label-text">{{ label }}</span>
      <span v-if="required" class="label-text-alt text-error" aria-label="required">*</span>
    </label>

    <!-- 2. ARIA attributes -->
    <input
      :id="id"
      :type="type"
      :aria-label="ariaLabel || label"
      :aria-required="required"
      :aria-invalid="!!error"
      :aria-describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
      class="input input-bordered"
    />

    <!-- 3. Error messaging with live region -->
    <div v-if="error" :id="`${id}-error`" class="label" role="alert" aria-live="polite">
      <span class="label-text-alt text-error">{{ error }}</span>
    </div>

    <!-- 4. Help text -->
    <div v-else-if="hint" :id="`${id}-hint`" class="label">
      <span class="label-text-alt">{{ hint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  id: string              // REQUIRED for accessibility
  label: string           // REQUIRED
  type?: string
  required?: boolean
  error?: string
  hint?: string
  ariaLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false
})
</script>
```

**Floating labels MUST also include:**
```css
/* Ensure label is always readable */
.floating-label {
  /* Minimum contrast 4.5:1 */
  color: var(--text-base);
  background: white;
  padding: 0 0.25rem;
  
  /* Ensure label stays visible on autofill */
  &:-webkit-autofill ~ label {
    transform: translateY(-1.5rem);
    font-size: 0.875rem;
  }
}
```

---

### Rule 3: Performance Requirements

**Floating labels MUST:**
- Animate at 60fps (use `transform`, not `top`)
- Use CSS transitions, not JavaScript
- Implement `will-change` sparingly
- Test on low-end devices (< 4GB RAM)

```css
/* Good: GPU-accelerated */
.floating-label {
  transform: translateY(0);
  transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Bad: Causes layout thrashing */
.floating-label {
  top: 0;
  transition: top 200ms;
}
```

---

### Rule 4: Application-Specific Guidelines

#### Store Application (DaisyUI)
- ✅ Floating labels allowed for: Login, Search, Quick Filters
- ❌ Traditional labels required for: Checkout, Registration, Account Settings

#### Admin Application (Soft UI)
- ❌ Traditional labels for ALL forms (consistency, data accuracy)

#### Management Application (Tailwind)
- ✅ Floating labels allowed for: Quick-edit modals, Search
- ❌ Traditional labels required for: Product/Tenant creation, Bulk operations

---

### Rule 5: Error Handling

**Traditional Labels:**
```vue
<label class="label">
  <span class="label-text">Email</span>
</label>
<input type="email" :class="{ 'input-error': error }" />
<label v-if="error" class="label">
  <span class="label-text-alt text-error">{{ error }}</span>
</label>
```

**Floating Labels:**
```vue
<div class="relative">
  <input 
    placeholder=" "
    :class="{ 'border-error': error }"
    class="peer"
  />
  <label class="floating-label peer-focus:text-primary"
         :class="{ 'text-error': error }">
    Email
  </label>
</div>
<div v-if="error" class="text-error text-sm mt-1" role="alert">
  {{ error }}
</div>
```

---

### Rule 6: Testing Requirements

**All form components MUST pass:**

```typescript
// Accessibility Tests (MANDATORY)
✅ WCAG 2.1 AA compliance
✅ Screen reader compatibility (NVDA, JAWS, VoiceOver)
✅ Keyboard navigation (Tab, Shift+Tab, Enter)
✅ Focus indicators visible (3px outline, 4.5:1 contrast)
✅ Error announcements via aria-live

// Visual Tests (MANDATORY)
✅ Animation at 60fps on low-end devices
✅ Label readable at all states (empty, focused, filled, error)
✅ No layout shift during animation (CLS = 0)
✅ Dark mode support

// Functional Tests (MANDATORY)
✅ Label remains visible after autofill
✅ Error message placement doesn't break layout
✅ Multi-language support (long labels don't overflow)
✅ Touch target minimum 44x44px (mobile)
```

---

### Rule 7: Documentation Requirements

**When implementing floating labels, MUST document:**

1. **In component file:**
```vue
<!--
  FloatingInput.vue
  
  USAGE RULES (see ADR-044):
  ✅ Use for: Simple forms (1-4 fields), login, search
  ❌ Don't use for: Complex forms, critical operations
  
  ACCESSIBILITY:
  - Requires id prop for label association
  - Error messages announced via aria-live
  - Tested with NVDA, JAWS, VoiceOver
-->
```

2. **In design system documentation:**
   - Component showcase with examples
   - Do's and Don'ts section
   - Accessibility notes
   - Browser compatibility matrix

---

## Migration Strategy

### Phase 1: Component Creation (Week 1)
- Create `FormInput.vue` (traditional) - Priority 1
- Create `FloatingInput.vue` - Priority 2
- Create shared `FormGroup.vue` wrapper
- Write comprehensive tests

### Phase 2: Store Application (Week 2)
- Replace login form with floating labels
- Replace search with floating labels
- Keep checkout as traditional labels
- A/B test if possible

### Phase 3: Evaluate & Expand (Week 3-4)
- Collect user feedback
- Measure accessibility metrics
- Decide on Admin/Management adoption
- Update design system docs

### Phase 4: Cleanup (Week 5)
- Remove old patterns
- Consolidate CSS
- Final accessibility audit

---

## Consequences

### Positive
✅ Clear rules prevent inconsistent implementation  
✅ Hybrid approach maximizes flexibility  
✅ Accessibility requirements enforced  
✅ Space savings where appropriate (25-30% vertical)  
✅ Modern aesthetic for customer-facing apps  

### Negative
❌ Two components to maintain instead of one  
❌ Development time: ~8 hours for floating labels  
❌ Testing complexity increased  
❌ Learning curve for team  
❌ Potential for misuse if rules not followed  

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Developers use floating labels incorrectly | Code review checklist, component prop validation |
| Accessibility regression | Automated a11y tests in CI/CD |
| Performance issues on mobile | Performance budget, lighthouse CI |
| User confusion | User testing, analytics monitoring |

---

## Compliance Checklist

**Before merging any floating label implementation:**

- [ ] Component has unique `id` prop requirement
- [ ] All ARIA attributes implemented correctly
- [ ] Screen reader tested (minimum 2 readers)
- [ ] Keyboard navigation fully functional
- [ ] 4.5:1 contrast ratio verified
- [ ] 60fps animation confirmed on low-end device
- [ ] Error states tested and accessible
- [ ] Dark mode support verified
- [ ] Multi-language tested (de, fr, es at minimum)
- [ ] Touch targets meet 44x44px minimum
- [ ] Code review by @TechLead or @Frontend
- [ ] UX review by @UX or @UI
- [ ] Accessibility review by @Security or designated a11y expert

---

## References

- [WCAG 2.1 Labels or Instructions](https://www.w3.org/WAI/WCAG21/Understanding/labels-or-instructions.html)
- [Nielsen Norman: Form Design](https://www.nngroup.com/articles/form-design-placeholders/)
- [Material Design: Text Fields](https://m2.material.io/components/text-fields)
- [DaisyUI Forms](https://daisyui.com/components/input/)
- [ADR-030: Vue-i18n Migration](./ADR-030-vue-i18n-v11-migration.md)
- [UX_GUIDE.md](../../docs/guides/UX_GUIDE.md)

---

## Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Coordinator | @SARAH | ✅ Approved | 2026-01-06 |
| UX Lead | @UX | ⏳ Pending | - |
| Frontend Lead | @Frontend | ⏳ Pending | - |
| Tech Lead | @TechLead | ⏳ Pending | - |
| Security/A11y | @Security | ⏳ Pending | - |

---

**Status**: Accepted (pending implementation reviews)  
**Next Review**: Before Phase 2 deployment  
**Owner**: @Frontend with @UX oversight
