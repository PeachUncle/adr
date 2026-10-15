# Decision: Architecture Hardening (Priority 5)

## Date
2024-11-29

## Context
- Need to improve maintainability and scalability.
- Priority 5 tasks: feature-based structure, move off makeStyles, standardize state (Zustand + React Query), centralized API client, granular error boundaries, structured logging.
- Current codebase is flat with mixed styling/state patterns and no shared logging/error boundary contracts.

## Decision
- Adopt feature-based directories under `src/features/*` with shared utilities under `src/shared/*`.
- Introduce shared “bricks” first: API client, state helpers, logging, error boundaries, styled wrapper.
- Use these bricks to migrate feature slices incrementally (starting with auth/configurator), moving stores to Zustand and data-fetch to React Query.
- Migrate makeStyles usage to a `styled` wrapper as slices are touched; no one-shot codemod across the repo.

## Options Considered
1) **Big-bang refactor** to feature structure and global state/styling migration.
   - Pros: uniform end state quickly.
   - Cons: high risk, large blast radius, long-lived branch, hard to test.

2) **Incremental “bricks first”** (chosen): lay shared contracts, then migrate features slice by slice.
   - Pros: bounded risk, testable increments, aligns with modular philosophy, enables regeneration.
   - Cons: temporary dual patterns until migration completes.

3) **Status quo with localized patches** (rejected): keep flat structure and patch hotspots.
   - Pros: lowest immediate effort.
   - Cons: perpetuates entropy; doesn’t meet Priority 5 goals.

## Rationale
- Modular “bricks & studs” reduces coupling and supports regeneration by agents.
- Shared contracts (API client, state, logging, error boundaries, styled) provide clear studs for feature teams.
- Incremental migration minimizes downtime and conflicts.

## Impact
- New directories: `src/shared/{api,state,logging,ui/error-boundaries,styles}` and `src/features/*`.
- Gradual adoption of Zustand + React Query; makeStyles deprecated in favor of `styled` wrapper.
- Centralized logging and error boundary usage across app.

## Rollout Plan
1) Add shared bricks (API client, state helpers, logging, error boundaries, styled wrapper).
2) Migrate first slice (auth/configurator) into `src/features/*` using new studs.
3) Migrate remaining features iteratively; remove legacy imports as they move.

## Review Triggers
- If shared bricks prove hard to consume or introduce perf issues.
- If feature migrations stall due to coupling or missing contracts.
