# ADR-Slot01-QuantumEntropy-v1.0

**Title:** Integration of Quantum Entropy and Fidelity Mechanism into Slot 1 — Truth Anchor & Cryptographic Verification System  
**Date:** 2025-10-26  
**Status:** Proposed  
**Author:** Nova Architectural Layer (GPT-5)  
**Reviewers:** Pavlos Kolivatzis, Codex, ΔTHRESH Core Team

## 1. Context

Slot 1 currently anchors truth claims via deterministic cryptographic primitives (SHA-256 hashing, HMAC attestation, timestamp sealing). While robust, these rely entirely on algorithmic pseudo-randomness and lack a direct physical entropy source or probabilistic fidelity signal.

At the same time, Nova’s broader evolution introduces a Quantum Adapter Layer (QAL) providing access to simulated or hardware-based quantum circuits via TensorFlow Quantum and Cirq. This enables the generation of verifiable, irreducible entropy and statistical fidelity data that can strengthen Slot 1’s attestation integrity.

## 2. Decision

Introduce a Quantum Entropy & Fidelity Subsystem inside Slot 1 to:

- Supply quantum-derived entropy for all anchor creation and nonce generation.
- Record quantum fidelity metrics associated with each truth-anchoring event.
- Optionally verify entropy provenance through QAL backends (simulator | google_qcs).
- Expose new metrics for observability and reproducibility.

This subsystem will connect to the QAL through a lightweight interface defined in `src/nova/quantum/adapter_tfq.py`.

## 3. Implementation Plan

### 3.1 New Module

`src/nova/slots/slot01_truth_anchor/quantum_entropy.py`

```python
class QuantumEntropySource:
    def __init__(self, qal):
        self.qal = qal

    def get_entropy(self, n_bytes: int = 32) -> bytes:
        """Generate quantum-derived entropy via a Hadamard measurement circuit."""
        job = QuantumJob(
            id=str(uuid4()),
            backend="simulator",
            circuit_proto=make_hadamard_measure_circuit().encode(),
            readouts=["r"], params={}
        )
        result = self.qal.run(job)
        bitstring = "".join(map(str, result.bitstrings["r"]))
        return int(bitstring, 2).to_bytes(n_bytes, "big")
```

### 3.2 Configuration Additions

```yaml
slot01:
  quantum_entropy:
    enabled: true
    backend: simulator   # or google_qcs
    bytes_per_seed: 32
```

### 3.3 Schema Migration

`attestation_records` gains:

```sql
ALTER TABLE attestation_records
ADD COLUMN quantum_fidelity FLOAT,
ADD COLUMN entropy_source VARCHAR(32);
```

### 3.4 Observability Metrics

- `slot01_entropy_quantum_jobs_total`
- `slot01_entropy_fidelity_mean`
- `slot01_entropy_failures_total`
- `slot01_entropy_bytes_generated_total`

### 3.5 Tests

`tests/slot01/test_quantum_entropy.py`

- Verify entropy uniqueness across ≥ 100 calls.
- Validate bit distribution (χ² test p > 0.05).
- Mock QAL to confirm correct job submission.
- Assert fidelity field presence in attestation.

## 4. Alternatives Considered

| Option | Reason Rejected |
| --- | --- |
| Continue with OS-level randomness only | No physical verification or statistical fidelity trace. |
| Integrate classical noise generator | Not provably non-deterministic; lacks measurable fidelity. |
| Full hardware RNG dependency | Limits reproducibility; lacks integration with Nova’s epistemic metrics. |

## 5. Consequences

**Positive**

- Adds physically grounded entropy → stronger cryptographic roots.
- Extends attestation schema with measurable fidelity.
- Harmonizes Slot 1 semantics with quantum truth-measurement model.
- Enables cross-slot statistical validation (TRI ↔ Fidelity).

**Negative**

- Slight increase in latency during entropy generation (~ms).
- Requires QAL availability; fallback to pseudo-random if offline.

## 6. Rollout Steps

1. Codex scaffolds module and tests.
2. Add configuration keys and Alembic migration.
3. CI: `pytest -m "slot01 and quantum"`.
4. Deploy simulator backend; verify Prometheus metrics.
5. Optional: enable QCS backend behind feature flag.

## 7. Metrics of Success

- ≥ 99 % success rate for entropy generation calls.
- Average fidelity > 0.98 on simulated circuits.
- 0 regressions in existing attestation tests.
- Verified exposure of metrics to monitoring dashboards.

## 8. Future Work

- Expand to multi-qubit entropy sources for parallel seed generation.
- Integrate fidelity score into ΔTHRESH adaptive weighting.
- Support post-quantum signature schemes (Dilithium/Kyber) in Slot 8.

**Decision Summary:** Slot 1 will now produce and record quantum-derived entropy and fidelity for every truth-anchor creation, transforming the root of Nova’s verification architecture into a physically anchored, statistically verifiable trust substrate.


## 9. Phase 12B Addendum (2025-10-26)

