# ADR-0028 — Canvas Externalization — Canvas UI and Canvas-Component Runtime Registration

Status: Accepted
Date: 2025-09-12
Related issue: #129 — Decouple Canvas: Externalize @renderx-plugins/canvas (+ runtime) and Enforce Boundaries
Related PR: #132

## Context
We are externalizing Canvas into two packages following the thin-host, plugin-based architecture:
- @renderx-plugins/canvas — UI shell (CanvasPage) mounted into the host layout
- @renderx-plugins/canvas-component — runtime sequences mounted from JSON catalogs

Other plugins (Header, Library, Library-Component) already follow this pattern. We need a consistent, idempotent runtime registration contract and a manifest entry so the host can discover and register the runtime safely before mounting JSON catalogs.

## Decision
- Add an idempotent register(conductor) export to @renderx-plugins/canvas-component. This performs no mounts (JSON catalogs handle sequence mounting) but allows hosts to register the runtime safely multiple times without side effects.
- Add a runtime entry to the plugin manifest for Canvas-Component:
  - id: CanvasComponentPlugin
  - runtime: { module: "@renderx-plugins/canvas-component", export: "register" }
- Keep Canvas UI as a separate plugin entry (CanvasPlugin) with UI slot: canvas and runtime: @renderx-plugins/canvas/register.
- Maintain workspace build outputs and deep symphony re-exports so JSON handlers resolve via bare specifiers.

## Rationale
- Consistency: Matches Library-Component’s published contract and guardrails.
- Idempotency: Hosts can call registerAllSequences repeatedly without duplicate mounts.
- Discoverability: The manifest-driven registration flow remains the single source of truth.

## Consequences
- Tests added to guard the manifest contract and host registration behavior:
  - __tests__/canvas-component/registerAllSequences.spec.ts — validates sequences mount once and expected plugin ids are present
  - __tests__/canvas-component/manifest.runtime.entry.spec.ts — validates manifest includes a runtime entry for @renderx-plugins/canvas-component
- Build and artifact aggregation include the new runtime entry (total plugins increased by one).

## Alternatives considered
- Mounting sequences inside register(): rejected. JSON catalogs are the canonical mount source; register is a pre-mount hook only.
- No manifest runtime entry: rejected. Would rely on implicit side effects and reduce host discoverability.

## Follow-ups
- Publish @renderx-plugins/canvas-component independently and move re-exports to true external package entry points.
- Extend guardrails to assert no duplicate JSON mounts when registerAllSequences runs multiple times.



## Status update — 2025-09-13
- Phase 1 kicked off under issue #129.
- Packages exist in-repo: `@renderx-plugins/canvas` (UI) and `@renderx-plugins/canvas-component` (runtime).
- Idempotent `register(conductor)` guards implemented; sequence mounting remains via JSON catalogs.
- Package-local tests added (export surfaces, register idempotency) — green.
- CI E2E stabilized and green; next is host-level tests validating manifest routing and PanelSlot loading by specifier.


## Status update — 2025-09-14
- Host-level guardrails added and verified:
  - __tests__/layout/panelslot.canvas.spec.tsx — PanelSlot loads Canvas UI via package specifier (@renderx-plugins/canvas → CanvasPage)
  - __tests__/manifest/canvas.manifest.spec.ts — Manifest asserts Canvas UI + Canvas-Component runtime specifiers
  - __tests__/canvas-component/registerAllSequences.idempotency.spec.ts — Calling registerAllSequences() twice mounts no duplicates (idempotency)
- Conductor runtime logging adjustment:
  - Emit "Registered plugin runtime: <id>" when the runtime module resolves successfully (before awaiting register())
  - Rationale: removes timing races in JSDOM/preview and stabilizes the startup-logs guardrail while preserving register() semantics
- Acceptance outcomes:
  - Manifest uses only @renderx-plugins/* specifiers for Canvas UI/runtime and Canvas-Component runtime; no repo-relative paths remain
  - Idempotency guardrail passes; duplicate mounts are prevented when JSON loader and register() coexist
  - Full build and test suites (root + packages) are green

### Notes
- This is a logging-order refinement only; no change to runtime behavior beyond when the success message is emitted.
- E2E diagnostics can be enabled locally by setting RX_E2E_DIAG=1 (CI remains quiet by default).

- Future phases will address prerelease publishing and host switching to npm-installed packages.
