# ADR 002: Hybrid API Approach (Minimal APIs + Controllers)

## Status
Accepted

## Context
The Ticketeer API has distinct requirements for different parts of the system:
1.  **High-Traffic Endpoints**: Public-facing read operations (e.g., checking seat availability for a blockbuster movie premiere) require maximum throughput and minimum latency.
2.  **Complex Business Logic**: Administrative operations (e.g., managing movies, cinemas, and financial reporting) involve complex validation, multiple service interactions, and structured error handling.
3.  **Maintainability**: As the project grows, code organization becomes critical to prevent "spaghetti code".

We need to choose an API implementation style that balances performance with maintainability.

## Alternatives Considered

### 1. Controllers Only (Classic ASP.NET Core)
*   **Description**: Using `ControllerBase` classes for all endpoints.
*   **Pros**: Well-known structure, excellent tooling support, built-in filters, easy to organize by domain.
*   **Cons**: Higher memory overhead and slightly slower startup/request processing due to the MVC pipeline (routing, filter instantiation, etc.).

### 2. Minimal APIs Only
*   **Description**: Defining all endpoints using `app.MapGet`, `app.MapPost` in `Program.cs` or extension methods.
*   **Pros**: Extremely low overhead, faster startup, less boilerplate code. Ideal for microservices.
*   **Cons**: Can become disorganized in large monolithic applications if not carefully structured. Lacks some built-in conveniences of Controllers (like easy attribute-based filters across groups).

## Decision
We decided to adopt a **Hybrid Approach**:

1.  **Minimal APIs** will be used for **"Hot Paths"** (High-Performance scenarios).
    *   *Criteria*: Public read endpoints, high-concurrency write endpoints (e.g., Ticket Purchase), and simple microservice-like features.
    *   *Goal*: Minimize latency and maximize throughput.

2.  **Controllers** will be used for **"Complex Paths"** and Backoffice operations.
    *   *Criteria*: CRUD operations for administrative resources, complex reporting, or endpoints requiring extensive attribute-based metadata.
    *   *Goal*: Maximize code organization and maintainability.

## Consequences

### Positive
*   **Performance Optimization**: We allocate performance resources where they matter most (customer-facing endpoints).
*   **Structured Growth**: We maintain a clean structure for the bulk of the business logic using Controllers.
*   **Learning Opportunity**: Allows the team to master both paradigms (a "Must Know" requirement).

### Negative
*   **Inconsistency**: The codebase will contain two different ways of defining endpoints. Developers must be disciplined in applying the criteria for choosing one over the other.
*   **Discovery**: Swagger/OpenAPI handles both seamlessly, but developers navigating the code need to look in two places (Controllers folder vs. Endpoint definitions).
