# ADR-0017: Stage Crew for DOM Changes (Centralized DOM Mutation Facade)

Status: Accepted
Date: 2025-08-17

## Links

- Related Issue: https://github.com/BPMSoftwareSolutions/MusicalConductor/issues/48
- This ADR (repo path): ../blob/main/tools/docs/wiki/adr/0017-stage-crew-dom-mutation-facade.md
- Related ADRs: 0012-data-baton-traceability, 0014-manifest-driven-panel-slot-plugins, 0016-callback-preservation-nested-play
- Testing docs: ./tools/docs (testing strategy and refactoring notes)

## Context

DOM changes initiated by plugins are currently dispersed and difficult to trace through logs and across plugin boundaries. This complicates:

- Observability (who changed what, when, why?)
- Ordering/atomicity of related mutations within a beat
- E2E verification that expected UI flows occurred (relying on log cues)

Architectural preferences already established:

- Plugins orchestrate via conductor.play(), not by emitting ad hoc events or directly returning data
- Correlation ID lives in the context; a "data baton" traces data across beats

We want a single, observable, testable path for DOM writes that aligns with the Conductor model and enables richer capabilities like auto-correlation (alignment, containment, snapping, leader–follower) over time.

## Decision

Introduce a Stage Crew: a DOM mutation facade owned by the Conductor. All plugin DOM writes must go through Stage Crew. Reads may remain direct (or go through Stage Crew for scoping), but writes are centralized to:

- Create a single choke-point for logging and attribution (pluginId, beatId, correlationId)
- Batch and order mutations per beat (transactional apply, optional rollback on error)
- Enforce scoping/guardrails (plugin mount roots, dev-mode detection of out-of-band writes)
- Provide a portable driver abstraction (browser DOM, virtual/no-op for SSR/tests)

## Architecture

- API and Transactions
  - stageCrew.beginBeat(correlationId, meta) -> BeatTxn
  - BeatTxn schedules write operations and commits/rolls back atomically for that beat; operations are batched and flushed (e.g., via requestAnimationFrame)
- Drivers
  - Browser DOM driver applies mutations
  - Test/SSR driver records a cue sheet without touching a real DOM
- Observability
  - On commit, Stage Crew emits a cue sheet with operation list, targets, diffs, timings, outcome
  - Logs are time-stamped and flow into /.logs, keyed by correlationId and pluginId
- Scope and Guardrails
  - Each plugin is scoped to a mount root; selectors and element refs are resolved within that scope
  - Dev-only guards warn on direct DOM writes that bypass Stage Crew

## V1 API Surface (illustrative)

- Transactions
  - beginBeat(correlationId, meta) -> txn
  - txn.commit() / txn.rollback(err)
  - txn.batch(fn) // coalesce logs and writes within a block
- Reads & Measures
  - stageCrew.measure(fn) // perform reads (getBoundingClientRect, computed styles) before writes
- Write Ops (scoped to plugin root)
  - txn.select(selector).addClass(name).removeClass(name).setAttr(k, v).setStyle(k, v)
  - txn.create(tag, { attrs, classes, style, text, html }).appendTo(selectorOrRef)
  - txn.update(selectorOrRef, { text, html, attrs, classes, style })
  - txn.move(selectorOrRef, { before: ref } | { after: ref } | { appendTo: ref })
  - txn.remove(selectorOrRef)
- Events/Observers
  - txn.onCommit(log => { /_ observers (telemetry/tests) _/ })

Notes:

- Keep the API fluent and DOM-like to reduce developer friction
- Reads happen in a dedicated read phase; writes are applied in a batched write phase

## Observability and Cue Sheets

Each commit produces a cue sheet entry including:

- correlationId, pluginId, beatId
- operations: [ { op, target, before, after } ]
- timing: { startedAt, endedAt, durationMs }
- outcome: committed | rolledBack
- dataBaton snapshot (optional)

Logs are written to /.logs with date-time stamps per existing log review protocol.

## Test Strategy

- Unit tests (TDD):
  - Given a sequence of scheduled ops within a txn, assert the emitted cue sheet and final DOM state (via test driver)
  - Verify scoping: selectors cannot escape plugin root
- E2E (Playwright, minimal):
  - Verify app/conductor startup using the published musical-conductor package
  - Assert that a known beat produces the expected cue sheet log line(s)
