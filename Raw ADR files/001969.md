# ADR-003: Batch Semantics & Validation Gates

Decision: Batch processing enforces BATCH_SIZE=50 with ALLOW_PARTIAL override; StateGraph wires validation pipeline with manifest recording.

## Status Update (PR-003)

- Implemented BatchProcessor with size enforcement and review.ndjson creation on insufficient nouns.
- Added ALLOW_PARTIAL=1 override with required PARTIAL_REASON env var and manifest logging.
- Created BatchResult with deterministic batch_id and hash proofs for input/output verification.
- Wired collect_nouns → validate_batch nodes in StateGraph with checkpointer integration.
- Added comprehensive contract tests for batch size enforcement and manifest recording.
- Integration tests verify graph pipeline execution and state preservation.

## Context

The pipeline must process nouns in deterministic batches while maintaining safety gates:

- Default batch size of 50 nouns prevents partial processing that could skew results
- ALLOW_PARTIAL override allows flexibility for testing/development with clear audit trail
- Manifest recording provides deterministic verification of processing integrity
- StateGraph integration ensures resumable execution with proper checkpointer wiring

## Decision

- BatchProcessor enforces BATCH_SIZE=50 (configurable via env)
- Insufficient nouns abort processing and create review.ndjson unless ALLOW_PARTIAL=1
- ALLOW_PARTIAL requires PARTIAL_REASON env var explaining override
- Batch IDs are deterministic SHA-256 hashes of sorted noun content
- Manifest includes input/output hash proofs and processing metadata
- StateGraph nodes: collect_nouns → validate_batch with checkpointer support
- BatchAbortError provides clear error messaging with review file path

## Consequences

- ✅ Deterministic batch processing with hash verification
- ✅ Safety gates prevent accidental partial processing
- ✅ Clear audit trail for ALLOW_PARTIAL overrides
- ✅ Resumable pipeline execution via StateGraph + checkpointer
- ✅ Comprehensive test coverage for all batch semantics
