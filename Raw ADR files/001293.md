# ADR-0003: Invariant Testing Framework Consolidation

Status: Proposed

Date: 2025-09-01

Supersedes: None

Superseded-By: None

## Context

Invariant tests currently exist for EnhancedRealYieldStrategy in a single file. As platform complexity grows (multi-strategy interactions, PortfolioManager rebalancing, emergency flows), scattered ad-hoc invariants become hard to audit and reason about. We need a unified methodology for defining, tagging, executing, summarizing, and gating invariants in CI.

## Decision

Adopt a standardized invariant framework layer:

- Naming: `<Contract>.invariants.test.(js|ts)` per domain + cross-contract suite
- Categories (prefix tags): `[STATE]`, `[ECON]`, `[ACCESS]`, `[TIME]`, `[GAS]`
- Common helper utilities for random scenario generation and time shifting
- Automated summary generator (already scaffolded: `invariants-summary.js`) extended to aggregate all invariant files
- CI job: run invariants separately; fail build on any invariant breach; upload coverage summary artifact

## Alternatives Considered

1. Property-based fuzzing via Foundry (deferred: would introduce second toolchain; revisit post audit)
1. Leave invariants embedded in integration tests (rejected: poor discoverability & inconsistent failure semantics)
1. Rely solely on manual review (rejected: non-scalable; high regression risk)

## Rationale

Consistent structure improves audit readiness, speeds regression isolation, and enables future migration to property-based fuzzing with minimal rework.

## Consequences

Positive: Clarity, audit traceability, easier maintenance.  
Negative: Slight CI runtime increase; additional organizational overhead.  
Risk: Tag misuse without linting (mitigate with pattern check script future).

## Implementation Sketch

- Extend `invariants-summary.js` to glob `*.invariants.test.*`
- Add `npm run test:invariants` script invoking Hardhat with grep
- Add CI step producing `invariant-reports/INVARIANTS-COVERAGE.md` artifact
- Optional: enforce minimum invariant count growth over time

## Testing Strategy

- Ensure failure of one invariant exits with non-zero code
- Add mock failing invariant for negative test (not committed) locally

## Follow-ups

- Add ADR for property-based fuzzing migration (future)
- Add invariant tag linter (script)

Last updated: 2025-09-01
