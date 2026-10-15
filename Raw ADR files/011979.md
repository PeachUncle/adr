# ADR 004: Custom Design System

**Date**: 2025-12-09
**Status**: Accepted
**Decision Makers**: Jason Moody

## Context

The portfolio application needs a UI component library and design system. We must decide between using an existing UI library (Material, PrimeNG, etc.) or building a custom design system from scratch.

## Decision

We will build a **custom design system** with our own component library, theme system, and design tokens, rather than using a pre-built UI framework.

## Rationale

### Why Custom Design System

1. **Portfolio Demonstration**

   - Showcases Angular component development skills
   - Demonstrates design system architecture
   - Shows CSS/SCSS expertise
   - Proves ability to build reusable components

2. **Complete Creative Control**

   - Unique visual identity
   - No "Material" or "Bootstrap" look
   - Custom animations and interactions
   - Brand-specific styling

3. **Performance Optimization**

   - Zero unused code (no tree-shaking needed)
   - Minimal bundle size
   - Only includes what we need
   - No framework overhead

4. **Learning Opportunity**

   - Deep understanding of accessibility
   - Component composition patterns
   - State management in components
   - Design token architecture

5. **Flexibility**
   - Easy to modify and extend
   - No framework constraints
   - Custom behavior implementation
   - Full control over breaking changes

### Design System Architecture

#### 1. Design Tokens (CSS Variables)

```scss
// src/styles/themes/_tokens.scss
:root {
  // Colors
  --color-primary: #4f46e5;
  --color-secondary: #7c3aed;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;

  // Spacing
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  // Typography
  --font-family-base: 'Inter', sans-serif;
  --font-size-base: 1rem;
  --line-height-base: 1.5;

  // Borders
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.5rem;
  --border-radius-lg: 1rem;

  // Shadows
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  // Z-index
  --z-dropdown: 1000;
  --z-modal: 2000;
  --z-toast: 3000;
}
```

#### 2. Component Library Structure

```
src/app/shared/components/
├── button/
│   ├── button.component.ts
│   ├── button.component.html
│   ├── button.component.scss
│   ├── button.component.spec.ts
│   └── README.md
├── card/
├── modal/
├── toast/
└── ...
```

#### 3. Theme System

```typescript
// src/app/core/theme/theme.service.ts
export type ThemeId = 'lumen' | 'aurora' | 'nocturne' | 'cosmos';

export const THEMES = {
  lumen: {
    name: 'Lumen',
    description: 'Bright and energetic',
    colors: {
      /* ... */
    },
  },
  // ... other themes
} as const;

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private themeSignal = signal<ThemeId>('lumen');
  readonly currentTheme = this.themeSignal.asReadonly();

  setTheme(theme: ThemeId) {
    this.themeSignal.set(theme);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }
}
```

#### 4. BEM Naming Convention

```scss
// Block
.button {
  display: inline-flex;
  align-items: center;

  // Element
  &__icon {
    margin-right: var(--spacing-sm);
  }

  // Modifier
  &--primary {
    background-color: var(--color-primary);
  }

  &--large {
    padding: var(--spacing-lg);
  }
}
```

### Component Design Principles

1. **Standalone Components**

   - Self-contained with explicit imports
   - Reusable across application
   - Easy to test in isolation

2. **Signal-Based Inputs**

   - Use `input()` for reactive properties
   - Computed values with `computed()`
   - Output events with `output()`

3. **Accessibility First**

   - WCAG 2.1 AAA compliance
   - Semantic HTML
   - ARIA attributes
   - Keyboard navigation

4. **Composition Over Inheritance**

   - Small, focused components
   - Compose complex UIs from simple parts
   - Content projection with `<ng-content>`

5. **Consistent API**
   - Similar components have similar APIs
   - Predictable behavior
   - Clear naming conventions

## Implementation

### Component Example

