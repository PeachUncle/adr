# ADR-002: WebSocket-Based Presence Tracking

## Status
Accepted

## Date
2026-01-01

## Context

The application originally used an HTTP heartbeat mechanism to track player presence:

```typescript
// Old approach (usePlayerHeartbeat)
setInterval(() => {
  fetch(`/api/players/${playerId}/heartbeat`, { method: 'POST' });
}, 10000); // Every 10 seconds
```

The heartbeat API would update the player's `last_heartbeat` timestamp in the database:

```typescript
// heartbeat/route.ts
await supabase
  .from('players')
  .update({ last_heartbeat: new Date().toISOString() })
  .eq('id', playerId);
```

### Problems with HTTP Heartbeat

1. **Spurious Realtime Events**: Every heartbeat update triggered Supabase Realtime `UPDATE` events on the `players` table. With 4 players, this generated 24 realtime events per minute (4 players × 6 heartbeats/min), causing unnecessary UI re-renders.

2. **Server Load**: Each heartbeat required an HTTP request → API route → database write → response cycle.

3. **Battery/Network Impact**: Mobile devices had to maintain HTTP polling even when idle.

4. **Latency**: 10-second polling meant up to 10 seconds delay detecting player disconnection.

## Decision

Replace HTTP heartbeat polling with **Supabase Realtime Presence**, a WebSocket-based presence tracking system built into Supabase.

### Implementation

```typescript
// New approach (usePlayerPresence)
const channel = supabase.channel(`presence:${sessionId}`, {
  config: {
    presence: { key: playerId },
  },
});

channel
  .on('presence', { event: 'sync' }, () => {
    const state = channel.presenceState();
    // state contains all online players
  })
  .on('presence', { event: 'join' }, ({ key, newPresences }) => {
    // Player came online
  })
  .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
    // Player went offline
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      await channel.track({
        player_id: playerId,
        player_name: playerName,
        online_at: new Date().toISOString(),
      });
    }
  });
```

### Key Changes

1. **Deleted**: `src/app/api/players/[playerId]/heartbeat/route.ts`
2. **Deleted**: `src/hooks/usePlayerHeartbeat.ts`
3. **Created**: `src/hooks/usePlayerPresence.ts`
4. **Updated**: Lobby and Play pages to use `usePlayerPresence`

## Consequences

### Positive

1. **No Database Writes**: Presence state is maintained in-memory by Supabase Realtime, not in the database. Zero spurious realtime events.

2. **Instant Detection**: WebSocket connections are monitored continuously. Disconnect is detected immediately when the socket closes.

3. **Lower Server Load**: No HTTP requests for presence. The WebSocket is already open for other realtime subscriptions.

4. **Better Battery Life**: WebSocket keepalive is more efficient than HTTP polling.

5. **Simpler Architecture**: No need for background cleanup jobs to mark stale players as inactive.

### Negative

1. **No Persistent State**: Presence is ephemeral. If you need to know "who was online 5 minutes ago," that data isn't stored.

2. **Different API**: Presence state is accessed via `channel.presenceState()` rather than database queries. Server-side code can't easily check who's online.

### Neutral

1. **Existing `last_heartbeat` Column**: The column remains in the database but is no longer updated. Could be removed in a future migration if not needed.

## Future Considerations

- Could expose presence state in the UI (green/gray dots for online/offline players)
- Could add server-side presence checks via Supabase Admin API if needed
- Could store presence snapshots periodically if historical data is needed
