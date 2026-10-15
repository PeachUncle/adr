# ADR-011: JSON-over-TCP/UDP Protocol

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** All integration issues
**Related Views:** `view-integration.md`, `view-data.md`

---

## Context

Air-Side, Ground-Side, and Dev-Tools must communicate. Questions:
1. What data format for messages?
2. Human-readable or binary?
3. Standardized or custom?

**Requirements:**
- Cross-language (C++, Kotlin, Python must all parse)
- Debuggable (inspect packets with tools)
- Extensible (add fields without breaking compatibility)
- Efficient enough for 5Hz broadcasting

---

## Decision

**Protocol: JSON over TCP/UDP**

**Message Structure:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command|response|status|heartbeat|notification",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": { ... }
}
```

**Encoding:** UTF-8, compact (no pretty-printing)

**Transport:** Raw JSON strings (no framing beyond TCP/UDP)

---

## Alternatives Considered

### Alternative 1: Protocol Buffers (protobuf)

**Pros:**
- Binary format (smaller messages)
- Schema definition (.proto files)
- Versioning support

**Cons:**
- ❌ Not human-readable (can't inspect with Wireshark plaintext)
- ❌ Requires protobuf compiler (build complexity)
- ❌ C++/Kotlin/Python all need protobuf libraries (dependencies)
- ❌ Schema changes require recompilation

**Rejection:** Human-readability important for debugging. JSON sufficient for our bandwidth (<10KB/sec).

---

### Alternative 2: MessagePack

**Pros:**
- Binary JSON (smaller than JSON text)
- Faster parsing than JSON

**Cons:**
- ❌ Not human-readable
- ❌ Requires MessagePack libraries
- ❌ Less ubiquitous than JSON (harder to debug)

**Rejection:** JSON parsing fast enough (<1ms). Human-readability more valuable than marginal speed gain.

---

### Alternative 3: Custom Binary Protocol

**Pros:**
- Maximum efficiency
- Exact fields we need

**Cons:**
- ❌ Must implement parser in 3 languages (C++/Kotlin/Python)
- ❌ Fragile (byte alignment, endianness)
- ❌ Hard to debug (hex dump analysis)
- ❌ Versioning difficult

**Rejection:** "Don't roll your own protocol." JSON is battle-tested.

---

### Alternative 4: XML

**Pros:**
- Human-readable
- Schema validation (XSD)

**Cons:**
- ❌ Verbose (10× larger than JSON)
- ❌ Slower to parse
- ❌ Overkill for simple messages

**Rejection:** JSON more concise and faster.

---

## Consequences

### Positive

✅ **Debuggable:** Wireshark shows plaintext JSON
✅ **Cross-Language:** Libraries in all languages (nlohmann/json C++, Gson/Kotlin, json Python)
✅ **Extensible:** Add fields without breaking parsers (ignore unknown fields)
✅ **Tooling:** curl, netcat, Postman can send test messages
✅ **Human-Readable:** Logs show actual message content

### Negative

⚠️ **Larger Messages:** JSON text ~2× size of binary (~1KB vs ~500B)
- Mitigation: Still <10KB/sec total, negligible on 20Mbps link

⚠️ **Parsing Overhead:** JSON parsing ~0.5-1ms
- Mitigation: Acceptable, not performance bottleneck

⚠️ **No Schema Enforcement:** Malformed JSON accepted by parsers
- Mitigation: Validate required fields in application code

---

## Message Examples

### Command (Ground → Air)

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

### Response (Air → Ground)

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

### Status Broadcast (Air → Ground, 5Hz)

```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 5678,
  "timestamp": 1698765434,
  "payload": {
    "system": {"cpu_percent": 18.5, "memory_mb": 147},
    "camera": {"connected": true, "iso": "400", "aperture": "5.6"}
  }
}
```

---

## Protocol Versioning

**Version Field:** `protocol_version` in every message

**Compatibility:**
- Minor version (1.0 → 1.1): Backward compatible (add optional fields)
- Major version (1.x → 2.x): Breaking changes (new parsers required)

**Future:** Version negotiation handshake (not yet implemented)

---

## Related Decisions

- **ADR-003:** TCP/UDP Protocol Split (JSON is payload format)
- **ADR-002:** Specification-First (property specs also in JSON)
- **ADR-010:** PropertyLoader Pattern (same JSON parsing libraries)

---

## References

- Integration View: `view-integration.md` (Complete protocol specs)
- Data View: `view-data.md` (JSON message protocol section)
- INTEGRATION_POINTS.md: Full message format examples
