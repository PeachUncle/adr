# ADR-13: Autonomous Verification Ledger (AVL) Design

**Status:** Proposed
**Date:** 2025-11-28
**Deciders:** Nova Architecture Team
**Context:** Phase 12 validated ORP physics; Phase 13 establishes provenance ledger

---

## Decision

Implement an **Autonomous Verification Ledger (AVL)** as an immutable, hash-chained record of all regime transitions with dual-modality verification and drift detection.

---

## Context

Phase 12 proved:
- ORP implementation matches contract oracle (100% agreement)
- Regime transitions preserve continuity invariants
- Hysteresis + min-duration enforcement are deterministic
- Amplitude triad remains within bounds

**Gap:** No persistent audit trail of live system behavior.

**Need:** Provenance ledger that enables:
1. Post-hoc analysis of any time window
2. Drift detection (implementation vs contract)
3. Continuity proofs (mathematical guarantees)
4. Regulatory compliance (immutable audit log)

---

## Design

### 1. Ledger Schema

```python
@dataclass
class AVLEntry:
    """Single ledger entry (one regime evaluation)."""

    # Identity & chain
    entry_id: str          # SHA256(timestamp + regime + factors_json)
    prev_entry_hash: str   # Hash of previous entry (chain pointer)

    # Temporal
    timestamp: str         # ISO8601 with timezone (e.g., "2025-01-01T12:00:00+00:00")
    elapsed_s: float       # Seconds since system start

    # ORP evaluation
    orp_regime: str                        # normal | heightened | controlled_degradation | emergency_stabilization | recovery
    orp_regime_score: float                # [0.0, 1.0]
    contributing_factors: Dict[str, float] # {urf, mse, pred, gap, csi}
    posture_adjustments: Dict[str, Any]    # {threshold_multiplier, traffic_limit, ...}

    # Oracle verification
    oracle_regime: str
    oracle_regime_score: float
    dual_modality_agreement: bool

    # Transition metadata
    transition_from: Optional[str]         # Previous regime (None if no transition)
    time_in_previous_regime_s: float       # Duration in previous regime

    # Invariants (per-entry validation)
    hysteresis_enforced: bool
    min_duration_enforced: bool
    ledger_continuity: bool
    amplitude_valid: bool

    # Drift detection
    drift_detected: bool
    drift_reasons: List[str]  # Empty if no drift

    # Metadata
    node_id: str          # Identifier for this Nova instance
    orp_version: str      # ORP implementation version (e.g., "phase11.3")
```

### 2. Storage Format

**Format:** JSON Lines (`.jsonl`)
- One entry per line
- Human-readable
- Streamable (can process line-by-line)
- Append-only

**Location:** `data/avl/avl_ledger.jsonl` (configurable via `NOVA_AVL_PATH`)

**Example Entry:**
```json
{"entry_id":"e3b0c44298fc1c14...", "prev_entry_hash":"d4735e3a265e16ee...", "timestamp":"2025-01-01T12:00:00+00:00", "orp_regime":"normal", "orp_regime_score":0.15, "oracle_regime":"normal", "dual_modality_agreement":true, "drift_detected":false}
```

### 3. Hash Chain Integrity

**Chain Construction:**
```python
def compute_entry_hash(entry: AVLEntry) -> str:
    """Compute deterministic hash of entry."""
    canonical_repr = json.dumps({
        "timestamp": entry.timestamp,
        "orp_regime": entry.orp_regime,
        "orp_regime_score": entry.orp_regime_score,
        "contributing_factors": entry.contributing_factors,
        "oracle_regime": entry.oracle_regime,
    }, sort_keys=True)
    return hashlib.sha256(canonical_repr.encode()).hexdigest()

def append_entry(ledger: List[AVLEntry], new_entry: AVLEntry) -> None:
    """Append entry with hash chain update."""
    if ledger:
        new_entry.prev_entry_hash = compute_entry_hash(ledger[-1])
    else:
        new_entry.prev_entry_hash = "0" * 64  # Genesis entry

    new_entry.entry_id = compute_entry_hash(new_entry)
    ledger.append(new_entry)
```

**Invariant:** `ledger[N].prev_entry_hash == compute_entry_hash(ledger[N-1])`

**Verification:**
```python
def verify_hash_chain(ledger: List[AVLEntry]) -> bool:
    """Verify entire hash chain is intact."""
    for i in range(1, len(ledger)):
        expected_hash = compute_entry_hash(ledger[i-1])
        if ledger[i].prev_entry_hash != expected_hash:
            return False
    return True
```

### 4. Drift Detection Rules

**Drift detected if ANY of:**

1. **Dual-modality disagreement:**
   ```python
   drift = (entry.orp_regime != entry.oracle_regime)
   reason = f"ORP={entry.orp_regime} vs Oracle={entry.oracle_regime}"
   ```

2. **Invariant violation:**
   ```python
   drift = not (entry.hysteresis_enforced and
                entry.min_duration_enforced and
                entry.ledger_continuity and
                entry.amplitude_valid)
   reason = "Invariant violation: [list failed checks]"
   ```

