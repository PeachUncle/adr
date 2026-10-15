# ADR 0001: Sundew Core SDK Public API Surface

## Status
Proposed (2025-10-07)

## Context
Phase 1 of the Sundew roadmap requires a stable SDK surface that exposes adaptive
energy gating across embedded deployments. The existing `sundew` package bundles
core algorithms, runtime adapters, and demos but lacks a clear public API for
firmware clients. We need to define the namespaces, configuration objects, and
interaction patterns so downstream teams can build firmware shims and
benchmarks without depending on internal modules.

## Decision
Introduce a `sundew_core_sdk` package with the following public modules:

- `sundew_core_sdk.config` — `SDKConfig` dataclass describing activation target,
  gate temperature, energy budget, firmware transport options, and optional
  telemetry sampling rate.
- `sundew_core_sdk.controller` — `AdaptiveGateController` facade exposing
  `load_native()`, `decide(features: Dict[str, Any]) -> bool`,
  `score(features) -> float` (planned), and `emit_telemetry() -> TelemetryEvent`.
  Internally this will wrap the refactored Sundew gating runtime.
- `sundew_core_sdk.telemetry` — typed payloads (`TelemetryEvent`,
  `TelemetryBatch`) and serialization helpers for firmware IPC.
- `sundew_core_sdk.firmware` — protocol definitions (`FirmwareGateInterface`,
  `FirmwareStatus`) plus utility functions for framing requests and responses.
- `sundew_core_sdk.hardware` — registry for board-specific adapters and
  provisioning scripts (`HardwareAdapter`, `HardwareRegistry`).
- `sundew_core_sdk.metrics` (new) — reusable metrics aggregate for activation
  rate, power draw, latency, geared toward benchmark collection.

The SDK will export these symbols from the package root for quick access.

The public API will avoid leaking the legacy `sundew.core` types; instead, the
controller bridges to an internal `NativeAdapter` that evolves alongside the
extraction effort. Semantic versioning (`0.x` during Phase 1) will communicate
breaking changes until the GA release.

## Consequences
- Documentation must reference the new namespaces and avoid direct imports from
  `sundew.core`.
- Unit tests and integration samples should target the SDK API rather than the
  legacy modules, encouraging separation.
- Additional modules (`metrics`, serialization helpers) need to be implemented
  before alpha release.
- Hardware adapters can now depend on a stable registry interface for board
  discovery and provisioning.

## Open Questions
- Exact shape of the telemetry payload (power, temperature, activation rate) —
  to be refined once benchmark instrumentation is prototyped.
- Packaging story for the firmware shim (shared library vs. microservice) — to
  be decided in the firmware IPC ADR.
