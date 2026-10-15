# ADR-0033 — Plugin-Served, Data-Driven E2E for Thin Host

- Status: Accepted
- Date: 2025-09-21
- Authors: RenderX core team
- Related: ADR-0023 — Host SDK and Plugin Decoupling; ADR-0026/27/28/29/30/31/32 — Externalization efforts

## Context

We externalized most UI and logic into plugins. Our existing end-to-end (E2E) and integration tests were host-coupled: they poked into plugin DOM/state and depended on host wiring details. With externalization, those tests became brittle and flaky.

The thin host should remain largely unaware of plugin internals. Tests must be owned and served by plugins, while the host provides only a generic harness and runner.

## Decision

Adopt a plugin-served, data-driven E2E testing architecture:

- Each plugin serves a versioned Test Manifest (JSON) describing scenarios and a Test Driver page that implements a small postMessage protocol.
- The host ships a single generic harness page and a Cypress suite that discovers plugin manifests, iframes the driver page, and executes steps/assertions defined by data.
- Readiness is deterministic via ordered phases (0 → 1 → 2). The host enforces per-phase and per-step timeouts to reduce flake.
- Plugins may author scenarios in Gherkin, compiled at build time to the normalized manifest consumed by the host.

This keeps the host ultra-thin and moves plugin-specific selectors and timing into plugin-owned artifacts.

### Amendment (2025-09-21): Switch to Cypress

We initially drafted this ADR around a Playwright-based generic runner. During implementation and CI hardening, we adopted Cypress as the host-side generic E2E runner. The protocol, harness, and plugin-owned artifacts remain unchanged; only the runner changed.

Rationale:
- Integrated dev workflow with Vite (fast feedback, watch mode) and simpler preview alignment.
- Mature retries, test skipping, and artifact capture out of the box (videos/screenshots), plus straightforward CI caching of the Cypress binary.
- CI stability improvements in our environment (preview port alignment; resilient handling when a plugin does not serve `/test/manifest.json`).
- Reduced dependencies: removed Node Playwright test packages from devDependencies. Note: Playwright (Python) remains for optional export tooling and is unaffected by this change.

## Architecture (ASCII)

```
+-----------------------------+        discovers        +---------------------------+
| Cypress Generic Runner      | ---------------------> | Plugin Registry (JSON)    |
| - one suite, no plugin code |                        | [plugin baseUrls]         |
+-----------------------------+                        +---------------------------+
             |
             | for each plugin
             v
+-----------------------------+    loads via iframe     +---------------------------+
| Host Harness Page           | ---------------------> | Plugin Test Driver Page   |
| test-plugin-loading.html    |                         | /test/driver.html         |
| - tiny postMessage proxy    |  <-------------------   | - loads plugin + driver   |
| - window.TestHarness API    |    replies events       | - implements protocol     |
+-----------------------------+                         +---------------------------+
             ^                                                         |
             |                                                         | interacts with
             |                                                         v
  Cypress test code                                      +-------------------------+
  - visit harness with driver/scenario                   | Plugin Under Test       |
  - waitForPhases(0,1,2) via TestHarness                 | actual runtime UI       |
  - runSteps/asserts from manifest                       +-------------------------+
  - collect logs/snapshots
```

## Roles & Responsibilities

Host (thin):
- Serve `src/test-plugin-loading.html` harness with a minimal `window.TestHarness` API.
- Implement a stable postMessage envelope, validation, timeouts, and logging.
- Provide a generic Cypress runner that:
  - Discovers plugins (via a local registry JSON or CI matrix) and fetches `/test/manifest.json`.
  - For each scenario: loads the harness with `driverUrl`, waits for phases, runs steps/asserts, collects artifacts (screenshots/videos as configured).

Plugin (owner of tests):
- Serve `/test/manifest.json` and `/test/driver.html` (driver loads plugin code and test driver script).
- Implement the driver: emit deterministic ready phases and execute normalized steps/asserts.
- Optionally author scenarios in Gherkin; compile to the normalized manifest.

## Protocol (postMessage)

Transport: `window.postMessage` between host harness and plugin driver (iframe). Messages are JSON objects with a `channel: "rx.test"`, `version`, `type`, and `payload`.

Message types (minimum viable):
- host:init → driver:ack
- driver:readyPhase { phase: 0|1|2, detail? }
- host:step { id, type, payload } → driver:stepResult { id, status: "ok"|"fail", detail? }
- host:assert { id, type, payload } → driver:assertResult { id, status, detail? }
- host:snapshot? → driver:snapshot { state }
- host:teardown → driver:teardownResult

