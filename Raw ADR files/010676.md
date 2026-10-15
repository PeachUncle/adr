# ADR-005: WebSocket Real-time Architecture

**Status**: Accepted
**Date**: 2025-10-22
**Decision Makers**: System Architecture Designer
**Context**: Real-time leaderboard updates and match notifications using WebSocket technology

## Context and Problem Statement

Love Rank Pulse requires real-time updates for:
- Live leaderboard rank changes as matches complete
- Match result notifications to players
- Active player count and online status
- Live match progress updates
- Multi-server synchronization for horizontal scaling

## Decision Drivers

- **Real-time Performance**: Sub-second update delivery
- **Scalability**: Support 10,000+ concurrent connections
- **Reliability**: Automatic reconnection and message delivery
- **Developer Experience**: Simple client and server APIs
- **Cross-Platform**: Support web and future mobile clients
- **Resource Efficiency**: Minimal server overhead

## Considered Options

### Option 1: Socket.IO + Redis Pub/Sub ✅ SELECTED

**Architecture:**
```
Browser WebSocket Client → Socket.IO Server → Redis Pub/Sub → Other Servers
                                  ↓
                           Event Handlers
                                  ↓
                           Database Updates
```

**Components:**
- **Client**: Socket.IO client library
- **Server**: Socket.IO server with Express integration
- **Message Broker**: Redis Pub/Sub for multi-server sync
- **Events**: Typed event definitions with Zod validation

**Pros:**
- Automatic fallback to HTTP long-polling
- Built-in reconnection logic
- Room-based event broadcasting
- TypeScript support with typed events
- Extensive ecosystem and documentation
- Binary data support for efficiency

**Cons:**
- Larger library size than native WebSocket
- Custom protocol (not pure WebSocket)

### Option 2: Native WebSocket + Custom Protocol

**Architecture:**
```
Browser WebSocket → ws library → Custom Event Router → Database
```

**Pros:**
- Smaller payload size
- Standard WebSocket protocol
- Full control over implementation
- Minimal dependencies

**Cons:**
- No automatic reconnection
- Manual room management
- No fallback for restricted networks
- More development effort required

### Option 3: Server-Sent Events (SSE)

**Architecture:**
```
Browser EventSource → Express SSE Endpoint → Database
```

**Pros:**
- Simple HTTP-based protocol
- Automatic reconnection
- No WebSocket firewall issues
- Easy to implement

**Cons:**
- Unidirectional (server → client only)
- No binary data support
- Limited browser support
- Cannot send client → server messages

## Decision Outcome

**Chosen Option**: Socket.IO + Redis Pub/Sub

### Justification

Socket.IO provides the best balance of reliability, scalability, and developer experience:

1. **Reliability**: Automatic reconnection with exponential backoff
2. **Scalability**: Redis adapter enables multi-server synchronization
3. **Developer Experience**: Clean API with TypeScript support
4. **Browser Compatibility**: Fallback to long-polling for restricted networks
5. **Production Ready**: Battle-tested in high-traffic applications

### Implementation Details

#### Server Setup

**WebSocket Server** (`/src/websocket/server.ts`):
```typescript
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createRedisClient } from './redis/pubsub';

export function createWebSocketServer(httpServer: Server) {
  const io = new Server(httpServer, {
    cors: {
      origin: process.env.CORS_ORIGIN,
      credentials: true,
    },
    transports: ['websocket', 'polling'],
  });

  // Redis adapter for multi-server sync
  const pubClient = createRedisClient();
  const subClient = pubClient.duplicate();
  io.adapter(createAdapter(pubClient, subClient));

  // Authentication middleware
  io.use(async (socket, next) => {
    const token = socket.handshake.auth.token;
    try {
      const user = await verifyToken(token);
      socket.data.user = user;
      next();
    } catch (error) {
      next(new Error('Authentication failed'));
    }
  });

  return io;
}
```

