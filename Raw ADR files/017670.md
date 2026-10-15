---
type: DRR
winner_id: preset-schema-with-file-based-registration
created: 2025-12-23T09:50:18-08:00
content_hash: 1cc561bb267a553d8e5f3e757c795d1f
---

# SpeedData Wire Encoding: AVRO with Preset Schemas and File-Based Configuration

## Context
## Problem Context

SpeedData requires a wire encoding format for UDP packets transmitted from remote agents (microcontrollers/embedded systems) to the relay. The encoding must:

- Support high-frequency transmission (5000 Hz channels with 10-100 fields)
- Work within microcontroller hot loop constraints (minimal overhead)
- Handle multi-rate channels (5000 Hz, 100 Hz, 10 Hz, async)
- Support custom data types (enums, bitpacked flags, structs)
- Tolerate UDP packet loss (no stateful compression)
- Be implementable by "barely-programmers" (simple API)
- Support multiple concurrent senders

**Baseline**: Currently using AVRO encoding with naive packing (double timestamp + float sequence). Port-per-channel architecture where each channel receives on dedicated UDP port. One packet per sample constraint for hot loop performance and UDP loss tolerance.

**Triggering Factors**: 
1. Need to evaluate if current "naive packing" is sufficient or needs improvement
2. Determine if preset schemas are feature (simplicity) or bug (inflexibility)
3. Establish registration mechanism for v0.2 (February 2025) - REST deferred to v0.4

**Alternatives Considered**: 5 hypotheses evaluated through FPF process:
- schema-registry-service (rejected at L1: requires network calls, violates hot loop constraint)
- dynamic-avro-container-files (rejected at L1: container overhead per packet unacceptable)  
- protobuf-with-service-discovery (rejected at L1: complex toolchain for MCUs)
- flatbuffers-with-hardcoded-schemas (rejected at L1: larger binary footprint)
- **preset-schema-with-file-based-registration** (PASSED L1, L2, Audit)

**User Vision**: "Super-hybrid" system allowing remote registration, local files, and REST overrides, with port-per-channel architecture where MCUs can hardcode ports.

## Decision
**Selected Option:** preset-schema-with-file-based-registration

**Adopt AVRO binary encoding with preset schemas and file-based registration for SpeedData v0.2 wire encoding.**

## Core Design

**1. Encoding Format**: AVRO binary encoding (schema-aware, compact)
   - Float: 4 bytes little-endian IEEE 754
   - Double: 8 bytes little-endian IEEE 754
   - Variable-length integers: zig-zag encoding
   - Strings/bytes: length prefix + data
   - **No field names in wire format** (schema provides structure)

**2. Schema Management**: File-based configuration at relay
   - Schemas stored in `/config/agents/{agent_id}.avsc` (JSON AVRO schema files)
   - One schema per channel, versioned in repository
   - Relay loads schemas at startup, validates incoming packets against schema

**3. Registration Mechanism**: Zero-registration protocol
   - MCUs hardcode UDP port from deployment config
   - Relay maps UDP port → schema via config file
   - No network registration required (satisfies hot loop constraint)
   - Agent ID prefix in packet payload (1-2 bytes) for disambiguation

**4. Port Architecture**: Port-per-channel (existing baseline)
   - Each channel has dedicated UDP port (ephemeral range 49152-65535)
   - MCU firmware includes hardcoded port constant
   - Relay binds to all configured ports, decodes via schema lookup

**5. Packet Structure**:
   ```
   [Agent ID: varint] [Timestamp: double] [Field1] [Field2] ... [FieldN]
   ```
   - Agent ID: variable-length integer (1-2 bytes typical)
   - Timestamp: 8-byte double (absolute time or offset)
   - Fields: encoded per schema field types

**6. MCU Implementation**: Manual AVRO packing
   - Simple encoding primitives (memcpy for floats/doubles, varint functions)
   - No AVRO library required on MCU (reduces binary size)
   - Schema known at compile-time (no runtime schema parsing)

**7. Relay Implementation**: AVRO-js decoder
   - Load schema from `/config/agents/{agent_id}.avsc`
   - Decode packets using `avro-js` library
   - Validate packet structure, log decode errors
   - Write to AVRO file storage (zero-copy from UDP to disk)

**8. Future Evolution Path** (v0.4, April 2025):
   - Add REST API for schema registration (POST `/config/agents/{id}`)
   - Optional remote registration endpoint for dynamic agents
   - Config file remains authoritative; REST updates config
   - Backward compatible with v0.2 hardcoded ports

## Rationale
## Why This Decision

**1. Meets All Performance Constraints**
   - ✅ Hot loop compatible: Manual AVRO packing is ~10 lines of C code per packet
   - ✅ No network calls in critical path (zero-registration)
   - ✅ Compact encoding: Binary AVRO is competitive with custom protocols
   - ✅ One packet per sample: No container overhead

**2. Validated Against Industry Practice** (L2 Corroboration)
   - ✅ Juniper, Cisco, IBM use file-based UDP port-to-schema mapping
   - ✅ AVRO confirmed in Azure IoT Hub, VMware Telco Cloud (Jan 2025)
   - ✅ Apache AVRO spec confirms manual binary encoding is straightforward
   - ✅ Config-driven registration is proven telemetry pattern

**3. Satisfies "Barely-Programmers" Requirement**
   - ✅ MCU code is simple: pack struct fields into byte buffer
   - ✅ No complex toolchain (Protobuf compiler, FlatBuffers schema compiler)
   - ✅ Schema errors caught at relay (fail-safe design)
   - ✅ Config file format is human-readable JSON

