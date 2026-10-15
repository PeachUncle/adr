# ADR 0002: Firmware IPC Specification

## Status
Draft (2025-10-07)

## Context
Embedded deployments (Jetson Nano, Coral Edge TPU, Raspberry Pi CM) will run a
lightweight firmware or daemon that exchanges sensor features with the Sundew
Core SDK. We need a consistent messaging contract covering initialization,
feature streaming, gating decisions, and telemetry so that board-specific
adaptations share tooling and tests.

## Decision
Adopt a binary framed protocol transported over gRPC or Unix domain sockets,
with the following layers:

- **Transport:** default to Unix domain socket (`/run/sundew-gate.sock`) with
  protobuf framed messages. Fallback to TCP loopback for boards without uds
  support.
- **Messages:** define protobuf schema `sundew.ipc.v1` with messages:
  - `InitRequest` (board info, firmware version, SDK config hash)
  - `InitResponse` (status, negotiated config, heartbeat interval)
  - `ScoreEvent` (monotonic timestamp, feature map as repeated key/value, power
    budget hints)
  - `GateDecision` (should_activate bool, confidence float, threshold float,
    optional risk probability)
  - `TelemetryPush` (activation rate, average power, energy buffer, custom tags)
  - `Acknowledge` (sequence number, status)
- **Flow:**
  1. Firmware connects and sends `InitRequest`.
  2. SDK replies with `InitResponse`; connection upgraded to streaming mode.
  3. Firmware streams `ScoreEvent` messages; SDK responds with `GateDecision` per
     event (bidirectional streaming).
  4. SDK periodically emits `TelemetryPush`; firmware acknowledges with
     `Acknowledge`.
  5. Heartbeats every 2 seconds; missing heartbeat for 10 seconds triggers
     reconnection.
- **Error Handling:** standardized status codes (OK, INVALID_PAYLOAD,
  UNSUPPORTED_FEATURE, OVERLOAD). Errors carried in `GateDecision` and
  `InitResponse` plus logs.

Additionally, we will offer a minimal C ABI in a shared library for firmware
that cannot host gRPC. The ABI mirrors the protobuf schema using packed structs
and function calls: `sdk_gate_init`, `sdk_gate_score`, `sdk_gate_poll`,
`sdk_gate_telemetry`.

## Consequences
- Requires generating protobuf bindings for Python (SDK), C++ (firmware shim),
  and optionally Rust.
- Documentation must cover socket permissions and reconnection behaviour.
- Benchmark harness can reuse the same IPC client to replay workloads.

## Open Questions
- Whether Jetson deployments prefer shared-memory transport for reduced latency
  — evaluate once prototype benchmarks are available.
- Authentication story for production deployments — outside Phase 1 scope but
  should be noted for Phase 2.
