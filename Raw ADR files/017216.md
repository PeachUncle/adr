# ADR 0001: Initial Architecture Choice

Date: 2026-01-08
Status: Accepted

## Context
We need to ship an end-to-end slice quickly while keeping a credible path to scale. The domain spans orders, inventory, fulfillment, routing, and notifications with integrations to external systems.

## Decision
Adopt a modular monolith for the initial implementation with:
- Clear domain modules (Orders, Inventory, Catalog, Fulfillment/Dispatch, Routing, Notifications, Identity)
- Relational database (e.g., PostgreSQL — recommended)
- Cache (e.g., Redis — optional)
- Domain events with an outbox pattern to decouple modules and enable integrations
- Strong internal interfaces and test seams to ease future extraction to services

## Rationale
- Speed: minimal operational overhead vs. microservices from day one
- Cohesion: easier end-to-end consistency while domain boundaries are evolving
- Safety: outbox and eventing provide integration points without tight coupling
- Optionality: straightforward path to service extraction where warranted

## Alternatives Considered
1. Microservices from the start
   - Pros: independent scaling, tech heterogeneity
   - Cons: higher complexity, slower iteration, operational burden early on
2. Layered monolith (no strong domain boundaries)
   - Pros: simple to begin
   - Cons: erosion of boundaries; harder to extract later; coupling to persistence
3. Serverless-first (functions for each use-case)
   - Pros: elastic scaling; pay-as-you-go
   - Cons: complex coordination, cold starts, and local dev friction for this domain

## Consequences
- Positive: fast initial delivery; testable domain seams; clear contracts
- Negative: shared persistence can become a bottleneck; strong discipline needed to keep boundaries clean
- Mitigations: schema-level isolation, module CI ownership, ADRs for boundary changes

## Migration Triggers
- Disproportionate resource usage or latency for a module
- Team ownership boundaries requiring independent deploy cadence
- Integration fan-out requiring independent scaling or SLAs

## Implementation Notes
- Establish domain event nomenclature and versioning
- Define correlation/causation IDs for traceability
- Treat persistence as an implementation detail of each module
