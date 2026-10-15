# ADR-0025 — Externalizing Plugins to NPM Packages, Aggregated Manifests, and Sequence Handling

- Status: Accepted
- Date: 2025-09-08
- Issue: #107
- Related: ADR-0014, ADR-0023, ADR-0024

> Update 2025-09-09
> - Implemented Phase 1–3 for the Header plugin: UI, handlers, and JSON sequences are now shipped from the `@renderx/plugin-header` workspace package and aggregated into the host at build time.
> - Loader updated to support bare specifiers with a Vite dev fallback (`/@id/<specifier>`), covered by tests.
> - All unit and e2e tests are green; this ADR is marked Accepted.


## Context
We want to transition in-repo plugins into separate repositories and distribute them as npm packages while keeping a thin host (src). The host today:
- Loads UI plugins via a consolidated `/plugins/plugin-manifest.json` and `PanelSlot` dynamic imports (package names/paths/URLs supported).
- Mounts runtime sequences from JSON catalogs (`json-sequences/<dir>/index.json` → sequence JSON → dynamic import of `handlersPath`).
- Supports an artifacts pipeline and integrity hashing (dev-time verification).

Key code references:
- Panel UI loading:
  - src/components/PanelSlot.tsx lazy-loads UI via manifest entries (package name, path, or URL).
- Sequence mounting:
  - src/conductor.ts loads catalog JSONs and imports handlers by `handlersPath`.
- Manifest:
  - Consolidated plugin manifest expected at `/plugins/plugin-manifest.json` (scripts/sync-plugins.js copies json-plugins → public/plugins).
- Artifacts & integrity:
  - scripts/build-artifacts.js; src/startupValidation.ts integrity verifier; src/env.ts HOST_ARTIFACTS_DIR.

## Decision
1) Distribution model
- Plugins are published as ESM npm packages with sourcemaps and an “exports” map (UI entry + optional handler subpaths).
- Host continues to load a consolidated `/plugins/plugin-manifest.json` (aggregated) describing UI and optional runtime registration entries.

