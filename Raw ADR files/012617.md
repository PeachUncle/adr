# ADR-13-Ledger-Final — Autonomous Verification Ledger

**Date:** 2025-10-27
**Status:** Accepted
**Version:** v13.0.0-beta
**Author:** Nova Architecture Team

## Context

Nova requires a self-verifying trust substrate that links:
- PQC-anchored attestations (Dilithium2 signatures)
- ΔTHRESH fidelity weights from quantum entropy
- Verification outcomes across slots (01/02/08)
- Tamper-evident provenance for all critical operations

Without a unified ledger, trust signals remain isolated within individual slots, preventing system-wide trust propagation and making tampering detection reactive rather than structural.

## Decision

Adopt the **Autonomous Verification Ledger (AVL)** with the following architecture:

### 1. Hash-Linked Chains (SHA3-256)

Each `LedgerRecord` contains:
- `rid`: UUIDv7 (time-sortable)
- `prev_hash`: SHA3-256 digest of previous record
- `hash`: SHA3-256 digest of canonical JSON representation
- Continuity breaks are immediately detectable

### 2. Canonical JSON Serialization

Deterministic serialization ensures:
- Sorted keys (alphabetical)
- UTF-8 encoding
- No whitespace variations
- Same input → same hash (cryptographic determinism)

### 3. PQC Signatures (Dilithium2)

Records can carry optional `sig` field:
- Post-quantum secure (ML-DSA, FIPS 204)
- Verified by Slot08 PQC service
- Key rotation tracked via `PQC_KEY_ROTATED` events

### 4. Composite Trust Score

Trust propagation formula:
```
T = w₁·F̄ + w₂·pqc_rate + w₃·verify_rate + w₄·continuity
```

Default weights: `[0.5, 0.2, 0.2, 0.1]`

Where:
- `F̄` = mean quantum fidelity from entropy samples
- `pqc_rate` = fraction of records with PQC signatures
- `verify_rate` = fraction of successful PQC verifications
- `continuity` = binary (1.0 if chain intact, 0.0 if broken)

### 5. Merkle Checkpoints

Periodic snapshots with:
- Merkle root of record batch
- PQC signature of root (future: Phase 14-2)
- Enables efficient batch verification

### 6. Slot Emitters

| Slot | Event | Payload |
|------|-------|---------|
| 01 | `ANCHOR_CREATED` | entropy_sha3_256, quantum_fidelity, fidelity_ci, abs_bias |
| 02 | `DELTATHRESH_APPLIED` | fidelity, weight, entropy_source |
| 08 | `PQC_VERIFIED` | key_id, algorithm, verified_at |
| 08 | `PQC_KEY_ROTATED` | old_key_id, rotated_at |

### 7. Observability

Prometheus metrics:
- `ledger_appends_total{slot,kind,status}` - Append operations counter
- `ledger_trust_score{anchor_id}` - Current trust score gauge
- `ledger_chain_length{anchor_id}` - Records per anchor gauge
- `ledger_verify_requests_total{result}` - Verification requests counter

REST API:
- `POST /ledger/append` - Emit new record
- `GET /ledger/chain/{anchor_id}` - Fetch ordered chain
- `POST /ledger/verify/{anchor_id}` - Verify chain + compute trust
- `GET /ledger/stats` - Ledger statistics

## Consequences

### Positive

✅ **Tamper-evident provenance** — Any modification breaks SHA3-256 chain
✅ **Quantifiable trust** — Numerical scores enable IDS/routing decisions
✅ **PQC durability** — Post-quantum signatures outlive classical crypto
✅ **Cross-slot visibility** — Unified ledger spans entire architecture
✅ **Observability** — Metrics + API for real-time monitoring

### Constraints

⚙️ **Persistence required** — In-memory store needs PostgreSQL backend (Phase 14-1)
⚙️ **Checkpoint automation** — Manual Merkle snapshots need automation (Phase 14-2)
⚙️ **Storage growth** — Append-only ledger requires retention policy
⚙️ **Trust weight tuning** — Default weights may need calibration per deployment

### Risks Mitigated

- **Data tampering** → Detected via hash chain breaks
- **Trust isolation** → Eliminated via composite scoring
- **Classical crypto sunset** → PQC signatures provide quantum resistance
- **Blind spots** → Eliminated via cross-slot emission coverage

## Alternatives Considered

### 1. Event Sourcing Only (No Hash Chains)
**Rejected** — Lacks cryptographic tamper detection

### 2. Blockchain (Proof-of-Work/Stake)
**Rejected** — Unnecessary computational overhead for single-authority ledger

### 3. Classical Signatures (RSA/ECDSA)
**Rejected** — Vulnerable to quantum attacks (Shor's algorithm)

### 4. External Ledger (e.g., Hyperledger)
**Rejected** — Adds dependency, latency, and deployment complexity

## Implementation

**Delivered in Phase 13:**
- RUN 13-1: Ledger scaffold (model, canon, store, metrics)
- RUN 13-2: Verification + trust scoring + API
- RUN 13-3: Slot emitters + integration tests

**File Structure:**
```
src/nova/ledger/
├── __init__.py
├── model.py          # LedgerRecord, Checkpoint, RecordKind
├── canon.py          # Canonical JSON + SHA3-256 hashing
├── store.py          # In-memory append-only store
├── verify.py         # ChainVerifier + trust scoring
├── client.py         # LedgerClient singleton for emitters
├── api.py            # Flask REST API blueprint
└── metrics.py        # Prometheus counters/gauges

migrations/
└── 001_create_ledger_tables.sql  # PostgreSQL schema (ready)

tests/ledger/
├── test_canon.py     # Canonical hashing + Merkle trees
├── test_store.py     # Store operations + continuity
└── test_verify.py    # Verification + trust scoring

tests/integration/
└── test_slot_emitters_ledger.py  # End-to-end Slot→Ledger→Verify
```

**Test Coverage:**
- 60 ledger + integration tests
- 1227 total tests (0 regressions)

## Next Steps (Phase 14)

| RUN | Focus | Deliverable | Tag |
|-----|-------|-------------|-----|
| 14-1 | PostgreSQL Persistence | Async writer + Alembic migrations | v13.1.0 |
| 14-2 | Checkpoint Automation | Merkle root snapshots + PQC signatures | v13.2.0 |
| 14-3 | Cross-Slot Trust Use | IDS/routing consume trust scores | v13.3.0 |
| 14-4 | Ledger UI | Web dashboard (explorer, metrics) | v13.4.0 |
| 14-5 | Specification | Public "Ledger v1.0" white-paper | v13.5.0 |

## References

- **Phase 13 Design Doc:** Phase 13 RUN 13-1/2/3 execution briefs
- **Trust Formula:** `src/nova/ledger/verify.py:279`
- **PQC Attestation:** ADR-12C-PQC-Attestation.md
- **Quantum Entropy:** ADR-12-Quantum-Entropy.md
- **Fidelity Weighting:** Phase 12B-2 integration

## Approval

**Accepted:** 2025-10-27
**Supersedes:** N/A (net-new capability)
**Effective:** v13.0.0-beta onwards