3. **Amplitude bounds exceeded:**
   ```python
   drift = not (0.5 <= entry.posture_adjustments["threshold_multiplier"] <= 2.0 and
                0.0 <= entry.posture_adjustments["traffic_limit"] <= 1.0)
   reason = "Amplitude out of bounds"
   ```

4. **Score computation drift:**
   ```python
   drift = abs(entry.orp_regime_score - entry.oracle_regime_score) > 1e-6
   reason = f"Score drift: ORP={entry.orp_regime_score:.6f} vs Oracle={entry.oracle_regime_score:.6f}"
   ```

**Response to drift:**
- Log drift event with full context
- Increment `nova_avl_drift_events_total` counter
- If `NOVA_AVL_HALT_ON_DRIFT=1`: Raise exception, halt transitions
- If `NOVA_AVL_HALT_ON_DRIFT=0`: Log warning, continue

### 5. Continuity Proofs

**Ledger Continuity Proof:**
```python
def prove_ledger_continuity(ledger: List[AVLEntry]) -> bool:
    """Prove from_regime[N] == to_regime[N-1] for all transitions."""
    for i in range(1, len(ledger)):
        if ledger[i].transition_from is not None:
            if ledger[i].transition_from != ledger[i-1].orp_regime:
                return False
    return True
```

**Temporal Continuity Proof:**
```python
def prove_temporal_continuity(ledger: List[AVLEntry]) -> bool:
    """Prove timestamps are monotonically increasing."""
    for i in range(1, len(ledger)):
        if ledger[i].elapsed_s <= ledger[i-1].elapsed_s:
            return False
    return True
```

**Amplitude Continuity Proof:**
```python
def prove_amplitude_continuity(ledger: List[AVLEntry], max_delta: float = 0.5) -> bool:
    """Prove no discontinuous jumps in amplitude parameters."""
    for i in range(1, len(ledger)):
        prev_mult = ledger[i-1].posture_adjustments["threshold_multiplier"]
        curr_mult = ledger[i].posture_adjustments["threshold_multiplier"]
        if abs(curr_mult - prev_mult) > max_delta:
            return False
    return True
```

**Regime Continuity Proof:**
```python
def prove_regime_continuity(ledger: List[AVLEntry]) -> bool:
    """Prove all transitions respect hysteresis + min-duration."""
    return all(entry.hysteresis_enforced and entry.min_duration_enforced
               for entry in ledger)
```

### 6. Query API

```python
class AVLLedger:
    def query_by_time_window(self, start: str, end: str) -> List[AVLEntry]:
        """Return entries in [start, end] time window."""

    def query_by_regime(self, regime: str) -> List[AVLEntry]:
        """Return all entries where orp_regime == regime."""

    def query_drift_events(self) -> List[AVLEntry]:
        """Return only entries with drift_detected=True."""

    def get_latest(self, n: int = 10) -> List[AVLEntry]:
        """Return last N entries."""

    def verify_integrity(self) -> bool:
        """Verify hash chain + all continuity proofs."""
```

---

## Invariants

**Must hold for ALL ledger entries:**

1. **Hash chain integrity:**
   - `entry[N].prev_entry_hash == SHA256(entry[N-1])`
   - Genesis entry: `prev_entry_hash = "0" * 64`

2. **Entry ID determinism:**
   - `entry_id == SHA256(timestamp + regime + factors)`
   - Same inputs → same entry_id (reproducible)

3. **Temporal ordering:**
   - `entry[N].elapsed_s > entry[N-1].elapsed_s` (strictly increasing)

4. **Ledger continuity:**
   - If `entry[N].transition_from != None`, then `entry[N].transition_from == entry[N-1].orp_regime`

5. **Dual-modality agreement (baseline):**
   - `drift_detected == False` on canonical trajectories
   - `drift_detected == True` triggers investigation

---

## Contracts

### AVLLedger Interface

```python
class AVLLedger:
    """Autonomous Verification Ledger."""

    def __init__(self, ledger_path: str):
        """Load ledger from file or create new."""

    def append(self, entry: AVLEntry) -> None:
        """Append entry with hash chain update. Atomic operation."""

    def query(...) -> List[AVLEntry]:
        """Query API (see above)."""

    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """Return (pass, violations). Empty violations if pass=True."""

    def export(self, path: str, format: str = "jsonl") -> None:
        """Export ledger to file."""
```

### DriftGuard Interface

```python
class DriftGuard:
    """Drift detection engine."""

    def check(self, entry: AVLEntry) -> Tuple[bool, List[str]]:
        """Return (drift_detected, reasons)."""

    def configure(self, halt_on_drift: bool = False) -> None:
        """Configure response strategy."""
```

### ContinuityProof Interface

```python
class ContinuityProof:
    """Continuity proof validators."""

    def prove_ledger_continuity(self, ledger: List[AVLEntry]) -> bool:
        """Ledger continuity proof."""

    def prove_temporal_continuity(self, ledger: List[AVLEntry]) -> bool:
        """Temporal continuity proof."""

    def prove_amplitude_continuity(self, ledger: List[AVLEntry]) -> bool:
        """Amplitude continuity proof."""

    def prove_regime_continuity(self, ledger: List[AVLEntry]) -> bool:
        """Regime continuity proof."""

    def prove_all(self, ledger: List[AVLEntry]) -> Dict[str, bool]:
        """Run all proofs, return results dict."""
```

