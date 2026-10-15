# Architectural Decision Record: Adoption of Hexagonal Architecture for Backend

## Status

Accepted (unanymously, i'm the only dev)

## Context

The Proletariat Budget backend needs an architecture that supports:

1. A clear separation between business logic and external deps
2. Flexibility to adapt to changing requirements and technologies
3. Testability of business logic in isolation
4. The ability to evolve different parts of the system independently
5. Support for multiple interfaces (REST API, CLI, etc.) and infrastructure components (DBs, external services)
6. A structure that aligns with our domain-driven approach to financial management

We need to decide on an architectural pattern that will guide our development and ensure the system remains maintainable
and adaptable as it grows.

## Decision

We will implement a Hexagonal Architecture (also known as Ports and Adapters) for the Proletariat Budget backend, with
the following specific characteristics:

1. **Core Domain Layer**: Contains pure business logic, domain models, and business rules with no dependencies on
   external frameworks or services.

2. **Application Layer (Use Cases)**: Orchestrates the flow of data to and from the domain layer and coordinates with
   ports to interact with external systems.

3. **Ports Layer**: Defines interfaces that the application core requires to interact with the outside world:
    - **Primary/Driving Ports**: Interfaces that allow external actors to use our application (e.g., API controllers)
    - **Secondary/Driven Ports**: Interfaces our application uses to interact with external systems (e.g., repositories,
      external services)

4. **Adapters Layer**: Implements the interfaces defined by ports:
    - **Primary/Driving Adapters**: Translate external requests into application-specific operations (e.g., REST
      controllers, CLI commands)
    - **Secondary/Driven Adapters**: Connect the application to external infrastructure (e.g., database implementations,
      external API clients)

5. **Fine-grained Adapter Implementation**: Each adapter will be implemented as a separate unit with a single
   responsibility, rather than creating monolithic adapters that handle multiple concerns.

6. **Plugin Architecture**: The hexagonal design will support a plugin system where third-party developers can create
   new adapters that implement our port interfaces without modifying the core application. This will enable:
    - Community-developed integrations with additional financial services
    - Custom data visualization and reporting tools
    - Alternative user interfaces
    - Specialized financial analysis modules
    - Regional adaptations for different economic contexts

## Consequences

### Positive

1. **Business Logic Isolation**: Core business rules remain unaffected by changes to external systems or UI.

2. **Testability**: Business logic can be tested without external dependencies through mock implementations of ports.

3. **Flexibility**: We can easily swap implementations of adapters (e.g., changing database technology) without
   affecting the core application.

4. **Independent Development**: Teams can work on different adapters concurrently without interfering with each other.

5. **Technology Agnosticism**: The core application is not tied to specific frameworks or libraries, reducing technical
   debt.

6. **Granular Adapters**: Fine-grained adapters allow for precise control over dependencies and make the system more
   modular.

7. **Clear Boundaries**: Explicit interfaces between layers make the system easier to understand and maintain

### Negative

1. **Initial Complexity**: More interfaces and abstractions lead to a steeper learning curve for new developers.

2. **Development Overhead**: Creating and maintaining interfaces for each interaction point requires additional code.

3. **Potential Over-engineering**: For simple use cases, this architecture might introduce unnecessary complexity.

4. **Performance Considerations**: Additional abstraction layers might introduce minor performance overhead.

5. **Adapter Proliferation**: Fine-grained adapters could lead to a large number of small components that need to be
   managed.

## Implementation Guidelines

1. **Domain Models**: Create pure domain models that encapsulate business rules and have no dependencies on external
   frameworks.

2. **Use Case Structure**: Each use case should:
    - Must follow the UML defined in the `usecases` folder
    - Accept input through a well-defined data structure
    - Interact with domain models and ports
    - Return output through a well-defined data structure
    - Not contain infrastructure concerns

3. **Port Interfaces**: Define clear interfaces for all external interactions, with:
    - Repository interfaces for data persistence
    - Service interfaces for external services
    - Controller interfaces for incoming requests

4. **Adapter Granularity**: Implement adapters at the appropriate level of granularity:
    - One adapter per external system integration
    - Adapters should have a single responsibility
    - Avoid creating "god adapters" that handle multiple concerns

5. **Dependency Injection**: Use dependency injection to provide implementations of ports to the application core.

6. **Package Structure**: Organize code to reflect the hexagonal architecture:

  ```
  /internal
     /adapter     # Adapter implementations
       /resthttp  # REST API adapters
       /mysql     # Database adapters
       /external  # External service adapters
     /core
       /domain      # Domain models and business logic
       /port        # Interface definitions
       /usecase     # Application use cases
```

## Alternatives Considered

1. **Traditional Layered Architecture**: Simpler but less flexible and more prone to coupling between layers.
2. **Clean Architecture**: Similar principles but with more prescribed layers and rules.
3. **Microservices**: Would introduce distributed system complexity before it's necessary.
4. **CQRS/Event Sourcing**: More complex than currently needed for our domain.

## References

- [Alistair Cockburn's original article on Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture)
- [Domain-Driven Design principles by Eric Evans](https://fabiofumarola.github.io/nosql/readingMaterial/Evans03.pdf)