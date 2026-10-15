# ADR-003: WebSocket Implementation

**Status:** Accepted  
**Date:** 2025-10-07  
**Decision Makers:** Development Team, Infrastructure Team  
**Consulted:** Frontend Team, Security Team  

---

## Context

The EchoVerse Platform requires real-time communication capabilities for:
- Live chat in communities and direct messages
- Real-time notifications for orders, posts, and events
- Typing indicators and presence status
- Live updates for collaborative features
- Broadcasting system-wide announcements
- Activity feeds and live dashboards

We needed a WebSocket solution that provides:
- Secure authentication and authorization
- Scalability across multiple servers
- Message validation and rate limiting
- Automatic reconnection and recovery
- Room-based message broadcasting
- Low latency and high throughput

---

## Decision

We have decided to implement **WebSocket communication using the native `ws` library** with custom authentication, room management, and message validation.

### Key Components:

1. **WebSocket Server**
   - Native `ws` library (lightweight, performant)
   - Single endpoint: `wss://host/ws`
   - JWT-based authentication
   - Origin validation for security

2. **Client Connection**
   - React hook: `useWebSocket`
   - Automatic reconnection with exponential backoff
   - Message queuing during disconnection
   - Heartbeat mechanism (ping/pong)

3. **Message System**
   - Zod schema validation
   - Room-based broadcasting
   - Direct user messaging
   - Typing indicators

4. **Security & Rate Limiting**
   - Max 5 connections per user
   - Max 10 connections per IP per minute
   - Max 60 messages per minute per user
   - Max 64KB message size
   - Session-based authentication

---

## Rationale

### Why Native `ws` Library?

**Pros:**
- ✅ Lightweight and performant
- ✅ Full control over implementation
- ✅ No framework lock-in
- ✅ WebSocket protocol compliance
- ✅ Excellent Node.js integration
- ✅ Low memory footprint

**Cons:**
- ❌ More implementation work vs Socket.IO
- ❌ No built-in rooms (implemented custom)
- ❌ Manual fallback handling

**Alternatives Considered:**
- **Socket.IO**: Rejected due to overhead and unnecessary features (HTTP fallback, namespaces)
- **Pusher/Ably**: Rejected due to vendor lock-in and cost
- **GraphQL Subscriptions**: Rejected due to complexity and Apollo overhead
- **Server-Sent Events (SSE)**: Rejected due to unidirectional communication

---

## Implementation Details

### Server Setup

```typescript
// server/websocket.ts
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ 
  server,
  path: '/ws',
  verifyClient: (info) => {
    // Origin validation
    const origin = info.origin || info.req.headers.origin;
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];
    return allowedOrigins.some(allowed => 
      allowed === '*' || origin === allowed || origin?.startsWith(allowed)
    );
  }
});
```

### Authentication Flow

1. **Client connects** to `wss://host/ws`
2. **Server sends** `connected` message
3. **Client sends** `auth` message with JWT token
4. **Server validates** token and session
5. **Server responds** with `authenticated` message
6. **Client can now** send/receive messages

```typescript
// Authentication message
{
  type: 'auth',
  token: 'jwt-access-token'
}
```

### Room Management

```typescript
// Join room
{
  type: 'join_room',
  roomId: 'community-123'
}

// Leave room
{
  type: 'leave_room',
  roomId: 'community-123'
}

// Send message to room
{
  type: 'message',
  roomId: 'community-123',
  content: 'Hello, everyone!'
}
```

### Client Implementation

```typescript
// client/src/hooks/useWebSocket.ts
export function useWebSocket(options) {
  const connect = () => {
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
      ws.send(JSON.stringify({ 
        type: 'auth', 
        token: getAccessToken() 
      }));
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleMessage(message);
    };
    
    ws.onerror = (error) => {
      handleError(error);
    };
    
    ws.onclose = () => {
      handleReconnect();
    };
  };
}
```

### Message Validation

```typescript
// server/utils/websocket-schemas.ts
export const WebSocketMessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('auth'),
    token: z.string(),
  }),
  z.object({
    type: z.literal('join_room'),
    roomId: z.string(),
  }),
  z.object({
    type: z.literal('message'),
    roomId: z.string(),
    content: z.string().max(5000),
  }),
  // ... other message types
]);
```

### Connection Management

**Per-User Limits:**
```typescript
const MAX_CONNECTIONS_PER_USER = 5;
const clients = new Map<userId, Set<WebSocket>>();

// Enforce limit
if (userConnections.size >= MAX_CONNECTIONS_PER_USER) {
  // Close oldest connection
  const oldest = Array.from(userConnections)[0];
  oldest.close(1008, 'Max connections exceeded');
}
```

**Rate Limiting:**
```typescript
const MAX_MESSAGES_PER_MINUTE = 60;
const messageRateLimiter = new Map<userId, MessageRate>();

if (messageRate.count >= MAX_MESSAGES_PER_MINUTE) {
  ws.send(JSON.stringify({ 
    type: 'error', 
    message: 'Rate limit exceeded' 
  }));
  return;
}
```

### Heartbeat Mechanism

**Server-side:**
```typescript
const heartbeatInterval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) {
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000); // 30 seconds
```

