# ADR-001: Adopt Hexagonal Architecture for User Service

## Status
Accepted (2025-09-25)

## Context
The pre-existing code concentrated persistence, business logic, and orchestration inside a monolithic `UserService` class. This impaired testability (difficult to isolate domain logic), limited substitution of infrastructure (e.g., alternate storage, caching), and encouraged controller-level duplication for response composition.

## Decision
Introduce a Hexagonal (Ports & Adapters) structure:
- Domain: Entities encapsulate core data & invariants (`UserEntity`).
- Application (Use Cases): Orchestrate domain + persistence operations without infrastructure details.
- Ports: Define repository contracts for users, profiles, contacts.
- Adapters: Implement ports via PostgreSQL (`Pg*Repository`).
- Composition: Central container wires concrete adapters to use cases and exposes them to controllers.
- Transitional Fallback: Controllers attempt hex use case first; on failure they fallback to legacy `UserService` to reduce migration risk.

## Alternatives Considered
1. Full Rewrite (Big Bang): Higher risk; delays delivery; harder to validate incrementally.
2. Layered Service (Service + DAO) Only: Improves some separation but still couples orchestration to persistence details.
3. CQRS Split Immediately: Overkill for current complexity; added cognitive + operational load.

## Consequences
Positive:
- Improved unit testability (pure use cases with fakes).
- Clear seams for adding caching/eventing later.
- Incremental decommissioning of legacy layer once confidence achieved.

Negative / Trade-offs:
- Temporary duplication (legacy + hex) adds short-term maintenance overhead.
- Slight controller complexity (try/catch fallback) until legacy removal.

## Validation
- Use case unit tests with in-memory fakes.
- Integration test ensuring controller wires to use case path.
- Manual E2E checklist validating unchanged external behavior.

## Follow-Up Actions
- Expand integration tests for mutations & error paths.
- Add repository tests using `pg-mem` (or testcontainers) for SQL correctness.
- Remove fallback blocks and delete legacy service after stability period.
- Generate OpenAPI spec & contract tests to guard boundaries.

## References
- Alistair Cockburn, Ports & Adapters.
- "Hexagonal Architecture" (c2 wiki).
