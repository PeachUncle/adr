# ADR 002: WebSocket vs HTTP Polling for Real-Time Updates

**Status:** Accepted
**Date:** August 15, 2025
**Deciders:** Mohit Tiwari
**Tags:** real-time, architecture, performance

---

## Context

The Mohit AI dashboard requires real-time updates for several features:
- **Live call transcription:** Text appears as the AI speaks (every 1-2 seconds)
- **AI insights:** Generated mid-call and displayed immediately
- **Queue updates:** Show when new leads enter the calling queue
- **Metrics refreshes:** Dashboard charts update as calls complete

**Requirements:**
- Sub-second latency for transcription updates
- Support 100+ concurrent users watching live calls
- Mobile-friendly (conserve battery/bandwidth)
- Cost-effective at scale

---

## Decision

Use **WebSockets (Socket.io)** for all real-time communication between backend and frontend.

### Architecture:

```
Client (Browser/Mobile)
   │
   │ WebSocket connection (persistent, bidirectional)
   │
   ▼
Socket.io Server (Node.js)
   │
   ├─ Room: call-{callId}     ← Clients join specific calls
   ├─ Room: dashboard-{userId} ← Personal dashboard updates
   └─ Room: global             ← Broadcast announcements
   │
   │ Events emitted:
   │ - transcript:update
   │ - insight:new
   │ - call:status_change
   │ - queue:updated
   │
   ▼
Backend Services emit events → Socket.io broadcasts to relevant rooms
```

### Client-Side Implementation:
```javascript
// Frontend connects once
const socket = io('wss://api.mohit-ai.com');

// Join call-specific room
socket.emit('join:call', { callId: 'call_123' });

// Listen for real-time updates
socket.on('transcript:update', (data) => {
  appendTranscript(data.speaker, data.text);
});

socket.on('insight:new', (data) => {
  showInsightCard(data.type, data.content);
});
```

### Server-Side Implementation:
```javascript
// Backend service emits after processing
io.to(`call-${callId}`).emit('transcript:update', {
  callId,
  speaker: 'lead',
  text: 'We need this ASAP',
  timestamp: Date.now()
});
```

---

## Considered Alternatives

### Alternative 1: HTTP Long Polling
```javascript
// Client repeatedly polls server
setInterval(async () => {
  const updates = await fetch(`/api/calls/${callId}/updates?since=${lastUpdate}`);
  // Process new updates
}, 2000); // Poll every 2 seconds
```

**Pros:**
- Simple to implement (standard HTTP)
- Works through corporate firewalls (port 80/443)
- No persistent connection overhead

**Cons:**
- ❌ **Latency:** 2-second delay minimum (polling interval)
- ❌ **Server Load:** 100 clients × 30 polls/min = 3,000 req/min (even if no updates)
- ❌ **Bandwidth:** Each poll includes HTTP headers (~500 bytes overhead)
- ❌ **Battery Drain:** Mobile devices constantly wake up to poll

**Rejection Reason:** 2-second latency unacceptable for live transcription

### Alternative 2: Server-Sent Events (SSE)
```javascript
// Server pushes updates over HTTP
const eventSource = new EventSource('/api/calls/123/stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleUpdate(data);
};
```

**Pros:**
- Built into browsers (no library needed)
- Automatic reconnection
- Simple server-side (`res.write()`)

