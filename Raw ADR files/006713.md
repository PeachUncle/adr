# ADR-001: Use Angular 20 and ng-matero for Frontend

## Status

**Accepted** - 2025-11-09

## Context

The b-ro application requires a modern, enterprise-ready frontend framework for the financial management user interface. The frontend needs to:

- Support complex data entry and visualization
- Provide a responsive, mobile-friendly experience  
- Enable rapid development with reusable components
- Maintain long-term supportability and active ecosystem
- Work seamlessly with .NET 9 backend API

## Decision

We will use **Angular 20** as the frontend framework with **ng-matero** as the admin template and **Angular Material 20** as the component library.

### Technology Stack

- **Angular 20.3.10** - Core framework
- **Angular Material 20.2.12** - Component library (Material Design)
- **ng-matero 20.1.0** - Admin dashboard template
- **TypeScript 5.9.3** - Type-safe JavaScript
- **ngx-formly 7.0** - Dynamic forms
- **ngx-translate 17.0** - Internationalization
- **RxJS 7.8** - Reactive programming

### Architecture Approach

- **Standalone Components** - Modern Angular architecture without NgModules
- **Lazy Loading Routes** - Route-based code splitting for performance
- **Signals & Change Detection** - Angular 20's new reactivity system
- **Service-based State** - Shared services for state management
- **Repository Pattern** - Clean separation of data access logic

## Rationale

### Why Angular 20?

1. **Enterprise Maturity**: Angular is backed by Google and widely adopted in enterprise applications
2. **TypeScript First**: Native TypeScript support aligns with .NET development practices
3. **Complete Framework**: Batteries-included approach reduces decision fatigue
4. **Long-term Support**: Predictable release schedule and LTS versions
5. **Strong Ecosystem**: Extensive libraries and tooling (Material, CDK, CLI)
6. **Latest Features**: 
   - Control flow syntax (@if, @for) for better templates
   - Signals for fine-grained reactivity
   - Standalone components reducing boilerplate
   - Improved build performance with esbuild

### Why ng-matero?

1. **Production-Ready**: Professional admin template with complete structure
2. **Angular 20 Compatible**: Up-to-date with latest Angular features
3. **Material Design**: Built on Angular Material for consistent UX
4. **Common Patterns**: Pre-built authentication, navigation, layouts
5. **Time-Saving**: Accelerates development by providing scaffolding
6. **Active Maintenance**: Regular updates and community support

### Why Angular Material?

1. **Official Library**: Maintained by Angular team
2. **Accessibility**: WCAG compliant components out of the box
3. **Customizable Theming**: Material Design 3 theming support
4. **Comprehensive**: 40+ components covering common UI patterns
5. **Well-Documented**: Extensive docs and examples

## Alternatives Considered

### React 19 + Next.js

**Pros:**
- Larger ecosystem and job market
- Server Components for better performance
- More flexible, library-based approach

**Cons:**
- Requires more architectural decisions
- Less opinionated structure
- TypeScript integration not as seamless
- State management fragmentation

**Verdict:** Rejected - Too many choices and less structure for enterprise app

### Vue 3 + Nuxt

**Pros:**
- Easier learning curve
- Good performance
- Composition API similar to React Hooks

**Cons:**
- Smaller enterprise adoption
- Less comprehensive ecosystem
- Fewer enterprise-grade component libraries

**Verdict:** Rejected - Less enterprise-proven than Angular

### Blazor WebAssembly

**Pros:**
- Same C# language as backend
- Strong typing across full stack
- No JavaScript required

**Cons:**
- Larger initial bundle size
- Less mature ecosystem
- Limited component libraries
- Performance concerns for complex UIs

**Verdict:** Rejected - Not mature enough for production financial app

## Consequences

### Positive

- **Rapid Development**: ng-matero template accelerates initial setup
- **Consistency**: Angular Material ensures consistent Material Design
- **Type Safety**: TypeScript reduces runtime errors
- **Maintainability**: Clear structure and conventions
- **Future-Proof**: Active development and regular updates
- **Developer Experience**: Excellent tooling (Angular CLI, Language Service)

### Negative

- **Learning Curve**: Angular is more complex than some alternatives
- **Bundle Size**: Initial bundle ~1.35 MB (can be optimized)
- **Framework Lock-in**: Migrating away from Angular would be costly
- **Opinionated**: Less flexibility in architectural choices

### Mitigation Strategies

1. **Bundle Optimization**: 
   - Enable lazy loading for all feature modules
   - Use Angular build optimizer
   - Implement code splitting strategies

2. **Training**: 
   - Document Angular patterns and conventions
   - Create style guide for component development

3. **Performance Monitoring**:
   - Set up Lighthouse CI in pipeline
   - Monitor Core Web Vitals
   - Regular performance audits

## Implementation Notes

### Project Structure

Following ng-matero conventions:
```
frontend/
├── src/
│   ├── app/
│   │   ├── core/           # Singleton services
│   │   ├── shared/         # Shared components, pipes, directives
│   │   ├── routes/         # Feature modules (lazy loaded)
│   │   │   └── finance/    # Finance domain routes
│   │   └── theme/          # Layout components
│   └── assets/             # Static assets
```

### Key Decisions

1. **Standalone Components**: No NgModules, using standalone APIs
2. **Lazy Loading**: All feature routes loaded on demand
3. **Signals**: Prefer signals over RxJS where appropriate
4. **Control Flow**: Use @if/@for syntax instead of *ngIf/*ngFor

## Related Decisions

- Future: State management approach (NgRx, Akita, or service-based)
- Future: Testing strategy (Jasmine/Karma vs Jest)
- Future: SSR/SSG requirements (Angular Universal)

## References

- [Angular 20 Release Notes](https://blog.angular.dev/angular-v20-is-now-available-5b6a5e0f62bd)
- [ng-matero GitHub](https://github.com/ng-matero/ng-matero)
- [Angular Material Documentation](https://material.angular.io/)
- [Angular Update Guide](https://angular.dev/update-guide?v=19.0-20.0&l=3)
