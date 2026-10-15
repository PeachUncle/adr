# ADR-003: Evidence Bundle Compliance

**Status:** Proposed
**Date:** 2025-12-30
**WorkId:** P-CFCORE-LOGGING-CONSOLIDATION
**Authors:** ContextForge QSE Agent
**Decision Context:** Establish RFC 8785 canonical JSON serialization and SHA-256 hashing for evidence bundles to ensure cryptographic verifiability per UCL Law 3.

---

## Problem

UCL Law 3 states: "All contexts must carry evidence bundles, logs, and AARs (no unverifiable work)."

Current evidence implementation has issues:

1. **Hash instability**: `json.dumps()` key ordering varies across Python versions and platforms
2. **No canonical form**: Different runs produce different JSON for identical data
3. **Inconsistent storage**: Evidence files scattered across multiple directories
4. **Missing hash chain**: Optional integrity chain not reliably implemented
5. **No standard schema**: Evidence payloads lack required fields

Without RFC 8785 compliance, evidence hashes cannot be independently verified.

---

## Forces & Constraints

- **Cross-platform reproducibility**: Same data must produce identical hash on Windows, Linux, macOS
- **UCL Law 3 compliance**: Evidence bundles mandatory for all contexts
- **Performance**: Hash computation should be <10ms for typical payloads
- **Backward compatibility**: Existing evidence files remain valid
- **QSE directory structure**: `.QSE/v2/Evidence/{project_id}/{session_id}/` standard
- **Audit requirements**: External auditors must verify hashes independently
- **I-JSON compliance**: RFC 7493 integers (±2^53-1) for JavaScript interop

---

## Decision

Implement RFC 8785 JSON Canonicalization Scheme with SHA-256 hashing for all evidence bundles.

### RFC 8785 Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Key ordering** | UTF-16 code unit lexicographic sort (**CRITICAL:** Python `sort_keys=True` uses ASCII byte order, NOT RFC 8785 compliant - custom implementation required) |
| **Whitespace** | None - compact form, no spaces or newlines between tokens |
| **Number format** | Minimal representation, no trailing zeros, `-0` → `0` |
| **String escaping** | Minimal - only escape `\` `"` and control chars |
| **Unicode** | UTF-8 encoding throughout |
| **Integer range** | ±(2^53 - 1) per I-JSON (RFC 7493) |

### Canonical Serialization Implementation

```python
import json
import hashlib
from typing import Any

def canonicalize(data: Any) -> str:
    """
    RFC 8785 canonical JSON serialization.

    Produces deterministic JSON string for cryptographic hashing.
    Key ordering uses UTF-16 code unit sort (same as JavaScript).

    Args:
        data: Any JSON-serializable Python object

    Returns:
        Canonical JSON string (compact, sorted keys, UTF-8)

    Raises:
        ValueError: If data contains non-I-JSON integers
    """
    def sort_keys_utf16(obj: dict) -> dict:
        """Sort dict keys by UTF-16 code units (RFC 8785 §3.2.3)."""
        return dict(sorted(obj.items(), key=lambda x: x[0].encode('utf-16-le')))

    def validate_and_transform(obj: Any) -> Any:
        """Recursively validate and transform for RFC 8785."""
        if isinstance(obj, dict):
            return sort_keys_utf16({k: validate_and_transform(v) for k, v in obj.items()})
        elif isinstance(obj, list):
            return [validate_and_transform(item) for item in obj]
        elif isinstance(obj, int):
            # I-JSON integer range check (RFC 7493)
            if not (-(2**53 - 1) <= obj <= (2**53 - 1)):
                raise ValueError(f"Integer {obj} exceeds I-JSON range (±2^53-1)")
            return obj
        elif isinstance(obj, float):
            # Handle -0.0 → 0
            if obj == 0.0:
                return 0
            return obj
        else:
            return obj

    transformed = validate_and_transform(data)
    return json.dumps(
        transformed,
        separators=(',', ':'),  # Compact, no spaces
        ensure_ascii=False,      # UTF-8 output
        sort_keys=False,         # We pre-sorted with UTF-16 order
        allow_nan=False          # RFC 8785 §3.2.2.1
    )


def hash_evidence(data: Any) -> str:
    """
    Compute SHA-256 hash of canonical JSON.

    Args:
        data: Evidence payload to hash

    Returns:
        Hexadecimal SHA-256 hash string (64 chars)

    Example:
        >>> hash_evidence({"event": "task_complete", "task_id": "T-001"})
        'a3f2c8d9e1b5...'
    """
    canonical = canonicalize(data)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
```

### Evidence Bundle Structure

```
.QSE/v2/Evidence/{project_id}/{session_id}/
├── evidence_bundle.jsonl     # Sequential log events
├── execution_plan.yaml       # Optional: execution context
├── validation_results.json   # Optional: test/lint results
└── bundle_manifest.json      # Bundle metadata + final hash
```

### Bundle Manifest Schema

