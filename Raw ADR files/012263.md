---
title: "ADR-002: Domain Boundary Definition"
status: APPROVED
owner: Architecture Team
date: 2026-01-13
---

# ADR-002: Domain Boundary Definition

## Decision

Define explicit boundaries for each domain using the following criteria:

1. Data ownership (what data the domain controls)
2. API contracts (how the domain exposes capabilities)
3. Event contracts (what events the domain emits)

## Context

Without clear boundaries, domains risk becoming entangled, leading to:

- Unclear ownership of data and behavior
- Breaking changes cascading across the system
- Difficulty in independent deployment and testing

## Options Considered

### Option A: No Formal Boundaries

- **Pros**: Faster initial development
- **Cons**: Technical debt, unclear ownership, integration nightmares

### Option B: Microservices per Feature

- **Pros**: Maximum isolation
- **Cons**: Over-engineering, operational complexity

### Option C: Bounded Contexts with Explicit Contracts (Chosen)

- **Pros**: Clear ownership, manageable complexity, explicit contracts
- **Cons**: Requires upfront design, contract versioning overhead

## Consequences

### Positive

- Each domain has clear ownership and accountability
- API contracts are versioned and documented
- Event schemas are explicit and validated
- Teams can work independently within their domain

### Negative

- Cross-domain features require coordination
- Contract changes need backward compatibility
- Initial setup requires more planning

## Domain Inventory

| Domain        | Data Owned                          | Primary Events                        |
| ------------- | ----------------------------------- | ------------------------------------- |
| BoardRoom     | Proposals, Decisions, Votes         | proposal.created, decision.ratified   |
| Accounting    | Ledger, Journals, Accounts          | transaction.posted, period.closed     |
| CRM           | Contacts, Opportunities, Activities | contact.created, opportunity.won      |
| Manufacturing | Orders, BOM, WorkCenters            | order.scheduled, production.completed |
| Supply Chain  | Inventory, Transfers, Locations     | stock.adjusted, transfer.completed    |

## Compliance

- Refuse List check: PASS (`docs/governance/REFUSE_LIST.md`)
- Silence Budget impact: +0 (no UI surface)
- Degradation plan: N/A (backend architecture)

## Links

- Related: `docs/governance/UX_RATIFICATION_PROCESS.md`
- See also: ADR-001 (Event-Driven), ADR-003 (Saga Pattern)
