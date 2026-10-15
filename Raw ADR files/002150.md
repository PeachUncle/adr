# ADR 0001: Project Folder Structure

## Status

Accepted

## Context

IAM Gate requires a clear and organized folder structure to facilitate development, maintenance, and scaling. We need to establish a consistent approach to organizing code and resources within the project to ensure that team members can easily navigate and understand the codebase organization.

The project primarily consists of:
- Architecture decision documentation
- Backend API server for IAM Gate
- Frontend interface for IAM Gate

A well-defined folder structure will help maintain separation of concerns, improve code organization, and facilitate future growth of the application.

## Decision

We will adopt the following top-level folder structure for the project:

1. **adr**: Contains all Architectural Decision Records (ADRs) documenting significant architectural decisions.

    * Each ADR will be named according to the pattern defined in ADR-0000 (`NNNN-kebab-case-title.md`).
    * This folder serves as the centralized location for all architectural documentation.

2. **backend**: Contains the IAM Gate API server implementation.

    * Will contain all server-side code, including API endpoints, authentication logic, and business rules.
    * Separates server-side concerns from client-side implementation.
    * Provides a clear location for backend-specific configuration, tests, and documentation.

3. **frontend**: Contains the IAM Gate user interface implementation.

    * Will contain all client-side code, including components, assets, and frontend application logic.
    * Separates UI concerns from backend implementation.
    * Provides a clear location for frontend-specific configuration, tests, and documentation.

4. **Root folder**: Will contain:
    * Project-wide configuration files
    * README and license information
    * Other top-level documents and files applicable to the entire project

## Consequences

* **Pros:**

  * Clear separation of concerns between frontend and backend components.
  * Simplified navigation for developers working on specific aspects of the application.
  * Improved organization of architectural documentation via the dedicated `adr` folder.
  * Easier onboarding for new developers who can quickly understand the project structure.
  * Facilitates potential future deployment as separate services if needed.
  * Allows for separate build processes and dependencies for frontend and backend.

* **Cons:**

  * Requires careful management of cross-cutting concerns that might span both frontend and backend.
  * May require additional configuration to manage integration between the separate components.
  * Could potentially lead to duplication of some code or models across frontend and backend.
