---
type: DRR
winner_id: conservative-single-channel-relay-c-stdio-buffering
created: 2025-12-24T09:22:10-08:00
content_hash: cb64614fff5c7213dd8bdb47ffba78ac
---

# v0.4 Relay Architecture: C stdio Per-Channel (Revised)

## Context
SpeedData v0.4 requires porting Python relay (rowdog) to compiled language. Initial analysis assumed monolithic 100Gbps requirement. User clarified: per-channel architecture with 5Gbps per-channel requirement (20 channels × 5Gbps = 100Gbps aggregate). v0.4 target deployment is Raspberry Pi with 1Gbps ethernet (bottleneck). User explicitly dislikes: big libraries, long compile times, async complexity when avoidable.

## Decision
**Selected Option:** conservative-single-channel-relay-c-stdio-buffering

Adopt C99 + stdio per-channel relay architecture. Each channel runs as isolated C process using synchronous I/O (select() for UDP, buffered stdio for disk). Python orchestrator manages process fleet. No async runtime, minimal dependencies, <1s compile time per binary.

## Rationale
**Per-channel performance requirement is 5Gbps, not 100Gbps aggregate:**
- C stdio ceiling (~5Gbps) exactly matches per-channel requirement
- 20 channels × 5Gbps = 100Gbps total throughput achieved via process parallelism
- v0.4 targets Raspberry Pi with 1Gbps ethernet (choke point) — C stdio has 5x headroom

**User constraints favor simplicity:**
- No async needed: per-channel = single UDP socket = synchronous select() loop sufficient
- Fast compile times: C compiles in <1s vs Rust tokio 30-60s
- Minimal dependencies: libc only, no large runtime libraries
- No learning curve: user already knows C

**Architectural benefits:**
- Fault isolation: process boundaries (same as Rust per-channel option)
- Fast startup: no tokio runtime initialization overhead
- Deterministic debugging: synchronous flow, no async state machines
- Per-channel upgradability: can rewrite individual channels to Rust/Zig later if bottleneck identified

**Rejected alternatives:**
- Rust tokio: 8x performance overkill (40Gbps vs 5Gbps need), large library, async complexity, long compiles
- Zig: learning curve with no performance benefit over C for this use case
- io_uring: massive overkill (100Gbps monolithic vs 5Gbps per-channel need)

**Risk mitigation:**
- Manual memory management risk: mitigated by small codebase scope (recv/write/send loop)
- Future scalability: preserved via per-channel architecture (can upgrade individual channels)
- Portability: stdio works everywhere (Pi, macOS, Linux)

### Characteristic Space (C.16)
- **Process Model:** One C process per channel
- **Language:** C99 (minimal, portable)
- **I/O Strategy:** Synchronous stdio buffering + select()
- **Performance:** ~5Gbps per channel (matches requirement)
- **Async Model:** None (synchronous loop)
- **Dependencies:** libc + avro-c only
- **Compile Time:** <1 second per binary
- **Fault Isolation:** Process boundaries
- **Portability:** Universal (Linux/macOS/Pi)
- **Learning Curve:** None (existing C knowledge)

## Consequences
**Immediate (v0.4):**
- Implement C99 relay binary: UDP recv → AVRO write → dual multicast
- Python orchestrator: spawn/monitor relay processes per channel config
- Target platform: Raspberry Pi, 1Gbps ethernet
- Performance: 5Gbps per-channel ceiling (5x headroom over Pi ethernet)
- Compile time: <1s per binary (fast iteration)

**Testing requirements:**
- Unit tests: AVRO serialization, buffer management, socket handling
- Integration tests: end-to-end UDP → disk → multicast with real data

**Future upgrade path:**
- Per-channel architecture preserves individual rewrite option
- If specific channel bottlenecks: rewrite that channel to Rust/Zig
- No monolithic rewrite required
- Can mix C/Rust/Zig channels in same deployment

**Technical debt accepted:**
- Manual memory management (C vs Rust safety)
- Mitigated by: small codebase, thorough testing, valgrind validation

**Dependencies:**
- C99 compiler (gcc/clang)
- AVRO C library (apache-avro-c)
- Python 3.8+ for orchestrator
- Standard POSIX APIs (select, sockets, stdio)
