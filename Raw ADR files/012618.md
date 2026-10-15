# ADR-15: Federation Foundation (Phase 15-1)

**Status:** Proposed  
**Date:** 2025-10-31  
**Authors:** Nova Architecture Group  
**Stakeholders:** Ledger Core, Slot02/04 owners, Observability, Infra/Sec

## 1. Context
Phase 14 delivered async PostgreSQL persistence, Dilithium2 checkpoint signing, and observability improvements. Checkpoints remain node-local; to evolve toward a trust fabric, Nova instances must exchange signed checkpoints, verify them, and record trust—without violating append-only Merkle continuity, PQC guarantees, or metrics hygiene.

## 2. Decision
Introduce a feature-flagged federation layer (`FEDERATION_ENABLED`, default `false`) that exposes REST endpoints for checkpoint exchange, loads peers from a static registry, verifies Dilithium2 signatures, computes a basic trust score, and emits federation metrics. The scaffold will provide interfaces and health tests only—no ledger mutation yet.

## 3. Invariants
- Ledger: append-only, SHA3-256 canonicalization, prev-hash + Merkle continuity.
- Crypto: Dilithium2 signatures for all envelopes; no downgrade allowed.
- Safety: opt-in via feature flag; safe defaults when disabled.
- Metrics: centralized registry accessors; resettable in tests.
- Performance: sustained load ≤ 1.5× versus baseline.

## 4. Implementation Outline
- Package `src/nova/federation/` with server/client stubs, schemas (canonical UTC-Z timestamps, enforced algo/version, merkle/signature validation), peer registry loader, trust model.
- Config loader in `src/nova/config/federation_config.py` supporting YAML + env overrides.
- FastAPI router registered in `orchestrator/app.py` only when the flag is enabled, enforcing content-type/body limits, clock-skew window, replay cache, per-peer rate limiting, and gradient trust responses.
- Outbound federation client (httpx) with configurable timeouts/jittered retries plus retry metrics (Phase 15-2, still behind the feature flag).
- Metrics helpers (`federation_verifications_total`, `federation_peers_up`, `federation_last_sync_seconds`, `federation_score_gauge`, `federation_client_retries_total`) with bounded peer-only labels and reset helpers.
- Tests under `tests/federation/` covering flag behaviour, schema validation, trust scoring (binary + gradient), registry loading, OpenAPI examples, metrics, and client retries.
- Observability stubs: Grafana dashboard JSON and runbook skeleton documenting env knobs, error codes, curl flows, and recommended panels.

## 5. Risks & Mitigations
| Risk | Mitigation |
| --- | --- |
| Replay or stale checkpoints | Monotonic nonce per peer; replay cache (`block|mark|allow`); metrics (`replay`, `rate_limited`). |
| PQC key mismatch | Require `key_id` and registry lookup; fail closed. |
| Metrics duplication | Centralized registry factory; `reset_test_registry()` for tests. |
| Performance regression | Keep Phase 15-1 read-only; perf smoke when sync logic lands. |
| Config drift | Validate registry schema on load; log/raise for malformed entries. |

## 6. Rollout & Rollback
- Deployment toggled via `FEDERATION_ENABLED`.
- Foreign proofs stored separately; disabling the flag stops routers without touching core ledger.
- Operator runbook documents enable/disable and registry maintenance.
- Metrics remain available with zero values after rollback.

## 7. Testing Strategy
- Health: flag off → no router; flag on → router registers endpoints.
- Unit: schema validation, registry loader, trust scoring.
- Metrics: ensure single registration; provide reset helper for tests and assert bounded label cardinality.
- Integration and fault injection deferred to Phase 15-2/15-3.

## 8. Future Work
- Implement secure federation sync (Dilithium2 mutual auth + Merkle continuity checks).
- Add trust propagation engine with gradient scores and peer reputation.
- Build multi-node simulation with fault injection.
- Expand Grafana dashboard and alert rules as metrics mature.

## 9. Phase 15-3 Additions (2025-11-02)
- Range proofs: bounded chunking (`NOVA_FEDERATION_RANGE_MAX` / `NOVA_FEDERATION_CHUNK_BYTES_MAX`) with hashed digests and tip continuity, exposed at `/federation/checkpoints/latest` and `/federation/range_proof`.
- RangeSyncer client: fetches range proofs, verifies continuity, records receipts, enforces divergence threshold (`NOVA_FEDERATION_MAX_DIVERGENCE`), and emits range/divergence metrics.
- Receipts: append-only continuity and key-rotation receipts persisted via `ReceiptsStore`; Grafana visualises `federation_range_*`, `federation_divergences_total`, and `federation_manifest_rotations_total`.
- Discovery: Dilithium-signed peer manifests fetched with TTL control (`NOVA_FEDERATION_MANIFEST_TTL_S`), generating rotation receipts on new key IDs.
- Telemetry: OpenTelemetry spans wrap verification, range sync, and manifest fetch paths for trace correlation.
