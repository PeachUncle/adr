# ADR 001: Standalone Components

**Date**: 2025-12-09
**Status**: Accepted
**Decision Makers**: Jason Moody

## Context

Angular introduced standalone components in v14 and made them the recommended approach in v15+. With Angular v21, we need to decide whether to use the traditional NgModule-based architecture or adopt standalone components for the portfolio application.

## Decision

We will use **standalone components** exclusively throughout the application, avoiding NgModules wherever possible.

## Rationale

### Benefits of Standalone Components

1. **Simpler Mental Model**

   - No need to manage NgModules and their imports/exports
   - Component dependencies are declared directly in the component
   - Clear, explicit dependency graph

2. **Better Tree-Shaking**

   - Unused components are more easily eliminated from bundles
   - Smaller bundle sizes in production
   - More granular code splitting

3. **Improved Developer Experience**

   - Less boilerplate code (no NgModule declarations)
   - Faster compilation times
   - Better IDE autocomplete and type checking
   - Easier to understand component dependencies

4. **Future-Proof**

   - Angular team recommends standalone as the default
   - NgModules are in maintenance mode
   - Aligns with Angular's long-term vision

5. **Easier Testing**
   - No need to create test modules
   - Simpler test setup with `TestBed.configureTestingModule()`
   - Components can be tested in isolation more easily

### Trade-offs

1. **Migration Path**: No migration needed (greenfield project)
2. **Community Resources**: Some older tutorials use NgModules, but v21 docs prioritize standalone
3. **Team Knowledge**: Standalone is the modern standard and should be learned

## Implementation

### Component Pattern

```typescript
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-example',
  standalone: true,
  imports: [CommonModule, OtherComponent],
  templateUrl: './example.component.html',
})
export class ExampleComponent {}
```

### Service Pattern

Services remain injectable without changes:

```typescript
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ExampleService {}
```

### Routing Configuration

```typescript
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'example',
    loadComponent: () => import('./example/example.component').then((m) => m.ExampleComponent),
  },
];
```

## Consequences

### Positive

- Cleaner, more maintainable codebase
- Faster build times and smaller bundles
- Better alignment with Angular's future
- Easier onboarding for new developers
- Simpler testing setup

### Negative

- Need to explicitly import dependencies in each component (not shared via modules)
- Some third-party libraries may still require NgModules (handled via compatibility layer)

## Alternatives Considered

1. **NgModule-based architecture**: Rejected due to added complexity and being legacy approach
2. **Hybrid approach (mix of modules and standalone)**: Rejected due to inconsistency and confusion

## Related Decisions

- [ADR 002: NgRx SignalStore](./002-ngrx-signal-store.md)
- [ADR 003: Mockend Pattern](./003-mockend-pattern.md)

## References

- [Angular Standalone Components Guide](https://angular.dev/guide/components/importing)
- [Angular v21 Documentation](https://v21.angular.dev)
- [Standalone Migration Guide](https://angular.dev/reference/migrations/standalone)
