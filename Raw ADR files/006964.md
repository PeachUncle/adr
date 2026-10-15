# 002 - Strongly-Typed Intents and ActionState Container

Date: 2025-09-27
Status: Accepted

## Context
- We are introducing a server-authoritative intent pipeline starting with M0 (Move), then expanding to additional intent kinds (Attack, Build, ...).
- The existing protobuf `Entity` focuses on physical state (`pos`, `vel`, `force`) and should remain stable/minimal for deterministic simulation and efficient deltas.
- We need a way to:
  - Represent incoming intents in a versionable, extensible schema.
  - Track the currently executing action per entity on the authoritative server.
  - Keep client/server types aligned across Rust and TypeScript.
- We want strong typing to improve determinism, validation, ergonomics, and observability, while leaving room to add new intents over time.

## Decision
- Adopt a strongly-typed intent envelope with a `oneof` for concrete intent kinds (Plan A).
- Track the executing action per entity in a single `ActionState` container that:
  - Echoes the original `Intent` for correlation/logging.
  - Holds a `oneof` for the per-kind execution state (`MoveState`, `AttackState`, `BuildState`, ...).
- Keep `Entity` focused on physical state. Do not embed `Intent` into `Entity`.
- Maintain per-entity intent queues in `IntentState.intent_queues` (generic across intent kinds).
- Replace the Move-specific `motion_targets` with `current_action: map<uint64, ActionState>`.

### Protobuf (summarized)
File: `packages/schemas/proto/intent.proto`
```
message MoveToLocationIntent { uint64 entity_id; Vec2 target; string client_cmd_id; string player_id; }
message AttackIntent         { uint64 entity_id; uint64 target_id; string client_cmd_id; string player_id; }
message BuildIntent          { uint64 entity_id; string blueprint_id; Vec2 location; string client_cmd_id; string player_id; }

message Intent {
  oneof kind {
    MoveToLocationIntent move = 1;
    AttackIntent         attack = 2;
    BuildIntent          build  = 3;
  }
}

message MoveState   { MotionTarget target = 1; }
message AttackState { uint64 target_id = 1; Vec2 last_known_pos = 2; }
message BuildState  { string blueprint_id = 1; Vec2 location = 2; float progress = 3; }

message ActionState {
  Intent intent = 1; // correlation/logging
  oneof exec {
    MoveState   move   = 2;
    AttackState attack = 3;
    BuildState  build  = 4;
  }
}

message IntentQueue { repeated Intent items = 1; }

message IntentState {
  map<uint64, IntentQueue> intent_queues  = 1; // per-entity queues
  map<uint64, ActionState> current_action = 2; // per-entity executing action
}
```

## Consequences
- **Determinism & Safety**: Strongly-typed messages across Rust/TS reduce schema drift and runtime ambiguity.
- **Extensibility**: New intent kinds are added by extending the `Intent` oneof and defining a matching `*State` if execution state is needed.
- **Observability**: `ActionState.intent` preserves the original request for logs and correlation; execution state carries progress/targets.
- **Separation of Concerns**: `Entity` stays focused on physical state; UI can optionally subscribe to a separate channel for action state if needed.

## Alternatives Considered
- Option B: `ActionState.exec_state: google.protobuf.Any`
  - Pros: maximum flexibility; schema stability.
  - Cons: weaker typing, more runtime checks, harder to guarantee determinism and version-compat.
- Option C: `ActionState.scratch: map<string, Scalar>` (KV bag)
  - Pros: minimal schema churn; highly flexible.
  - Cons: least safety/ergonomics; poor codegen support; brittle contracts.

## Migration & Rollout
- Short-term (M0):
  - Replace server-only `motion_targets` with `current_action.move`.
  - Keep `IntentState` internal (not published) until specific UI needs arise.
- Medium-term (M1+):
  - Use `IntentQueue` for queueing behaviors (append/replace/clear) per entity.
  - Add `AttackIntent` / `BuildIntent` and corresponding `*State` as features land.
- Long-term:
  - If scripting adds dynamic actions, introduce a `ScriptedIntent` + `ScriptedState` branch in the oneof, with explicit versioned IDs to preserve determinism.

## References
- `docs/milestones.md` (M0–M10, networking/idempotency/versioning milestones)
- `docs/milestones/m0-hello-rts.md` (M0 detailed plan)
- `docs/requirements/entity-intents.md`
- `docs/adr/001-scripting-engine-and-sandbox.md`
