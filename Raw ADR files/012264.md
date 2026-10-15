---
title: "ADR-003: Saga Pattern for Cross-Domain Operations"
status: APPROVED
owner: Architecture Team
date: 2026-01-13
---

# ADR-003: Saga Pattern for Cross-Domain Operations

## Decision

Use the Saga pattern (choreography-based) for operations that span multiple
domains.

## Context

Cross-domain operations (e.g., "Approve Proposal and Update Accounting") require
coordination across bounded contexts while maintaining:

- Atomicity (all-or-nothing semantics)
- Consistency (eventual, not immediate)
- Auditability (full trace of steps)
- Resilience (graceful failure handling)

## Options Considered

### Option A: Distributed Transactions (2PC)

- **Pros**: Strong consistency
- **Cons**: Performance bottleneck, single point of failure, complex recovery

### Option B: Orchestration Saga

- **Pros**: Centralized control, easier debugging
- **Cons**: Orchestrator is a single point of failure, tight coupling

### Option C: Choreography Saga (Chosen)

- **Pros**: No central coordinator, domains remain autonomous, resilient
- **Cons**: Harder to visualize full flow, requires correlation IDs

## Consequences

### Positive

- No central coordinator to fail
- Domains react to events independently
- Compensation actions are explicit and testable
- Full audit trail via correlation IDs

### Negative

- Flow visualization requires distributed tracing
- Developers must implement compensation logic
- Testing requires event simulation

## Saga Examples

### Proposal Approval Saga

```
1. BoardRoom emits: proposal.approved {proposalId, correlationId}
2. Accounting reacts: creates journal entry, emits: journal.created
3. Audit reacts: creates audit record, emits: audit.recorded
4. BoardRoom reacts: marks proposal as fully processed
```

### Compensation Flow

```
If step 2 fails:
1. Accounting emits: journal.creation.failed {reason, correlationId}
2. BoardRoom reacts: reverts proposal to pending-review
3. Notification emits: approval.requires.attention
```

## Compliance

- Refuse List check: PASS (`docs/governance/REFUSE_LIST.md`)
- Silence Budget impact: +0 (no UI surface)
- Degradation plan: N/A (backend architecture)

## Links

- Related: `docs/governance/UX_RATIFICATION_PROCESS.md`
- See also: ADR-001 (Event-Driven), ADR-002 (Domain Boundaries)
