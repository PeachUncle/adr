# ADR-002: 100% Standalone Components Architecture

## Status
Accepted (January 2025)

## Context
Angular 14+ introduced standalone components as an alternative to NgModules. For CompileForge, we needed to decide on our component architecture approach:

- Legacy Angular apps use NgModules for organization
- Standalone components offer simpler mental model
- Angular 17+ defaults to standalone in new projects
- Team had mixed experience with both patterns

## Decision
Adopt 100% standalone component architecture with zero NgModules (except for third-party library requirements).

### Component Structure
```typescript
@Component({
  selector: 'app-submission-card',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    GradeDisplayComponent,
    StatusBadgeComponent
  ],
  template: `...`,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SubmissionCardComponent {
  submission = input.required<Submission>();
  onGrade = output<GradeEvent>();
}
```

### Routing Configuration
```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component')
      .then(m => m.DashboardComponent)
  },
  {
    path: 'submissions',
    loadChildren: () => import('./submissions/submissions.routes')
      .then(m => m.SUBMISSIONS_ROUTES)
  }
];
```

## Alternatives Considered

### 1. Traditional NgModules
- **Pros:** Familiar pattern, existing documentation
- **Cons:** Verbose, harder tree-shaking, slower builds
- **Rejected:** Deprecated pattern, Angular moving away

### 2. Hybrid Approach
- **Pros:** Gradual migration, lower risk
- **Cons:** Inconsistent codebase, confusion
- **Rejected:** Creates technical debt

### 3. SCAM Pattern (Single Component Angular Modules)
- **Pros:** Better tree-shaking than traditional modules
- **Cons:** Still requires module files, extra boilerplate
- **Rejected:** Standalone achieves same goals with less code

## Consequences

### Positive
- 43% reduction in bundle size (850KB → 485KB)
- Faster build times (reduced by ~30%)
- Clearer dependency graph per component
- Better tree-shaking by bundler
- Simplified mental model for developers
- Easier testing with fewer test module configurations

### Negative
- More imports per component file
- Need to remember all direct dependencies
- Some third-party libraries still require NgModules

### Mitigations
- Created barrel files for common imports
- ESLint rule to enforce standalone: true
- Wrapper modules for third-party libraries when needed

## Migration Notes
For teams migrating existing apps:
1. Use `ng generate @angular/core:standalone` schematic
2. Start with leaf components (no children)
3. Work up the component tree
4. Convert routes last

## References
- [Angular Standalone Components Guide](https://angular.io/guide/standalone-components)
- [RFC: Standalone Components](https://github.com/angular/angular/discussions/43784)