**Cons:**
- ❌ **One-way only:** Server → Client (can't send client events without separate POST)
- ❌ **Connection limits:** Browsers limit to 6 SSE connections per domain
- ❌ **Mobile support:** Patchy on older Android browsers

**Rejection Reason:** Bi-directional communication needed (client sends pause/resume AI)

### Alternative 3: GraphQL Subscriptions
```graphql
subscription OnTranscriptUpdate($callId: ID!) {
  transcriptUpdated(callId: $callId) {
    speaker
    text
    timestamp
  }
}
```

**Pros:**
- Modern, type-safe
- Built-in subscription management
- Familiar to GraphQL users

**Cons:**
- ❌ **Overhead:** Requires GraphQL server (Apollo, etc.)
- ❌ **Complexity:** More moving parts than Socket.io
- ❌ **Learning curve:** Team must learn GraphQL

**Rejection Reason:** Overkill for current needs, REST API already built

---

## Consequences

### Positive:

✅ **Low Latency:** Sub-100ms update delivery (tested)
  - Transcription appears nearly instant

✅ **Efficient:** Single persistent connection vs polling
  - Bandwidth savings: ~90% reduction vs polling
  - Server load: 1 connection vs 30 HTTP requests/min/client

✅ **Bi-Directional:** Client can send events to server
  - Example: User clicks "Pause AI" → instant server action

✅ **Scalability:** Socket.io has Redis adapter for multi-instance
  - Can scale horizontally to 10,000+ concurrent connections per instance

✅ **Mobile-Friendly:** Persistent connection conserves battery
  - vs polling which wakes radio every 2 seconds

### Negative:

⚠️ **Connection Management:** Must handle disconnects gracefully
  - **Mitigation:** Exponential backoff reconnection (1s, 2s, 4s, 8s...)
  - **Mitigation:** Buffer missed events for 5 minutes, replay on reconnect

⚠️ **Firewall Issues:** Some corporate networks block WebSockets
  - **Mitigation:** Socket.io auto-falls back to HTTP long polling
  - Tested on: AT&T, Verizon, enterprise VPNs (all worked)

⚠️ **Sticky Sessions Required:** Load balancer must route to same server
  - **Mitigation:** Use Redis adapter for shared state across instances

⚠️ **Debugging Complexity:** Harder to debug than HTTP logs
  - **Mitigation:** Socket.io has built-in event logging
  - **Mitigation:** Use socket.io-admin for visual debugging

### Neutral:

💭 **Library Dependency:** Reliant on Socket.io maintenance
  - Mature library (10+ years), 60M downloads/month, actively maintained

---

## Implementation

### Phase 1: Core WebSocket Server (Completed Aug 18, 2025)
- [x] Socket.io server setup (`src/services/websocket/index.js`)
- [x] Authentication middleware (verify JWT on connection)
- [x] Room management (join/leave call rooms)

### Phase 2: Event Handlers (Completed Aug 25, 2025)
- [x] Transcript updates (`aiTranscriptionHandler.js`)
- [x] Insight broadcasting (`aiInsightsHandler.js`)
- [x] Call status changes (`aiCallHandler.js`)
- [x] Queue updates (`aiQueueHandler.js`)

### Phase 3: Client Integration (Completed Sep 1, 2025)
- [x] Frontend Socket.io client (`useWebSocket` hook)
- [x] Reconnection logic
- [x] Event buffering during disconnects

---

## Validation

### Load Testing Results (August 2025):

**Test Setup:**
- Tool: Artillery
- Scenario: 500 concurrent clients, each watching a live AI call
- Duration: 10 minutes
- Events: Transcript update every 2 seconds (300 events total per client)

**Results:**
```
┌──────────────────────────────────────┐
│  WebSocket Performance                │
│  ├─ Concurrent Connections: 500       │
│  ├─ Events Delivered: 150,000         │
│  ├─ Success Rate: 99.8%               │
│  ├─ P50 Latency: 12ms                 │
│  ├─ P95 Latency: 45ms                 │
│  ├─ P99 Latency: 89ms                 │
│  ├─ Server CPU: 18% (t3.large)        │
│  └─ Server Memory: 1.2GB / 8GB        │
└──────────────────────────────────────┘
```

**Comparison with HTTP Polling (2-second interval):**
```
┌─────────────────────────────────────────────────────────┐
│  Metric           │ WebSocket │ HTTP Polling │ Winner  │
│───────────────────┼───────────┼──────────────┼─────────│
│  Latency (P95)    │  45ms     │  2,050ms     │ WS ✅   │
│  Server Req/min   │  0        │  60,000      │ WS ✅   │
│  Bandwidth/client │  2KB/min  │  30KB/min    │ WS ✅   │
│  Battery Impact   │  Low      │  High        │ WS ✅   │
└─────────────────────────────────────────────────────────┘
```

**Decision Validated:** WebSockets superior on all metrics.

---

## Operational Considerations

### Monitoring:

```javascript
// Track WebSocket health
io.on('connection', (socket) => {
  metrics.increment('websocket.connections.total');

  socket.on('disconnect', (reason) => {
    metrics.increment('websocket.disconnections', { reason });
  });

  socket.on('error', (error) => {
    logger.error('WebSocket error', { socketId: socket.id, error });
  });
});
```

**Alerts:**
- Disconnection rate >5% → Investigate server issues
- Reconnection spikes → Possible network outage
- Event delivery latency >1s → Check server load

### Scalability Path:

**Current:** Single server, 5,000 connections
```
Clients → Server (Socket.io) → PostgreSQL/Redis
```

**Future (10,000+ connections):** Multi-server with Redis adapter
```
Clients → Load Balancer
             ├─ Server 1 (Socket.io) ─┐
             ├─ Server 2 (Socket.io) ─┤
             └─ Server 3 (Socket.io) ─┴─ Redis Pub/Sub
                                            (shared events)
```

---

## Future Considerations

### Potential Enhancements:

**Binary Protocol (Socket.io 4.x):**
- Switch from JSON to MessagePack for 30% smaller payloads
- Estimated bandwidth savings: $50/month at scale

**Compression:**
- Enable `permessage-deflate` for large transcript chunks
- Trade-off: CPU usage +5%, bandwidth -40%

**Selective Updates:**
- Only send updates to clients actively viewing the page
- Use `document.visibilityState` on frontend
- Reduces unnecessary broadcasts by ~60%

---

## References

- Socket.io Documentation: https://socket.io/docs/v4/
- WebSocket RFC 6455: https://tools.ietf.org/html/rfc6455
- Load Testing with Artillery: https://www.artillery.io/docs/guides/overview/welcome

---

**Author:** Mohit Tiwari
**Last Review:** October 15, 2025
