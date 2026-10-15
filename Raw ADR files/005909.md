# ADR-0002: Angular Monorepo Structure

## Status

Accepted

## Context

As our application grows, we need to establish a clear structure for organizing code that promotes:

1. Code reusability across multiple applications
2. Clear boundaries between different parts of the system
3. Maintainable and scalable architecture
4. Efficient development workflows
5. Consistent build and test processes

The World Demographics Visualization project requires multiple components, services, and potentially multiple applications in the future, making the project structure decision critical.

## Decision

We will adopt an Nx-powered Angular monorepo structure with the following organization:

```
angular-monorepo/
├── apps/
│   └── angular-case-study/      # Main application
├── libs/
│   └── visualizations/
│       ├── domain/              # Domain entities, interfaces, services
│       ├── feature-world-demographics/  # Feature components (smart)
│       └── ui-circle-packging-visualization/  # UI components (dumb)
```

Our libraries will follow these categorizations:

1. **Domain Libraries**: Contain business logic, data models, and interfaces

   - Example: `libs/visualizations/domain`

2. **Feature Libraries**: Contain smart components that implement specific features

   - Example: `libs/visualizations/feature-world-demographics`

3. **UI Libraries**: Contain presentational components with no business logic
   - Example: `libs/visualizations/ui-circle-packging-visualization`

Each library will have a clear public API exposed through its `index.ts` file, and internal implementation details will be kept private.

## Consequences

### Positive

- Clear separation of concerns with well-defined boundaries
- Improved code reuse across different parts of the application
- Better encapsulation of implementation details
- Simplified testing with clear dependencies
- Nx provides powerful tooling for managing the monorepo
- Enables incremental builds and affected commands for better CI/CD

### Negative

- Steeper learning curve for developers new to monorepo concepts
- Requires discipline to maintain proper boundaries between libraries
- More complex initial setup compared to a standard Angular project
- Potential for over-engineering if libraries are created too granularly

### Neutral

- Requires understanding of Nx tooling and concepts
- Teams need to agree on and follow consistent naming and organization conventions

## Alternatives Considered

### Standard Angular Project Structure

A traditional Angular project structure would be simpler but would not provide the same level of code organization and reuse as the monorepo approach.

### Multiple Separate Repositories

Using separate repositories for different parts of the system would provide stronger isolation but would make it harder to share code and coordinate changes across repositories.

### Different Monorepo Tools

Other monorepo tools like Lerna or Turborepo were considered, but Nx was chosen for its strong Angular integration and comprehensive tooling.

## References

- [Nx Documentation](https://nx.dev/concepts/more-concepts/library-types)
- [Angular Style Guide](https://angular.io/guide/styleguide)
- [Monorepo Patterns](https://www.atlassian.com/git/tutorials/monorepos)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