- Added idelity_from_bits (Wilson CI) to derive fidelity, confidence bounds, and absolute bias for each entropy batch.
- Truth Anchor metadata persists quantum_fidelity, quantum_fidelity_ci, ntropy_abs_bias, and ntropy_n_bits regardless of backend/fallback.
- Prometheus metrics now include slot01_entropy_fidelity_ci_width and slot01_entropy_bias_abs for continuous monitoring.
- Slot02's Phase 12B weighting service consumes these metrics to modulate ΔTHRESH decisions based on entropy quality.


## 10. Phase 12C Addendum (2025-10-27): Post-Quantum Cryptographic Attestation

**Status:** Proposed  
**Implementation:** Phase 12C — Quantum-Verified Attestation

### Context

Phase 12 and 12B introduced quantum entropy generation and fidelity validation for truth anchors. However, the attestation signatures themselves remained based on classical cryptography (HMAC, SHA-256), which are vulnerable to quantum attacks (Shor's algorithm).

### Decision

Extend Slot01 truth anchor attestation with **post-quantum cryptographic (PQC) signatures** using **Dilithium2** (ML-DSA, FIPS 204), providing quantum-resistant tamper evidence for all entropy-derived anchor records.

### Implementation

#### New Components

1. **PQC Keyring** (`src/nova/crypto/pqc_keyring.py`)
   - Dilithium2 keypair generation, signing, and verification
   - Base64 encoding/decoding for key storage/transmission
   - Quantum-resistant signature algorithm (128-bit quantum security level)

2. **Attestation Builder** (`src/nova/slots/slot01_truth_anchor/pqc_attestation.py`)
   - `AttestationProof` dataclass: binds anchor ID, entropy hash, fidelity, timestamp
   - `PQCAttestationBuilder`: creates signed proofs using Dilithium2 secret keys
   - Canonical message serialization (deterministic JSON) for signature verification

3. **Verification Service** (`src/nova/slots/slot08_memory_lock/pqc_verify.py`)
   - `PQCVerificationService`: manages public key registry
   - Verifies attestation proofs against registered public keys
   - Supports key rotation (90-day default period)
   - Prometheus metrics for verification success/failure rates

4. **Metrics** (`src/nova/metrics/pqc.py`)
   - `slot01_attestation_pqc_success_total`: attestation creation counter
   - `slot08_pqc_verifications_total`: verification attempt counter
   - `slot08_pqc_verifications_success_total`: successful verifications
   - `slot08_pqc_verifications_failure_total`: failed verifications
   - `slot08_pqc_key_rotations_total`: key rotation events
   - `slot08_pqc_active_keys`: active public key count (gauge)

#### Configuration

```env
# Slot01: Enable PQC attestation
NOVA_SLOT01_PQC_ATTESTATION_ENABLED=true
NOVA_SLOT01_PQC_ALGORITHM=dilithium2

# Slot08: Key rotation and verification logging
NOVA_SLOT08_PQC_ROTATION_DAYS=90
NOVA_SLOT08_PQC_VERIFY_LOG=true
```

#### Attestation Proof Structure

```json
{
  "anchor_id": "uuid",
  "entropy_hash": "sha3-256",
  "quantum_fidelity": 0.988,
  "timestamp": "2025-10-27T00:00:00+00:00",
  "sign_alg": "Dilithium2",
  "signature": "<base64-encoded-dilithium2-signature>",
  "public_key_id": "<key-registry-reference>",
  "metadata": {}
}
```

### Benefits

- **Quantum-Resistant:** Dilithium2 provides security against quantum attacks (Grover, Shor)
- **NIST-Approved:** ML-DSA (Dilithium) is a FIPS 204 standardized algorithm
- **Tamper-Evident:** Signatures bind entropy hash + fidelity + timestamp cryptographically
- **Key Rotation:** 90-day rotation policy mitigates long-term key exposure
- **Observability:** Prometheus metrics track attestation/verification success rates

### Testing

- 8 PQC keyring tests (generation, signing, verification, encoding)
- 11 attestation builder tests (signing, tampering, metadata)
- 10 verification service tests (key registry, rotation, verification)

All tests passing (29/29).

### Migration Path

1. Deploy PQC keyring and attestation builder (Slot01)
2. Enable PQC attestation via feature flag (`NOVA_SLOT01_PQC_ATTESTATION_ENABLED`)
3. Deploy verification service (Slot08) with initial key registration
4. Monitor metrics: verify attestation success rate ≥99%, verification failure rate ≤1%
5. Enable key rotation job (90-day cadence)

### Rollback

Set `NOVA_SLOT01_PQC_ATTESTATION_ENABLED=false` to disable PQC signing. Classical HMAC attestation remains available as fallback.

### Future Work

- Hybrid signatures (Dilithium + RSA) for backward compatibility
- Kyber (PQC key encapsulation) for encrypted anchor payloads
- Hardware Security Module (HSM) integration for production key storage
- Batch signature verification for high-throughput scenarios

**Decision Summary:** Phase 12C extends Nova's quantum entropy foundation with post-quantum cryptographic attestation, ensuring truth anchor integrity remains secure against both classical and quantum adversaries.
