# ADR-003: Game Logic Location

## Status

**Accepted** - 2026-01-01

## Context

Mahjong game logic includes:
- Tile shuffling and dealing
- Turn management
- Action validation (discard, Pong, Kong, Chow, Win)
- Faan calculation
- Score computation

The location of this logic affects security, latency, and maintainability.

## Decision Drivers

- **Anti-Cheat**: Players must not be able to see other players' tiles or manipulate game state
- **Fairness**: Randomization (shuffling) must be verifiable
- **Latency**: Actions should feel responsive (<200ms)
- **Consistency**: All players must see the same game state
- **Scalability**: Handle many concurrent games
- **Maintainability**: Single source of truth for rules

## Considered Options

### Option 1: Server-Authoritative via Edge Functions (Selected)

**Pros**:
- Complete anti-cheat (client never sees hidden tiles)
- Single source of truth
- Verifiable randomization
- Scalable (stateless functions)
- Can enforce rate limits

**Cons**:
- Added latency for each action
- More complex than client-only
- Cold start potential (mitigated by edge)

### Option 2: Client-Side with Server Validation

**Pros**:
- Instant local feedback
- Reduced server load
- Simpler initial implementation

**Cons**:
- Client must have hidden tile data for validation
- Cheat potential (client can read memory)
- Complex reconciliation logic
- Multiple sources of truth

### Option 3: Hybrid (Optimistic Updates)

**Pros**:
- Fast feedback for valid actions
- Server remains authoritative
- Best of both worlds

**Cons**:
- Complex rollback logic
- Client still needs validation code
- State divergence edge cases

### Option 4: Peer-to-Peer with Consensus

**Pros**:
- No server dependency during game
- Lowest latency between players

**Cons**:
- Cheating trivial (one peer has all state)
- Consensus overhead
- Connection issues cause game failures
- No hidden information possible

## Decision

**We will use server-authoritative game logic via Supabase Edge Functions.**

### Architecture

```
Client Action                    Server (Edge Function)
    │                                    │
    ├── {action: DISCARD, tile: "3B"} ──►│
    │                                    │ 1. Load game state
    │                                    │ 2. Validate action
    │                                    │ 3. Apply to state
    │                                    │ 4. Store new state
    │                                    │ 5. Broadcast delta
    │◄── {type: DISCARD, by: 0, tile}  ──┤
    │                                    │
```

### Game State Storage

```typescript
// Postgres game_players table
{
  game_id: uuid,
  user_id: uuid,
  seat: 0-3,
  hand_tiles: ["1B", "2B", "3B", ...],  // Server only
  discards: ["5C", "RD", ...],          // Visible to all
  melds: [...],                         // Visible to all
  score: number
}
```

### Client Receives (per player)

```typescript
// Own player: full hand
{ seat: 0, hand: ["1B", "2B", ...], discards: [...], melds: [...] }

// Other players: hand count only
{ seat: 1, handCount: 13, discards: [...], melds: [...] }
```

## Rationale

1. **Anti-Cheat Priority**: Mahjong's hidden information is critical. Server authority is the only way to prevent cheating.

2. **Edge Functions**: Run close to users, minimizing latency. Cold starts mitigated by Supabase's architecture.

3. **Atomic Operations**: Each action is a transaction - validate, apply, store, broadcast. No partial states.

4. **Reconnection**: Game state in database allows seamless reconnection.

5. **Replay Support**: Action log enables replays without client-side recording.

## Consequences

### Positive
- Cheating effectively prevented
- Single source of truth
- Fair randomization
- Clean replay data
- Reconnection support

### Negative
- Every action has network round-trip
- Server cost per action
- More complex deployment

### Latency Mitigation

| Strategy | Implementation |
|----------|----------------|
| Edge deployment | Edge Functions run globally |
| Optimistic UI | Disable tile during action, restore on error |
| Debounce | Batch rapid actions (rare in turn-based) |
| Precomputation | Cache valid actions client-side |

## Security Measures

1. **Hidden Tile Protection**: `hand_tiles` column filtered by RLS, never sent to other players
2. **Action Validation**: Full rule check on server before state change
3. **Rate Limiting**: Max 1 action per 500ms per player
4. **Timestamp Verification**: Actions rejected if too fast (bot detection)
5. **Session Binding**: Actions tied to authenticated session

## Technical Implementation

### Edge Function: game-action

```typescript
// supabase/functions/game-action/index.ts
export async function handler(req: Request) {
  const { gameId, action } = await req.json();
  const userId = getAuthUser(req);

  // Load game state
  const game = await loadGame(gameId);

  // Validate action
  const result = validateAction(game, userId, action);
  if (!result.valid) {
    return Response.json({ error: result.reason }, { status: 400 });
  }

  // Apply action
  const newState = applyAction(game, action);

  // Store and broadcast
  await saveGame(gameId, newState);
  await broadcastAction(gameId, action, newState.publicDelta);

  return Response.json({ success: true });
}
```

## Related Decisions

- ADR-001: Real-time Architecture (broadcast mechanism)
- ADR-006: Tile Encoding (data format)
