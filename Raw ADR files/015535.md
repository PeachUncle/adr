# ADR-0036 — Host SDK v1 Adoption — Externalize `src/core`

- Status: Proposed
- Date: 2025-09-25
- Related Issue: #253 — Externalize src/core into @renderx-plugins/host-sdk to make the thin host super thin
- Supersedes/Builds on: ADR-0023 — Host SDK and Plugin Decoupling

## Context
The host currently contains orchestration/runtime logic under `src/core/**` (conductor, events, manifests, startup validation, environment/flags). A stable, shared SDK (`@renderx-plugins/host-sdk`) has reached v1.0.0, providing these primitives for hosts and plugins.

## Decision
Adopt `@renderx-plugins/host-sdk@^1.0.0` and migrate all imports from `src/core/**` to SDK entry points:
- `@renderx-plugins/host-sdk/conductor`
- `@renderx-plugins/host-sdk/events`
- `@renderx-plugins/host-sdk/manifests`
- `@renderx-plugins/host-sdk/startup`
- `@renderx-plugins/host-sdk/env`

We will remove `src/core/**` from this repo after verification. Temporary re-export shims may be used during migration, but the final state is SDK-only.

## Rationale
- Makes the host “super thin,” aligning with plugin-first architecture
- Single source of truth for orchestration, easier testing and semver governance
- Reduces duplication and drift across hosts

## Consequences
- Requires dependency bump and code refactors for import paths
- Some vendor- or build-time helpers (e.g., Vite `import.meta.glob` integration) move behind SDK utilities
- CI/Tests must be updated to reference SDK where needed

## Verification
- Add TDD test asserting v1 SDK surface exists and is consumable (see `src/core-to-sdk.migration.test.ts`)
- Build, lint, and all tests must pass
- E2E readiness beacons unchanged (library/canvas load)

## Rollout Plan
1. Add failing test for SDK v1 surface (TDD)
2. Upgrade dependency to `@renderx-plugins/host-sdk@^1.0.0`
3. Migrate imports (conductor/events/manifests/startup/env)
4. Run unit/E2E tests; fix regressions
5. Remove `src/core/**` and update docs

## References
- Issue #253
- ADR-0023 — Host SDK and Plugin Decoupling
- docs/design-reviews/NEW_STRUCTURE.md

