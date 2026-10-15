# ADR-0003: Standalone Components

## Status

Accepted

## Context

Angular has traditionally used NgModules to organize and encapsulate components, directives, and pipes. However, with Angular 14+, standalone components were introduced as a way to simplify the component development experience. As we develop the World Demographics Visualization application, we need to decide on the component architecture approach.

Key considerations include:

1. Developer experience and ease of use
2. Maintainability and scalability
3. Compatibility with our monorepo structure
4. Future-proofing our application

## Decision

We will use Angular's standalone components throughout the application instead of the traditional NgModule-based approach. This means:

1. All components will be declared with `standalone: true` in their decorator
2. Dependencies will be imported directly in the component via the `imports` array
3. No feature modules will be created for organizing components
4. The application bootstrap will use standalone bootstrapping

Example implementation:

```typescript
@Component({
  selector: 'visualizations-circle-packing',
  standalone: true,
  imports: [CommonModule, SomeOtherComponent],
  templateUrl: './circle-packing.component.html',
  styleUrls: ['./circle-packing.component.css'],
})
export class CirclePackingComponent {
  // Component implementation
}
```

## Consequences

### Positive

- Simplified component development with less boilerplate code
- Clearer dependency management at the component level
- Better tree-shaking and potential bundle size improvements
- Aligns with Angular's future direction (Angular 17+ emphasizes standalone components)
- Easier to understand component dependencies by looking at the component itself
- Simplified testing as components declare their own dependencies

### Negative

- Requires Angular 14+ (not an issue for new projects)
- Some third-party libraries may still use NgModule architecture
- Team members need to learn the standalone component pattern
- Existing documentation and examples often use NgModule approach

### Neutral

- Different mental model for organizing code (component-centric vs. module-centric)
- May require bridging between standalone and NgModule worlds for some libraries

## Alternatives Considered

### Traditional NgModule Approach

Using NgModules to organize components would follow the established Angular pattern but would introduce more boilerplate and complexity.

### Hybrid Approach

A hybrid approach where some parts use standalone components and others use NgModules was considered but rejected to maintain consistency across the codebase.

### Custom Module System

Creating our own module system was briefly considered but rejected as it would add unnecessary complexity and deviate from Angular best practices.

## References

- [Angular Standalone Components Documentation](https://angular.io/guide/standalone-components)
- [Angular Roadmap](https://angular.io/guide/roadmap)
- [Nx and Standalone Components](https://nx.dev/recipes/angular/using-standalone-components)
- [Angular Architecture Guide](https://angular.io/guide/architecture)