---

## Migration Path

**Phase:** Simulation → Production AVL

**Step 1:** Use simulation engine to generate sample ledger
```bash
python scripts/simulate_nova_cycle.py tests/e2e/trajectories/canonical_normal_to_heightened.json \
  --output data/avl/simulation_ledger/
```

**Step 2:** Convert simulation results to AVL entries
```python
# scripts/migrate_simulation_to_avl.py
for step_result in simulation_results:
    avl_entry = AVLEntry(
        timestamp=step_result.timestamp,
        orp_regime=step_result.orp_regime,
        oracle_regime=step_result.oracle_regime,
        # ... (see Phase13_Migration_Map.md)
    )
    avl_ledger.append(avl_entry)
```

**Step 3:** Integrate AVL with live ORP evaluations
```python
# src/nova/continuity/operational_regime.py
def evaluate(...) -> RegimeSnapshot:
    snapshot = self._compute_snapshot(...)

    # Write to AVL
    if _avl_enabled():
        avl_entry = _snapshot_to_avl_entry(snapshot)
        get_avl_ledger().append(avl_entry)

        # Drift check
        drift_detected, reasons = get_drift_guard().check(avl_entry)
        if drift_detected and _halt_on_drift():
            raise DriftDetectedError(reasons)

    return snapshot
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOVA_ENABLE_AVL` | `0` | Enable AVL logging (0=disabled, 1=enabled) |
| `NOVA_AVL_PATH` | `data/avl/avl_ledger.jsonl` | Ledger file path |
| `NOVA_AVL_HALT_ON_DRIFT` | `0` | Halt on drift detection (0=log only, 1=halt) |
| `NOVA_AVL_NODE_ID` | `hostname` | Node identifier for multi-instance deployments |
| `NOVA_AVL_VERSION` | `phase13.1` | AVL schema version |

---

## Consequences

### Positive

- ✅ Immutable audit trail of all regime transitions
- ✅ Drift detection catches implementation bugs in production
- ✅ Continuity proofs provide mathematical guarantees
- ✅ Post-hoc analysis enables debugging historical issues
- ✅ Regulatory compliance (tamper-evident ledger)

### Negative

- ⚠️  Ledger grows unbounded (mitigation: archival strategy in Phase 14)
- ⚠️  Hash computation adds latency (<1ms, acceptable)
- ⚠️  Disk I/O on every transition (mitigation: async writes)
- ⚠️  Drift false positives possible (mitigation: tunable thresholds)

### Risks

- **Hash chain breaks:** If entry hash computation is non-deterministic → Fix: Canonical JSON ordering
- **Ledger corruption:** If file write fails mid-append → Fix: Atomic writes with temp file + rename
- **Drift storm:** Many false positives → Fix: Adjust thresholds, add drift suppression window
- **Query performance:** Linear scan on large ledgers → Fix: Add indexing (Step 7, future)

---

## Alternatives Considered

### Alt 1: Use existing logging (rejected)
**Pro:** No new infrastructure
**Con:** No hash chain, no drift detection, not queryable

### Alt 2: Use database (SQLite/Postgres) (rejected)
**Pro:** Built-in indexing, transactions
**Con:** Complexity, not append-only by default, not human-readable

### Alt 3: Use blockchain (rejected)
**Pro:** Distributed, consensus-based
**Con:** Massive overkill, latency, complexity

---

## Decision Rationale

AVL strikes balance between:
- **Simplicity:** JSON Lines, stdlib-only, human-readable
- **Integrity:** Hash chain, append-only, tamper-evident
- **Performance:** <1ms overhead, async writes possible
- **Debuggability:** Direct file inspection, no DB required

**Chosen design aligns with Nova's "Rule of Sunlight" principle:**
- Everything is visible (human-readable ledger)
- Everything is verifiable (hash chain + proofs)
- Everything is reversible (flag-gated, can disable)

---

## Implementation Checklist

- [ ] Create `src/nova/continuity/avl_ledger.py`
- [ ] Create `src/nova/continuity/drift_guard.py`
- [ ] Create `src/nova/continuity/continuity_proof.py`
- [ ] Write unit tests (ledger, drift, proofs)
- [ ] Integrate with ORP evaluation
- [ ] Add Prometheus metrics (`nova_avl_drift_events_total`, `nova_avl_entries_total`)
- [ ] Run E2E validation (20 trajectories → ledger)
- [ ] Document migration path
- [ ] Add CI test lane (`phase13-avl.yml`)

---

## References

- Phase 12 Summary: `docs/Phase12_Summary.md`
- ORP Contract: `contracts/orp@1.yaml`
- Contract Oracle: `src/nova/continuity/contract_oracle.py`
- Simulation Engine: `scripts/simulate_nova_cycle.py`
