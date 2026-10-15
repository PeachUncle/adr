# ADR-0026 — Library Decoupling: Host-owned Inventory and Externalized Library Plugin

Status: Accepted (Phase 1 implemented in-repo; externalization pending)
Date: 2025-09-10
Relates to: #115

## Context
- The Header plugin has been externalized as an npm package and is loaded via package specifier in the plugin manifest.
- The Library plugin remains in-repo and is coupled to:
  - repo-local component JSON (/json-components) access paths, and
  - a cross-plugin import of Control Panel’s `cssRegistry` store.
- For long-term scalability, orchestration, and runtime extensibility, the host should own the unified component inventory and expose it via a stable SDK.
- Plugins should interact only through the Host SDK boundary and avoid importing host internals or other plugins’ internals.

## Decision
- Host-owned inventory, exposed via @renderx-plugins/host-sdk with minimal, composable APIs:
  - `listComponents(): Promise<ComponentSummary[]>`
  - `getComponentById(id: string): Promise<ComponentDetail | undefined>`
  - `onInventoryChanged(cb: (event) => void): () => void` (unsubscribe)
  - (optional) `registerComponents(components: ComponentDetail[])`
- Introduce an SDK facade for CSS registry management used by plugins:
  - `cssRegistry.hasClass(name)`, `cssRegistry.createClass(name, content)`, `cssRegistry.updateClass(name, content)`
- Externalize the Library plugin as `@renderx-plugins/library` and load it via package specifier for both UI and runtime registration.
- Sequences continue to be registered into the Conductor during host startup; plugins provide a `register(conductor)` runtime export.
- Enforce boundaries with a new ESLint rule forbidding cross-plugin imports (complements existing no-host-internals-in-plugins).

## Architecture (Mermaid)
```mermaid
flowchart LR
  subgraph Host_App_Thin_Shell
    PanelSlot
    Conductor
    Inv["Inventory Aggregator"]
  end

  subgraph External_Packages
    SDK["@renderx-plugins/host-sdk (Facade, npm)"]
  end

  subgraph Plugins
    Lib["@renderx-plugins/library"]
    Head["@renderx-plugins/header"]
    CP["Control Panel"]
  end

  PanelSlot -- "manifest: UI module" --> Lib
  PanelSlot -- "manifest: UI module" --> Head

  Lib -- "listComponents()/getComponent()" --> SDK
  Lib -- "cssRegistry.*()" --> SDK

  SDK --> Inv
  SDK -- "facade" --> CP

  Host_App_Thin_Shell -- "manifest: runtime register" --> Conductor
  Conductor -. "calls" .-> Lib
  Conductor -. "calls" .-> Head

  CP -. "contributes (optional)" .-> Inv
  Lib -. "contributes (optional)" .-> Inv
```

## Future Structures (ASCII)
```
renderx-plugins-demo/                    # host repo
├─ docs/
│  └─ adr/
├─ json-plugins/
│  └─ plugin-manifest.json               # uses package specifiers for Library/Header
├─ src/
│  ├─ conductor.ts                       # runtimePackageLoaders includes @renderx-plugins/library
│  └─ ...

# External packages/repos (consumed via npm)
@renderx-plugins/host-sdk                # separate repo; exposes inventory + cssRegistry facades
renderx-plugin-library/                  # separate repo; externalized Library plugin
├─ package.json (exports ./dist/index.js)
├─ src/
│  ├─ index.ts                           # export LibraryPanel, export async function register(conductor)
│  ├─ ui/LibraryPanel.tsx
│  └─ symphonies/load.symphony.ts        # uses SDK inventory + cssRegistry
└─ dist/
```

## Consequences
- Clear separation of concerns: host orchestrates and exposes inventory; plugins consume via SDK.
- Library becomes portable and distributable; the host manifest uses package specifiers.
- Boundary violations (e.g., cross-plugin imports) are prevented by lint policy.
- Additional host responsibility: aggregate inventories (built-in + contributions), keep APIs stable under semver.