**Event Handlers** (`/src/websocket/events/leaderboardEvents.ts`):
```typescript
import { Server, Socket } from 'socket.io';

export function registerLeaderboardEvents(io: Server, socket: Socket) {
  // Subscribe to leaderboard updates
  socket.on('leaderboard:subscribe', async () => {
    socket.join('leaderboard:global');

    // Send initial data
    const leaderboard = await getLeaderboard();
    socket.emit('leaderboard:initial', leaderboard);
  });

  // Unsubscribe from updates
  socket.on('leaderboard:unsubscribe', () => {
    socket.leave('leaderboard:global');
  });
}

// Broadcast leaderboard update to all subscribers
export function broadcastLeaderboardUpdate(io: Server, update: LeaderboardUpdate) {
  io.to('leaderboard:global').emit('leaderboard:update', update);
}
```

**Redis Pub/Sub** (`/src/websocket/redis/pubsub.ts`):
```typescript
import { createClient } from 'redis';

export const CHANNELS = {
  LEADERBOARD_UPDATE: 'leaderboard:update',
  MATCH_RESULT: 'match:result',
  PLAYER_ONLINE: 'player:online',
};

export function createRedisClient() {
  return createClient({
    url: process.env.REDIS_URL,
    socket: {
      reconnectStrategy: (retries) => Math.min(retries * 50, 500),
    },
  });
}

// Publish event to all servers
export async function publishEvent(channel: string, data: any) {
  const redis = createRedisClient();
  await redis.connect();
  await redis.publish(channel, JSON.stringify(data));
  await redis.disconnect();
}

// Subscribe to events from all servers
export async function subscribeToChannel(
  channel: string,
  handler: (data: any) => void
) {
  const redis = createRedisClient();
  await redis.connect();
  await redis.subscribe(channel, (message) => {
    handler(JSON.parse(message));
  });
}
```

#### Client Setup

**React Hook** (`/src/hooks/useWebSocketSync.ts`):
```typescript
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export function useWebSocketSync(token: string | null) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!token) return;

    const newSocket = io(process.env.VITE_WS_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    newSocket.on('connect', () => setConnected(true));
    newSocket.on('disconnect', () => setConnected(false));

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [token]);

  return { socket, connected };
}
```

**Leaderboard Sync** (`/src/hooks/useLeaderboardSync.ts`):
```typescript
export function useLeaderboardSync() {
  const { socket } = useWebSocketSync(token);
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    if (!socket) return;

    // Subscribe to updates
    socket.emit('leaderboard:subscribe');

    // Handle initial data
    socket.on('leaderboard:initial', (data) => {
      setLeaderboard(data);
    });

    // Handle real-time updates
    socket.on('leaderboard:update', (update) => {
      setLeaderboard((prev) => applyUpdate(prev, update));
    });

    return () => {
      socket.emit('leaderboard:unsubscribe');
      socket.off('leaderboard:initial');
      socket.off('leaderboard:update');
    };
  }, [socket]);

  return { leaderboard };
}
```

### Event Types

**Leaderboard Events:**
- `leaderboard:subscribe` - Client subscribes to updates
- `leaderboard:unsubscribe` - Client unsubscribes
- `leaderboard:initial` - Server sends initial data
- `leaderboard:update` - Server broadcasts rank changes
- `leaderboard:player_rank` - Player's rank changed

**Match Events:**
- `match:created` - New match scheduled
- `match:started` - Match begins
- `match:result` - Match completed with result
- `match:cancelled` - Match cancelled

**Player Events:**
- `player:online` - Player connected
- `player:offline` - Player disconnected
- `player:stats_update` - Player stats changed

### Multi-Server Synchronization

**Challenge**: Multiple backend servers need to share real-time events

**Solution**: Redis Pub/Sub acts as message broker

**Flow:**
```
Server 1: Match Result → Redis Publish → All Servers Subscribe
Server 2: Receive Event → Broadcast to Connected Clients
Server 3: Receive Event → Broadcast to Connected Clients
```