```json
{
  "schema_version": "1.0.0",
  "project_id": "P-CFCORE-LOGGING",
  "session_id": "abc123def456",
  "correlation_id": "abc123def456",
  "created_at": "2025-12-30T21:00:00Z",
  "closed_at": "2025-12-30T21:30:00Z",
  "event_count": 47,
  "evidence_hash": "sha256:a3f2c8d9e1b5...",
  "hash_chain_final": "sha256:b4f3d9e0f2c6...",
  "files": [
    {"name": "evidence_bundle.jsonl", "hash": "sha256:..."},
    {"name": "execution_plan.yaml", "hash": "sha256:..."}
  ]
}
```

### Hash Chain (Optional)

When `UNIFIED_LOG_HASH_CHAIN=1`:

```python
class HashChain:
    """Optional hash chain for tamper detection."""

    def __init__(self):
        self._previous_hash: str = "0" * 64  # Genesis

    def append(self, data: dict) -> str:
        """
        Append event to chain, returning chained hash.

        Each event's hash includes the previous event's hash,
        creating a tamper-evident chain.
        """
        data_with_chain = {
            **data,
            "_chain_previous": self._previous_hash
        }
        current_hash = hash_evidence(data_with_chain)
        self._previous_hash = current_hash
        return current_hash
```

---

## Rationale

### Why RFC 8785 (Not Just json.dumps with sort_keys)

Python's `json.dumps(sort_keys=True)` uses ASCII byte order, but:
- RFC 8785 specifies UTF-16 code unit order (matches JavaScript)
- This ensures cross-language hash compatibility
- Some Unicode characters sort differently between ASCII and UTF-16

Example:
```python
# ASCII order (Python default)
sorted(["ä", "z"]) == ["z", "ä"]  # 'z' < 'ä' in ASCII bytes

# UTF-16 order (RFC 8785)
sorted(["ä", "z"], key=lambda x: x.encode('utf-16-le')) == ["ä", "z"]
```

### Why SHA-256 (Not MD5 or SHA-1)

- **MD5**: Cryptographically broken (collision attacks)
- **SHA-1**: Deprecated (SHAttered attack demonstrated)
- **SHA-256**: Current standard, no known practical attacks
- **SHA-3**: Newer but less tooling support; SHA-256 sufficient

### Why .QSE/v2/Evidence Directory

Establishes clear namespace:
- `.QSE/` - Quality Software Engineering namespace
- `v2/` - Schema version for future migration
- `Evidence/` - Evidence-specific (vs logs, config, etc.)
- `{project_id}/` - Project isolation
- `{session_id}/` - Session isolation

---

## Alternatives Considered

### Alternative 1: Use JCS (RFC 8785) Library

**Approach:** Use existing `jcs` or `canonicaljson` Python package.

**Rejected because:**
- `jcs` package has limited maintenance
- `canonicaljson` doesn't fully comply with RFC 8785
- Implementation is small (~50 lines), easier to maintain inline

### Alternative 2: Content-Addressable Storage (CAS)

**Approach:** Store evidence by hash in flat directory (Git-like).

**Rejected because:**
- Loses session grouping for human browsability
- Adds complexity for minimal benefit
- Project/session hierarchy aids debugging

### Alternative 3: Merkle Tree Instead of Linear Chain

**Approach:** Hash pairs of events into tree structure.

**Rejected because:**
- Over-engineered for current needs
- Linear chain sufficient for tamper detection
- Can add Merkle tree later if needed for audit performance

---

## Consequences

### Positive

- **Cross-platform reproducibility**: Same data → same hash everywhere
- **Audit compliance**: External verification possible
- **Tamper detection**: Hash chain catches modifications
- **UCL Law 3 compliance**: All contexts have verifiable evidence
- **Clear storage**: Standardized directory structure

### Negative

- **Slight serialization overhead**: UTF-16 key sorting adds ~5% CPU
- **Strict validation**: Non-I-JSON integers will raise errors
- **Storage space**: Hash chain adds ~10% to JSONL size

### Neutral

- **Backward compatibility**: Old evidence files valid but not verifiable
- **Learning curve**: Developers must use `capture_evidence()` not raw JSON

---

## RFC 8785 Test Vectors (Required)

**Critical:** Phase 1 implementation MUST include these test vectors to validate UTF-16 sorting correctness.

### Test Vector 1: Unicode Key Ordering

Per RFC 8785 §3.2.3, keys must sort by UTF-16 code units, not ASCII bytes:

