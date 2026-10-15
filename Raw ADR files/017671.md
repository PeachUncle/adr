---
type: DRR
winner_id: hdf5-hierarchical-data-format-5
created: 2025-12-23T11:54:04-08:00
content_hash: 7f988cf014091e0c81690a1ec993d46d
---

# Use HDF5 for Pivot Disk Serialization

## Context
SpeedData's pivot component needs a disk serialization format for row-to-column transformation output. The format must support column-oriented storage for efficient signal analysis, integrate with Roelle DataSet (v0.2 roadmap requirement), produce discrete file-based output (Sets containing 2-100 channels), and enable time-range queries with minimal implementation complexity for the v0.2 timeline (February 2025).

## Decision
**Selected Option:** hdf5-hierarchical-data-format-5

We decided to use HDF5 (Hierarchical Data Format 5) as the disk serialization format for SpeedData's pivot component.

## Rationale
All five L2 hypotheses achieved R_eff = 1.00 (perfect assurance score), requiring decision based on qualitative risk factors. HDF5 was selected for the following reasons:

**Lowest Integration Risk**: Requires only 1-5 lines of deserialization code per signal, compared to 15-40 LOC for alternatives.

**Existing Proof-of-Concept**: catcol.py already demonstrates HDF5 export working with SpeedData's architecture. No other hypothesis has working implementation.

**Better Context Alignment**: CL2 congruence (general Python ecosystem vs SpeedData telemetry) outperforms Parquet and Arrow IPC's CL1 mismatch (big data/IPC vs small archival files).

**Mature Ecosystem**: h5py library provides stable, well-documented API. h5dump and HDFView enable third-party inspection.

**Hierarchical Structure Match**: Signal→dataset, Channel→group, Set→file mapping aligns naturally with SpeedData's data model (context.md lines 30, 35, 41).

**Fatal Disqualifiers for Alternatives**: SQLite's row-major storage contradicts column-oriented requirement (context.md line 47). Custom format has no implementation and creates long-term maintenance burden. Parquet and Arrow IPC have context mismatches for small archival files (8KB-80MB vs multi-GB big data).

### Characteristic Space (C.16)
- Column-oriented storage: HDF5 datasets store signals as contiguous arrays
- Hierarchical structure: Groups organize channels, files represent sets
- Self-describing: Metadata embedded in file (signal names, units, timestamps)
- Compression: Built-in gzip/lzf reduces file size for archival
- Random access: Efficient time-range queries via dataset slicing
- NumPy integration: h5py datasets slice directly to numpy.ndarray
- Third-party tooling: h5dump (CLI), HDFView (GUI), h5ls (inspection)

## Consequences
**Immediate Actions Required**:
- Add h5py dependency to requirements (Python package, ~3MB)
- Enhance catcol.py proof-of-concept to production quality
- Implement Roelle DataSet loader (1-5 LOC wrapper)

**Accepted Trade-offs**:
- Hierarchical traversal overhead for multi-channel access (acceptable for 2-100 channels per file)
- HDF5 format version compatibility management required for long-term archival
- Dependency on h5py library (stable but external)

**Risk Mitigation**:
- catcol.py proof-of-concept reduces implementation uncertainty
- h5dump enables file inspection independent of SpeedData codebase
- Format version compatibility managed via h5py's built-in migration support

**v0.2 Timeline Impact**: Positive - existing catcol.py implementation accelerates v0.2 delivery (February 2025 deadline).
