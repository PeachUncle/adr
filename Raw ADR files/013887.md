# ADR-0001: Adopt Layered Architecture with Dependency Injection

Status: Proposed

Deciders: QuentinDess

Date: 2025-07-16

Technical Story: Refactor the application's core logic to improve modularity, testability, and scalability, as seen in Pull Request #4.

Context and Problem Statement
The application was initially implemented with a simple structure where all logic was tightly coupled with the Probot framework event handlers. As the application's complexity is expected to grow, this monolithic approach presents challenges for maintenance, testing, and scalability. It is difficult to test business logic in isolation from the framework, and managing dependencies becomes cumbersome. How can we refactor the application to ensure better separation of concerns and improve its long-term maintainability and testability?

Decision Drivers
Testability: The need to test application logic independently of the Probot framework.

Separation of Concerns: The desire to decouple business logic from infrastructure concerns (e.g., GitHub events, Docker execution).

Scalability: The need for an architecture that can gracefully accommodate new features and complexity.

Maintainability: The desire for a clear and organized codebase that is easy for developers to understand and modify.

Considered Options
Adopt a Layered Architecture with a Dependency Injection (DI) framework (InversifyJS).

Implement a layered architecture with manual dependency injection.

Retain the existing simple, monolithic structure.

Decision Outcome
Chosen option: "Adopt a Layered Architecture with a Dependency Injection (DI) framework (InversifyJS)", because it systematically addresses all decision drivers by enforcing a clean separation of concerns through layers (Presentation, Application, Domain, Infrastructure) and providing a robust, automated mechanism for managing dependencies. This structure significantly enhances testability by allowing components to be mocked easily and provides a solid foundation for future development.

Positive Consequences
Core application logic is decoupled from the Probot framework.

Improved testability; components can be unit-tested in isolation.

Clearer code organization improves readability and maintainability.

The architecture is more scalable and easier to extend with new features.

Negative Consequences
Introduces additional complexity with the layered architecture and DI container setup.

A learning curve is required for developers not familiar with InversifyJS or Domain-Driven Design concepts.

Increases the number of third-party dependencies (inversify, reflect-metadata).

Pros and Cons of the Options
Adopt a Layered Architecture with a Dependency Injection (DI) framework (InversifyJS)
Good: Enforces strong separation of concerns.

Good: Greatly simplifies testing through mockable dependencies.

Good: The DI container automates object creation and wiring.

Good: Establishes a scalable pattern for future features.

Bad: Adds a new framework dependency and a learning curve.

Bad: Requires more boilerplate code for setting up modules and interfaces.

Implement a layered architecture with manual dependency injection
Good: Achieves separation of concerns without adding a new library.

Good: Avoids the "magic" of a DI framework.

Bad: Managing the dependency graph manually is cumbersome and error-prone.

Bad: Requires writing and maintaining custom factory/injection logic.

Retain the existing simple, monolithic structure
Good: Simple and quick for small-scale, trivial applications.

Good: No learning curve; continues with the existing pattern.

Bad: Does not scale well with increasing complexity.

Bad: Components are tightly coupled, making them difficult to test or modify in isolation.
