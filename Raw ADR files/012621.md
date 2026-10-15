# ADR-13b: Oracle Pre-Transition Evaluation

**Status:** Accepted  
**Date:** 2025-11-30  
**Phase:** 13b  
**Supersedes:** None (extends ADR-13-Init)

## Context

Phase 13 introduced the Autonomous Verification Ledger (AVL) with dual-modality verification, where both the ORP implementation and a contract oracle independently compute the expected regime. The intent was to detect implementation drift by comparing ORP's decision against the oracle's independent calculation.

### The Bug

In the original implementation, `_write_to_avl()` called `compute_and_classify()` with:

```python
oracle_result = compute_and_classify(
    factors.to_dict(),
    current_regime=self._current_regime.value,  # BUG: Already updated!
    time_in_regime_s=time_in_previous_regime_s,
)
```

The problem: `self._current_regime` was already updated to the **new** regime (line 359) before `_write_to_avl()` was called (line 399). This meant:

1. On a **downgrade** (e.g., HEIGHTENED → NORMAL), the oracle would evaluate using `current_regime="normal"` instead of `"heightened"`
2. The oracle's hysteresis and min-duration checks would never trigger because it was evaluating from the post-transition state
3. Illegal downgrades would be silently accepted because both ORP and oracle would agree on the new regime

### Impact

- **Dual-modality verification was ineffective for downgrades**
- Premature downgrades violating hysteresis rules would not be detected
- Premature downgrades violating min-duration rules would not be detected
- The AVL's core safety guarantee was compromised

## Decision

Modify `_write_to_avl()` to receive and use the **pre-transition** regime and duration:

```python
def _write_to_avl(
    self,
    snapshot: RegimeSnapshot,
    factors: ContributingFactors,
    previous_regime: Regime,      # NEW: Pre-transition regime
    previous_duration_s: float,   # NEW: Pre-transition duration
) -> None:
    # Oracle evaluates using PRE-TRANSITION state
    oracle_result = compute_and_classify(
        factors.to_dict(),
        current_regime=previous_regime.value,  # FIXED: Use pre-transition
        time_in_regime_s=previous_duration_s,   # FIXED: Use pre-transition
    )
```

The caller captures pre-transition state **before** any updates:

```python
# BEFORE any updates
previous_regime = self._current_regime
previous_duration_s = time_in_regime_s

# ORP updates state
new_regime = self.classify_regime(...)
if new_regime != self._current_regime:
    self._current_regime = new_regime  # State updated here

# Pass pre-transition state to AVL
self._write_to_avl(
    snapshot,
    factors,
    previous_regime=previous_regime,
    previous_duration_s=previous_duration_s,
)
```

## Consequences

### Positive

1. **Oracle can now detect illegal downgrades**: By evaluating from the same starting point as ORP, the oracle can independently validate whether a transition was legal
2. **Hysteresis violations detected**: If ORP downgrades when score is above hysteresis threshold, oracle will disagree
3. **Min-duration violations detected**: If ORP downgrades before min-duration elapsed, oracle will disagree
4. **Dual-modality verification is now effective**: The core safety guarantee of AVL is restored

### Negative

1. **Slight API change**: `_write_to_avl()` signature changed (internal method, no external impact)
2. **Additional parameters**: Two new parameters to track and pass

### Neutral

1. **No performance impact**: Same number of computations, just different input values
2. **Backward compatible**: AVL entries remain structurally identical

## Verification

Four new tests added to `tests/integration/test_orp_avl.py`:

1. `test_oracle_detects_illegal_downgrade_hysteresis` - Oracle stays in HEIGHTENED when score above hysteresis
2. `test_oracle_detects_illegal_downgrade_min_duration` - Oracle stays in HEIGHTENED when duration < min
3. `test_oracle_allows_legal_downgrade` - Legal downgrades still work correctly
4. `test_oracle_pretransition_evaluation_on_upgrade` - Upgrades work correctly with pre-transition state

All 13 integration tests pass.

## Implementation Details

### Files Modified

| File | Change |
|------|--------|
| `src/nova/continuity/operational_regime.py` | Capture pre-transition state, pass to `_write_to_avl()` |
| `tests/integration/test_orp_avl.py` | 4 new tests for oracle pre-transition validation |
| `contracts/autonomous_verification_ledger@1.yaml` | Version 1.1.0, document oracle evaluation context |
| `specs/nova_framework_ontology.v1.yaml` | Version 1.7.1, document Phase 13b fix |

### Version Bumps

- `orp_version`: `phase13.1` → `phase13.2`
- Contract version: `1.0.0` → `1.1.0`
- Ontology version: `1.7.0` → `1.7.1`

## References

- [ADR-13-Init.md](./ADR-13-Init.md) - Original AVL design
- [autonomous_verification_ledger@1.yaml](../../contracts/autonomous_verification_ledger@1.yaml) - AVL contract
- [operational_regime.py](../../src/nova/continuity/operational_regime.py) - ORP implementation
- [contract_oracle.py](../../src/nova/continuity/contract_oracle.py) - Oracle implementation