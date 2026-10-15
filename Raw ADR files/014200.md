# ADR 0004: Different State Management Patterns Per App

**Status**: Accepted

**Date**: 2025-11-08 (Documented retroactively)

**Deciders**: AI Agent (experimental learning approach)

## Context

The workspace contains two applications built at different times:
- **Reward Chart** (built first): Complex state with multiple streams
- **Family Calendar** (built later): Simpler state requirements

Angular offers multiple state management approaches:
1. RxJS BehaviorSubject/Observables
2. Angular Signals (introduced in Angular 16+)
3. Third-party libraries (NgRx, Akita, etc.)

## Decision

Use **different state management patterns** for each app based on their specific needs and timing:
- **Reward Chart**: RxJS BehaviorSubject
- **Family Calendar**: Angular Signals

## Rationale

### Chosen: Mixed Approach (RxJS + Signals)

**Advantages**:
- ✅ **Right Tool for the Job**: Each app uses best-fit pattern
- ✅ **Learning Opportunity**: Playground workspace allows experimentation
- ✅ **No Migration Needed**: Reward Chart works well with RxJS
- ✅ **Modern Adoption**: Signals showcase Angular's latest reactivity
- ✅ **Performance**: Signals offer fine-grained reactivity

**Disadvantages**:
- ⚠️ **Inconsistency**: Different patterns confuse developers switching between apps
- ⚠️ **Documentation Overhead**: Must explain both approaches

### Rejected: Standardize on RxJS

**Why Rejected**:
- Signals are Angular's future direction
- Simpler cases don't need RxJS complexity
- Missing opportunity to learn Signals

### Rejected: Standardize on Signals

**Why Rejected**:
- Reward Chart works perfectly with RxJS
- Migration effort not justified for working code
- RxJS still valuable for complex async operations

### Rejected: Third-Party State Management

**Why Rejected**:
- NgRx/Akita overkill for small personal apps
- Additional bundle size
- More complexity than needed

## Consequences

### Reward Chart - RxJS BehaviorSubject Pattern

**Why RxJS Fits**:
- Complex data with multiple related streams
- Need for observable composition
- Built when Angular 20.3 was new (Signals less established)

**Implementation**:
```typescript
export class ChartDataService {
  private chartDataSubject = new BehaviorSubject<ChartData>(initialData);
  public chartData$: Observable<ChartData> = this.chartDataSubject.asObservable();

  updateStars(memberId: string, day: string, habitIndex: number, value: boolean) {
    const current = this.chartDataSubject.value;
    // ... update logic
    this.chartDataSubject.next(updatedData);
  }
}
```

**Usage in Components**:
```typescript
export class ChildCardComponent implements OnInit {
  chartData: ChartData | null = null;

  ngOnInit(): void {
    this.chartDataService.chartData$.subscribe(data => {
      this.chartData = data;
    });
  }
}
```

**Characteristics**:
- Observable subscriptions in components
- BehaviorSubject for current value access
- Good for complex data transformations

### Family Calendar - Angular Signals Pattern

**Why Signals Fit**:
- Simpler state (list of events)
- Built later when Signals were mature
- Fine-grained reactivity for calendar updates
- Less boilerplate than RxJS

**Implementation**:
```typescript
export class EventService {
  private events = signal<CalendarEvent[]>([]);
  readonly eventsSignal = this.events.asReadonly();

  async addEvent(event: CalendarEvent): Promise<void> {
    const newEvents = [...this.events(), { ...event, id: this.generateId() }];
    this.events.set(newEvents);
  }

  getEvents(): CalendarEvent[] {
    return this.events();
  }
}
```

**Usage in Components**:
```typescript
export class CalendarComponent {
  events = this.eventService.eventsSignal;

  // Signal automatically updates template when events change
}
```

**Characteristics**:
- Signals for reactive state
- No subscriptions needed
- Automatic change detection

### Positive Consequences

**Learning Value**: Developers (AI agents) understand both patterns
**Flexibility**: Can choose best pattern for future apps
**Modern Angular**: Showcases latest Angular features (Signals)
**No Breaking Changes**: Reward Chart continues working perfectly

### Negative Consequences

**Mental Context Switching**: Different patterns when working across apps
**No Shared State Service**: Can't easily extract common pattern to library
**Documentation Burden**: Must explain "why different?" in docs

## Implementation

**Current State**:
- Reward Chart: `apps/reward-chart/src/app/services/chart-data.service.ts` (RxJS)
- Family Calendar: `apps/family-calendar/src/app/services/event.service.ts` (Signals)

**Future Considerations**:
- New apps can choose either pattern based on requirements
- Could migrate Reward Chart to Signals if needed (but no strong reason to)
- Hybrid approach possible (RxJS for async, Signals for sync state)

## Follow-up

- ✅ Both patterns working well in production
- ✅ Documented differences for AI agents
- 🔮 Future: Consider hybrid approach (Signals + RxJS interop)
- 🔮 Future: If creating shared library, support both patterns

## References

- [Angular Signals Guide](https://angular.dev/guide/signals)
- [RxJS BehaviorSubject](https://rxjs.dev/api/index/class/BehaviorSubject)
- [Angular Signals + RxJS Interop](https://angular.dev/guide/signals/rxjs-interop)
- Implementations: See service files in respective apps
