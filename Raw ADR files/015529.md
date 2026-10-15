# ADR-0030 — Control Panel Externalization — UI + Sequences to NPM Package

- Status: Proposed
- Date: 2025-09-15
- Issue: #144 — Decouple Control Panel: Externalize @renderx-plugins/control-panel (UI + sequences) and Enforce Boundaries
- Related: ADR-0014 (JSON-defined sequences), ADR-0023 (Host SDK and decoupling), ADR-0025 (Externalizing plugins), ADR-0027 (Library-Component externalization)

## Context
The Control Panel currently lives inside the host repo under `plugins/control-panel`, and its sequences are cataloged under `json-sequences/control-panel`. We are moving to a model where plugin UIs and runtime sequences ship as external npm packages, consumed via the host manifest and orchestrated through the Host SDK.

We want:
- A standalone `@renderx-plugins/control-panel` package exporting `ControlPanel` UI and `async function register(conductor)` for runtime sequences.
- The host to reference the package by bare specifier in `json-plugins/plugin-manifest.json` for both UI and runtime entries.
- Boundary enforcement: no imports from host internals, no cross-plugin imports; only import from the Host SDK and package-local code.
- Compatibility with JSON-mounted sequences and handler export validation via existing lint rules.

## Decision
- Update host manifest to point Control Panel UI and runtime to `@renderx-plugins/control-panel`.
- Keep sequence definitions data-driven (JSON), with handlers exported from the package. The host loader may mount from catalogs aggregated at build-time or via the runtime `register(conductor)` when provided.
- Enforce boundary rules (ESLint) identical to other externalized plugins, and extend tests to cover manifest expectations for Control Panel.

## Migration Plan (Phased)
1) Host-side switch (this PR/issue):
   - Add unit test to require manifest references to `@renderx-plugins/control-panel` (UI + runtime).
   - Update `json-plugins/plugin-manifest.json` accordingly.
   - Ensure lints and unit tests pass.

2) Package availability + dev ergonomics:
   - Add `@renderx-plugins/control-panel` dependency in the host (npm install) and Vite dev prebundle include.
   - If the package ships JSON catalogs, include them in artifact aggregation (docs already cover approach).

3) Boundary and handler validation:
   - Ensure `valid-handlers-path` and `handler-export-exists` rules support package-based handlersPath for Control Panel catalogs.
   - Add/extend ESLint `RuleTester` coverage if needed (package specifier path variant).

## Consequences
- Host no longer builds/bundles Control Panel UI from repo-local sources; it loads from package.
- Runtime orchestration can be validated independently in the package; host focuses on integration.
- Clear boundaries enforced by ESLint reduce coupling and accidental breakage.

## Notes
- This ADR follows the same pattern deployed for `@renderx-plugins/library` and `@renderx-plugins/library-component`.
- Future follow-up may include extracting remaining in-repo Control Panel code and deleting `plugins/control-panel/**` once the package is fully adopted by CI and e2e tests.

