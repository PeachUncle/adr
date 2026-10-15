# ADR-004: Performance Optimization Strategy

## Status
Accepted (January 2025)

## Context
CompileForge must handle:
- 10,000+ concurrent users
- 50,000+ monthly submissions
- Large data tables (1000+ rows)
- Complex forms with real-time validation
- Sub-2-second initial load time
- 95+ Lighthouse score target

Initial prototype had:
- 8-second load time
- 68 Lighthouse score
- Janky scrolling on large lists
- 220ms average re-render time

## Decision
Implement comprehensive performance optimization across multiple layers.

### 1. Bundle Optimization
```typescript
// Route-level code splitting
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component')
  },
  {
    path: 'grading',
    loadComponent: () => import('./grading/grading.component'),
    // Preload after initial render
    data: { preload: true }
  }
];

// Custom preloading strategy
@Injectable()
export class SelectivePreloadStrategy implements PreloadAllModules {
  preload(route: Route, load: () => Observable<any>) {
    return route.data?.['preload'] ? load() : of(null);
  }
}
```

### 2. Change Detection Optimization
```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @for (item of items(); track item.id) {
      <app-item [data]="item" />
    }
  `
})
export class ListComponent {
  items = input.required<Item[]>();
}
```

### 3. Virtual Scrolling
```typescript
@Component({
  template: `
    <cdk-virtual-scroll-viewport itemSize="72" class="viewport">
      <app-submission-row
        *cdkVirtualFor="let submission of submissions; trackBy: trackById"
        [submission]="submission"
      />
    </cdk-virtual-scroll-viewport>
  `
})
export class SubmissionListComponent {
  @Input() submissions: Submission[] = [];
  trackById = (index: number, item: Submission) => item.id;
}
```

### 4. Image Optimization
- WebP format with PNG fallback
- Lazy loading with Intersection Observer
- Responsive images with srcset
- CDN delivery via Cloudflare

### 5. Caching Strategy
```typescript
// HTTP interceptor for caching
@Injectable()
export class CacheInterceptor implements HttpInterceptor {
  private cache = new Map<string, HttpResponse<any>>();

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    if (req.method !== 'GET') return next.handle(req);

    const cached = this.cache.get(req.urlWithParams);
    if (cached) return of(cached.clone());

    return next.handle(req).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          this.cache.set(req.urlWithParams, event.clone());
        }
      })
    );
  }
}
```

## Alternatives Considered

### SSR with Angular Universal
- **Pros:** Faster FCP, better SEO
- **Cons:** Complex deployment, server costs
- **Deferred:** Will implement in Phase 2 if needed

### Web Workers for Heavy Computation
- **Pros:** Offload main thread
- **Cons:** Complexity, data serialization overhead
- **Rejected:** Not needed after other optimizations

## Consequences

### Results Achieved
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial Load | 8s | <2s | 75% |
| Lighthouse | 68 | 95 | +27 points |
| Bundle Size | 850KB | 485KB | 43% |
| Re-render Time | 220ms | 18ms | 92% |
| Time to Interactive | 6.2s | 1.8s | 71% |

### Positive
- Excellent user experience on all devices
- Reduced infrastructure costs (less bandwidth)
- Better Core Web Vitals scores
- Improved SEO potential

### Negative
- More complex codebase
- Need to maintain performance budget
- Virtual scrolling requires fixed heights

### Monitoring
- Lighthouse CI in GitHub Actions
- Web Vitals tracking in production
- Performance budget enforcement

## References
- [Angular Performance Checklist](https://angular.io/guide/performance)
- [Web Vitals](https://web.dev/vitals/)
