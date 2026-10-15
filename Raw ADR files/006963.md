# 001 - Scripting Engine and Sandbox

Date: 2025-09-25
Status: Proposed

## Context
- We want data-driven entities/abilities with scripted validation/execution hooks that run on the authoritative server.
- Matches must be deterministic and fair (including long-running matches lasting weeks/months).
- Scripts must be safe (no I/O, no host access), resource-bounded, and versioned with content packs.

## Decision
- Use Lua (Lua 5.4 or Luau) as the initial scripting engine, embedded server-side only.
- Provide a tightly sandboxed environment:
  - No wall-clock, filesystem, network, OS threads, or reflection into host.
  - Deterministic RNG exposed via `rand()` API seeded with `{match_id, server_tick, script_id}`.
  - Constrain numeric ops to be deterministic across platforms (prefer fixed-point helpers for sensitive math; otherwise guard floating point usage with tolerance bounds and forbidden non-deterministic functions).
  - CPU and memory quotas per script invocation; hard timeouts for `canExecute` and `onTick`.
- Define the versioned ability hook API:
  - `canExecute(ctx) -> { ok: bool, reason?: string, cost?: { resource: amount }[], reservations?: { type, key, amount }[] }`
  - `onStart(ctx) -> void`
  - `onTick(ctx) -> { continue: bool, progress?: float }` (false => complete)
  - `onInterrupt(ctx, cause) -> void`
  - `onComplete(ctx) -> void`
- Targeting schema specified in data (`self|entity|position|area`) + filters (faction, tag, range) and validated host-side before hook execution.
- Server remains the sole executor of scripts. Clients mirror static data for UX; no client script execution in v1.

### Version Awareness
- Scripts and definitions are addressed by versioned identifiers: `ability_id@version`, `entity_type_id@version`.
- Each live entity is bound to an immutable `entity_type_id@version`. Ability intents reference a specific `ability_id@version` (from the entity’s bound definition or explicit ability version).
- The script loader/dispatcher resolves modules by exact version and maintains a VM/module cache keyed by versioned IDs to avoid cross-version state sharing.

## Consequences
- Determinism: Centralized server execution avoids client divergence; fixed RNG and quotas keep outcomes stable.
- Performance: Quotas and batching required to protect the simulation. We will need a script VM pool and amortized invocations.
- Modding: Lua is approachable and well-documented; later we can add JS/WASM behind the same sandbox API if needed.

## Alternatives Considered
- JavaScript (QuickJS or V8 isolates): richer ecosystem but heavier footprint; determinism needs more guardrails.
- WASM: strong sandboxing, multi-language support; higher integration effort and deterministic FP still requires constraints.
- No scripting (pure data/DSL): simpler but less flexible for emergent behaviors.

## Implementation Notes
- VM lifecycle: prewarm a pool per shard, reset state per call; no global mutation outside `ctx`.
- `ctx` surface (read-only queries + action outputs only):
  - `entity`: includes `entity_type_id@version`, current stats, position, squad/stance, cooldowns.
  - `ability`: includes `ability_id@version`, declared targeting schema, configured costs.
  - `match`: `server_tick`, deterministic RNG seed fragment, content pack/version info.
  - Read APIs: distances, LOS/visibility, tech state, player resources, reservations.
  - Write outputs: validation result, desired costs/reservations, progress, completion.
- Error handling: script errors mark the intent as `FAILED` with `SCRIPT_ERROR`; log with correlation IDs (`player_id`, `entity_id`, `intent_id`, `ability_id`).
- Testing: cross-platform deterministic harness that runs hooks with golden outputs; fuzz inputs for quota/timeouts.

## References
- `docs/requirements/entity-intents.md`
- `docs/requirements/entities-and-abilities.md`
- `docs/adr/README.md`
