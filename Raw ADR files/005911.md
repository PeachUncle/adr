# ADR-0004: Signal-based State Management

## Status

Accepted

## Context

State management is a critical aspect of any Angular application, especially one involving complex data visualizations. The World Demographics Visualization application needs to manage:

1. Hierarchical data for countries, regions, and continents
2. User interactions like selecting countries and changing metrics
3. Loading and error states during data fetching
4. Component communication across different levels

Angular has introduced Signals as a first-class primitive for fine-grained reactivity in version 16+. We need to decide on our state management approach for this application.

## Decision

We will use Angular's Signals as our primary state management solution, combined with the facade pattern to encapsulate state logic. This approach includes:

1. Using `signal()` for component-level state
2. Using facades to encapsulate domain state and operations
3. Using computed signals for derived state
4. Using effects for side effects when state changes
5. Avoiding external state management libraries like NgRx unless complexity increases significantly

Example implementation:

```typescript
// In a component
export class WorldDemographicsComponent {
  private facade = inject(WorldDemographicsFacade);

  // State signals
  dataset = this.facade.dataset;
  isLoading = this.facade.isLoading;
  error = this.facade.error;
  sizeBy = signal<'population' | 'land_area_km2'>('population');
  selectedCountry = signal<CountryData | null>(null);

  onSizeByChanged(metric: 'population' | 'land_area_km2'): void {
    this.sizeBy.set(metric);
  }
}

// In a facade
@Injectable({ providedIn: 'root' })
export class WorldDemographicsFacade {
  private dataVisualizationService = inject(DataVisualizationService);

  // State signals
  private _dataset = signal<CountryData[] | null>(null);
  private _isLoading = signal<boolean>(false);
  private _error = signal<string | null>(null);

  // Public API
  dataset = this._dataset.asReadonly();
  isLoading = this._isLoading.asReadonly();
  error = this._error.asReadonly();

  loadWorldDemographics(): void {
    this._isLoading.set(true);
    this._error.set(null);

    this.dataVisualizationService.getWorldDemographics().subscribe({
      next: (data) => {
        this._dataset.set(data);
        this._isLoading.set(false);
      },
      error: (err) => {
        this._error.set(err.message);
        this._isLoading.set(false);
      },
    });
  }
}
```

## Consequences

### Positive

- Fine-grained reactivity with better performance than traditional RxJS-only approaches
- Simplified state management with less boilerplate compared to NgRx
- Better TypeScript integration and type safety
- Aligns with Angular's future direction
- Easier debugging as state changes are explicit and traceable
- Reduced learning curve compared to external state management libraries

### Negative

- Signals are relatively new in Angular, with evolving best practices
- May require refactoring if application complexity grows beyond what signals can handle efficiently
- Less community resources compared to established solutions like NgRx
- Potential for state management code to be scattered if not carefully organized

### Neutral

- Different mental model from RxJS-only approaches
- Team needs to learn and adopt signals pattern
- May need to combine with RxJS for certain async operations

## Alternatives Considered

### NgRx/Redux Pattern

A full Redux implementation with NgRx would provide more structure for complex state but would introduce significant boilerplate and complexity that isn't justified for our current needs.

### RxJS-only Approach

Using BehaviorSubjects and observables directly is a common Angular pattern but lacks the performance benefits and ergonomics of signals.

### Component Inputs/Outputs Only

For very simple applications, relying solely on component inputs and outputs might be sufficient, but this approach doesn't scale well for applications with complex state requirements.

## References

- [Angular Signals Documentation](https://angular.io/guide/signals)
- [Angular Reactive State Management](https://angular.io/guide/state-management)
- [Facade Pattern in Angular](https://thomasburlesonia.medium.com/ngrx-facades-better-state-management-82a04b9a1e39)
- [Signals vs. RxJS](https://blog.angular.io/angular-signals-8d1f5fc514a1)