2) Manifest aggregation (build-time)
- Host adds a pre-build aggregation step to:
  - Discover installed plugin packages (by keyword, e.g., "renderx-plugin").
  - Merge each package’s manifest fragment into json-plugins/plugin-manifest.json.
  - Copy plugin-provided JSON sequences and handler assets into a composed artifacts set (either to public/* for dev or to dist/artifacts for production integrity).

3) Sequence catalogs (two supported patterns)
- Phase A (default first): Path-based handlers with asset copy
  - Keep `handlersPath` as file paths served under `/plugins/<pkg>/...`; aggregator copies plugin assets accordingly.
- Phase B (optional advanced): Bare package specifiers in `handlersPath`
  - Allow `handlersPath` like "@scope/plugin/symphonies/resize/start.js".
  - Loader detects bare specifiers and imports as-is (no "/" prefixing).

4) Loader compatibility
- Update the conductor’s `handlersPath` normalization to:
  - If URL (http/https) → import as-is
  - If bare package specifier (not starting with "/" or ".") → import as-is
  - Else treat as a path (current normalization preserved)

5) Catalog directory naming
- Deprecate legacy pluginId→catalog-dir mappings; introduce a manifest field (e.g., `catalogDirs: ["canvas-component"]`) for clarity during the transition.
- In mixed mode, keep existing mappings but prefer manifest-provided directories when present.

6) Host SDK as the contract (reinforces ADR-0023)
- Plugins must import host capabilities from `@renderx/host-sdk` (stable, versioned surface) and not from `src/**`.
- Host SDK evolves via semver; CI checks the public API surface.

7) Artifacts integrity (extends ADR-0024)
- Aggregated artifacts (including external plugin JSONs and any copied handler assets) are hashed into artifacts.integrity.json (SHA-256 per file + aggregate).
- Dev-only runtime verification continues to warn on mismatches; can be disabled via env.

8) Debugging & DX
- Plugins publish sourcemaps; devtools show original TS/TSX.
- Local development uses workspaces/npm link for HMR; Vite defaults suffice if packages ship prebuilt ESM.
- Avoid importing plugin TS sources directly from the host to keep build simple.

## Consequences
- Phased migration with minimal risk:
  - UI import via package name already works today.
  - Sequences work via artifacts copy without loader changes.
  - Later, bare specifiers can remove the need for copying handler files.
- Security and supply-chain are improved by npm packaging and integrity checks (avoid arbitrary URL imports by default).
- Manifest remains a single source of truth, enabling both dev and build flows.

## Implementation Notes
- UI loading (already supports packages):
  - PanelSlot imports `ui.module` as provided (package/path/URL).
- Sequence loader adjustment (small change):
  - Detect bare specifiers/URLs before prefixing paths.
- Manifest aggregation:
  - Add a script to scan node_modules for packages with keyword "renderx-plugin".
  - Expected package fields:
    - `"renderx"`: { "manifest": "./dist/plugin-manifest.json", "catalogDirs": ["..."] }
    - or embed plugin entries into package.json `renderx`.
  - Merge fragments into json-plugins/plugin-manifest.json.
  - Copy `json-sequences/<dir>` and handler assets to public/json-sequences and public/plugins (dev) or into dist/artifacts (prod).
- Backward compatibility:
  - Continue supporting local json-sequences dirs and repo-local plugin code during migration.

## Migration Plan (Phased)
1. Phase 1 — UI-first pilot
   - Externalize the “header” plugin UI into a package; set manifest `ui.module` to the package name.
   - Verify devtools visibility and HMR via workspaces/link.

2. Phase 2 — Externalize handlers (keep JSON in host)
   - Move handler modules into the package; aggregator copies built JS handlers to `/public/plugins/<pkg>/...`.
   - `handlersPath` remains path-based.

3. Phase 3 — Externalize JSON sequences
   - Package ships `json-sequences/<dir>/*`; aggregator copies into host’s public/json-sequences (or artifacts dir).

4. Phase 4 — Optional: bare specifiers
   - Switch `handlersPath` to package subpaths; conductor imports bare specifiers without path normalization.

5. Phase 5 — Standardize and harden
   - Remove legacy id→dir mappings once all packages declare catalogDirs.
   - Enforce lint boundary (plugins import only `@renderx/host-sdk`).
   - Integrate integrity into CI along with artifact pack/verify.

## Risks
- Mixed-mode complexity (local + external packages) → mitigated by keeping both code paths and aggregation.
- Handler path divergence (path vs bare specifier) → mitigated by loader detection and gradual rollout.
- Duplicate IDs (pluginId/sequenceId) across repos → require CI validation in aggregator.

## Testing
- PanelSlot e2e tests loading UI from package names.
- Conductor unit tests:
  - Index + sequence JSON fetch flow (browser) and fs fallback (Node) remain green.
  - Loader: ensure URL, bare specifier, and path modes resolve correctly.
- Startup integrity:
  - Tamper test on artifact JSON triggers dev warning (as in current tests).
- Aggregation script:
  - Snapshot test on merged plugin-manifest.json; verify copied assets set.

## Security
- Prefer npm packages and artifact integrity over URL imports.
- If URL imports are needed, restrict to allowed origins and consider Subresource Integrity when feasible.

## Open Questions
- Final schema and place for `catalogDirs` and per-package manifest fragments.
- Version compatibility between host and plugin packages (SDK semver and optional feature gates).
- Plugin-to-plugin dependencies: allowed or discouraged? If allowed, document pattern and version checks.

## Links
- PanelSlot: src/components/PanelSlot.tsx
- Sequence loader: src/conductor.ts
- Env & artifacts: src/env.ts, scripts/build-artifacts.js, scripts/sync-plugins.js
- Integrity: src/startupValidation.ts
- Host SDK surface: packages/host-sdk/public-api.ts

