# ADR-001: Persistent Socket Connections for Customer Interface

**Status:** Accepted  
**Date:** 2025-07-01  
**Deciders:** Development Team  

## Context

The Mulisa customer interface needs to manage socket connections for real-time communication with the signaling server. When a customer ends a call, we needed to decide whether to:

1. **Maintain persistent connection** and keep socket open with an "idle" state
2. **Disconnect/reconnect** pattern where socket is closed after each call

This decision directly impacts user experience, server resource usage, and code complexity.

## Decision

We will **maintain persistent socket connections** with an "idle" state for customers between calls.

## Rationale

### Performance Benefits
- **Faster subsequent calls**: No connection handshake delay (~200-500ms saved)
- **Immediate responsiveness**: Button enables instantly after call ends
- **No loading states**: Users don't see "Connecting..." between multiple calls

### User Experience
- **Professional feel**: Instant responsiveness expected in customer service
- **Multiple call scenarios**: Customers often need follow-up calls
- **Real-time updates**: Server can push agent availability notifications

### Server Efficiency
- **Resource optimization**: Server maintains customer context/session
- **Queue management**: Can track customer position in queue
- **Load balancing**: Better distribution of connection overhead

## Consequences

### Positive
- ✅ Superior performance for repeat calls
- ✅ Better UX with instant call initiation
- ✅ Enables real-time features (queue updates, agent availability)
- ✅ More professional/enterprise-grade feel

### Negative
- ⚠️ More complex state management (multiple connection + call states)
- ⚠️ More edge cases to handle (connection loss during idle state)
- ⚠️ Slightly higher server memory usage (persistent connections)
- ⚠️ More debugging complexity (multi-state system)

## Alternatives Considered

### Alternative: Disconnect/Reconnect Pattern

**Approach:** Disconnect socket after each call, reconnect when requesting new call.

**Benefits:**
- Simpler state management
- Clean slate for each call
- Lower server resource usage
- Easier debugging

**Drawbacks:**
- 200-500ms delay for each call
- More network overhead (TCP handshake + WebSocket upgrade)
- Lost server context between calls
- Less professional user experience

**Verdict:** Rejected due to performance and UX concerns for customer service use case.

## Implementation Details

```typescript
// Connection states: 'disconnected' | 'connecting' | 'connected'
// Call states: 'idle' | 'requesting' | 'waiting' | 'ringing' | 'connected'

// When ending call:
const endCall = () => {
  socketService.current.emit('customer-end-call');
  webrtcService.current?.cleanup(); // Only clean WebRTC
  setCallState('idle'); // Return to idle, keep socket connected
};

// Automatic reconnection on disconnect:
socket.on('disconnect', () => {
  setConnectionState('disconnected');
  if (callState !== 'idle') {
    setCallState('idle');
    // Clean up and show reconnection UI
  }
});
```

## Review Date

This decision should be reviewed if:
- User patterns show infrequent repeat calls
- Server resource constraints become an issue
- Significant connection reliability problems emerge
- Mobile usage patterns change the cost/benefit analysis

---

**Related:** ADR-002 (WebRTC Signaling), ADR-003 (Port Configuration)
