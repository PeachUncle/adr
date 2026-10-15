# Presentation tier description

* Status: accepted
* Deciders: Alejandro Garcia Prada and Jaime Ochoa de Alda Cerdán
* Date: 2025-11-02

## Context and Problem Statement

Within the 3-tier architecture, we need to define how the system's users interact with the presentation tier and how this layer communicates with the business logic tier.

The goal is to design a SOLID and maintainable solution that clearly defines presentation layer responsibilities while supporting multiple client types (desktop, mobile, and web).


## Decision Drivers

* RF-16 Gestión de permisos de usuarios internos

## Considered Options

* 0006-1-Bridge-Pattern
* 0006-2-Facade-Pattern

## Decision Outcome

Chosen option: "0006-1-Bridge-Pattern" because it allows us to separate the abstraction (user types and their interactions) from the implementation (client applications such as web, mobile, or desktop).

This design decision promotes flexibility and scalability while maintaining a clean separation between the presentation tier and the business logic tier. Communication between these tiers will be handled through HTTP/HTTPS protocols.

### Positive Consequences

* Changes in one end of the bridge (either the client or the abstraction) do not affect the other.
* Clear separation of responsibilities and adherence to SOLID principles.
* High scalability when adding new user roles or client types.
* Promotes flexibility for future integration with other posible devices.

### Negative Consequences

* Introduces additional classes and abstractions that may seem unnecessary for small or simple systems.
* Requires careful coordination between interface and implementation layers.

## Pros and Cons of the Options

### 0006-1-Bridge Pattern

The Bridge Pattern decouples abstraction from implementation, allowing both to evolve independently.
In the presentation tier, this means that user interfaces (UI components) and user behavior models can be developed and extended separately, avoiding rigid dependencies.

More info: https://www.geeksforgeeks.org/system-design/bridge-design-pattern/

* Good, because it allows the abstraction (user behavior or role) to evolve independently from the implementation (UI type or client technology).
* Good, because it promotes SOLID principles, especially Open/Closed and Dependency Inversion.
* Good, because teams can develop abstractions and implementations in parallel, improving scalability and maintainability.
* Good, because testing becomes simpler—each part can be mocked or replaced independently.
* Bad, because it introduces additional classes and interfaces, increasing structural complexity.
* Bad, because the interface is not flexible and all the concrete clases must follow it.

## 0006-2-Facade Pattern

The Facade Pattern provides a unified and simplified interface to a set of interfaces in a subsystem.
In the presentation tier, this means that user interfaces interact through a single access point that hides the complexity of underlying business logic and services.

More info: https://refactoring.guru/design-patterns/facade

* Good, because it simplifies interactions between the presentation tier and internal components by exposing a single, cohesive interface.
* Good, because it reduces coupling, allowing the UI to remain unaffected by internal subsystem changes.
* Good, because it improves readability and makes the system easier to understand for new developers.
* Good, because it provides a clear entry point for communication, improving maintainability and consistency.
* Bad, because the Facade can become a bottleneck if it grows too large or starts handling too many responsibilities.
* Bad, because over time it may hide too much of the underlying functionality, reducing flexibility for more complex or specialized operations.
* Bad, because relying solely on the Facade can discourage direct, efficient use of underlying components when necessary.
