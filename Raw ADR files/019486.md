# ADR-007: Data Integrity Verification

**Date:** 2026-01-02
**Status:** Accepted

## Context

The project is scaling from 50 to 300+ ASRS records. For dissertation reproducibility,
we need guarantees that:

1. Raw source data has not been modified since acquisition
2. Any data corruption is detected before analysis runs
3. Data provenance is documented in machine-readable format

Without integrity verification, silent data corruption or accidental edits to the
raw CSV could invalidate downstream analysis without any warning.

## Decision

Implement SHA-256 hash verification and file locking for raw data files.

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `compute_raw_hash()` | `R/data_integrity.R` | Generate SHA-256 hash |
| `verify_raw_integrity()` | `R/data_integrity.R` | Verify hash, abort on mismatch |
| `lock_raw_data()` | `R/data_integrity.R` | Set file to read-only (chmod 444) |
| `unlock_raw_data()` | `R/data_integrity.R` | Restore write permissions (chmod 644) |
| `create_manifest()` | `R/data_integrity.R` | Write JSON manifest with metadata |
| `read_manifest()` | `R/data_integrity.R` | Read manifest, optionally verify |

### Manifest Schema

The manifest (`data/data_manifest.json`) captures:

- Source metadata (NASA ASRS, fetch date, curation notes)
- File metadata (name, size, modification time)
- SHA-256 hash for verification
- Data summary (record count, column count, date range)
- Integrity status (locked flag, verification command)

### Integration

The import pipeline (`scripts/import_data.R`) now:

1. Verifies existing manifest hash before import (if manifest exists)
2. Runs import as before
3. Locks raw data file (read-only)
4. Creates/updates manifest with current hash

## Consequences

### Positive

- **Reproducibility**: Hash verification ensures identical source data across runs
- **Fail-loud**: Integrity failures abort with clear error messages
- **Provenance**: Manifest documents data source and acquisition details
- **Protection**: File locking prevents accidental modification

### Negative

- **Unix-only locking**: `chmod` is not fully supported on Windows
- **Manual unlock**: Raw data edits require explicit `unlock_raw_data()` call

### Mitigations

- Windows users receive warning message with manual permission instructions
- `unlock_raw_data()` function provided for intentional updates

## Dependencies

- `digest` package for SHA-256 hashing (already in renv.lock)
- `jsonlite` package for manifest JSON (already in renv.lock)

## References

- ADR-005: Quality Gates - Fail-loud error handling philosophy
- ADR-006: Data Product Location - Raw data stored in `data/`
