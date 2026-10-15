# ADR-003: TCP/UDP Protocol Split

**Status:** Accepted
**Date:** 2024-10 (Initial protocol design)
**Updated:** 2025-11-11
**Deciders:** Development Team, Network Engineer
**Related Issues:** #11 (Network monitoring)
**Related Views:** `view-integration.md`, `view-data.md`

---

## Context

DPM-V2 requires two types of communication between Air-Side and Ground-Side:

1. **Commands** (user-initiated actions):
   - Camera capture
   - Property changes (ISO, shutter speed, aperture)
   - System queries
   - **Requirements:** Reliable delivery, guaranteed response, error handling
   - **Frequency:** Sporadic (user-triggered, <1/sec average)
   - **Criticality:** HIGH (failed command = user frustration)

2. **Status Updates** (continuous monitoring):
   - System telemetry (CPU, memory, temperature)
   - Camera state (connected, properties, battery)
   - Network statistics
   - **Requirements:** Real-time, low latency, acceptable packet loss
   - **Frequency:** Continuous (5Hz = 200ms interval)
   - **Criticality:** MEDIUM (single lost packet acceptable, next update in 200ms)

**Network Environment:**
- R16 wireless data link: 20-50 Mbps, 20-50ms latency
- Occasionally lossy (WiFi interference, distance)
- Must support both production (R16) and development (WiFi) networks

**Design Question:** Use same protocol for commands and status, or split them?

---

## Decision

**We will use a split protocol design:**

1. **TCP for Commands** (Port 5000)
   - Long-lived bidirectional connection
   - JSON request/response
   - Sequence ID correlation
   - 5-second timeout
   - Error responses with codes

2. **UDP for Status Broadcast** (Port 5001)
   - Unidirectional (Air → Ground/Tools)
   - Fire-and-forget (no acknowledgment)
   - Fixed 5Hz rate (200ms interval)
   - Sequence number (detect loss, for diagnostics only)

3. **UDP for Heartbeat** (Port 5002)
   - Bidirectional (Air ↔ Ground ↔ Tools)
   - 1Hz rate
   - 10-second timeout → triggers reconnect
   - Connection health monitoring

**Rationale:** Match transport protocol to communication pattern characteristics

---

## Protocol Specifications

### TCP Command Channel (Port 5000)

**Command Message:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "iso",
      "value": "400"
    }
  }
}
```

**Response Message:**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1234,
  "timestamp": 1698765435,
  "payload": {
    "status": "success",
    "result": {
      "property": "iso",
      "value": "400"
    }
  }
}
```

**Error Response:**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1234,
  "timestamp": 1698765435,
  "payload": {
    "status": "error",
    "error_code": "CAMERA_NOT_CONNECTED",
    "error_message": "Camera is not connected, cannot set property"
  }
}
```

**Characteristics:**
- **Reliable:** TCP retransmits lost packets
- **Ordered:** Responses arrive in order
- **Stateful:** Connection tracks session
- **Blocking:** Client waits for response (with timeout)

---

### UDP Status Broadcast (Port 5001)

**Status Message:**
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 5678,
  "timestamp": 1698765434,
  "payload": {
    "system": {
      "cpu_percent": 18.5,
      "memory_mb": 147,
      "disk_gb": 235,
      "temperature_c": 45.2,
      "uptime_seconds": 3600
    },
    "camera": {
      "connected": true,
      "model": "ILCE-1",
      "mode": "M",
      "iso": "400",
      "aperture": "5.6",
      "shutter_speed": "1/250",
      "focus_mode": "AF-S",
      "battery_percent": 78
    },
    "network": {
      "packets_sent": 1500,
      "packets_received": 3200,
      "errors": 0
    }
  }
}
```

**Characteristics:**
- **Lossy:** Lost packets NOT retransmitted
- **Unordered:** May arrive out of sequence
- **Stateless:** Each packet independent
- **Non-blocking:** No acknowledgment, no waiting

---

### UDP Heartbeat (Port 5002)

**Heartbeat Message:**
```json
{
  "protocol_version": "1.1.0",
  "message_type": "heartbeat",
  "sequence_id": 42,
  "timestamp": 1698765434,
  "payload": {
    "sender": "ground",
    "client_id": "H16",
    "uptime_seconds": 3600
  }
}
```

**Characteristics:**
- **Bidirectional:** Both Air and Ground send heartbeats
- **Fixed Rate:** 1Hz (every second)
- **Timeout Detection:** No heartbeat for 10 seconds → connection lost
- **Lightweight:** ~100 bytes per packet

