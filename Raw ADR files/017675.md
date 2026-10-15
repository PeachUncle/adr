---
type: DRR
winner_id: per-channel-relay-in-rust-user-proposed
created: 2025-12-24T08:58:09-08:00
content_hash: 67852dd02fec64d0c5d9849a8dc3de96
---

# v0.4 Relay Architecture: Rust Per-Channel with Python Orchestrator

## Context
SpeedData v0.4 requires porting the Python relay (rowdog) to a compiled language to achieve 10Mbps-100Gbps performance range across platforms from Raspberry Pi to Xeon servers. The relay must handle UDP multicast receive, AVRO file writing, and dual-rate multicast relay (full + decimated). Design space included process models (monolithic vs per-channel), I/O strategies (stdio vs io_uring vs O_DIRECT), and language choices (Rust, Zig, C, C++20).

## Decision
**Selected Option:** per-channel-relay-in-rust-user-proposed

Adopt Rust-based per-channel relay architecture with Python orchestrator for lifecycle management. Each channel runs as isolated Rust process using tokio async runtime for UDP/disk/multicast operations. Standard async I/O (no io_uring initially). Python manages process fleet via configuration-driven spawning.

## Rationale
User explicitly requested "Rust and process per channel" combination. This architecture balances multiple priorities:

**Alignment with constraints:**
- Supports full platform range (Raspberry Pi to Xeon, Linux/macOS)
- Requires only kernel 3.10+ via tokio (user accepted 5.10+ modernization)
- Service-oriented architecture preserved (Python orchestrator)
- Learning curve acceptable (user has Rust tutorial experience, willing to learn)

**Technical strengths:**
- Fault isolation: channel process crash doesn't affect others
- Memory safety: Rust borrow checker prevents common C bugs
- Performance headroom: tokio proven to 40Gbps (~1M pkt/s), sufficient for initial target
- Incremental scaling: can add io_uring later if 100Gbps needed without architectural rework
- Ecosystem maturity: tokio production-proven (Discord, AWS, Cloudflare)

**Risk mitigation:**
- Lower complexity than monolithic io_uring (6-12 month timeline avoided)
- Higher stability than bleeding-edge XDP (rejected in Phase 2)
- Better fault isolation than C++20 threads (shared memory risks)
- More familiar ecosystem than Zig (smaller community)
- Safer than C stdio (memory safety without performance ceiling)

**Rejected conservative alternative:**
C stdio would minimize risk but caps at ~5Gbps, requiring future rewrite. Since user willing to learn and tokio proven, incremental approach (C → Rust later) introduces double migration cost.

**Weakest link:** User Rust proficiency (tutorial-level). Mitigated by: tokio extensive documentation, active community, async/await similar to other languages, can prototype single channel first.

### Characteristic Space (C.16)
- **Process Model:** One Rust process per channel (fault isolation)
- **Language:** Rust 1.70+ (memory safety + performance)
- **Async Runtime:** tokio (proven, 40Gbps capable)
- **I/O Strategy:** tokio async I/O (upgrade to io_uring preservable)
- **Orchestration:** Python lifecycle manager (config-driven)
- **Portability:** Linux/macOS, kernel 3.10+
- **Performance Tier:** 10-40Gbps (sufficient for v0.4 targets)
- **Fault Model:** Isolated failures (channel crash doesn't cascade)
- **Learning Curve:** Medium (user has tutorials, tokio well-documented)

## Consequences
**Immediate (v0.4):**
- Implement Rust relay binary with tokio UDP/file/multicast
- Python orchestrator reads channel configs, spawns/monitors relay processes
- Learning investment: async Rust, tokio ecosystem (~2-4 weeks initial)
- Performance target: 10-40Gbps range (covers Pi to mid-range servers)

**Future options preserved:**
- io_uring upgrade path: tokio-uring crate integrates cleanly if 100Gbps needed
- Process model validated: can reuse orchestrator if monolithic needed later
- Language investment: Rust skills transfer to other SpeedData components

**Technical debt accepted:**
- Initial implementation uses tokio async I/O (not zero-copy io_uring)
- macOS support included (may drop post-v1.0 if unused)
- User proficiency ramp-up time vs immediate C implementation

**Dependencies:**
- Rust toolchain (rustc 1.70+, cargo)
- tokio runtime library
- Python 3.8+ for orchestrator
- AVRO Rust bindings (apache-avro crate)

**Migration path from Python rowdog:**
1. Implement single-channel Rust relay (parity with current)
2. Add Python orchestrator (spawn/monitor)
3. Test with example.sine_wave channel
4. Iterate on remaining channels
5. Deprecate Python relay when all channels migrated
