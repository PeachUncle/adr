# ADR-0003: Evidence Traceability Standard

**Date:** 2025-12-26  
**Status:** Accepted  

## Context

Regulated AI workflows require auditable decision trails. When a system produces an output (summary, recommendation, alert), stakeholders must be able to trace that output back to its original source evidence.

This is especially critical in financial services, healthcare, and other regulated industries where:
- Compliance teams may audit AI-assisted decisions
- Model outputs must be defensible under regulatory scrutiny
- Errors or hallucinations must be diagnosable to root cause

Without a consistent traceability standard, each module would implement its own approach, creating gaps and inconsistencies.

## Decision

All modules in the Regulated AI Workflow Toolkit must maintain **evidence chains** with the following requirements:

### 1. Raw Evidence Preservation
- Original API responses, HTML snapshots, or source documents must be saved
- Raw evidence is immutable once captured
- Location: `data/evidence/raw/`

### 2. Schema Versioning
- All artifacts use explicit schema versions (e.g., `normalized_signal.v1`, `hydrated_signal.v1`)
- Schema changes require version increments
- Older artifacts remain valid under their declared schema

### 3. Evidence Pointers
- Every processed artifact must include `evidence` fields pointing to upstream sources
- Pointers use relative paths within the module
- Chain must be traceable: output → intermediate → raw

### 4. Timestamps
- All artifacts include `collected_at` (ISO 8601 UTC)
- Enables temporal debugging and audit trails

## Example Evidence Chain
```
synthesis_output.v1
  └── evidence: retrieval_set.v1
        └── evidence: hydrated_signal.v1
              └── evidence: normalized_signal.v1
                    └── evidence: raw RSS snapshot
```

## Consequences

**Benefits:**
- ✅ Any output can be audited back to original source
- ✅ Supports compliance review and regulatory defense
- ✅ Enables debugging of model errors or data quality issues
- ✅ Consistent pattern across all modules

**Costs:**
- ⚠️ Increased storage requirements (raw evidence preserved)
- ⚠️ Slightly higher implementation complexity per module
- ⚠️ Must maintain discipline in evidence pointer hygiene

## Modules Implementing This Standard

- Market Intelligence Monitor (MVP complete)
- ROI Decision Engine (planned)
- Requirements Guardrails (planned)
- Compliance RAG Assistant (planned)

## Links

- Market Intelligence Monitor: [`/modules/market-intelligence-monitor/`](../../modules/market-intelligence-monitor/)
- Related ADR: [ADR-0001 - Verification-First Scaffold](ADR-0001%20-%20first%20decision.md)