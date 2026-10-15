# ADR: Screaming Architecture for Project Organization

## Context

In software development, the structure and organization of the codebase play a critical role in ensuring
maintainability, scalability, and clear communication of the system's intent. Clean Architecture principles advocate
for designing systems around their use cases and business rules rather than technical frameworks or
implementation details.

To achieve this, we have decided to adopt a **Screaming Architecture** approach for this project. The goal is for the
folder structure and code organization to "scream" the purpose of the system by making the core use cases and domain
visible and central.

---

## Decision

We will organize the project into the following high-level folders, based on their architectural roles:

### Folder Structure

1. **`domain/`**
   - Contains the core business entities, rules, and domain logic.
   - Includes:
     - Entities (e.g., `Mesh`, `ThickeningTransformation`).
     - Value objects.
     - Domain-specific exceptions.

1. **`use_cases/`**
   - Encapsulates application-specific behavior and orchestrates domain logic.
   - Each use case is represented as a class or module.
     - Example: `process_thickening.py`.

1. **`adapters/`**
   - Handles communication between the system and external components (e.g., file systems, databases,
third-party libraries).
   - Includes adapters and humble objects
     - Implementations for STL format.

1. **`interfaces/`**
   - Handles communication between the use cases and adapters with Protocol-based interfaces:
     - `MeshReader` and `MeshWriter` protocols.

1. **`cli/`**
   - Defines communication points between the system and users via Command-line interfaces (CLI).

1. **`tests/`**
   - Contains unit, integration, and end-to-end tests.
   - Mirrors the folder structure of the main application.
   - Contains fixtures and utilities for testing.

1. **`docs/adrs/`**
   - Stores architectural decision records (ADRs).
   - Documents the reasoning and trade-offs behind significant design decisions.

---

## Rationale

- **Clarity of Purpose**: Organizing the codebase around its business intent (use cases and domain) ensures that the
system's purpose is evident to new developers and stakeholders.
- **Separation of Concerns**: Clearly delineates the responsibilities of different layers in the architecture.
- **Extensibility**: Facilitates adding new features or integrating with new external systems without disrupting
the core logic.
- **Maintainability**: Reduces coupling between components and makes it easier to test and refactor code.

---

## Alternatives Considered

1. **Framework-Centric Organization**
   - Organizing code based on technical frameworks (e.g., `models/`, `views/`, `controllers/`).
   - Rejected because it obscures the system's intent and couples the architecture to specific frameworks.

2. **Flat Structure**
   - Keeping all files in a single folder or minimally grouping them.
   - Rejected due to scalability and maintainability concerns.

---

## Consequences

- **Positive**:
  - Enhances system readability and onboarding of new developers.
  - Encourages adherence to clean architecture principles.
- **Negative**:
  - Requires discipline to maintain folder boundaries and avoid shortcuts.
  - May introduce additional boilerplate for adapters and protocols.

---

## Status

Accepted