---

## Alternatives Considered

### Alternative 1: TCP for Everything

**Approach:** Use TCP for both commands and status updates

**Status Broadcast Implementation:**
```
Air-Side: Send status via TCP every 200ms
Ground-Side: Read from TCP socket continuously
```

**Pros:**
- Single protocol, simpler implementation
- Guaranteed delivery of all status updates
- No packet loss

**Cons:**
- ❌ **Head-of-Line Blocking:** Lost packet blocks ALL subsequent packets until retransmit
  - Example: Packet 100 lost → Packets 101-110 delayed even if received
  - Result: Status display freezes for seconds (unacceptable for real-time UI)
- ❌ **TCP Overhead:** Acknowledgments, flow control, congestion control add latency
- ❌ **Bandwidth Waste:** Retransmitting stale status (e.g., 5 seconds old) pointless
- ❌ **Buffer Bloat:** TCP buffers accumulate during congestion → stale data shown

**Rejection Reason:** Real-time status display cannot tolerate head-of-line blocking. Next status in 200ms makes retransmission of old status wasteful.

---

### Alternative 2: UDP for Everything

**Approach:** Use UDP for both commands and status

**Command Implementation:**
```
Air-Side: Receive command via UDP, send response via UDP
Ground-Side: Implement retry logic (resend if no response in 1 second)
```

**Pros:**
- Single protocol, no head-of-line blocking
- Low latency for all communication

**Cons:**
- ❌ **Reliability Complexity:** Must reimplement TCP features (retransmission, ordering, deduplication)
- ❌ **Application-Layer Retries:** Ground-Side must detect timeouts and retry
  - What if response lost but command succeeded? (e.g., capture triggered twice)
- ❌ **Idempotency Required:** Commands must be safe to retry (hard for some operations)
- ❌ **Error Handling:** Must distinguish "no response" from "error response lost"

**Rejection Reason:** "Don't reimplement TCP poorly." Commands need reliability → use TCP.

---

### Alternative 3: Single Multiplexed Protocol

**Approach:** Custom protocol over single TCP connection with message type field

**Message Format:**
```json
{
  "type": "command|status|heartbeat",
  "payload": {...}
}
```

**Pros:**
- Single connection, single port
- Type field allows different handling per message

**Cons:**
- ❌ **Still Has Head-of-Line Blocking:** TCP blocks all messages if one packet lost
- ❌ **Complexity:** Must implement framing (where does one message end, next begin?)
- ❌ **Status Broadcast Blocked:** Continuous 5Hz status stream clogs TCP pipeline
  - Commands must wait for status messages to drain from buffer
- ❌ **Not Standard:** Custom protocol harder to debug than standard TCP/UDP

**Rejection Reason:** Doesn't solve fundamental TCP head-of-line blocking issue. Adds framing complexity.

---

### Alternative 4: HTTP/WebSocket

**Approach:** REST API (HTTP) for commands, WebSocket for status stream

**Pros:**
- Standard protocols, many libraries
- HTTP debugging tools (curl, Postman)
- WebSocket provides bidirectional stream

**Cons:**
- ❌ **Overhead:** HTTP headers large (~200 bytes), wasteful for small commands
- ❌ **Complexity:** Requires HTTP server on Air-Side (added dependency)
- ❌ **WebSocket Still TCP:** Doesn't solve head-of-line blocking for status
- ❌ **Overkill:** Don't need HTTP features (routing, headers, cookies, compression)

**Rejection Reason:** Too heavyweight for simple embedded system. HTTP overhead not justified.

---

## Consequences

### Positive

✅ **Optimal for Use Case:** Each protocol matches communication pattern
- Commands: TCP reliability prevents user frustration (failed commands)
- Status: UDP low latency prevents UI lag (real-time display)
- Heartbeat: UDP lightweight connection monitoring

✅ **Real-Time Status Display:** No head-of-line blocking
- Lost status packet → UI shows previous value for 200ms, then updated
- No multi-second freezes
- User experience: smooth, responsive UI

✅ **Command Reliability:** TCP ensures commands executed
- User clicks capture → guaranteed camera triggers (or error message)
- Property changes confirmed before UI updates
- Error responses always delivered

✅ **Network Efficiency:**
- No retransmission of stale status data
- Commands use reliable channel, status uses efficient channel
- Bandwidth usage optimized: ~10KB/sec typical (5Hz × 1KB + sporadic commands)

✅ **Debugging Simplicity:** Standard protocols
- Wireshark can capture and analyze TCP/UDP traffic
- netcat can send test commands (`nc 10.0.1.53 5000`)
- SystemTools can monitor packets without custom protocol parsing

