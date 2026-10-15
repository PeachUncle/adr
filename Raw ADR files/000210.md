# ADR-002: WebRTC Signaling Through Socket.IO

**Status:** Accepted  
**Date:** 2025-07-01  
**Deciders:** Development Team  

## Context

Real-time voice communication requires WebRTC for peer-to-peer audio transmission. However, WebRTC needs a signaling channel to exchange connection information (offers, answers, ICE candidates) between peers before the direct connection can be established.

Options for signaling channel:
1. **Socket.IO over existing connection**
2. **Separate REST API endpoints**
3. **WebSocket with custom protocol**
4. **Third-party signaling service**

## Decision

We will use **Socket.IO over our existing connection** for WebRTC signaling.

## Rationale

### Reuse Existing Infrastructure
- **Single connection**: Leverage existing Socket.IO connection for customer-agent communication
- **Consistent protocol**: Same event-driven pattern for all real-time communication
- **Simplified architecture**: No additional signaling service needed

### Real-time Performance
- **Low latency**: Socket.IO already optimized for real-time communication
- **Reliable delivery**: Built-in acknowledgments and error handling
- **Automatic fallbacks**: WebSocket with polling fallback for network issues

### Development Efficiency
- **Familiar patterns**: Team already using Socket.IO for other features
- **Unified debugging**: All real-time events in one place
- **Easier testing**: Single protocol to mock/test

## Consequences

### Positive
- ✅ Leverages existing infrastructure and knowledge
- ✅ Consistent event-driven architecture throughout
- ✅ Built-in reliability and fallback mechanisms
- ✅ Simplified deployment (one protocol, one port)

### Negative
- ⚠️ Tight coupling between signaling and application logic
- ⚠️ Socket.IO overhead for simple signaling messages
- ⚠️ All communication depends on single connection

## Implementation

```typescript
// Client side - Customer Interface
socket.on('offer', async ({ offer }) => {
  const answer = await webrtcService.current.createAnswer(offer);
  socket.sendAnswer(answer, 'agent');
});

socket.on('ice-candidate', async ({ candidate }) => {
  await webrtcService.current.addIceCandidate(candidate);
});

// Server side - Route between customer and agent
socket.on('offer', ({ offer, targetUserId }) => {
  io.to(targetUserId).emit('offer', { offer, userId: socket.id });
});
```

## Alternatives Considered

### Alternative: Dedicated Signaling API

**Approach:** Separate REST endpoints for WebRTC signaling.

**Benefits:**
- Decoupled from application logic
- Could be cached/optimized separately
- Protocol-agnostic

**Drawbacks:**
- Additional latency (HTTP request/response vs real-time)
- More complex error handling
- Doesn't fit real-time use case well

### Alternative: Third-party Service (Twilio, Agora)

**Benefits:**
- Professional-grade signaling
- Global infrastructure
- Built-in scaling

**Drawbacks:**
- Additional cost and complexity
- External dependency
- Less control over implementation

**Verdict:** Rejected for this phase; could be reconsidered for scaling

## Review Criteria

This decision should be reviewed if:
- Signaling latency becomes a bottleneck
- Socket.IO connection reliability issues emerge
- Need to support federation with external systems
- Scale requires dedicated signaling infrastructure

---

**Related:** ADR-001 (Persistent Connections), ADR-003 (Port Configuration)
