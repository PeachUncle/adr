# ADR-002: State Management Strategy

## Status
Accepted

## Date
2024-07-29

## Context

Our Angular application needs a consistent approach to managing application state. We need to handle:
- User authentication state
- UI state (loading, errors)
- Data from APIs
- Form state
- Component communication

The application is expected to grow with multiple features and team members, so we need a scalable and maintainable approach.

## Decision

We decided to use a **Service-based State Management** approach with RxJS Observables:

- **BehaviorSubject** for state storage
- **Observable streams** for state exposure
- **Service layer** for state management logic
- **Reactive forms** for form state
- **Local component state** for simple UI state

## Consequences

### Positive
- **Simple to understand**: No additional learning curve for team members familiar with Angular services
- **Flexible**: Can easily adapt to different state management needs
- **Performance**: Efficient with OnPush change detection strategy
- **Type safety**: Full TypeScript support
- **Testable**: Easy to unit test services in isolation
- **Gradual adoption**: Can introduce more complex state management later if needed

### Negative
- **Manual boilerplate**: More code required compared to dedicated state management libraries
- **No time-travel debugging**: Unlike Redux DevTools
- **Memory leaks**: Requires careful subscription management
- **No built-in middleware**: Custom implementation needed for logging, persistence

## Alternatives Considered

### NgRx
- **Pros**: Powerful DevTools, predictable state updates, great for complex apps
- **Cons**: High learning curve, verbose boilerplate, overkill for current needs

### Akita
- **Pros**: Less boilerplate than NgRx, good DevTools
- **Cons**: Additional dependency, smaller community

### Simple Services (No Observables)
- **Pros**: Very simple, minimal code
- **Cons**: No reactivity, manual change detection, harder to test

## Implementation Pattern

### State Service Example
```typescript
@Injectable({
  providedIn: 'root'
})
export class UserStateService {
  private readonly usersSubject = new BehaviorSubject<User[]>([]);
  private readonly loadingSubject = new BehaviorSubject<boolean>(false);
  private readonly errorSubject = new BehaviorSubject<string | null>(null);

  // Public observables
  readonly users$ = this.usersSubject.asObservable();
  readonly loading$ = this.loadingSubject.asObservable();
  readonly error$ = this.errorSubject.asObservable();

  // Computed state
  readonly viewModel$ = combineLatest([
    this.users$,
    this.loading$,
    this.error$
  ]).pipe(
    map(([users, loading, error]) => ({ users, loading, error }))
  );

  // State mutations
  setUsers(users: User[]): void {
    this.usersSubject.next(users);
  }

  setLoading(loading: boolean): void {
    this.loadingSubject.next(loading);
  }
}
```

### Component Usage
```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserListComponent {
  readonly vm$ = this.userState.viewModel$;

  constructor(private userState: UserStateService) {}
}
```

## Guidelines

### State Service Structure
1. Use `BehaviorSubject` for state storage
2. Expose state via `asObservable()`
3. Provide methods for state mutations
4. Use `combineLatest` for computed state
5. Implement proper error handling

### Subscription Management
1. Use `async` pipe in templates when possible
2. Implement `OnDestroy` for manual subscriptions
3. Use `takeUntil` pattern for cleanup
4. Consider `shareReplay` for expensive operations

### Testing
1. Test state services in isolation
2. Mock dependencies with jasmine spies
3. Test state transitions and side effects
4. Verify observable emissions

## Migration Path

If the application grows in complexity, we can gradually migrate to NgRx:
1. Keep existing service-based state for simple features
2. Introduce NgRx for complex features requiring:
   - Time-travel debugging
   - Complex state interactions
   - Advanced middleware needs

## Related Decisions
- ADR-001: Frontend Framework Selection (Angular with RxJS)
- ADR-004: Testing Strategy (Testing observables with marble testing)

## Review Date
This decision should be reviewed in 6 months (January 2025) or when the application reaches significant complexity that warrants a more sophisticated state management solution.