- Follow Red-Green-Refactor; ensure all tests pass before merging

## Consequences

- Benefits: traceability, safer mutations, consistent orchestration, better tests
- Costs: initial API surface and migration; small runtime overhead (mitigated by batching and adjustable log levels)
- Developer experience: slight friction compared to raw DOM, reduced by ergonomic API and escape hatches (guarded)

## Implementation Notes (Initial)

- Provide Stage Crew via plugin handler context; require all writes through it
- Implement a minimal browser driver and a virtual/test driver
- Add dev-only guards that warn on direct writes (e.g., patched Element.prototype methods)
- Feature flag the integration to allow incremental rollout

### Scope V1 (for review)

- Focus on transactional write batching, minimal ops (select/update/create/remove), and cue sheet logging
- Defer correlation engine to follow-up work; this ADR includes the roadmap for awareness and planning only

## Rollout Plan

1. Implement Stage Crew core with transactions, a few high-value ops, and logging
2. Integrate with one pilot plugin and migrate its writes
3. Add unit tests for ops + cue sheets; add a minimal Playwright E2E startup/cue verification
4. Enable dev guards, document migration guidance for plugins
5. Expand ops based on usage feedback

## Future Evolution: Correlation Engine (Auto-Correlation)

Stage Crew can host a correlation layer that maintains relationships among elements and computes reactive layout updates during interactions (drag/resize). Core concepts:

- Correlation Graph

  - Nodes: elements (components, resize handles, containers), each with stable refs and bounds suppliers
  - Edges/constraints: leader–follower, align-edges, pin-to-container, keep-offset, equal-size, aspect lock
  - Groups: named correlation groups (e.g., selection-123) with a leader and N followers

- Reactive Engine

  - Read phase: measure via ResizeObserver + on-demand getBoundingClientRect under rAF
  - Solve phase: compute positions/sizes from constraints (fast heuristics first; optional solver later)
  - Write phase: apply batched DOM writes via the Stage Crew txn; emit cue sheet with group and constraint info

- API Sketch (illustrative)

  - stageCrew.correlation.createGroup({ id, leader, followers, meta })
  - group.constrain.alignHandlesToLeaderEdges({ offset: 0 })
  - group.constrain.resizeFromHandle(handle, { min, max, aspect })
  - group.constrain.leaderToContainer(container, { mode: "contain", padding: 4 })
  - group.constrain.snap({ grid: 8, guides: [...] })
  - stageCrew.interactions.onDrag(leader).pipe(stageCrew.correlation.apply(group))
  - stageCrew.interactions.onResize(handle).pipe(stageCrew.correlation.apply(group))

- Maps to Intended Capabilities

  - Provide multiple components to auto-correlate (group registration)
  - Align resize handles to component while moving (leader=component; followers=handles)
  - Align component to handles during resize (leader=handle; follower=component)
  - Align within nested containers (containment constraints with coordinate transforms)
  - Snap multiple components with leader–follower relative positions (group snapping)

- Phased Roadmap

  - V1: Leader–follower basics; align handles to component; resize component from handle; containment in a single container; grid snapping
  - V2: Nested containers and transform-aware coordinates; guides-based snapping (edges, centers, other components)
  - V3: Declarative constraint sets with priorities and conflict resolution
  - V4: Optional constraint solver (e.g., Kiwi/Cassowary) for complex layouts; keep fast-path heuristics for common cases

- Performance & Precision
  - Normalize coordinate spaces; cache transform matrices; prefer transforms for motion, width/height for resize
  - Coalesce read/write per frame; avoid layout thrash; tune snapping tolerance with devicePixelRatio awareness

## Alternatives Considered

- Keep direct DOM writes and attempt to infer/aggregate logs: incomplete traceability and weak guardrails
- Rely solely on event bus patterns: increases coupling and hidden side effects
- CSS-only alignment for interactions: insufficient for correlated drag/resize behaviors

## Status and Next Steps

- Status: Accepted
- Next steps (tracked by Issue #48):
  1. Implement Stage Crew core behind a flag with logging
  2. Pilot with one plugin; migrate writes
  3. Ship tests (unit + minimal E2E) and enable dev guards
  4. Design correlation V1 API and spike implementation
