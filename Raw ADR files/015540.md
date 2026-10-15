# ADR-0016 — Preserve callbacks across nested play() via correlationId-scoped registry

Status: Accepted
Date: 2025-08-14
Related Issue: #42

## Context
In PR preview/dev environments, payloads may be serialized/cloned across `play()` boundaries, stripping function-valued fields (callbacks) like `onComponentCreated`. When a sequence performs a nested `conductor.play()`, downstream symphonies miss callbacks and UI updates never occur, despite successful orchestration.

## Decision
Implement orchestrator-level callback preservation:
- Attach a correlationId to `play()` context.
- Extract function-valued fields into an in-memory registry per correlationId and replace them with JSON-safe placeholders.
- Propagate correlationId to nested `play()` calls.
- Rehydrate callbacks at plugin handler entry using the registry.
- Provide TTL-based cleanup to avoid memory leaks.

CorrelationId is attached to context (not the baton), as an internal field (`__mc_correlation_id__`) used only for transport/rehydration.

## Consequences
- Transparent to plugins: existing code that passes and uses callbacks continues to work.
- Works in preview envs where function payloads are stripped, as well as in live envs.
- Ties into existing logging/traceability (no changes required).
- Minor memory overhead from the registry with TTL cleanup.

## Alternatives
- Require plugins to re-wire callbacks manually — rejected (leaks architecture and breaks encapsulation).
- Switch all outcomes to events — rejected per ADR-0005 (callbacks preferred for direct outcomes).

## Implementation Summary
- New: `modules/communication/sequences/orchestration/CallbackRegistry.ts`.
- MusicalConductor.play(): preserve callbacks and attach correlationId on the outgoing context.
- PluginManager subscription boundary: rehydrate callbacks from registry; propagate correlationId into nested `conductor.play()` contexts if missing.
- Unit test simulates JSON cloning on the inner `play()` and verifies callbacks still fire downstream.

## Follow-ups
- Optional: cleanup registry entries on sequence completion using `SEQUENCE_COMPLETED` and correlationId plumbing; TTL is in place as a safety net.

