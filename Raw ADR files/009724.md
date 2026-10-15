# ADR-001: Real-time Architecture

## Status

**Accepted** - 2026-01-01

## Context

The multiplayer Mahjong game requires real-time communication for:
- Game state synchronization (tile draws, discards, melds)
- Chat messages
- Player presence (online/offline status)
- WebRTC signaling for voice chat

We need to choose a real-time infrastructure that balances performance, developer experience, and operational complexity.

## Decision Drivers

- **Latency**: Game actions must reflect within 200ms
- **Reliability**: Game state cannot be lost
- **Scalability**: Support 10,000 concurrent users
- **Developer Experience**: Minimize infrastructure management
- **Cost**: Predictable, manageable costs at scale
- **Integration**: Works well with chosen auth/database solution

## Considered Options

### Option 1: Supabase Realtime (Selected)

**Pros**:
- Unified stack with auth, database, and edge functions
- Built-in presence for online status
- Broadcast channels for game events
- Postgres Changes for persistent state sync
- No separate WebSocket server to manage
- Good TypeScript support

**Cons**:
- Less control than self-hosted
- Vendor lock-in to Supabase
- Usage-based pricing at scale

### Option 2: Socket.io (Self-hosted)

**Pros**:
- Full control over implementation
- Large ecosystem and community
- No vendor lock-in
- Predictable costs (server-based)

**Cons**:
- Requires server management
- Horizontal scaling complexity
- Additional infrastructure to maintain
- Must implement presence manually

### Option 3: Liveblocks

**Pros**:
- Purpose-built for real-time collaboration
- Excellent conflict resolution
- Managed infrastructure

**Cons**:
- Additional vendor dependency
- Usage-based pricing
- Overkill for turn-based game state
- Less control over sync behavior

### Option 4: PartyKit

**Pros**:
- Edge-based, low latency
- Durable Objects pattern
- Good developer experience

**Cons**:
- Newer platform, less proven
- Cloudflare ecosystem lock-in
- Separate from auth/database

## Decision

**We will use Supabase Realtime** with the following channel structure:

```typescript
// Game state and presence
room:{roomId}

// Chat messages (backed by Postgres)
room:{roomId}:chat

// WebRTC signaling
room:{roomId}:voice

// Matchmaking notifications
matchmaking
```

## Rationale

1. **Unified Stack**: Supabase provides auth, database, realtime, and edge functions in one platform, reducing integration complexity.

2. **Postgres Changes**: Game state persists in database and syncs automatically via Postgres Changes, ensuring no data loss.

3. **Broadcast for Ephemeral Events**: Game actions broadcast immediately for low latency, while database serves as source of truth.

4. **Presence Built-in**: Player online/offline status handled natively.

5. **Edge Functions**: Server-authoritative game logic runs on Edge Functions with direct database access.

## Consequences

### Positive
- Reduced infrastructure complexity
- Single SDK for all backend services
- Automatic reconnection handling
- Built-in presence management

### Negative
- Dependent on Supabase reliability
- Less flexibility than custom solution
- May need to migrate if outgrowing Supabase

### Risks
- Supabase outage affects all game functionality
- Rate limits may require careful channel design

## Compliance

- No PII transmitted over realtime channels (only game state)
- Messages stored in Postgres with RLS policies
- Voice signaling only (audio is P2P, not stored)

## Related Decisions

- ADR-003: Game Logic Location (Edge Functions)
- ADR-004: Voice Chat Implementation (WebRTC via Realtime signaling)
