# ADR-0034 — Auto-generate Interaction Catalogs from Plugin-Served Artifacts

Status: Accepted
Date: 2025-09-23
Related Issue: #229
Related PRs: #230 (Phase 1), <pending> (Phase 2)

## Context
Host-maintained interaction catalogs under `catalog/json-interactions/*.json` tended to drift from the plugin-served sequences. In #226 we established plugin-served artifacts (generated/public manifests + served sequences) as the source of truth for lint/validation. We want interaction routing to be derived from those same artifacts to eliminate duplication.

## Decision
- Generate per-plugin interaction catalogs from plugin-served data at build time.
- Write generated catalogs to `catalog/json-interactions/.generated/*.json`.
- Remove host-authored catalogs under `catalog/json-interactions/*.json` and add guardrails to prevent reintroduction.
- Update the manifest build pipeline so `generate-interaction-manifest` consumes the generated catalogs (no fallbacks).

## Consequences
- Single source of truth for routes: plugin-served sequences.
- Deterministic, build-time generation; fewer hand-maintained files in host.
- A small generator script and tests added to host.

## Implementation Summary
- New script: `scripts/generate-json-interactions-from-plugins.js` (module + CLI)
  - Reuses the existing external sequence derivation to construct an interactions map.
  - Splits routes by first segment and emits per-group catalogs with a `plugin` field and `routes` map.
- Pipeline: `pre:manifests` runs the generator before `generate-interaction-manifest`.
- `generate-interaction-manifest`: reads only `.generated` catalogs (Phase 2), removing reliance on hand-authored files.
- Tests:
  - Integration: generator creates `.generated/library.json` containing `library.load`.
  - Hygiene: fail CI if any non-generated files exist in `catalog/json-interactions/`.

## Alternatives Considered
- Keep host-authored catalogs and validate against plugins — rejected (duplication/drift).
- Generate on-the-fly at runtime — rejected (prefer build-time determinism and simpler runtime).

## Rollout
- Phase 1 (PR #230): add generator, prefer `.generated` while coexisting.
- Phase 2: remove hand-authored catalogs, `generate-interaction-manifest` uses only `.generated`, add CI/test guardrails, and ensure e2e remains green.

