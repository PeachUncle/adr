# ADR-004: Voice Chat Implementation

## Status

**Accepted** - 2026-01-01

## Context

The game requires real-time voice communication between 4 players for a social experience. Voice chat must:
- Enable conversation during gameplay
- Support individual mute controls
- Offer push-to-talk option
- Work reliably across network conditions
- Not require additional server infrastructure

## Decision Drivers

- **Latency**: Voice should feel real-time (<150ms)
- **Quality**: Clear audio for conversation
- **Reliability**: Handle network variations gracefully
- **Privacy**: Audio not stored on servers
- **Infrastructure**: Minimize server requirements
- **Cost**: No per-minute billing at scale

## Considered Options

### Option 1: WebRTC P2P with Supabase Signaling (Selected)

**Pros**:
- Peer-to-peer: lowest latency, no media server
- No audio storage (privacy)
- Free once connected (no per-minute costs)
- Supabase Realtime handles signaling
- Works with NAT via STUN

**Cons**:
- Mesh topology: 6 connections for 4 players
- TURN needed for restrictive NATs (rare)
- Connection state management complexity

### Option 2: LiveKit (Managed WebRTC)

**Pros**:
- SFU architecture handles any group size
- Built-in quality adaptation
- Managed infrastructure
- Recording capabilities

**Cons**:
- Per-minute pricing at scale
- Additional vendor dependency
- Overkill for 4-player fixed groups
- Higher latency (server relay)

### Option 3: Daily.co

**Pros**:
- Very easy integration
- Good developer experience
- Managed infrastructure

**Cons**:
- Per-minute pricing
- Vendor lock-in
- Black-box implementation
- Less control

### Option 4: Agora

**Pros**:
- Enterprise-grade reliability
- Global infrastructure
- Feature-rich SDK

**Cons**:
- Complex pricing model
- Heavy SDK
- Per-minute costs
- Overkill for small groups

## Decision

**We will use WebRTC peer-to-peer with mesh topology, signaling via Supabase Realtime.**

### Architecture

```
         ┌─────────────────────────────────────┐
         │     Supabase Realtime Channel       │
         │     (room:{roomId}:voice)           │
         │                                     │
         │  Signaling Only:                    │
         │  - SDP Offers/Answers               │
         │  - ICE Candidates                   │
         └─────────────────────────────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
  ┌───────┐         ┌───────┐         ┌───────┐
  │Player │◄───────►│Player │◄───────►│Player │
  │   A   │         │   B   │         │   C   │
  └───┬───┘         └───┬───┘         └───┬───┘
      │                 │                 │
      │                 │                 │
      │            ┌────┴────┐            │
      │            │ Player  │            │
      └───────────►│    D    │◄───────────┘
                   └─────────┘

  Mesh Topology: 6 P2P connections for 4 players
  Audio flows directly between peers (no server)
```

### Signaling Protocol

```typescript
// Join voice channel
channel.send({
  type: 'broadcast',
  event: 'voice:join',
  payload: { peerId: myPeerId }
});

// Exchange SDP offer
channel.send({
  type: 'broadcast',
  event: 'voice:offer',
  payload: { from: myPeerId, to: targetPeerId, sdp: offer }
});

// Exchange SDP answer
channel.send({
  type: 'broadcast',
  event: 'voice:answer',
  payload: { from: myPeerId, to: targetPeerId, sdp: answer }
});

// Exchange ICE candidates
channel.send({
  type: 'broadcast',
  event: 'voice:ice',
  payload: { from: myPeerId, to: targetPeerId, candidate }
});
```

## Rationale

1. **4-Player Limit**: Mesh topology works well for exactly 4 players (6 connections). Larger groups would need SFU.

2. **Supabase Integration**: Already using Supabase Realtime for game state. Voice signaling uses same infrastructure.

3. **Cost**: No per-minute fees. Only signaling messages through Supabase (minimal).

4. **Privacy**: Audio never touches our servers. Direct peer-to-peer.

5. **Latency**: P2P provides lowest possible latency for voice.

## Consequences

### Positive
- Zero media server costs
- Lowest latency possible
- Audio privacy (P2P only)
- No vendor lock-in
- Scales with Supabase

### Negative
- Mesh doesn't scale beyond 4-6 users
- Some NAT configurations require TURN
- Connection management complexity
- No recording capability

### Mitigations

| Issue | Mitigation |
|-------|------------|
| Symmetric NAT | Use Google STUN; fallback to TURN if needed |
| Connection failures | Reconnection logic with exponential backoff |
| Audio quality | Opus codec with adaptive bitrate |
| Debugging | Log ICE connection states |

## Technical Implementation

### Dependencies

```json
{
  "simple-peer": "^9.11.1"
}
```

### Peer Manager

```typescript
// src/lib/voice/peer-manager.ts
class VoicePeerManager {
  private peers: Map<string, SimplePeer>;
  private localStream: MediaStream | null;

  async initialize() {
    this.localStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      },
      video: false
    });
  }

  createPeer(targetId: string, initiator: boolean) {
    const peer = new SimplePeer({
      initiator,
      stream: this.localStream,
      config: {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' }
        ]
      }
    });

    peer.on('signal', (data) => this.sendSignal(targetId, data));
    peer.on('stream', (stream) => this.handleRemoteStream(targetId, stream));
    peer.on('close', () => this.handlePeerClose(targetId));

    this.peers.set(targetId, peer);
    return peer;
  }

  mute(targetId: string) { /* ... */ }
  setVolume(targetId: string, volume: number) { /* ... */ }
  togglePushToTalk(enabled: boolean) { /* ... */ }
}
```

### UI Components

```typescript
// Mute controls per player
<VoiceControls>
  <MuteButton peerId={player.id} />
  <VolumeSlider peerId={player.id} />
  <SpeakingIndicator peerId={player.id} />
</VoiceControls>

// Push-to-talk toggle
<PushToTalkToggle
  enabled={settings.pushToTalk}
  onToggle={handleToggle}
/>
```

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome 74+ | Full |
| Firefox 66+ | Full |
| Safari 14.1+ | Full |
| Edge 79+ | Full |
| Mobile Chrome | Full |
| Mobile Safari | Full |

## Related Decisions

- ADR-001: Real-time Architecture (signaling channel)
- ADR-002: 3D Rendering (voice indicator UI)
