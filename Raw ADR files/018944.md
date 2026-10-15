# ADR 008: Clean Architecture as the Foundational Pattern

## Status
Accepted

## Context
The Ticketeer project serves as a learning platform to master "Must Know" .NET concepts. We need an architectural pattern that:
1.  Enforces **separation of concerns** to teach SOLID principles.
2.  Maximizes **testability** (unit tests without external dependencies).
3.  Provides **flexibility** to swap infrastructure (databases, messaging) without rewriting business logic.
4.  Is **industry-standard** and transferable to professional environments.

The roadmap lists several architectural patterns:
- Clean Architecture
- Vertical Slices Architecture
- Event Sourcing
- Domain-Driven Design (DDD)
- Modular Monoliths
- Event-Driven Architecture

## Decision
We decided to use **Clean Architecture** as the foundational pattern.

### Structure
The codebase will be organized into four concentric layers:

```
┌─────────────────────────────────────┐
│  API (Presentation)                 │  ← Controllers, Middleware, DTOs
├─────────────────────────────────────┤
│  Infrastructure                     │  ← EF Core, Dapper, Redis, MassTransit
├─────────────────────────────────────┤
│  Application                        │  ← Use Cases, Services, Interfaces
├─────────────────────────────────────┤
│  Domain                             │  ← Entities, Value Objects, Business Rules
└─────────────────────────────────────┘
```
### Visual Diagram

```mermaid
flowchart TB
    API --> App
    API --> Infra
    API --> Domain
    Infra --> App
    Infra --> Domain
    Tests --> API
    Tests --> App
    Tests --> Domain
    Tests --> Infra
    App --> Domain
```
**Dependency Rule**: Inner layers never depend on outer layers. Dependencies point inward.

## Alternatives Considered and Rejected

### 1. Vertical Slices Architecture
*   **Description**: Organize code by feature (e.g., `Features/PurchaseTicket/` contains Controller, Service, Repository).
*   **Pros**: Less ceremony, faster for small features, cohesive feature code.
*   **Cons**: 
    - Business logic becomes tightly coupled to infrastructure (harder to test in isolation).
    - Less educational for learning SOLID and Dependency Inversion.
    - Better suited for rapid prototyping, not deep architectural learning.
*   **Reason for Rejection**: Does not emphasize separation of concerns as clearly. Mixes business rules with infrastructure details.

### 2. Event Sourcing
*   **Description**: Store state as a sequence of events (e.g., `TicketReserved`, `TicketPaid`) instead of current state.
*   **Pros**: Complete audit trail, time-travel debugging, natural fit for event-driven systems.
*   **Cons**:
    - Extremely high complexity (requires Event Store, event replay, projections).
    - Counter-intuitive for developers new to the pattern.
    - Overkill for a cinema booking system.
*   **Reason for Rejection**: Disproportionate complexity for the learning goals. Better suited for financial systems or domains requiring full auditability.

### 3. Domain-Driven Design (DDD)
*   **Description**: A philosophy focused on modeling complex business domains using Aggregates, Entities, Value Objects, and Ubiquitous Language.
*   **Reason for Rejection**: **Not an alternative, but a complement.** Clean Architecture and DDD work together. DDD informs how we design the Domain layer, while Clean Architecture defines the overall structure. We will use DDD tactical patterns (Entities, Value Objects) within the Domain layer.

### 4. Modular Monoliths
*   **Description**: A monolithic application divided into independent modules (e.g., `Movies`, `Tickets`, `Cinemas`), each with its own database schema and API.
*   **Pros**: Prepares for microservices without distributed system complexity.
*   **Cons**: Adds organizational overhead (module boundaries, inter-module communication) without clear benefit for a learning project.
*   **Reason for Rejection**: Premature optimization. Clean Architecture already provides modularity through layers. We can refactor to modules later if needed.

### 5. Event-Driven Architecture
*   **Description**: Components communicate via asynchronous events (e.g., `MovieCreated` triggers ElasticSearch sync).
*   **Reason for Rejection**: **Not an alternative, but a complement.** We are already using event-driven communication (MassTransit + RabbitMQ) within the Clean Architecture structure. Event-Driven is a communication strategy, not a layering strategy.

## Consequences

### Positive
*   **Educational Value**: Forces developers to think in terms of abstractions, interfaces, and dependency inversion (the "D" in SOLID).
*   **Testability**: Domain and Application layers can be unit-tested without databases, HTTP, or external services.
*   **Flexibility**: Infrastructure can be swapped (e.g., PostgreSQL → MongoDB, REST → gRPC) without touching business logic.
*   **Industry Alignment**: Clean Architecture is widely adopted in enterprise .NET projects. Skills are transferable.
*   **Complementary**: Works seamlessly with DDD (Domain layer), Event-Driven (Application layer), and CQRS (Application layer with Dapper for reads).

### Negative
*   **Boilerplate**: More files and folders than Vertical Slices (e.g., separate DTOs, interfaces, implementations).
*   **Learning Curve**: Developers must understand dependency inversion and abstraction layers before being productive.
*   **Over-Engineering Risk**: For trivial CRUD operations, the layering can feel excessive. Requires discipline to avoid unnecessary abstraction.

## Implementation Notes
*   **Projects**: Create separate .NET projects for each layer (`Ticketeer.Domain`, `Ticketeer.Application`, `Ticketeer.Infrastructure`, `Ticketeer.API`).
*   **Dependencies**: Enforce dependency rules via project references (Domain has no references, Application references Domain, etc.).
*   **DDD Tactical Patterns**: Use Entities, Value Objects, and Aggregates in the Domain layer.
*   **CQRS-lite**: Use EF Core for writes (Commands) and Dapper for reads (Queries) in the Application layer.
