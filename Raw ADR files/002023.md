# ADR-0002: Use Angular for Frontend Framework

## Status

Accepted

## Context

Grafana-banana requires a modern frontend framework for building a responsive, maintainable web application. The frontend needs to:

- Provide excellent developer experience
- Support TypeScript for type safety
- Enable component-based architecture
- Offer robust routing and state management
- Have strong tooling and CLI support
- Support modern web standards
- Integrate well with RESTful APIs
- Provide good performance
- Have comprehensive documentation
- Support testing frameworks
- Enable progressive web app (PWA) capabilities

## Decision

We will use Angular 20+ as the frontend framework, implementing standalone components and modern Angular practices.

### Key Technologies
- **Angular 20+**: Modern Angular with standalone components
- **TypeScript**: Strongly-typed JavaScript for reliability
- **RxJS**: Reactive programming for async operations
- **Angular CLI**: Command-line tools for development
- **OpenTelemetry**: Browser instrumentation for observability
- **Jasmine/Karma**: Testing frameworks

## Consequences

### Positive

1. **Type Safety**: TypeScript provides compile-time type checking
2. **Complete Framework**: Batteries-included with routing, HTTP, forms, etc.
3. **CLI Tooling**: Excellent CLI for scaffolding and development
4. **Dependency Injection**: Built-in DI system for clean architecture
5. **Two-Way Data Binding**: Simplifies form handling
6. **Standalone Components**: Modern, simplified component model
7. **Strong Opinions**: Conventions reduce decision fatigue
8. **Enterprise Ready**: Proven in large-scale applications
9. **Observability**: OpenTelemetry browser support
10. **Long-Term Support**: Regular LTS releases
11. **Performance**: Good runtime performance with AOT compilation
12. **Documentation**: Comprehensive official documentation
13. **Community**: Large, active community and ecosystem

### Negative

1. **Learning Curve**: Steeper learning curve than simpler frameworks
2. **Bundle Size**: Larger initial bundle size than minimal frameworks
3. **Complexity**: More complex than lightweight alternatives
4. **Frequent Updates**: Major versions require migration effort
5. **Opinionated**: Less flexibility in architectural choices
6. **Verbosity**: More boilerplate than some alternatives

### Neutral

1. **Google Backing**: Primarily developed by Google
2. **TypeScript Required**: Cannot opt out of TypeScript
3. **Template Syntax**: Unique template syntax to learn
4. **Change Detection**: Automatic change detection can be magic

## Implementation

### Timeline
- Initial implementation: Completed
- Migration to Angular 20: Completed
- Ongoing: Keep updated with Angular LTS releases

### Owner
@markcoleman

### Dependencies
- Node.js 20+ for development
- npm 10+ for package management
- TypeScript 5.x
- Angular CLI installed globally or via npx

### Architecture Decisions

1. **Standalone Components**: Use standalone components (no NgModule)
2. **Signals**: Adopt Angular Signals for state management
3. **Reactive Forms**: Prefer reactive forms over template-driven
4. **Services**: Use services with dependency injection for business logic
5. **RxJS**: Leverage observables for async operations
6. **Lazy Loading**: Implement lazy loading for larger features

## Alternatives Considered

### Alternative 1: React

**Pros:**
- Larger community and ecosystem
- More job market demand
- Simpler mental model (just components)
- Flexible, unopinionated
- Better support for mobile (React Native)
- Smaller bundle sizes possible
- More third-party component libraries

**Cons:**
- Need to choose and integrate many libraries (routing, state, forms)
- Less standardization across projects
- JSX learning curve
- State management complexity (Redux, Context, etc.)
- No built-in dependency injection
- More decision fatigue

**Why Rejected:**
While React has a larger ecosystem, Angular's complete, opinionated framework reduces setup time and provides better standardization. For an enterprise-grade application, Angular's structure and conventions are beneficial.

### Alternative 2: Vue.js

**Pros:**
- Gentler learning curve
- Flexible (can be progressive)
- Good documentation
- Smaller bundle size
- Template syntax similar to HTML
- Growing community
- Composition API similar to React Hooks

**Cons:**
- Smaller enterprise adoption
- Less corporate backing than Angular/React
- Smaller ecosystem
- TypeScript support improving but not as mature
- Less standardization in large projects
- Fewer enterprise tooling options

**Why Rejected:**
Vue's gentler learning curve is attractive, but Angular's enterprise adoption, TypeScript integration, and comprehensive tooling make it better suited for a long-term, maintainable application.

### Alternative 3: Svelte/SvelteKit

**Pros:**
- Compile-time framework (no runtime)
- Smallest bundle sizes
- Excellent performance
- Simple, intuitive syntax
- Less boilerplate
- Growing rapidly

**Cons:**
- Smaller community and ecosystem
- Less enterprise adoption
- Fewer third-party components
- Less mature tooling
- Limited TypeScript support historically
- Less proven in large-scale apps
- Smaller talent pool

**Why Rejected:**
Svelte is promising, but its smaller ecosystem and less proven track record in enterprise applications make it riskier. Angular's maturity and comprehensive features are more suitable for this project.

### Alternative 4: Vanilla JavaScript + Web Components

**Pros:**
- No framework dependency
- Standards-based
- Maximum control
- Smallest possible bundle
- No breaking changes from framework updates
- Can integrate with any backend

**Cons:**
- High development effort
- Need to build/integrate routing, state management, etc.
- Less productivity
- More code to maintain
- Harder to find developers
- No standard patterns
- Limited tooling
- Complex state management

**Why Rejected:**
While standards-based web components are appealing, the development velocity and maintainability benefits of a full framework far outweigh the costs. Angular provides needed productivity and standardization.

### Alternative 5: Next.js (React with SSR)

**Pros:**
- Server-side rendering out of the box
- Great SEO
- Excellent developer experience
- Fast page loads
- Built-in routing
- API routes in same project
- Good documentation

**Cons:**
- Requires Node.js server (not static)
- More complex deployment
- React ecosystem fragmentation
- Opinionated about deployment (Vercel)
- Additional complexity if SSR not needed
- Still need state management library

**Why Rejected:**
For a SPA with a separate API backend, Angular provides better structure without the complexity of SSR. The application doesn't require SSR for SEO since it's an internal tool.

## References

- [Angular Documentation](https://angular.dev/)
- [Angular Style Guide](https://angular.dev/style-guide)
- [Standalone Components](https://angular.dev/guide/components/importing)
- [Angular Signals](https://angular.dev/guide/signals)
- [OpenTelemetry Browser](https://opentelemetry.io/docs/instrumentation/js/)
- [Project Repository](https://github.com/markcoleman/Grafana-banana)

## Related ADRs

- [ADR-0001: Use .NET 9 for Backend Framework](./ADR-0001-dotnet-backend-framework.md)
- [ADR-0003: Use Grafana Stack for Observability](./ADR-0003-grafana-observability-stack.md)

## Metadata

| Field | Value |
|-------|-------|
| **Created** | 2025-10-25 |
| **Updated** | 2025-10-25 |
| **Author** | @markcoleman |
| **Reviewers** | Architecture Review Board |
| **Status** | Accepted |
| **Implementation Status** | Complete |