Determinism: the driver emits phases in order once. The harness enforces per-phase and per-step timeouts and aborts with diagnostics on violation.

## Test Manifest (served by plugin)

Stable, versioned JSON. Example shape:

```
{
  "testApiVersion": "1.0.0",
  "plugin": { "id": "rx.library.button", "version": "2.5.0" },
  "driverUrl": "/test/driver.html",
  "capabilities": ["selectors", "stateSnapshot", "screenshot"],
  "scenarios": [
    {
      "id": "button-renders-default",
      "title": "Button renders with default props",
      "tags": ["render", "smoke"],
      "readiness": { "phases": [0,1,2], "timeoutMs": 6000 },
      "env": { "viewport": { "width": 1024, "height": 768 }, "theme": "light" },
      "steps": [
        { "type": "setProps", "payload": { "label": "Click me" } },
        { "type": "mount" }
      ],
      "asserts": [
        { "type": "selectorText", "selector": "[data-testid=btn-label]", "equals": "Click me" }
      ],
      "artifacts": { "screenshot": true, "snapshot": true }
    }
  ]
}
```

Capability negotiation: The host checks `testApiVersion` and `capabilities`. Incompatible manifests are skipped with an actionable message.

## Gherkin authoring (optional, plugin-side)

- Author `.feature` files and step definitions inside the plugin.
- Build step compiles features → normalized manifest (`/test/manifest.json`).
- The driver uses the same step catalog to execute normalized steps/asserts.
- The host does not parse Gherkin.

Example feature → normalized steps:

```
Feature: Button renders
  Scenario: Button renders with default props
    Given the button props:
      | label | Click me |
    When the component mounts
    Then I should see text "Click me" in "[data-testid=btn-label]"
```

Compiles to:

```
"steps": [
  { "type": "setProps", "payload": { "label": "Click me" } },
  { "type": "mount" }
],
"asserts": [
  { "type": "selectorText", "selector": "[data-testid=btn-label]", "equals": "Click me" }
]
```

## Migration Plan

1. Define and publish the contract
   - Types and schema for manifest and protocol (shared types or small package).
   - Update `src/test-plugin-loading.html` to expose `window.TestHarness` and enforce protocol/timeouts.
   - Add dev/CI plugin registry (local JSON, Vite proxy rules).

2. Pilot with 1–2 plugins
   - Add `/test/manifest.json` and `/test/driver.html` in pilot plugins.
   - Implement 3–5 smoke scenarios each using normalized steps/asserts.
  - Create generic Cypress spec to discover and run scenarios.

3. Scale and harden
   - Add tags, capability negotiation, and skip/only controls.
   - Standardize data-testid usage and optional `stateSnapshot` for less brittle assertions.
   - Wire artifacts to CI (screenshots, logs, snapshots) and flaky-test triage.

4. Decommission host-coupled tests
   - Keep only thin-host responsibilities (loader contracts, CSS isolation/registry, event routing, ready-phase orchestration).
   - Remove or migrate old plugin-coupled e2e/integration tests.

## Risks and Mitigations

- Version drift: Mitigate with `testApiVersion` range checks and clear skip messages.
- Cross-origin messaging: Use origin checks; locally rely on Vite proxy to keep same-origin.
- Flake from async timing: Deterministic ready phases and per-phase budgets; prefer state snapshots over deep DOM poking.
- Increased plugin burden: Provide a tiny driver kit (helpers, types) and authoring docs.

## Consequences

- Host test suite becomes stable, data-driven, and plugin-agnostic.
- Plugins own their quality gates; selectors and UX specifics live with the code they validate.
- CI can matrix host x plugin versions with clearer failure ownership.

## Open Questions

- Do we centralize the driver kit as a shared package, or duplicate minimal helpers per plugin initially?
- How do we version the protocol (semver) across host and plugins? (Proposed: `testApiVersion` with a compat window.)
- Artifact storage: standardized folder layout and retention per scenario?

## References

- `src/test-plugin-loading.html` (existing harness to extend)
- ADR-0023 (decoupling), ADR-0026–0032 (externalization)
- Cypress config and existing E2E folder structure (e.g., `cypress.config.ts`, `cypress/e2e/generic-plugin-runner.cy.ts`)
