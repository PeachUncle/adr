# ADR-0001: Adopt Trigger Handler + Domain Pattern

Status: Accepted
Date: 2025-12-11
Superseded by: —

## Context
- We need a consistent, testable, and maintainable approach for Apex triggers across multiple sObjects (e.g., Account, Order).
- Common problems with ad-hoc triggers: duplicated logic, recursion issues, and poor separation of concerns.
- We want to standardize on a domain-driven pattern that isolates trigger orchestration from business rules and services.

## Decision
Adopt a trigger framework with:
- A base abstract TriggerHandler (template) implementing lifecycle hooks (before/after insert/update/delete/undelete)
- Per-object Domain classes that extend TriggerHandler and encapsulate business rules
- Triggers that directly instantiate the Domain class and call run(), e.g.:
  - new AccountDomain().run();
- Recursion safety via a utility and/or idempotent design
- Dependency creation via Application/Service factories to support DI/mocking in tests

## Consequences
Positive:
- Single-responsibility triggers with predictable lifecycle
- Domain logic is discoverable and unit-testable
- Easier to extend to new objects by adding a new Domain class

Negative / Risks:
- Requires discipline to keep business logic out of triggers
- Slight upfront boilerplate
- Devs must learn the framework conventions

## Alternatives Considered
1. Logic directly in triggers
   - Pros: Less boilerplate
   - Cons: Error-prone, hard to test/scale, encourages duplication
2. Single “dispatcher-style” class
   - Pros: Centralized entry
   - Cons: Can become a god-object; less explicit per-object ownership

## Technical Notes
- Handlers must defensively handle null Trigger maps as context varies by operation
- Domain classes should avoid DML/SOQL inside loops and respect governor limits
- Service calls should expose interfaces for mocking
- Use with sharing and USER_MODE where needed to respect security
- Trigger pattern used:
  - trigger AccountTrigger on Account (...) {
      new AccountDomain().run();
    }

## Links
- Feature example: docs/features/FEATURE-0007-account-postal-code-validation.md
- Diagrams:
  - docs/diagrams/trigger-flow.mmd
  - docs/diagrams/architecture-overview.mmd
- PR: Link to PR that introduced the framework (if available)
