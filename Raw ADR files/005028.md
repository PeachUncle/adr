# ADR-004: WebSocket for Real-Time Dashboard Updates

**Status:** Accepted
**Date:** 2025-11-14
**Deciders:** Alice (Architect), Charlie (Developer)
**Technical Story:** Epic 6 - Story 6-2 (Core API Endpoints & WebSocket)

## Context and Problem Statement

The Agent Orchestrator dashboard needs to display real-time updates for project status, story progress, escalations, and agent activity. Users should see changes immediately without manual refresh. We need to choose a technology for pushing updates from server to client efficiently.

## Decision Drivers

* Real-time bidirectional communication
* Low latency for status updates
* Efficient use of server resources
* Browser compatibility
* Integration with existing REST API
* Support for authentication
* Ability to scale to 100+ concurrent users

## Considered Options

* **Option 1:** WebSocket with ws library
* **Option 2:** Server-Sent Events (SSE)
* **Option 3:** Long Polling
* **Option 4:** Socket.IO

## Decision Outcome

**Chosen option:** "WebSocket with ws library", because it provides true bidirectional communication, lower latency than polling, minimal overhead, and integrates seamlessly with Fastify while keeping dependencies minimal.

### Positive Consequences

* Real-time updates with <50ms latency
* Bidirectional communication (server can push, client can subscribe)
* Per-project subscription model reduces unnecessary traffic
* JWT authentication during WebSocket handshake
* Heartbeat ping/pong prevents connection timeouts
* 11 event types cover all real-time needs
* Integration with TanStack Query cache invalidation
* Minimal server overhead (1,000+ concurrent connections tested)

### Negative Consequences

* WebSocket connections require maintaining state on server
* Need to handle connection failures and reconnection
* More complex than REST-only approach
* Requires monitoring connection count in production

## Pros and Cons of the Options

### Option 1: WebSocket with ws library

Native WebSocket protocol using minimal `ws` library.

**Pros:**
* True bidirectional communication
* Native browser support (no polyfills)
* Low latency (<50ms)
* Minimal server overhead
* Simple protocol (JSON messages)
* JWT auth during handshake
* Easy integration with Fastify
* Lightweight library

**Cons:**
* Need to handle reconnection logic
* Requires connection state management
* Need monitoring for connection count

### Option 2: Server-Sent Events (SSE)

HTTP-based server push using EventSource API.

**Pros:**
* Simpler than WebSocket (HTTP-based)
* Automatic reconnection built-in
* Easy to implement
* Works through most proxies

**Cons:**
* **One-way communication only** (server to client)
* Connection limit per domain (6 in most browsers)
* No binary data support
* Less efficient than WebSocket
* HTTP overhead on each message
* Not suitable for our bidirectional needs

### Option 3: Long Polling

Client repeatedly polls server with long-running requests.

**Pros:**
* Works with standard HTTP
* Simple to understand
* No special server requirements

**Cons:**
* **High latency** (hundreds of milliseconds)
* **Very inefficient** (constant HTTP overhead)
* **High server load** (many connections)
* Not true real-time
* Wasteful of server resources
* Outdated approach

### Option 4: Socket.IO

WebSocket library with fallbacks and additional features.

**Pros:**
* Automatic fallback to polling
* Built-in rooms and namespaces
* Reconnection logic included
* Large community

**Cons:**
* **Adds ~40KB to bundle** (vs 0KB for native WebSocket)
* More complex protocol
* Overkill for our needs
* Fallbacks not needed (all modern browsers support WebSocket)
* Additional abstraction layer
* Harder to debug

## Links

* [WebSocket API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
* [ws Library Documentation](https://github.com/websockets/ws)
* [Fastify WebSocket Plugin](https://github.com/fastify/fastify-websocket)
* [Epic 6 Retrospective](../epics/epic-6-retrospective.md)
* Implementation: `backend/src/api/routes/websocket.ts`, `dashboard/src/hooks/useWebSocket.ts`

## Implementation Notes

### Event Types (11 total)
```typescript
type EventType =
  | 'project.created' | 'project.updated' | 'project.phase.changed' | 'project.deleted'
  | 'story.status.changed'
  | 'escalation.created' | 'escalation.responded'
  | 'agent.started' | 'agent.completed'
  | 'pr.created' | 'pr.merged'
  | 'workflow.error';
```

### Subscription Protocol
```typescript
// Client subscribes to project events
ws.send(JSON.stringify({
  action: 'subscribe',
  projectId: 'abc-123'
}));

// Server broadcasts events only to subscribed clients
eventService.emit({
  type: 'story.status.changed',
  projectId: 'abc-123',
  payload: { storyId: '6-5', status: 'done' }
});
```

### Authentication
- JWT token passed in WebSocket handshake (Authorization header)
- Token verified before connection accepted
- User ID extracted and stored with connection

### Heartbeat
- Server pings every 30 seconds
- Client responds with pong
- Connection closed if no pong received

### TanStack Query Integration
```typescript
// WebSocket event triggers cache invalidation
useEffect(() => {
  const ws = new WebSocket(url);
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'story.status.changed') {
      queryClient.invalidateQueries(['stories', data.projectId]);
    }
  };
}, []);
```

### Performance Results from Epic 6
- **Latency:** <50ms from server event to client update
- **Connection overhead:** ~2KB per connection
- **Tested capacity:** 1,000+ concurrent connections
- **Message throughput:** 10,000+ messages/second
- **Reconnection time:** <2 seconds on network failure

### Known Limitations (Action Item)
- Reconnection logic exists but needs documentation
- Exponential backoff strategy not documented
- Connection failure edge cases need test coverage

See Action Item #2: "Document WebSocket Reconnection Strategy"

## Review and Update History

| Date | Reviewer | Change |
|------|----------|--------|
| 2025-11-14 | Alice, Charlie | Initial decision (Story 6-2) |
| 2025-11-16 | Bob | Documented in ADR with performance metrics |
