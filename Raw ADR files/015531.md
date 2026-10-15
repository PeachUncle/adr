# ADR-0031 — Control Panel Externalization Follow-Through — Boundary Enforcement

Status: Accepted
Date: 2025-09-17
Related Issue: #159
Related ADRs: ADR-0030, ADR-0020, ADR-0025

## Context
We externalized the Control Panel into the workspace npm package `@renderx-plugins/control-panel` and updated plugin-manifest and JSON sequence catalogs to use bare package specifiers. A legacy host fallback still allowed loading the internal path `/plugins/control-panel/index.ts`, which weakens boundary guarantees and risks regressions where the host accidentally couples to internal plugin sources.

## Decision
- Remove the host runtime fallback mapping for `/plugins/control-panel/index.ts`.
- Enforce package consumption via statically-known loader for `@renderx-plugins/control-panel` only.
- Add guardrail tests:
  - Assert no `/plugins/control-panel/index.ts` fallback is present in `src/conductor.ts`.
  - Assert the manifest points to `@renderx-plugins/control-panel` for both UI and runtime.
- Add package smoke tests to ensure the package exports are stable (UI export and a symphony `handlers` export).

## Consequences
- Hardens boundaries: host cannot accidentally import internal Control Panel sources.
- CI now fails if a fallback is reintroduced or the manifest regresses to path-based modules.
- The internal `plugins/control-panel` directory remains only as legacy source; it can be removed in a separate cleanup once downstream consumers are verified.

## Alternatives Considered
- Keep the fallback until all consumers migrate: rejected to avoid split-brain behavior and silent coupling.
- ESLint-only enforcement: added tests provide stronger guarantees and catch non-lint regressions.

## Work Items
- Update `src/conductor.ts` to drop the internal path fallback.
- Add `__tests__/guardrails/control-panel.externalization.guardrail.spec.ts`.
- Add `packages/control-panel/__tests__/exports.spec.ts`.
- Ensure build and full test suite pass.

## Rollback Plan
If an unforeseen environment requires the internal fallback, the mapping can be reintroduced temporarily behind a feature flag; however, prefer fixing the environment to resolve the package properly.

