# 10. architecture design pattern selection

Date: 2024-05-08

## Status

Accepted

## Context

We need to choose an architecture design pattern for our FastAPI application.
The architecture design pattern will define how the application is structured, how the components interact with each other, and how the code is organized.
It will follow the following evaluation criteria
1. Performance.
2. How easy to maintain and extend.
3. Code readability.
4. Solution architecture and code design.
5. Testing strategy.
The main options are:
- **MVC**:
  - *Pros*:
    - Code Readability: Separation of concerns Model (data), View (presentation) and Controller (logic).
    - Easier to testing.
    - Performance: For small applications.
  - *Cons*:
    - Maintain and extend: in complex applications.
    - Performance Overhead: in complex applications.
- **Event-Driven**:
  - *Pros*:
    - Scalability.
    - Code Readability: Separation of concerns.
    - Solution Architecture and Code Design: Decoupling of components into producer/consumer.
    - Testing Strategy: Easier to test.
    - Ease of Maintenance and Extension.
  - *Cons*:
    - Complexity: Event-driven architecture introduce communication complexity, making it harder to observe and monitor.
    - Performance Overhead: Specially for simple CRUD operations.
- **Domain-Driven Design**:
  - *Pros*:
    - Code Readability: Separation of concerns.
    - Solution Architecture and Code Design: Decoupling by domain.
    - Easier to test than ED or MVC.
    - Easier of Extension.
  - *Cons*:
    - Complexity: Requires an understanding of the domain logic to create a _ubiquitous language_.
    - Hard to maintain: Steeper learning curve due to the implementation of abstractions and domain rules.
- **Hexagonal**:
  - *Pros*:
    - Code Readability: separation of primary (users or systems) and secondary actors (framework).
    - Solution Architecture: Encapsulate visibility and dependency injection rules.
    - Testing Strategy: Easier to test.
    - Easier of Extension and maintain than DDD.
  - *Cons*:
    - Complexity: Requires abstraction layers to communicate ports and adapters.

## Decision

Taking into account that performance is the key factor, and the application need to be extensible and easier to maintaiun,
the chosen architecture is **Hexagonal** architecture design pattern.

The file and folder structure will follow the recommended guidelines for FastAPI as [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

## Consequences

The Hexagonal architecture design pattern will separate the use case placed in the domain to the ports and adapters,
used to interact with the data persistence layer, file storage, the web server, and the communication with external services.