```typescript
import { Component, input, output, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';
export type ButtonSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'app-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [class]="buttonClasses()"
      [type]="type()"
      [disabled]="disabled()"
      (click)="handleClick($event)"
    >
      <ng-content></ng-content>
    </button>
  `,
  styleUrls: ['./button.component.scss'],
})
export class ButtonComponent {
  variant = input<ButtonVariant>('primary');
  size = input<ButtonSize>('md');
  disabled = input<boolean>(false);
  type = input<'button' | 'submit' | 'reset'>('button');

  clicked = output<MouseEvent>();

  buttonClasses = computed(() =>
    [
      'button',
      `button--${this.variant()}`,
      `button--${this.size()}`,
      this.disabled() ? 'button--disabled' : '',
    ]
      .filter(Boolean)
      .join(' ')
  );

  handleClick(event: MouseEvent) {
    if (!this.disabled()) {
      this.clicked.emit(event);
    }
  }
}
```

## Consequences

### Positive

- Unique visual identity that stands out
- Demonstrates component development expertise
- Complete control over styling and behavior
- Optimal bundle size (only what we use)
- Deep accessibility implementation experience
- Portfolio piece in itself
- No license restrictions

### Negative

- More upfront development time
- Need to implement all features ourselves
- Potential for bugs in custom components
- No community support for components
- Must maintain and update ourselves

### Mitigation Strategies

1. **Comprehensive testing**: >90% coverage on components
2. **Accessibility testing**: Automated and manual audits
3. **Documentation**: README for each component
4. **Storybook**: Visual documentation and testing
5. **Incremental development**: Build as needed

## Component Library

### Completed Components (21 total)

**UI Components**:

- ButtonComponent (5 variants, 3 sizes)
- CardComponent (4 variants)
- ModalComponent (4 variants)
- ToastComponent (4 variants, 6 positions)
- LoadingSpinnerComponent (4 sizes, 4 variants)
- SkeletonComponent (3 shapes, 3 animations)
- BadgeComponent (6 variants, 3 sizes)
- IconComponent (90+ Heroicons, 6 sizes)
- TabsComponent (4 variants)
- BreadcrumbComponent (4 variants)

**Form Components**:

- InputComponent (7 types, validation)
- TextareaComponent (auto-resize)
- SelectComponent (single/multi, searchable)
- CheckboxComponent (indeterminate)
- RadioComponent (arrow navigation)
- FormFieldComponent (error handling)

**Layout Components**:

- ContainerComponent (5 max-widths)
- GridComponent (12-column)
- StackComponent (vertical/horizontal)
- DividerComponent (with labels)

### Quality Metrics

- **Unit Tests**: 2,364+ passing tests
- **Coverage**: >95% statement/line coverage
- **E2E Tests**: 170 passing tests
- **Accessibility**: 100% WCAG 2.1 AAA compliant
- **Documentation**: 21 component READMEs + Storybook
- **Themes**: 4 themes with AAA contrast ratios

## Alternatives Considered

1. **Angular Material**: Rejected

   - Pros: Mature, accessible, well-tested
   - Cons: Heavy bundle, opinionated styling, "Material" look

2. **PrimeNG**: Rejected

   - Pros: Comprehensive component set
   - Cons: Heavy bundle, less modern, licensing

3. **Tailwind Components**: Rejected

   - Pros: Utility-first, flexible
   - Cons: Not Angular-specific, less portfolio value

4. **ng-bootstrap**: Rejected
   - Pros: Bootstrap ecosystem
   - Cons: Bootstrap look, heavier than custom

## Related Decisions

- [ADR 001: Standalone Components](./001-standalone-components.md)
- [ADR 002: NgRx SignalStore](./002-ngrx-signal-store.md)

## References

- [Angular Component Guide](https://angular.dev/guide/components)
- [WCAG 2.1 AAA Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [BEM Methodology](https://getbem.com/)
- [Design Tokens](https://designtokens.org/)
- [CSS Variables](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
