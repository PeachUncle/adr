# ADR-0015: Split RenderX and Plugins out of MusicalConductor; Deprecate E2E here; align with ADR‑0014

Status: Accepted
Date: 2025-08-12

## Context

MusicalConductor currently hosts three concerns in a single repository:
- Core orchestration library (modules/communication)
- RenderX UI (React/Vite thin shell) and runtime plugin loader
- E2E tests (Playwright) that validate browser integration and plugins

ADR‑0014 established a thin-shell, manifest‑driven panel slot plugin model where UI delegates orchestration to conductor.play(). To reinforce architectural separation, we will split UI and plugins out of this repository and keep this repo focused on the core library.

## Decision

- Keep only the core library (musical-conductor) in this repo.
- Extract RenderX UI into a new repository (renderx-shell) that consumes musical-conductor via NPM.
- Extract plugins into dedicated package(s) (e.g., renderx-plugins/*), either separate repos or a subfolder of renderx-shell initially.
- Deprecate and remove E2E tests from this repo; E2E moves to renderx-shell.
- Maintain ADR‑0014 contract: plugins initiate flows through conductor.play(); the conductor must not directly know plugin specifics.

## Rationale

- Architectural clarity: core orchestration is independent of any UI/runtime hosting.
- Release cadence: core can be versioned and published independently of UI/UX changes.
- Test ownership: browser/E2E concerns live with the UI that exercises them.
- Developer experience: simpler local dev for core; UI/plugin dev flows are tailored in their own repo.

## Scope and Impact

In this repository (MusicalConductor):
- Remove UI and plugin code currently under RenderX/
- Remove E2E test suite under e2e-tests/
- Retain modules/communication and related unit tests, types, and CLI (if any)
- Update documentation to reflect the split and provide migration guidance

In new repositories:
- renderx-shell: React/Vite app with PanelSlot + manifest loader per ADR‑0014; imports musical-conductor from NPM
- renderx-plugins: Plugin packages built as ESM, exported via manifest with named UI entry points for slots

## Migration Plan

1) Documentation
- Add deprecation notices to READMEs in this repo (root, RenderX, e2e-tests)
- Publish this ADR and reference ADR‑0014

2) Code Moves (follow-up PRs/repos)
- Create renderx-shell repo, import RenderX/ contents (minus local alias), configure to depend on musical-conductor from NPM
- Move plugins from RenderX/public/plugins/* into a plugins workspace (single repo or multiple packages) and adjust build to output ESM bundles
- Port E2E tests from e2e-tests/ to renderx-shell, keeping the minimal Chrome-only smoke test as baseline

3) Core Cleanup
- Remove RenderX/ and e2e-tests/ from this repo
- Prune dev dependencies not needed by core (React/Vite/Playwright)
- Ensure no plugin-specific logic remains in core (e.g., no ElementLibrary debugging or special-casing in registration)

4) Versioning and Release
- Publish a minor version of musical-conductor indicating the repo split and E2E deprecation
- Note in release that RenderX UI and plugins are now developed and validated in renderx-shell(+plugins)

## Testing Strategy Post-Split

- Core (this repo):
  - Unit tests for sequences, executors, event bus, and orchestration APIs
  - Optional jsdom-based smoke to validate basic import/use in a browser-like env
- UI/Plugins (renderx-shell):
  - Playwright E2E in CI; minimal Chrome-only startup smoke as baseline
  - Console log capture for “data baton” traces across beats

## Risks and Mitigations

- Risk: Breaking consumer flows that relied on in-repo E2E
  - Mitigation: Clear deprecation notices and migration instructions; temporary overlap period if necessary
- Risk: Plugin build differences after extraction
  - Mitigation: Establish plugin build contracts (ESM output, named exports for slots) and validate in shell E2E
- Risk: Path alias drift (vite alias “musical-conductor”)
  - Mitigation: Consume musical-conductor from NPM in shell; remove repo-local alias usage

## Alternatives Considered

- Keep everything in one monorepo: rejected for now to maximize core independence and simplify publishing. May revisit later if shell+plugins benefit from a monorepo.

## Timeline

- T0: Add ADR‑0015 and deprecation notices (this PR)
- T1: Create renderx-shell repo, migrate UI and minimal E2E
- T2: Extract plugins into packages and wire manifest-driven mounting
- T3: Remove UI/E2E from this repo; publish musical-conductor minor release

## References

- ADR‑0014: tools/docs/wiki/adr/0014-manifest-driven-panel-slot-plugins.md
- RenderX Vite config (dev-time plugin loader): RenderX/vite.config.ts
- RenderX plugin manifest (dev): RenderX/public/plugins/manifest.json

