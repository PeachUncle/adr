# ADR 002: Local WebSocket vs BroadcastChannel for Dev Sync

**Date**: 2025-11-21
**Status**: Accepted
**Deciders**: Development Team

## Context

We need a dev-time sync adapter for testing real-time collaboration. Two options:

1. **BroadcastChannel API** - Browser native, tabs on same origin
2. **Local WebSocket Server** - Node.js server, any device

## Decision

Use **Local WebSocket Server** for dev sync adapter.

## Rationale

### Why NOT BroadcastChannel

**Critical Limitation**: Only works on same device, same browser, same origin.

Example scenario that FAILS with BroadcastChannel:
```
Developer A (laptop)       Developer B (phone)
    ↓                           ↓
Open /s/ABC123           Open /s/ABC123
    ↓                           ↓
Create task                 ❌ NO SYNC!
    ↓
See task locally
```

**BroadcastChannel only syncs**:
- ✅ Tab 1 → Tab 2 (same browser)
- ❌ Laptop → Phone
- ❌ Developer A → Developer B
- ❌ Chrome → Firefox (even same machine)

This means **we can't test the PRIMARY use case** (multi-user collaboration) until deploying to production WebSocket infrastructure.

### Why WebSocket Server

**Advantages**:
1. ✅ **Tests Real Collaboration**: Multiple devices, users, browsers
2. ✅ **Matches Production**: Local WebSocket behaves like Netlify WebSocket
3. ✅ **Simple Implementation**: `ws` package, 137 lines of code
4. ✅ **Room-Based Routing**: Same sessionId logic as prod
5. ✅ **Easy to Run**: `pnpm ws:dev` in background

**Example Working Scenario**:
```
Developer A (laptop:4200)      Local WS Server       Developer B (phone:4200)
        ↓                           (port 8080)                ↓
   Create task                         |                 Receive sync message
        ↓                               |                       ↓
   Publish to WS ──────────────────────┼──────────────────> See task appear!
        ↓                               |                       ↓
   See own task                         |                  Mark task done
        ↓                               |                       ↓
   Receive sync <──────────────────────┴──────────────── Publish to WS
        ↓
   See done status!
```

## Implementation

**Server**: `/server/ws-server.ts`
- Runs on port 8080
- Rooms keyed by sessionId
- Broadcasts to all clients in room (excluding sender)
- Graceful shutdown handling

**Adapter**: `/src/adapters/sync/local-ws.adapter.ts`
- Implements SyncBusPort interface
- Connects to `ws://localhost:8080`
- Validates messages with Zod schemas
- Filters out own messages (prevents echo)

## Trade-offs

**Pros**:
- ✅ Tests actual collaboration
- ✅ Discovers WebSocket bugs early
- ✅ Prod-like behavior

**Cons**:
- ⚠️  Requires running separate process (`pnpm ws:dev`)
- ⚠️  Port 8080 must be available
- ⚠️  Slightly slower startup (wait for WS server)

## Consequences

**Positive**:
- E2E tests can simulate real multi-user scenarios
- Developers can test collaboration locally (laptop + phone)
- Found and fixed connection handling bugs before prod

**Negative**:
- CI must start WebSocket server before tests
- Developers must remember to run `pnpm ws:dev`

## Decision Matrix

| Feature | BroadcastChannel | WebSocket Server |
|---------|-----------------|------------------|
| Multi-device | ❌ | ✅ |
| Multi-user | ❌ | ✅ |
| Cross-browser | ❌ | ✅ |
| Prod-like | ❌ | ✅ |
| Simple setup | ✅ | ⚠️  (extra process) |
| Zero dependencies | ✅ | ❌ (requires ws package) |

## Alternatives Considered

**1. BroadcastChannel + Manual Testing in Prod**
- Rejected: Can't test main feature until deploy

**2. Socket.io Instead of ws**
- Rejected: Overkill, heavier bundle, we don't need fallbacks

**3. Service Worker + BroadcastChannel**
- Rejected: Still doesn't solve cross-device problem

## References

- [BroadcastChannel MDN](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel)
- [WebSocket RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [ws npm package](https://github.com/websockets/ws)