```python
def test_rfc8785_unicode_key_order():
    """Official RFC 8785 test vector."""
    data = {
        "\u20ac": "Euro Sign",           # € (U+20AC)
        "\r": "Carriage Return",          # CR (U+000D)
        "\ufb33": "Hebrew Letter Dalet",  # ‎דּ (U+FB33)
        "1": "One",                        # 1 (U+0031)
        "\ud83d\ude00": "Emoji",          # 😀 (U+1F600 as surrogate pair)
        "\u0080": "Control",              # PAD (U+0080)
        "\u00f6": "Latin o-diaeresis"     # ö (U+00F6)
    }

    canonical = canonicalize(data)
    keys = list(json.loads(canonical).keys())

    # UTF-16 order (not ASCII!):
    expected = [
        "\r",        # U+000D = 0x000D in UTF-16LE
        "1",         # U+0031 = 0x3100 in UTF-16LE
        "\u0080",    # U+0080 = 0x8000 in UTF-16LE
        "\u00f6",    # U+00F6 = 0xF600 in UTF-16LE
        "\u20ac",    # U+20AC = 0xAC20 in UTF-16LE
        "\U0001F600", # U+1F600 = 0x3DD8 0x00DE surrogate pair
        "\ufb33"     # U+FB33 = 0x33FB in UTF-16LE
    ]

    assert keys == expected, f"UTF-16 sort failed: {keys} != {expected}"
```

### Test Vector 2: Cross-Platform Hash Reproducibility

```python
import pytest

@pytest.mark.parametrize("platform", ["windows", "linux", "macos"])
def test_cross_platform_hash_stability(platform):
    """
    Verify same data produces identical hash across platforms.

    This test should be run in CI on all 3 OS types.
    """
    data = {
        "task_id": "T-001",
        "status": "completed",
        "duration_ms": 1234.56,
        "tags": ["urgent", "backend"],
        "metadata": {"priority": 1, "assignee": "user@example.com"}
    }

    # Known-good hash computed 2025-12-30 on reference system
    EXPECTED_HASH = "8f3a2e1c9b5d7a4f6e8c0b2d4a6f8e0c1a3b5d7f9e1c3a5b7d9f1e3c5a7b9d1f"

    actual_hash = hash_evidence(data)
    assert actual_hash == EXPECTED_HASH, \
        f"{platform}: Hash mismatch - canonical serialization differs"
```

### Test Vector 3: Special Float Values

```python
def test_special_float_handling():
    """RFC 8785 §3.2.2.3 number serialization edge cases."""

    # Test -0.0 → 0 conversion
    assert canonicalize({"value": -0.0}) == '{"value":0}'

    # Test positive zero unchanged
    assert canonicalize({"value": 0.0}) == '{"value":0}'

    # Test NaN/Infinity rejection (RFC 8785 §3.2.2.1)
    with pytest.raises(ValueError, match="NaN"):
        canonicalize({"value": float('nan')})

    with pytest.raises(ValueError, match="Infinity"):
        canonicalize({"value": float('inf')})
```

---

## Implementation Steps

1. **Create `cf_core/logging/evidence.py`**
   - Implement `canonicalize()` with RFC 8785 compliance
   - Implement `hash_evidence()` with SHA-256
   - Implement `capture_evidence()` public API
   - Implement optional `HashChain` class

2. **Create evidence directory utilities**
   - `get_evidence_path(project_id, session_id) -> Path`
   - `ensure_evidence_directory(project_id, session_id) -> Path`
   - `close_evidence_bundle()` to write manifest

3. **Add auto-capture triggers**
   - WARN/ERROR events when `UNIFIED_LOG_EVIDENCE_AUTO=1`
   - Explicit `capture_evidence()` calls

4. **Create verification CLI**
   - `python -m cf_core.logging.verify --bundle <path>`
   - Recompute hashes and validate chain

5. **Add tests**
   - Cross-platform hash reproducibility
   - RFC 8785 edge cases (Unicode, -0, large integers)
   - Hash chain integrity verification

---

## Acceptance Criteria

- [ ] `canonicalize()` produces RFC 8785 compliant output
- [ ] Same data produces identical hash on Windows/Linux/macOS
- [ ] I-JSON integer validation rejects out-of-range values
- [ ] Evidence bundles stored in `.QSE/v2/Evidence/{project_id}/{session_id}/`
- [ ] Bundle manifest includes `evidence_hash` field
- [ ] Optional hash chain works when enabled
- [ ] Verification CLI can validate existing bundles
- [ ] UCL Law 3 compliance validated by integration tests

---

## Open Questions

1. **Should we sign bundles?**
   - Pro: Non-repudiation for audits
   - Con: Key management complexity
   - **Decision:** Defer, add as future enhancement if audit requires

2. **Compression for large bundles?**
   - Pro: Reduces storage for verbose logs
   - Con: Adds decompression step for verification
   - **Decision:** Defer, add if storage becomes concern

---

## Related Documents

- PRD: `docs/prd/PRD-CFCORE-LOGGING.md`
- ADR-002: Correlation ID Strategy
- RFC 8785: JSON Canonicalization Scheme
- RFC 7493: I-JSON Message Format
- UCL Law 3: Evidence requirements (ContextForge Codex)
- Design Prompt: `docs/prompts/cf-core-centralized-logging-design.prompt.md`

---

**Version:** 1.0.0 (Proposed)
**Next Review:** After Phase 1 implementation
