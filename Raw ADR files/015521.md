# ADR-0021 — Centralized Feature & Perf Flags Registry

- Status: Accepted
- Date: 2025-08-26
- Issue: #37

## Context

Feature and performance toggles are currently ad-hoc, making it hard to see what flags exist, their lifecycle, and who owns them. We also want guardrails so usage is deliberate and observable, and to avoid typos or dead flags.

## Decision

- Create a single source of truth JSON registry at `data/feature-flags.json` with metadata per flag: `status`, `created`, `verified`, `description`, `owner`.
- Add a small runtime helper `src/feature-flags/flags.ts` exposing:
  - `isFlagEnabled(id)` → boolean (on|experiment = true; unknown/off = false)
  - `getFlagMeta(id)`, `getAllFlags()`
  - `getUsageLog()` in-memory usage log for tests/local debugging
- Add ESLint rule `feature-flags/enforce-flag-ids` to require that `isFlagEnabled("...")` uses a literal, known ID from the registry (prevents typos/dynamic usage).
- Track usage calls in-memory; provide a stable seam to integrate real telemetry later (without adding IO/side-effects to UI code).

## Consequences

- Static validation prevents drift: unknown or dynamic flag IDs fail lint.
- Runtime helper is a stable import point that can be swapped for server/backed config later.
- Tests can assert usage via `getUsageLog()` without side effects.

## Implementation Notes

- Registry file: `data/feature-flags.json` (resolved by ESLint rule via repo CWD).
- Runtime module: `src/feature-flags/flags.ts` imports JSON (Vite/Vitest support `assert { type: "json" }`).
- ESLint plugin: `eslint-rules/feature-flags.js` with rule `enforce-flag-ids`, wired in `eslint.config.js` as `"feature-flags/enforce-flag-ids": "error"` for all source files.
- Tests:
  - ESLint `RuleTester` in `__tests__/eslint-rules/feature-flags.spec.ts` with valid/invalid suites.
  - Runtime spec in `__tests__/feature-flags/flags.runtime.spec.ts` validating enablement and usage logging.

## Example

```ts
import { isFlagEnabled } from "../../src/feature-flags/flags";

if (isFlagEnabled("perf.fast-initial-drag")) {
  // fast path
}
```

`data/feature-flags.json` entry:

```json
{
  "perf.fast-initial-drag": {
    "status": "on",
    "created": "2025-08-01",
    "verified": "2025-08-26",
    "description": "Enable optimized path to reduce initial drag latency in UI",
    "owner": "control-panel"
  }
}
```

## Follow-ups

- Optionally extend the runtime to surface a hook `setUsageLogger((id, when) => { ... })` for forwarding to app-wide telemetry.
- Add a small README in `src/feature-flags/` clarifying usage patterns.

## Links

- Issue: https://github.com/BPMSoftwareSolutions/renderx-plugins-demo/issues/37
- Related: ADR-0014 (JSON-defined default sequences), ADR-0019 (Interaction manifest single source of truth)

