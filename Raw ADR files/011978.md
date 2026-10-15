# ADR 003: Mockend Pattern for Development

**Date**: 2025-12-09
**Status**: Accepted
**Decision Makers**: Jason Moody

## Context

The portfolio is a static site deployed to GitHub Pages without a backend. We need a way to develop and test features that would normally require an API, such as project listings, case studies, and contact form submissions, without maintaining a separate backend service.

## Decision

We will use the **Mockend pattern** - services that return mock data in development and can be easily swapped with real API calls in production if needed.

## Rationale

### Why Mockend Pattern

1. **Rapid Development**

   - No backend setup required
   - Instant data availability
   - Fast iteration cycles
   - Easy to modify mock data

2. **Realistic Development Environment**

   - Simulates API responses
   - Can mimic loading states and errors
   - Realistic async behavior with observables
   - Test error handling without backend

3. **Production-Ready Structure**

   - Service abstraction layer ready for real APIs
   - Same interfaces for mock and real data
   - Easy migration path if backend is added
   - Environment-based configuration

4. **Testing Benefits**

   - Consistent test data
   - No external dependencies for tests
   - Predictable behavior
   - Easy to create edge case scenarios

5. **Static Hosting Compatible**
   - Works perfectly with GitHub Pages
   - No server-side requirements
   - All data bundled with application
   - Offline-first by default

### Alternative Approaches Considered

#### Real Backend (Rejected)

- Adds operational complexity
- Requires hosting costs
- Overkill for static portfolio
- Maintenance burden

#### JSON Files Only (Rejected)

- No loading states or error simulation
- Harder to evolve to real API
- No abstraction layer
- Direct data coupling

#### Public Mock APIs (Rejected)

- External dependency
- Rate limiting issues
- Unreliable availability
- No control over data

## Implementation

### Service Pattern

```typescript
import { Injectable, inject } from '@angular/core';
import { Observable, of, delay, throwError } from 'rxjs';
import { environment } from '@environments/environment';

export interface Project {
  id: string;
  title: string;
  description: string;
  technologies: string[];
  // ... other fields
}

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  private readonly mockData: Project[] = [
    {
      id: '1',
      title: 'Portfolio Website',
      description: 'Personal portfolio built with Angular',
      technologies: ['Angular', 'TypeScript', 'SCSS'],
    },
    // ... more projects
  ];

  /**
   * Fetches all projects
   * In production, this would call: this.http.get<Project[]>('/api/projects')
   */
  getAll(): Observable<Project[]> {
    if (!environment.production) {
      // Simulate network delay in development
      return of(this.mockData).pipe(delay(500));
    }

    // Production: would fetch from real API
    // return this.http.get<Project[]>('/api/projects');
    return of(this.mockData);
  }

  /**
   * Fetches a single project by ID
   */
  getById(id: string): Observable<Project | null> {
    const project = this.mockData.find((p) => p.id === id) ?? null;

    if (!environment.production) {
      return of(project).pipe(delay(300));
    }

    // Production: would fetch from real API
    // return this.http.get<Project>(`/api/projects/${id}`);
    return of(project);
  }

  /**
   * Simulates error scenarios for testing
   */
  getWithError(): Observable<never> {
    return throwError(() => new Error('Failed to fetch projects'));
  }
}
```

### Mock Data Organization

```
src/app/
├── core/
│   └── services/
│       └── project.service.ts (service with mock data)
└── shared/
    └── models/
        └── project.model.ts (TypeScript interfaces)
```

### Environment-Based Behavior

```typescript
// environment.ts (development)
export const environment = {
  production: false,
  apiUrl: '', // Not needed for mock
  mockDelay: 500, // Simulate network latency
};

// environment.prod.ts (production)
export const environment = {
  production: true,
  apiUrl: 'https://api.example.com', // If real API is added later
  mockDelay: 0,
};
```

## Consequences

### Positive

- Fast development without backend setup
- Realistic async behavior for testing
- Easy to simulate loading and error states
- Clean migration path to real API
- Works seamlessly with static hosting
- Predictable, version-controlled data

### Negative

- Mock data must be manually maintained
- Can diverge from real API behavior (if added later)
- Bundle size includes mock data (minimal impact)
- No dynamic data in production

### Mitigation Strategies

1. **Keep mock data realistic**: Model after actual API responses
2. **Document data structure**: Clear TypeScript interfaces
3. **Use environment flags**: Easy toggle between mock and real
4. **Version control**: Track mock data changes
5. **Extract to JSON**: Move large datasets to static JSON files

## Migration Path

If a real backend is added later:

1. **Phase 1**: Keep service interface, swap implementation

   ```typescript
   getAll(): Observable<Project[]> {
     return this.http.get<Project[]>(`${environment.apiUrl}/projects`);
   }
   ```

2. **Phase 2**: Remove mock data (or keep for fallback)
3. **Phase 3**: Update tests to use real API or keep mocks

## Guidelines

### When to Use Mockend

✅ Use for:

- Project listings
- Case studies data
- Static content (skills, experience)
- User preferences (localStorage-backed)

❌ Don't use for:

- Contact form (use EmailJS or serverless)
- Analytics (use GA4)
- Authentication (if added, use real service)
- Real-time features (if added, use WebSockets/SSE)

### Mock Data Best Practices

1. **Realistic data**: Use actual project information
2. **Complete objects**: Include all required fields
3. **Type safety**: Define TypeScript interfaces
4. **Variety**: Include different scenarios (empty states, errors)
5. **Consistency**: Match production data structure

## Testing Strategy

```typescript
describe('ProjectService', () => {
  let service: ProjectService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProjectService);
  });

  it('should return all projects', (done) => {
    service.getAll().subscribe((projects) => {
      expect(projects.length).toBeGreaterThan(0);
      expect(projects[0]).toHaveProperty('id');
      done();
    });
  });

  it('should return project by id', (done) => {
    service.getById('1').subscribe((project) => {
      expect(project).toBeTruthy();
      expect(project?.id).toBe('1');
      done();
    });
  });
});
```

## Alternatives Considered

1. **Real Backend (Express/NestJS)**: Too complex for static portfolio
2. **Firebase/Supabase**: Unnecessary for static data
3. **GraphQL mocks**: Overkill for simple data needs
4. **MSW (Mock Service Worker)**: Good for testing but not needed for development

## Related Decisions

- [ADR 002: NgRx SignalStore](./002-ngrx-signal-store.md) - Store uses services as data source
- [ADR 001: Standalone Components](./001-standalone-components.md) - Services inject directly

## References

- [Angular HttpClient](https://angular.dev/guide/http)
- [RxJS Observable](https://rxjs.dev/guide/observable)
- [Angular Environment Files](https://angular.dev/tools/cli/environments)
