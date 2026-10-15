# ADR 002: NgRx SignalStore for State Management

**Date**: 2025-12-09
**Status**: Accepted
**Decision Makers**: Jason Moody

## Context

The portfolio application needs a state management solution for managing theme preferences, project data, case studies, and other application state. We need to choose between various state management approaches available in Angular v21.

## Decision

We will use **NgRx SignalStore** as our primary state management solution for domain-specific state, with Angular Signals for component-local state.

## Rationale

### Why NgRx SignalStore

1. **Signal-Based Reactivity**

   - Built on Angular Signals (v16+)
   - Automatic change detection optimization
   - Fine-grained reactivity without zone.js overhead
   - Native integration with Angular's signal-based features

2. **Lightweight and Simple**

   - Much simpler than traditional NgRx Store
   - No actions, reducers, or effects boilerplate
   - Direct state updates with computed values
   - Smaller bundle size (~5KB vs ~50KB for full NgRx)

3. **Type-Safe**

   - Full TypeScript support with type inference
   - Compile-time type checking
   - Excellent IDE autocomplete
   - No need for type guards or discriminated unions

4. **Composable**

   - Features can be added via plugins/extensions
   - Easy to create reusable store patterns
   - Clean separation of concerns
   - Supports rxMethod for async operations

5. **Developer Experience**
   - Less boilerplate than traditional NgRx
   - Easier to learn and onboard
   - Better debugging with Angular DevTools
   - Clear, readable code

### Comparison with Alternatives

#### vs. Traditional NgRx Store

- ❌ NgRx Store: Complex setup, lots of boilerplate, actions/reducers/effects
- ✅ SignalStore: Simple API, direct updates, signal-based reactivity

#### vs. Component State (Signals)

- ✅ Component Signals: Perfect for local component state
- ✅ SignalStore: Better for shared state across components and routes

#### vs. Services with BehaviorSubject

- ❌ Services: Manual subscriptions, memory leak risks, verbose
- ✅ SignalStore: Automatic cleanup, signal-based, cleaner API

#### vs. Akita or Elf

- Similar philosophies but SignalStore has first-party Angular support
- Better integration with Angular DevTools
- Official Angular team support and maintenance

## Implementation

### Store Pattern

```typescript
import { signalStore, withState, withComputed, withMethods } from '@ngrx/signals';
import { rxMethod } from '@ngrx/signals/rxjs-interop';
import { computed, inject } from '@angular/core';
import { pipe, switchMap, tap } from 'rxjs';

interface ProjectsState {
  projects: Project[];
  isLoading: boolean;
  error: string | null;
  selectedId: string | null;
}

const initialState: ProjectsState = {
  projects: [],
  isLoading: false,
  error: null,
  selectedId: null,
};

export const ProjectsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    selectedProject: computed(() => store.projects().find((p) => p.id === store.selectedId())),
  })),
  withMethods((store, projectService = inject(ProjectService)) => ({
    loadProjects: rxMethod<void>(
      pipe(
        tap(() => store.update({ isLoading: true })),
        switchMap(() => projectService.getAll()),
        tap({
          next: (projects) => store.update({ projects, isLoading: false, error: null }),
          error: (error) => store.update({ isLoading: false, error: error.message }),
        })
      )
    ),
    selectProject(id: string) {
      store.update({ selectedId: id });
    },
  }))
);
```

### Component Usage

```typescript
import { Component, inject, OnInit } from '@angular/core';
import { ProjectsStore } from './projects.store';

@Component({
  selector: 'app-projects',
  standalone: true,
  template: `
    @if (store.isLoading()) {
    <p>Loading...</p>
    } @else if (store.error()) {
    <p>Error: {{ store.error() }}</p>
    } @else { @for (project of store.projects(); track project.id) {
    <div>{{ project.name }}</div>
    } }
  `,
})
export class ProjectsComponent implements OnInit {
  readonly store = inject(ProjectsStore);

  ngOnInit() {
    this.store.loadProjects();
  }
}
```

## Consequences

### Positive

- Simpler state management with less boilerplate
- Signal-based reactivity improves performance
- Type-safe with excellent developer experience
- Easy to test and maintain
- Official Angular support and future-proof

### Negative

- Newer API with less community resources (compared to traditional NgRx)
- Team needs to learn SignalStore patterns
- Some advanced NgRx features (entity adapters, router store) require additional setup

### Mitigation

- Document store patterns in codebase
- Create reusable store utilities
- Provide examples and best practices
- Use traditional services for simple state

## Guidelines

### When to Use SignalStore

✅ Use for:

- Domain state (projects, case studies, user preferences)
- Shared state across multiple components
- State that needs to be persisted
- Complex state with computed values
- Async data fetching with loading/error states

❌ Don't use for:

- Simple component-local state (use signals instead)
- Form state (use reactive forms)
- One-time data fetching (use services directly)

### Store Organization

```
src/app/
├── core/
│   └── theme/
│       └── theme.service.ts (SignalStore for theme state)
└── features/
    ├── projects/
    │   ├── projects.store.ts
    │   └── projects.service.ts
    └── case-studies/
        ├── case-studies.store.ts
        └── case-studies.service.ts
```

## Alternatives Considered

1. **Traditional NgRx Store**: Rejected due to complexity and boilerplate
2. **Akita**: Good alternative but not first-party Angular
3. **Elf**: Similar to Akita, lacks official support
4. **Services with BehaviorSubject**: Too manual, potential memory leaks
5. **Component State Only**: Not suitable for shared/persistent state

## Related Decisions

- [ADR 001: Standalone Components](./001-standalone-components.md)
- [ADR 004: Custom Design System](./004-custom-design-system.md)

## References

- [NgRx SignalStore Documentation](https://ngrx.io/guide/signals/signal-store)
- [Angular Signals Guide](https://angular.dev/guide/signals)
- [NgRx SignalStore Deep Dive](https://ngrx.io/guide/signals)
