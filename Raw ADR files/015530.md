# ADR-0030 — Control Panel Externalization — UI and Sequences via Host SDK

## Status
Proposed — 2025-09-15

## Context
The Control Panel plugin remains the last in-repo plugin that has not been externalized. Other plugins (Header, Library, Canvas, Library-Component) have been migrated to npm packages and are consumed via package specifiers in the host manifest. Control Panel is already sequence-driven and has a clean UI entry, but still has a few tight couplings to host internals (src/**) and its sequence catalogs reference repo paths for handlers.

Related issues/ADRs:
- Issue #144 — Decouple Control Panel: Externalize @renderx-plugins/control-panel (UI + sequences)
- ADR-0020 — Control Panel UI Sequence Orchestration
- ADR-0023 — Host SDK and Plugin Decoupling
- ADR-0025 — Externalizing Plugins to NPM Packages
- ADR-0026 — Library Decoupling — Host-owned Inventory and Externalized Library Plugin
- ADR-0027 — Library-Component Externalization
- ADR-0028/0029 — Canvas Externalization Phases

## Decision
Create an external npm package `@renderx-plugins/control-panel` that provides:
- UI export: `ControlPanel`
- Runtime export: `async function register(conductor)` (idempotent)
- Symphony handler modules under `symphonies/*/*.symphony` exporting `handlers`

And update the host to consume it via package specifiers:
- plugin-manifest.json: `"module": "@renderx-plugins/control-panel"` for UI and runtime
- json-sequences/control-panel/index.json: handlersPath entries use bare package specifiers, e.g. `"@renderx-plugins/control-panel/symphonies/ui/ui.symphony"`

Replace any host-internal imports with Host SDK:
- `EventRouter`, `resolveInteraction`, `useConductor`, `isFlagEnabled` from `@renderx-plugins/host-sdk`

## Consequences
- Control Panel becomes portable and versioned independently; the host remains a thin shell.
- Tests/lint in both repos enforce boundaries (no `src/**` imports; only SDK, React, manifest-tools in build tooling where applicable).
- Sequence handler loading relies on bare specifiers (already supported by the host’s loader and lint rule `valid-handlers-path`).

## Implementation Notes
- Package setup: ESM + types, `exports` map, `sideEffects`, CSS strategy (emit ControlPanel.css and import in UI entry or CSS-in-JS).
- Dependencies:
  - `@renderx-plugins/host-sdk` as a peerDependency (and devDependency for local tests/build)
  - `@renderx-plugins/manifest-tools` only if the package generates/validates its own manifest fragments (devDependency)
- Tests (external package):
  - Unit: handler exports shape; basic UI smoke
  - Registration: `register(conductor)` idempotence and plugin id correctness
  - Packaging: importability via package specifier; ESM/types; tree-shakeable
- Host-side tests/guards:
  - Manifest: `ControlPanelPlugin` UI/runtime module uses the package name
  - Sequences: all control-panel handlersPath start with `@renderx-plugins/control-panel/`
  - Integration smoke: selection → render; classes add/remove; field change → canvas update via SDK interaction resolution
  - Lint: `valid-handlers-path` and boundary rules clean

## Plan & Phases (TDD-first)
1) Temporary package + host wiring
- Create/ext link `@renderx-plugins/control-panel`; export UI + register
- Replace repo-relative imports with SDK in selection/ui/update/classes/css-management handlers
- Ensure `handlers` exports exist across symphonies
- Update host manifest and sequence catalogs to use package specifiers
- Add/enable tests and lint guardrails

2) Pre-release npm package
- Build `dist` (ESM + types), verify `sideEffects` and CSS emission
- Publish prerelease (e.g., `0.1.0-rc.x`); validate via `npm pack`/verdaccio
- Host consumes prerelease; tests pass

3) Stabilize & remove in-repo code
- Soak running with npm package (lint/test/build + E2E)
- Remove any remaining in-repo Control Panel code after soak window

## Acceptance Criteria
- Host manifest references `@renderx-plugins/control-panel` for UI/runtime
- Control Panel sequence catalog uses bare handlersPath package specifiers
- No `src/**` imports remain in the Control Panel package (lint enforced)
- Unit/integration tests pass (selection render, field change dispatch, classes management)
- Build and E2E pass in CI without runtime loader errors

## Risks & Mitigations
- Bare specifier resolution in browser preview → Host already normalizes/bundles bare specifiers; ensure Vite optimizeDeps/runtime loader map are aligned
- CSS loading from package → Adopt a consistent CSS emission/import strategy and validate in preview/E2E
- Duplicate mounts → Guard `register()` and avoid double-mounting during transition

## Decision Drivers
- Consistency with previous externalization work and thin-shell architecture
- Reduced coupling to host internals; improved release cadence
- Clear, testable boundaries via the Host SDK and manifest-driven routing

## References
- Issue: #144
- ADRs: 0020, 0023, 0025, 0026, 0027, 0028, 0029

