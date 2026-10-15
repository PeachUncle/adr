---
title: "ADR-003: Prefer Modular Monoliths"
date: 2025-11-13
status: Accepted
tags: [architecture, modular-monolith, microservices, design-principles]
---

# ADR-003: Prefer Modular Monoliths

## Status

Accepted

## Date

2025-11-13

## Context

Teams regularly face a choice between a classic (layered) monolith and a microservices architecture when starting new systems. Classic monoliths are simple to deploy but often evolve into tightly coupled codebases with weak boundaries, making change risky and slowing delivery. Microservices promise independent scaling and deployment, but they introduce significant operational complexity (distributed transactions, versioning, resiliency, observability, CI/CD, cross-service testing, data consistency).

Many systems don’t initially have concrete scale, latency, or organizational demands that justify microservices on day one. However, we still need a structure that enables evolution as needs become clearer. A modular monolith provides that path: clear, enforceable boundaries inside a single process with the option to extract modules into services later when there is explicit demand.

## Decision

We will adopt a "modular monolith first" strategy.

1. For all new projects, strongly advise building a modular monolith rather than a classic monolith.
2. Favor cohesive, independently testable modules with clear boundaries and published contracts.
3. Allow splitting one or more modules into separate microservices only when there is an explicit, validated demand (e.g., independent scaling, regulatory isolation, team autonomy, or fault isolation) and the cost/benefit is favorable.
4. Avoid classic monoliths with weak boundaries and high coupling between layers/components.
5. Expect systems to mature over time: start simple, measure, and evolve architecture incrementally as needs emerge.

## Rationale

- Modularity supports evolutionary architecture: good internal boundaries make future extraction feasible at lower cost.
- Most early-stage products do not require microservices’ operational overhead; developer productivity and cycle time are better in-process.
- A modular monolith preserves transactional simplicity (single database transaction across modules) and reduces distributed-system failure modes while keeping options open.
- Clear module contracts (interfaces, domain events, application services) improve maintainability, testability, and onboarding.
- Microservices remain a powerful option when justified by explicit demands (scale, isolation, cadence, compliance), not by default.

## Consequences

### Positive
- Faster time-to-market and simpler operations for new systems.
- Strong boundaries reduce coupling and increase maintainability.
- Easier end-to-end testing; fewer moving parts in development and CI.
- Lower infrastructure costs and operational complexity early on.
- Smoother path to microservices extraction if/when justified.

### Negative
- One process and deployment can limit independent release cadence until extraction.
- Requires discipline to enforce module boundaries (code reviews, tooling, tests).
- Teams may postpone needed extraction if success criteria and triggers aren’t defined.

## Guidelines for Modular Monoliths

### What is a Module?
- A module encapsulates a cohesive business capability (DDD-style bounded context where possible).
- Each module owns its domain model, application services, and persistence mapping.
- Modules communicate via explicit contracts (interfaces) and domain/application events.

### Boundary Enforcement
- No cross-module data access: never reach into another module’s persistence or internal types.
- Expose only public contracts; keep internals hidden (internal types/assemblies, separate projects when helpful).
- Prefer dependency inversion: modules depend on abstractions, not concrete implementations.
- Validate boundaries with tests and static analysis (analyzers, Architecture Tests).

### Persistence
- Prefer schema ownership per module. Shared database server is acceptable; avoid shared tables.
- Use separate EF Core DbContext per module; prevent cross-context joins.
- Cross-module transactions should be rare; prefer eventual consistency via in-process events.

### Communication Patterns (in-process)
- Synchronous: call other modules through well-defined interfaces registered in DI.
- Asynchronous: publish domain/application events; subscribe within other modules.
- Avoid direct references to other modules’ entities; use IDs and DTOs across boundaries.

### Solution Structure (example)
```
src/
  MyApp.Api/                     # API boundary; thin controllers
  MyApp.Modules.Orders/          # Module: Orders
  MyApp.Modules.Customers/       # Module: Customers
  MyApp.Modules.Inventory/       # Module: Inventory
  MyApp.Shared/                  # Shared primitives (value objects, base abstractions)
```

### Observability and Operations
- Implement structured logging, tracing, and metrics at module boundaries.
- Feature flags and configuration per module where it adds autonomy.

## When to Split Out Microservices

Only split a module into a service when explicit demand exists and benefits outweigh costs. Typical triggers:
- Independent scaling or SLOs (e.g., high-throughput ingestion vs. low-latency read path).
- Team autonomy and ownership boundaries require independent release cadence.
- Regulatory or data isolation requirements.
- Fault isolation to protect critical paths.

### Readiness Checklist for Extraction
- Module boundaries enforced (no hidden coupling or cross-module DB access).
- Clear contract surface (API, events, and data contracts versioned).
- Adequate test coverage (unit, contract, and integration tests).
- Observability in place (logs, metrics, traces).
- Backward-compatible migration plan defined (strangler pattern where applicable).

## Migration Paths

### Classic Monolith → Modular Monolith
1. Identify capabilities and define preliminary module boundaries.
2. Extract code into modules (namespaces/projects), hide internals, expose contracts.
3. Establish per-module persistence mapping (contexts/schemas) and remove cross-module data access.
4. Introduce in-process events to replace implicit couplings.

### Modular Monolith → Microservices (Selective Extraction)
1. Select a single module with explicit demand; define service API and events.
2. Create a new service hosting that module; duplicate its persistence with owned schema.
3. Implement anti-corruption/strangler at the API boundary; route traffic gradually.
4. Migrate data ownership and stop in-process calls; replace with HTTP/gRPC/messaging.
5. Update observability and SLOs; roll out safely with canaries and feature flags.

## Non-Goals
- Mandating microservices for all systems.
- Preventing evolution toward microservices when justified.
- Enforcing a specific technology for inter-module communication beyond C#/.NET norms.

## Alternatives Considered
- Classic monolith (rejected): weak boundaries, harder long-term maintainability.
- Microservices by default (rejected): high operational cost and premature complexity.

## Implementation

- Update project templates and internal docs to reflect modular monolith-first.
- Provide example repositories demonstrating module structure, contracts, and tests.
- Add architecture checks (analyzers/ArchUnitNET-style tests) to CI to enforce boundaries.
- Include guidance in onboarding and code review checklists.

## Monitoring and Review
- Revisit architecture quarterly to confirm current needs and triggers for extraction.
- Track incidents where coupling violates module rules; address with refactoring.
- Review extraction candidates against the readiness checklist.

## References
- Martin Fowler – "Monolith First" (reference).
- ThoughtWorks Technology Radar – Modular Monolith (reference).
- Sam Newman – Building Microservices (reference).
- Team Topologies – Autonomous teams and boundaries (reference).

## Related Documents
- ADR-001: Migration to .NET 10
- ADR-002: Adoption of Aspire for Distributed Application Development
- Architecture Guidelines: Microservices Design
- Coding Standards: .NET Project Structure