**Implementation:**
```typescript
// When match result is submitted
await publishEvent(CHANNELS.MATCH_RESULT, {
  matchId: match.id,
  winnerId: result.winner_id,
  eloChanges: {
    [player1.id]: +25,
    [player2.id]: -25,
  },
});

// All servers receive and broadcast
subscribeToChannel(CHANNELS.MATCH_RESULT, (data) => {
  io.to('leaderboard:global').emit('match:result', data);
});
```

## Consequences

### Positive
- **Real-time Updates**: Sub-second leaderboard synchronization
- **Scalability**: Horizontal scaling with Redis adapter
- **Reliability**: Automatic reconnection and message delivery
- **Developer Experience**: Clean API with TypeScript support
- **Cross-Browser**: Fallback ensures compatibility

### Negative
- **Complexity**: Additional infrastructure (Redis)
- **Resource Usage**: Persistent connections consume memory
- **Debugging**: Real-time issues harder to reproduce

### Performance Characteristics

**Connection Overhead:**
- WebSocket handshake: ~100ms
- Memory per connection: ~10KB
- Max connections per server: ~10,000 (with 8GB RAM)

**Message Latency:**
- Local: <10ms
- Multi-server (Redis): 20-50ms
- Cross-region: 100-300ms

**Throughput:**
- Messages per second: ~50,000 (single server)
- Concurrent connections: ~10,000 (single server)

### Risks and Mitigation

**Risk**: Redis failure breaks real-time sync
**Mitigation**:
- Redis cluster for high availability
- Graceful degradation (polling fallback)
- Monitoring and alerts

**Risk**: Memory exhaustion from connections
**Mitigation**:
- Connection limits per server
- Automatic scaling based on load
- Idle connection timeout

**Risk**: Message storms during peak load
**Mitigation**:
- Rate limiting on event publishing
- Message batching and throttling
- Priority queues for critical events

## Testing Strategy

**Load Testing:**
```typescript
// /src/__tests__/websocket/loadTest.ts
test('handles 1000 concurrent connections', async () => {
  const clients = [];

  for (let i = 0; i < 1000; i++) {
    clients.push(io(WS_URL, { auth: { token } }));
  }

  await waitForConnections(clients);
  expect(clients.every(c => c.connected)).toBe(true);
});
```

**Integration Testing:**
```typescript
test('broadcasts leaderboard update to all subscribers', async () => {
  const client1 = io(WS_URL);
  const client2 = io(WS_URL);

  client1.emit('leaderboard:subscribe');
  client2.emit('leaderboard:subscribe');

  const promise1 = new Promise(resolve => {
    client1.on('leaderboard:update', resolve);
  });
  const promise2 = new Promise(resolve => {
    client2.on('leaderboard:update', resolve);
  });

  broadcastLeaderboardUpdate(io, { type: 'rank_change' });

  await Promise.all([promise1, promise2]);
});
```

## Migration Path

**Phase 1: Basic WebSocket (Completed)**
- Socket.IO server setup
- Authentication middleware
- Basic event handlers

**Phase 2: Redis Integration (Completed)**
- Redis Pub/Sub setup
- Multi-server synchronization
- Event broadcasting

**Phase 3: Client Integration (Completed)**
- React WebSocket hooks
- Leaderboard synchronization
- Match notifications

**Phase 4: Optimization (Future)**
- Message compression
- Binary protocol for efficiency
- CDN for WebSocket distribution

## Related Decisions
- ADR-003: Authentication Mechanism (JWT for WebSocket auth)
- ADR-006: Caching Strategy (Redis for Pub/Sub)
- ADR-004: Deployment Strategy (multi-server scaling)

## References
- [Socket.IO Documentation](https://socket.io/docs/)
- [Redis Pub/Sub](https://redis.io/docs/manual/pubsub/)
- [Socket.IO Redis Adapter](https://socket.io/docs/v4/redis-adapter/)
- Implementation: `/workspaces/love-rank-pulse/src/websocket/`
- Tests: `/workspaces/love-rank-pulse/src/__tests__/websocket/`
