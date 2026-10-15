# ADR-0014: Manifest‑Driven Panel Slot Plugins (Thin Shell + Orchestrated Panels)

Status: Accepted
Date: 2025-08-11

## Context
We are migrating the client UI to a thin shell that delegates panel rendering to plugin‑provided React components. The previous approach mixed feature logic into the shell (ElementLibrary, ControlPanel), and subscriptions sometimes duplicated work (e.g., multiple component load sequences under React StrictMode).

We already rely on Musical Conductor sequences and beats for orchestration. The UI should remain thin and initiate flows via conductor.play, receiving results via explicit callbacks rather than subscribing to general events.

## Decision
Adopt a Manifest‑Driven Panel Slot Plugin pattern:
- Thin shell renders layout with named slots (left, center, right)
- For each slot, a PanelSlot component resolves a plugin UI from a manifest and lazily mounts it
- Each plugin UI uses callback‑first orchestration via conductor.play
- Loading is handled by Suspense; failures are isolated by ErrorBoundary
- Legacy React panels remain as fallbacks during the transition and are removed later

### Terminology
- PanelSlot: Shell component that loads and renders a plugin UI for a slot, with a fallback
- Plugin UI: React component exported by a plugin (resolved via manifest in dev; global export in prod)
- Orchestration Plugin: Registers sequences/movements/beats with handlers, coordinates workflows via the conductor

## Architecture
- Shell (thin)
  - AppContent controls layout and toggles
  - PanelSlot(slot, fallback) mounts plugin UI or fallback
  - Suspense provides loading UI; ErrorBoundary provides failure isolation

- Plugins (orchestration)
  - Register sequences, movements, and beats with handlers
  - Can communicate with other components via the conductor; can also call back to the UI through on… callbacks
  - Idempotent guards (e.g., window.__rx_library_played__) to avoid duplicates under StrictMode

- Plugin UI (per slot)
  - References React via window.React; explicitly destructures used hooks
  - Initiates flows using conductor.play with callback props (onComponentsLoaded, on…)
  - Avoids broad event subscriptions; subscribe only if multi‑source, incremental updates are required

- Manifest
  - Lists plugins and, optionally, a ui entry: { slot, export }
  - Dev: PanelSlot dynamically imports /plugins/{path}/index.js and uses the named export
  - Prod: PanelSlot looks up window.RenderXPlugins[export] (planned), falling back to legacy

## Rationale
- Clear separation of concerns; reduces coupling between shell and features
- Smooth UX: Suspense handles loading; ErrorBoundary prevents full‑app crashes
- Performance: Panels are lazy‑loaded; only visible UIs are downloaded/mounted
- Simpler data flow: Callback‑first avoids duplicated work vs. broad event subscriptions
- Incremental migration: Slot by slot; legacy fallbacks preserved until replaced

## Consequences
- Manifest becomes a contract; drift will break panel resolution
- Plugins must expose React components correctly and destructure required hooks from window.React
- Need idempotent guards due to StrictMode remounts
- A production UI loader path is required for builds that cannot dynamically import from /public/plugins

## Implementation Notes
- ElementLibrary
  - Renders <PanelSlot slot="left" fallback={<LegacyElementLibrary/>} />
  - LibraryPanel plugin UI waits for plugin mount, calls conductor.play("load-components-symphony"), and uses onComponentsLoaded callback
  - Removed redundant event subscriptions and StrictMode duplicates

- ControlPanel
  - Renders <PanelSlot slot="right" fallback={<LegacyControlPanel/>} />
  - Right‑slot plugin UI to be implemented; fallback in use for now

- PanelSlot
  - Dev: fetches manifest, lazily imports plugin index.js, uses named export
  - Wrapped in Suspense + ErrorBoundary by caller
  - Planned: Prod path to use window.RenderXPlugins

## Test Strategy
- E2E (Playwright)
  - Verify single execution of Component Library loading symphony
  - Library renders components and supports drag → canvas create
  - No legacy loader logs unless fallback is active

- Unit tests (tests/unit/renderx/plugins)
  - Component Library Plugin: play("load-components-symphony") invokes onComponentsLoaded
  - Library drag/drop plugins: correct emits/forwarding to Canvas create symphony
  - Canvas create/drag/resize/selection plugins: handler contracts and payloads

## Rollout Plan
1) Left slot (done): ElementLibrary via LibraryPanel
2) Right slot (next): ControlPanel via ControlPanelPanel plugin UI + manifest
3) Center slot (later): Canvas via canvas‑ui plugin UI + manifest
4) Production loader: window.RenderXPlugins lookup in PanelSlot when not in dev
5) Remove legacy panels after stability period

## Alternatives Considered
- Keep subscriptions: Increases complexity, risk of duplicate updates; rejected for default path
- Bundle plugin UIs into the app: Reduces plugin decoupling; acceptable for monoliths but not preferred here

## Status and Next Steps
- Implement right‑slot Control Panel UI plugin and manifest entry
- Add production UI loader in PanelSlot
- Write/extend unit tests for the related plugins
- Remove legacy fallbacks after confirmation in prod

