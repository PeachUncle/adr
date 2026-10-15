# ADR-006: WebSocket Real-Time Architecture

## Status
Accepted

## Date
2024-01-19

## Context

NEURECTOMY requires real-time communication for:
1. **Agent Status Updates**: Live status changes, metrics
2. **Conversation Streaming**: Token-by-token LLM responses
3. **System Notifications**: Alerts, maintenance notices
4. **Collaborative Features**: Multi-user editing (future)

Requirements:
- Low latency (< 100ms)
- Scalable to thousands of concurrent connections
- Reliable message delivery
- Support for channels/topics

## Decision

We will implement a **WebSocket-based real-time system** using:
- **Axum WebSocket**: Server-side WebSocket handling
- **NATS JetStream**: Message distribution and persistence
- **Channel-based routing**: Topic-based message subscription

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         Clients                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Browser │  │   CLI   │  │  Mobile │  │  Other  │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
│       │            │            │            │                   │
│       └────────────┴────────────┴────────────┘                   │
│                         │                                        │
│                    WebSocket                                     │
│                         │                                        │
├─────────────────────────┼────────────────────────────────────────┤
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  WebSocket Manager                        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │   │
│  │  │ Connection │  │ Connection │  │ Connection │  ...     │   │
│  │  │   Pool     │  │   Auth     │  │   Router   │          │   │
│  │  └────────────┘  └────────────┘  └────────────┘          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│                    NATS Pub/Sub                                  │
│                         │                                        │
│  ┌──────────────────────┼──────────────────────────────────┐    │
│  │                 NATS JetStream                           │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │    │
│  │  │ agent.* │  │ user.*  │  │ system.*│  │ chat.*  │    │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Message Protocol
```json
{
  "type": "subscribe|unsubscribe|publish|ping|pong|error",
  "channel": "agent:uuid",
  "payload": { ... },
  "id": "message-uuid",
  "timestamp": 1704067200000
}
```

### Channel Naming Convention
| Pattern | Description | Example |
|---------|-------------|---------|
| `agent:{id}` | Agent-specific updates | `agent:550e8400-e29b-41d4-a716-446655440000` |
| `user:{id}` | User notifications | `user:123e4567-e89b-12d3-a456-426614174000` |
| `conversation:{id}` | Chat messages | `conversation:...` |
| `system` | System-wide broadcasts | `system` |
| `metrics:{agent_id}` | Real-time metrics | `metrics:...` |

## Consequences

### Positive
- **Low Latency**: Direct WebSocket connections
- **Scalability**: NATS handles cross-instance messaging
- **Flexibility**: Channel-based subscription model
- **Reliability**: JetStream provides message persistence
- **Efficiency**: Binary message support when needed

### Negative
- **Complexity**: Additional infrastructure (NATS)
- **State Management**: Connection state must be tracked
- **Reconnection Logic**: Clients need robust reconnection
- **Debugging**: Real-time systems harder to debug

### Mitigations
- Implement connection heartbeats (30s interval)
- Store last N messages for reconnection replay
- Comprehensive logging with correlation IDs
- Health checks for NATS connectivity

## Message Types

### Client → Server
| Type | Purpose | Auth Required |
|------|---------|---------------|
| `authenticate` | Provide JWT token | No |
| `subscribe` | Subscribe to channel | Yes |
| `unsubscribe` | Unsubscribe from channel | Yes |
| `publish` | Send message to channel | Yes |
| `ping` | Keepalive | No |

### Server → Client
| Type | Purpose |
|------|---------|
| `authenticated` | Auth success |
| `subscribed` | Subscription confirmed |
| `unsubscribed` | Unsubscription confirmed |
| `message` | Channel message |
| `error` | Error response |
| `pong` | Keepalive response |

## Alternatives Considered

### 1. Server-Sent Events (SSE)
- ✅ Simpler, HTTP-based
- ✅ Auto-reconnect
- ❌ Unidirectional (server → client only)
- ❌ Less efficient for bidirectional communication

### 2. Long Polling
- ✅ Works everywhere
- ❌ Higher latency
- ❌ More server resources
- ❌ Not truly real-time

### 3. WebSocket Only (No NATS)
- ✅ Simpler architecture
- ❌ Single-instance limitation
- ❌ No message persistence
- ❌ Custom pub/sub implementation needed

## Scaling Considerations

### Horizontal Scaling
```
┌─────────────────────────────────────────────────────────────┐
│                       Load Balancer                          │
│                    (Sticky Sessions)                         │
├───────────────┬───────────────┬───────────────┬─────────────┤
│   Instance 1  │   Instance 2  │   Instance 3  │   ...       │
│  ┌─────────┐  │  ┌─────────┐  │  ┌─────────┐  │             │
│  │   WS    │  │  │   WS    │  │  │   WS    │  │             │
│  │ Manager │  │  │ Manager │  │  │ Manager │  │             │
│  └────┬────┘  │  └────┬────┘  │  └────┬────┘  │             │
│       │       │       │       │       │       │             │
└───────┴───────┴───────┴───────┴───────┴───────┴─────────────┘
                        │
                   NATS Cluster
```

### Connection Limits
| Resource | Limit | Rationale |
|----------|-------|-----------|
| Connections per user | 5 | Prevent resource abuse |
| Subscriptions per connection | 50 | Memory management |
| Message size | 1MB | Network efficiency |
| Messages per second | 100 | Rate limiting |

## References
- [WebSocket RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)
- [NATS Documentation](https://docs.nats.io/)
- [Axum WebSocket](https://docs.rs/axum/latest/axum/extract/ws/index.html)
