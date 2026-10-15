# ADR-0019: Beat Kind Taxonomy and DOM Mutation Policy (Deprecate StageCrew V1)

Status: Proposed
Date: 2025-08-22
Related Issue: <link to GitHub issue once created>
Supersedes/Amends: ADR-0017 (Stage Crew DOM Mutation Facade)

## Context

Recent plugin work (e.g., overlay CSS and instance style updates) revealed that enforcing DOM writes exclusively through StageCrew leads to behavior drift compared to direct DOM usage:
- Inline `<style>` sync vs `<link href="data:…">` async attach causes flicker and timing differences
- Remove+append changes sheet order and cascade precedence
- Missing content ops (e.g., `textContent`) require invasive API growth
- Selectors-only addressing and lack of move/prop/measure features constrain components as they scale

We still value observability, guardrails, and SPA constraints. However, constraining all DOM writes through the current StageCrew V1 surface introduces correctness and UX risks for fast‑evolving UI plugins.

## Decision

1. Introduce a Beat `kind` attribute to classify handler intent and runtime permissions.
2. Allow plugins to access and mutate the DOM directly when the current beat `kind` permits it.
3. Deprecate StageCrew V1 as a mandatory path for DOM writes. StageCrew remains available but optional; it is recommended only when its semantics match the needed behavior.
4. Preserve observability by emitting beat metadata (including `kind`) and by optionally logging StageCrew cues when used.
5. Enforce policy via lint rules in plugin repos and via dev‑mode runtime guardrails that respect `kind`.

This ADR does not remove StageCrew; it reclassifies it from required to optional and defines a taxonomy and enforcement model for safe direct DOM access.

## Beat Kind Taxonomy (initial)

- `compute` (default): pure computation; no DOM writes; reads allowed if incidental
- `dom.read`: DOM reads (layout/measure) permitted; no writes
- `dom.write`: DOM writes permitted (including content/style/structure)
- `stage-crew`: DOM writes intended via StageCrew (plugins may choose to constrain themselves to StageCrew in these beats)
- `io`: network/storage/other side effects; no DOM guarantee

Notes:
- Kinds are orthogonal to movement priority and timing; they describe intent and enable policy.
- Additional kinds may be added as needed (e.g., `canvas`, `webgl`, `shadow-dom`).

## Enforcement and Instrumentation

- Lint (plugins):
  - Disallow `document.*` and direct DOM mutation APIs in beats not marked `dom.write` or `stage-crew`.
  - Allow in `dom.write` and optionally require StageCrew in `stage-crew` beats.
  - Simple implementation: an ESLint rule using a per‑file/handler annotation or a code‑mod that maps sequence metadata to handler files.

- Runtime (core):
  - Propagate `kind` into handler context and Conductor logs.
  - StageDomGuard: continue to warn in dev, but silence warnings when current beat `kind` is `dom.write` or during StageCrew internal apply; warn otherwise.
  - SPAValidator: include `kind` in violation reports; keep allow‑list for StageCrew `stage:cue` emissions.

- Observability:
  - Emit beat start/finish with `kind` and correlation id.
  - When StageCrew is used, continue emitting `stage:cue` with meta `{ __stageCrewInternal: true }`.

## Deprecation of StageCrew V1

- StageCrew V1 becomes optional. It is deprecated as a requirement, not as an available tool.
- Rationale for deprecation: API gaps (content/move/prop/measure), async attach differences for stylesheet strategies, cascade order side effects, and selector brittleness.
- We will maintain StageCrew for backward compatibility and auditing benefits while we evaluate either:
  - a) a richer Stage API that truly preserves DOM semantics, or
  - b) relying on direct DOM with `kind`‑based policy for most plugins.

## Consequences

- Pros
  - Restores precise DOM semantics where needed; avoids flicker/order drift
  - Keeps strong guardrails via `kind` + lint + dev‑mode guard
  - Maintains observability through beat metadata and optional StageCrew cues

- Cons
  - More responsibility on plugin authors to follow `kind` policy
  - Requires minor core changes (propagate `kind`, update StageDomGuard/SPAValidator)
  - Lint integration needed in plugin repositories

## Alternatives Considered

- Keep StageCrew mandatory and extend API (text/html/move/prop/measure/refs)
  - Rejected for now: larger surface and still risks semantic mismatches
- Wrapper document facade backed by StageCrew
  - Useful for small patterns but not a general replacement; still requires content ops; retained as optional helper

## Migration Plan

1) Schema: Add optional `kind` to Sequence/Movement/Beat definitions with default `compute`.
2) Conductor: Pass `kind` into handler context; include in logs/telemetry.
3) StageDomGuard: respect `kind` (silence for `dom.write` and StageCrew internals; warn otherwise).
4) SPAValidator: attach `kind` to violations and continue allow‑listing StageCrew cues.
5) Plugins: annotate beats with appropriate `kind`; remove mandatory StageCrew usage where harmful; add ESLint rule to enforce policy per beat.
6) Documentation: Mark ADR‑0017 as revised by this ADR and update README to reflect policy.

## Test Strategy

- Unit
  - Conductor passes `kind` through context and logs
  - StageDomGuard warnings align with `kind`
  - SPAValidator includes `kind` and does not flag permitted `dom.write` beats
- Integration
  - Canvas/overlay flows: no flicker; measurements match expected after in‑place inline style updates
- Lint
  - Rule catches DOM writes in non‑DOM beats in plugin repos

## Status and Next Steps

- Status: Proposed (awaiting issue number and review)
- Next Steps
  - Open a GitHub issue to track implementation tasks and link it here
  - Implement schema and guard changes behind a feature flag
  - Coordinate with plugin repos to add ESLint rule and migrate beats