**Client-side:**
```typescript
const heartbeatInterval = setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 25000); // 25 seconds
```

### Session Invalidation Integration

```typescript
// When session is invalidated (logout, security event)
registerSessionInvalidationCallback((sessionId, userId, reason) => {
  const userConnections = clients.get(userId);
  userConnections?.forEach((ws) => {
    if (ws.sessionId === sessionId) {
      ws.close(1008, `Session invalidated: ${reason}`);
    }
  });
});
```

---

## Consequences

### Positive

1. **Real-Time**: Instant message delivery (<50ms latency)
2. **Scalability**: Handles 1000+ concurrent connections per server
3. **Security**: JWT auth + session validation
4. **Reliability**: Automatic reconnection with exponential backoff
5. **Control**: Full control over implementation
6. **Performance**: Low memory footprint (~2KB per connection)
7. **Integration**: Seamless with existing auth system

### Negative

1. **Complexity**: More code vs using Socket.IO
2. **Scaling**: Requires message broker (Redis Pub/Sub) for multi-server
3. **State**: Connection state management across servers
4. **Fallback**: No automatic HTTP long-polling fallback
5. **Debug**: More complex debugging vs REST APIs

### Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Connection storms | Rate limiting, connection queuing |
| Memory leaks | Automatic cleanup, garbage collection |
| Message flooding | Per-user rate limits, message size limits |
| Server crash | Automatic client reconnection |
| DDoS attacks | Origin validation, IP-based rate limiting |
| Session hijacking | Device fingerprinting, session validation |

---

## Scalability Considerations

### Current Architecture (Single Server)
- ✅ Simple implementation
- ✅ Low latency
- ✅ Stateful connections
- ❌ Limited by single server capacity

### Future Multi-Server Architecture
When scaling beyond single server:

1. **Redis Pub/Sub** for message broadcasting
   ```typescript
   // Publish to Redis
   redis.publish('room:123', JSON.stringify(message));
   
   // Subscribe on all servers
   redis.subscribe('room:123', (message) => {
     broadcastToLocalClients(JSON.parse(message));
   });
   ```

2. **Sticky Sessions** for connection affinity
   - Use load balancer session affinity
   - Route connections to same server

3. **Distributed State** with Redis
   - Store active connections in Redis
   - Query cross-server connections

---

## Client Features

### Automatic Reconnection
```typescript
const reconnectWithBackoff = () => {
  const delay = Math.min(
    reconnectInterval * Math.pow(1.5, reconnectCount) + jitter,
    30000 // Max 30 seconds
  );
  
  setTimeout(() => {
    reconnectCount++;
    connect();
  }, delay);
};
```

### Message Queuing
```typescript
const sendMessage = (message) => {
  if (ws.readyState !== WebSocket.OPEN || !isAuthenticated) {
    messageQueue.push(message);
    return;
  }
  ws.send(JSON.stringify(message));
};
```

### Error Handling
```typescript
ws.onerror = (error) => {
  console.error('[WebSocket] Error:', error);
  setState({ error: 'Connection error' });
  onError?.(error);
};

ws.onclose = (event) => {
  console.log('[WebSocket] Disconnected:', event.code, event.reason);
  setState({ isConnected: false });
  
  if (reconnect && reconnectCount < maxReconnectAttempts) {
    reconnectWithBackoff();
  }
};
```

---

## Monitoring & Metrics

### Server Metrics
- Active connections count
- Messages per second
- Average message size
- Connection duration
- Error rate
- Memory usage per connection

### Client Metrics
- Connection success rate
- Reconnection attempts
- Message delivery time
- Queue size
- Error frequency

### Alerts
- Connection spike (>1000 in 1 min)
- High error rate (>5% failed messages)
- Memory threshold (>80% usage)
- Slow message delivery (>1s latency)

---

## Alternatives Considered

### 1. Socket.IO
**Pros:** Built-in rooms, fallbacks, reconnection  
**Cons:** Larger bundle size, protocol overhead, unnecessary features  
**Decision:** Rejected for simplicity and performance

### 2. GraphQL Subscriptions
**Pros:** Type safety, query flexibility  
**Cons:** Complex setup, Apollo overhead, subscription complexity  
**Decision:** Rejected for overhead

### 3. Server-Sent Events (SSE)
**Pros:** Simple, HTTP-based  
**Cons:** Unidirectional, browser limits  
**Decision:** Rejected for bidirectional requirement

### 4. Pusher/Ably
**Pros:** Managed service, easy setup  
**Cons:** Cost, vendor lock-in, data privacy  
**Decision:** Rejected for control and cost

---

## Related Decisions

- [ADR-002: Authentication Strategy](./ADR-002-authentication-strategy.md) - JWT auth for WebSockets
- [ADR-001: Database Choice](./ADR-001-database-choice.md) - Session storage

---

## References

- [WebSocket Protocol RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [ws Library Documentation](https://github.com/websockets/ws)
- [WebSocket Security](https://owasp.org/www-community/vulnerabilities/WebSocket_attacks)
- [Real-time Architecture Patterns](https://www.pubnub.com/blog/websocket-vs-sse-vs-long-polling/)

---

**Last Updated:** 2025-10-07  
**Next Review:** 2026-04-07