## Implementation Plan (Phased, TDD-first)
1) Policy & Tests
- Add ESLint rule `no-cross-plugin-imports` and unit tests.
- Add a manifest validation test ensuring Library uses a package specifier when enabled.
- Add import-path tests ensuring Library references SDK for inventory and cssRegistry.

2) SDK + Host Aggregator
- Update external @renderx-plugins/host-sdk to add inventory APIs.
- Update external @renderx-plugins/host-sdk to add cssRegistry facade.
- Implement host-side aggregator (dev/test: read /json-components; support runtime contributions).

3) Library Refactor
- Replace `../../control-panel/state/css-registry.store` import with SDK `cssRegistry`.
- Replace repo-path JSON access with SDK inventory calls (browser + test paths).

4) Externalization & Manifest
- Create/publish `@renderx-plugins/library`.
- Update `json-plugins/plugin-manifest.json` to use package specifier for Library UI/runtime.
- Add `@renderx-plugins/library` to runtimePackageLoaders and Vite optimizeDeps.

5) Stabilization
- Unit tests and E2E: Library panel render + basic interaction.
- Optional short transition window (feature-flagged) before removing in-repo Library.

## Alternatives Considered
- Library owning the inventory: rejected for orchestration and duplication concerns.
- Keeping JSON catalogs as the sole source for Library: acceptable during transition, but programmatic registration via `register(conductor)` is preferred long term.
- Moving cssRegistry into a separate shared package instead of SDK: possible, but SDK facade provides a single, stable boundary and aligns with ADR-0023.

## Risks & Mitigations
- Runtime loading issues for external package → Prebundle config and runtimePackageLoader entries; CI E2E smoke.
- API creep in inventory → Start minimal (list/get/observe); iterate under semver.
- Transitional complexity → Feature flag + dual-mode support temporarily.

## External Library Repo — Tests (Minimum Suite)
- Unit: LibraryPanel renders from SDK-provided inventory stubs; mirrors data-* attributes; basic event/prop wiring.
- Runtime registration: `register(conductor)` registers sequences; plugin id available to `play()`; no cross-plugin imports.
- SDK integration: exercises `cssRegistry.has/create/update` via the SDK facade; no direct Control Panel import.
- Packaging: `dist/index.js` exports (types/ESM), `sideEffects` correctness, importable via package specifier.
- Manifest/host compatibility: minimal harness or mock to simulate host loading the UI module via package specifier.
- Linting: boundary rule active in the plugin repo (no host internals, no cross-plugin imports).

## Migration Strategy (Incremental Externalization)
1) Temporary in-repo package
- Move Library into /packages/renderx-plugin-library (workspace package)
- Wire workspace build/lint/tests; enable boundary lint rules
- Update plugin manifest to reference the workspace package specifier for UI/runtime
- Gate to next phase when CI is green and no cross-plugin imports remain

2) Pre-release npm package
- Publish 0.x prerelease (or use npm pack/verdaccio) and validate install/import
- Run plugin repo tests; verify `dist/index.js` exports are correct (types/ESM) and `sideEffects` config is accurate
- Gate to next phase when package consumers pass smoke tests

3) Host switches to npm package
- Change host manifest to use @renderx-plugins/library from npm (feature-flag if needed)
- Ensure runtimePackageLoaders and dev prebundle (optimizeDeps) include the package
- Soak/stabilize; remove any residual repo-path assumptions

4) Split repo and remove temporary package
- Create standalone repo for renderx-plugin-library and migrate history
- Remove /packages/renderx-plugin-library from host repo
- Keep semver discipline; stabilize CI in both repos

## References
- Issue #115 — Decouple Library Plugin: Host-owned Inventory via SDK, Externalize @renderx-plugins/library, and Enforce Boundaries
- ADR-0023 — Host SDK and Plugin Decoupling
- docs/design-reviews/library-decoupling-review.md
- docs/host-sdk/USING_HOST_SDK.md

