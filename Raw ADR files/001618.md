# 4. Choice of Simple Service Layer over Repository Pattern for POC/MVP

*   **Status:** Accepted
*   **Date:** 2025-11-4

## Context

For the initial POC/MVP phases of the "EzraTask" narrative, our data access logic is simple CRUD (Create, Read, Update, Delete) against a single `Todo` entity. We must choose a data access pattern that is appropriate f
or this level of complexity, prioritizing speed of delivery while acknowledging future needs.

### Options Considered:

1.  **Simple Service Layer:** Business logic services (e.g., `TodoService`) interact directly with the `DbContext` from Entity Framework Core.
2.  **Repository & Unit of Work Pattern:** Introduce a generic repository abstraction for each entity and a Unit of Work to manage transactions. This pattern fully decouples business logic from the data access technolo
gy (EF Core).

## Decision

We will use a **Simple Service Layer** for the initial development phases. We are consciously **deferring the implementation of the Repository pattern**. This is a strategic decision to avoid premature abstraction.

## Consequences

### Positive:

*   **Reduced Boilerplate:** Avoids the creation of multiple repository interfaces and implementations for simple CRUD operations, leading to less code and faster development.
*   **Adherence to YAGNI ("You Ain't Gonna Need It"):** The additional abstraction of a repository is not needed for the current requirements. Implementing it now would be a form of over-engineering.
*   **Clarity and Simplicity:** For a simple domain, direct `DbContext` access in a service is often easier to read and trace than navigating through multiple layers of abstraction.
*   **Narrative Alignment:** Aligns with the story of building a quick, high-quality internal POC where unnecessary complexity is actively avoided.

### Negative:

*   **Tighter Coupling:** The business logic in the service layer is now directly coupled to EF Core. Swapping out the ORM in the future would be more difficult.
*   **Technical Debt:** This is a form of intentional technical debt. As the application's domain logic and data access needs grow more complex, this pattern will become insufficient.

### Mitigation and Remediation Plan

This architectural choice will be revisited as part of the work in `TDT-21: Document Data Persistence and Migration Strategy`. When the application migrates to a persistent database and the domain complexity increases,
 a formal Repository/Unit of Work pattern will be introduced to decouple the service layer from the data access implementation.