**4. Enables User's "Super-Hybrid" Vision**
   - ✅ File-based registration (v0.2 baseline)
   - ✅ REST registration path clear (v0.4 extension)
   - ✅ Port-per-channel allows MCU hardcoding
   - ✅ Agent ID prefix enables remote registration future-proofing

**5. Manageable Risk Profile** (R_eff = 1.00)
   - Schema evolution: Mitigated by AVRO's default value mechanism
   - Config drift: Mitigated by version control + validation tooling
   - Silent failures: Mitigated by packet count monitoring
   - Port exhaustion: Mitigated by 16K port range (>>typical deployments)

**6. Existing Baseline Alignment**
   - ✅ Already using AVRO (no migration cost)
   - ✅ Port-per-channel already implemented (README line 53)
   - ✅ Per-channel schemas already designed (README line 34)
   - ✅ Preset schemas confirmed as feature, not bug

**7. Reversibility** (2-week undo window)
   - Config files easy to modify (text-based)
   - MCU firmware update cycle determines schema change latency
   - Can add registration service without breaking existing agents
   - File-based config is lowest-commitment starting point

### Characteristic Space (C.16)
## Decision Characteristics

**Type**: Architectural (wire protocol definition)

**Reversibility**: MEDIUM (2-week to 2-month undo window)
- Config changes: immediate (text files)
- MCU firmware rollback: 2-14 days (deployment dependent)
- Schema migration: 1-2 months (requires coordinated update)

**Scope**: SpeedData v0.2 wire encoding, affects:
- Remote agent MCU firmware
- Relay UDP receiver module
- Config file structure
- Deployment procedures

**Stakeholders**:
- MCU developers (encoding implementation)
- Relay operators (config management)
- "Barely-programmers" (simple encoding API)
- System architects (future REST integration)

**Dependencies**:
- `avro-js` library (already in use, v1.12.0)
- Port-per-channel architecture (already implemented)
- AVRO baseline (existing, confirmed in README)

**Risk Level**: MEDIUM
- Technical risk: LOW (validated pattern)
- Operational risk: MEDIUM (config coordination required)
- Reversibility risk: MEDIUM (MCU firmware cycle)

**Time Horizon**: v0.2 (February 2025) baseline, v0.4 (April 2025) extension

**Evidence Quality**: L2 (Corroborated) with R_eff = 1.00
- Logical verification: PASS (no internal contradictions)
- Empirical validation: PASS (industry precedent confirmed)
- Risk audit: PASS (9 risks identified, all mitigated)
- External congruence: CL1-CL2 (commercial telemetry systems)

## Consequences
## Implementation Consequences

### Immediate (v0.2 - February 2025)

**1. Relay Configuration**
   - Create `/config/agents/` directory structure
   - Define `.avsc` schema file format
   - Implement config loader at relay startup
   - Add UDP port → schema mapping table

**2. MCU Library**
   - Implement AVRO binary encoding primitives:
     - `avro_encode_double(buf, val)`
     - `avro_encode_float(buf, val)`
     - `avro_encode_varint(buf, val)`
     - `avro_encode_agent_id(buf, id)`
   - Document encoding patterns for common field types
   - Provide example packet construction code

**3. Validation Tooling**
   - Schema validation: `validate-schema.js` to check `.avsc` files
   - Packet decoder: `decode-packet.js` for debugging MCU payloads
   - Config linter: check port conflicts, agent ID uniqueness

**4. Documentation**
   - "Adding a New Channel" guide for operators
   - MCU encoding cookbook with examples
   - Schema evolution best practices

**5. Monitoring**
   - Per-channel packet rate dashboard
   - Decode error alerting
   - Schema mismatch detection (packet size vs expected size)

### Deferred (v0.4 - April 2025)

**6. REST Registration API**
   ```
   POST /config/agents/{agent_id}
   Body: { "schema": {...}, "port": 50123 }
   ```
   - Writes to `/config/agents/{agent_id}.avsc`
   - Triggers hot-reload of relay config
   - Validates schema before accepting

**7. Remote Registration Protocol**
   - MCU sends registration packet to control port
   - Relay assigns port, responds with assignment
   - MCU switches to assigned port for data transmission
   - Falls back to file-based config if registration fails

### Operational Impact

**8. Deployment Changes**
   - Channel additions require config commit + relay restart (SIGHUP)
   - MCU firmware bundles schema as compile-time constant
   - Port assignments must be coordinated (risk of conflicts)
   - Schema changes require synchronized MCU firmware update

**9. Failure Modes**
   - Invalid schema → relay refuses to start (fail-fast)
   - Missing config → packet dropped, logged (observable)
   - Schema mismatch → decode error, logged (detectable)
   - Port conflict → relay binding error at startup (fail-fast)

**10. Maintenance Burden**
   - Config files must be versioned and reviewed
   - Schema changes require release coordination
   - No runtime schema evolution (requires relay restart)
   - Operational discipline required for config hygiene

### Non-Consequences (Explicitly Out of Scope)

- ❌ Dynamic schema negotiation (deferred to v0.4+)
- ❌ Automatic port assignment (deferred to v0.4+)
- ❌ Stateful compression across packets (violates UDP tolerance)
- ❌ Self-describing packets (violates hot loop constraint)
- ❌ Backward compatibility with non-AVRO formats (AVRO is baseline)