✅ **Independent Scaling:**
- Increase status rate (5Hz → 10Hz) without affecting command reliability
- Add more status fields without command protocol changes
- Protocols version independently

---

### Negative

⚠️ **UDP Packet Loss:** Status updates may be lost
- **Mitigation:** High broadcast rate (5Hz) → loss doesn't matter, next update in 200ms
- **Mitigation:** Sequence numbers allow detection (for diagnostics, not functional requirement)
- **Measured Loss:** <0.1% on local network, <2% on R16 link (acceptable)

⚠️ **Dual Protocol Complexity:** Must implement both TCP and UDP
- **Impact:** Air-Side: 2 network threads (TCP server, UDP broadcaster)
- **Impact:** Ground-Side: 2 clients (TcpCommandClient, UdpStatusListener)
- **Mitigation:** Standard socket APIs, well-documented patterns

⚠️ **Port Management:** Three ports required (5000, 5001, 5002)
- **Mitigation:** Static port assignment, documented in INTEGRATION_POINTS.md
- **Mitigation:** Firewall rules straightforward (3 rules)

⚠️ **Out-of-Order Status:** UDP packets may arrive out of order
- **Example:** Packet 100 arrives after packet 101 → shows old value briefly
- **Mitigation:** Sequence ID allows Ground-Side to discard older packets
- **Mitigation:** High rate (5Hz) means out-of-order window is <200ms

⚠️ **Command/Status Desync:** Command may succeed but UI not updated until next status
- **Example:** Set ISO=400 → TCP response "success" → UI shows old value until next UDP status
- **Mitigation:** Ground-Side optimistically updates UI on command success (don't wait for status)
- **Mitigation:** Next status (200ms) confirms change

---

## Performance Characteristics

**Measured Latency:**
- TCP Command Round-Trip: 20-30ms typical (WiFi), 30-50ms (R16)
- UDP Status One-Way: 5-15ms typical (WiFi), 15-30ms (R16)
- Heartbeat Round-Trip: 10-20ms typical

**Bandwidth Usage:**
- Status Broadcast: 5KB/sec (5Hz × 1KB)
- Commands: <1KB/sec average (sporadic)
- Heartbeat: 0.1KB/sec (1Hz × 100B)
- **Total:** <10KB/sec typical, <50KB/sec peak

**Packet Loss Impact:**
- Status: Single lost packet → 200ms stale data (negligible)
- Command: Never lost (TCP retransmits)
- Heartbeat: 1 lost packet OK (timeout requires 10 consecutive losses)

---

## Implementation Notes

**Air-Side Threading Model:**
- Thread 1: TCP accept loop (waits for connections)
- Thread 2: TCP command handler (processes incoming commands, sends responses)
- Thread 3: UDP status broadcaster (5Hz timer, broadcasts current state)
- Thread 4: UDP heartbeat handler (1Hz send, continuous receive)

**Ground-Side Coroutines:**
- TcpCommandClient: Suspending functions for send/receive
- UdpStatusListener: Background coroutine collecting status
- HeartbeatClient: Background coroutine for bidirectional heartbeat

**Network Configuration:**
- Air-Side IP: 10.0.1.53 (development), 192.168.144.53 (production R16)
- Ground-Side IP: 10.0.1.92 (development), 192.168.144.92 (production R16)
- Dev-Tools IP: 10.0.1.x (various workstations)

---

## Future Enhancements

**Considered for Phase 2:**
- **TLS for TCP:** Encrypt command channel (low priority, closed network)
- **DTLS for UDP:** Encrypt status broadcast (low priority)
- **Protocol Versioning:** Negotiation for backward compatibility
- **Compression:** Reduce bandwidth (not needed, <10KB/sec sufficient)
- **Multicast UDP:** Support multiple Ground-Side listeners (not needed yet)

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (explains network communication necessity)
- **ADR-009:** UDP Status Broadcast Rate (5Hz) (why 200ms interval)
- **ADR-011:** JSON-over-TCP/UDP Protocol (message format design)
- **ADR-014:** Auto-Reconnect Strategy (handling TCP/UDP failures)

---

## References

- Integration View: `docs/architecture/view-integration.md` (Protocol patterns section)
- Data View: `docs/architecture/view-data.md` (Data flow diagrams)
- Integration Points: `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` (Full protocol specs)
- LESSONS_LEARNED.md: Network & Communication section
- Issue #11: Network monitoring and packet analysis (SystemTools)
