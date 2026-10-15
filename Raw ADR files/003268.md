# ADR-005: Micro-frontend Architecture Pattern

## Status
Accepted (Applied at CSG International & Cinglevue)

## Context
Enterprise applications at CSG and Cinglevue required:
- Multiple teams working independently
- Different release cycles per feature area
- Gradual migration from legacy systems
- Technology flexibility (Angular + React coexistence at Cinglevue)
- Independent deployability

Traditional monolithic frontend approaches caused:
- Merge conflicts across teams
- Coupled release schedules
- Slow build times (45+ minutes)
- Difficulty in legacy migration

## Decision
Implement micro-frontend architecture using Module Federation (CSG) and Angular Elements (Cinglevue).

### Pattern 1: Module Federation (CSG)
```javascript
// webpack.config.js - Shell Application
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'shell',
      remotes: {
        customerModule: 'customer@http://localhost:3001/remoteEntry.js',
        billingModule: 'billing@http://localhost:3002/remoteEntry.js',
        analyticsModule: 'analytics@http://localhost:3003/remoteEntry.js'
      },
      shared: ['@angular/core', '@angular/common', '@angular/router']
    })
  ]
};

// Remote module exposure
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'customer',
      filename: 'remoteEntry.js',
      exposes: {
        './CustomerModule': './src/app/customer/customer.module.ts'
      }
    })
  ]
};
```

### Pattern 2: Angular Elements (Cinglevue)
```typescript
// Legacy wrapper for Angular Elements
@NgModule({
  declarations: [StudentDashboardComponent],
  entryComponents: [StudentDashboardComponent]
})
export class StudentDashboardModule {
  constructor(private injector: Injector) {
    const element = createCustomElement(StudentDashboardComponent, { injector });
    customElements.define('student-dashboard', element);
  }
}
```

### Shared State Strategy
```typescript
// Cross-MFE event bus
@Injectable({ providedIn: 'root' })
export class MicroFrontendEventBus {
  private events$ = new Subject<MFEEvent>();

  emit(event: MFEEvent): void {
    this.events$.next(event);
    window.dispatchEvent(new CustomEvent('mfe-event', { detail: event }));
  }

  on<T>(eventType: string): Observable<T> {
    return this.events$.pipe(
      filter(e => e.type === eventType),
      map(e => e.payload as T)
    );
  }
}
```

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Shell Application                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Routing │  │   Auth   │  │  Shared  │  │  Event   │    │
│  │          │  │  State   │  │   UI     │  │   Bus    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │Customer │    │ Billing │    │Analytics│    │ Support │
    │ Module  │    │ Module  │    │ Module  │    │ Module  │
    │(Team A) │    │(Team B) │    │(Team C) │    │(Team D) │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

## Alternatives Considered

### 1. Iframe-based Integration
- **Pros:** Complete isolation
- **Cons:** Poor UX, communication overhead, styling issues
- **Rejected:** User experience unacceptable

### 2. NPM Package per Feature
- **Pros:** Simple, well-understood
- **Cons:** Coupled releases, version conflicts
- **Rejected:** Doesn't solve team independence

### 3. Monorepo with Nx
- **Pros:** Shared code, consistent tooling
- **Cons:** Still coupled builds without MFE
- **Used:** Combined with MFE for best of both

## Consequences

### Positive
- Teams deploy independently (CSG: 75% faster deployments)
- Parallel development without merge conflicts
- Gradual migration of 100K+ LOC (Cinglevue)
- Technology flexibility when needed
- Fault isolation (one MFE crash doesn't break app)

### Negative
- Initial setup complexity
- Shared dependency version management
- Larger total bundle if not optimized
- Need for consistent design system

### Metrics (CSG)
| Metric | Before | After |
|--------|--------|-------|
| Build Time | 45min | 8min per MFE |
| Deploy Frequency | Weekly | Daily per team |
| Team Coupling | High | Low |
| Developer Satisfaction | 65% | 89% |

### Metrics (Cinglevue)
| Metric | Value |
|--------|-------|
| Modules Migrated | 20+ |
| Legacy Code Replaced | 100,000+ LOC |
| Migration Duration | 14 months |
| Zero Downtime | Yes |

## References
- [Module Federation Documentation](https://webpack.js.org/concepts/module-federation/)
- [Angular Elements Guide](https://angular.io/guide/elements)
- [Micro Frontends](https://micro-frontends.org/)
