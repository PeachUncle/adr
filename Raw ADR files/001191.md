# ADR: SessionManager Standardization (CF_CORE CLI & QSE Integration)

Status: Draft
Date: 2025-11-10
WorkId: P-CF-CLI-ALIGNMENT-001
Authors: CF QSE Agent
Decision Context: Unify existing Python `ContextForgeUnifiedSessionManager` and TypeScript `session-manager.ts` semantics; establish minimal, race-safe session lifecycle with standardized evidence emission to replace ad-hoc backfill.

## Problem
Session coverage remediation required manual backfill (`backfill_evidence_bundle.py`). Multiple session manager patterns exist (Python unified manager, diagnostic research scripts, TypeScript TaskMan session manager). Without a unified contract, duplication risk and uneven evidence emission persist; CI coverage gating cannot reliably enforce ≥80% across latest 20 sessions.

## Forces & Constraints
- Need reuse window (<4h) for shortContext slug to group related sessions without inflating counts.
- Must provide atomic daily sequence increment (SEQ) per shortContext to generate `QSE-LOG-[shortContext]-[YYYYMMDD]-[SEQ].yaml` deterministically.
- Evidence emission must be automatic at start/end (idempotent) to eliminate manual backfill.
- Cross-platform locking (Windows + WSL) needed for concurrent invocations.
- Backward compatibility: existing evidence.jsonl remains valid; detector still accepts legacy bundle naming patterns.
- Avoid over-engineering (Complex Solution Bias learning recorded) – start with smallest viable API.

## Decision
Implement a thin `session_manager_adapter.py` providing a minimal API:
```python
get_or_create_session(short_context: str) -> SessionInfo
end_session(status: Literal['success','error']) -> None
emit_evidence_bundle(payload: dict, mode: Literal['append','standardize']='append') -> Path
```
Behavior: On `get_or_create_session`, acquire file lock (`portalocker`). Determine reuse vs new sequence by scanning existing session log filenames in date folder. Reuse if last session <4h and same slug; else increment sequence. On start and end, emit evidence record lines to `evidence.jsonl` (create if missing). Each record contains correlation IDs, event type, timestamp, sha256(payload) truncated, parentEvent (if standardize mode), and version metadata.

## Rationale
This adapter leverages existing unified manager for rich console, logging, ETW integration, but adds explicit reuse window logic and standardized evidence emission. Keeping the contract small eases testing and avoids divergence from TypeScript implementation.

## Alternatives Considered
1. Extend existing `ContextForgeUnifiedSessionManager` directly – rejected to keep separation of concerns (avoid large diff; adapter can be replaced later).
2. Build new bespoke manager ignoring existing code – rejected (duplication; lost functionality).
3. Defer standardization until >20 sessions exist – rejected (blocks proactive CI gate readiness).

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Lock contention under heavy parallel start | Delayed session creation | Use short retry with jitter + clear error after timeout |
| Divergent evidence formats | Coverage regression | Provide version field + fallback ingestion for legacy lines |
| Over-engineering (feature creep) | Delay implementation | Enforce minimal API scope per constitution rule |
| Backfill script confusion | Double writes | Mark backfill tool deprecated post rollout; add guard detecting standardized records |

## Implementation Steps (Ordered)
1. Create adapter module with locking, reuse window, sequence logic.
2. Integrate adapter into entry points needing session creation (cf_cli, dbcli, test harness).
3. Add unit tests: reuse window, sequence increment, concurrency (threads), idempotent emission, legacy coexistence.
4. Configure CI coverage gate (warning mode) consuming `evidence_coverage_scan.py` JSON output.
5. Update README/integration docs with usage examples.
6. Deprecate manual backfill tool (warn if run when evidence.jsonl already standardized).
7. Flip CI gate to enforce (fail) after burn-in.

## Acceptance Criteria
- Adapter returns deterministic sessionId with correct sequence and reuse boolean.
- Evidence file contains ≥2 standardized records (start/end) per session without duplication.
- Coverage scan >=80% (enforced once session count ≥20) with gate script integrated into CI.
- All tests pass (reuse, concurrency) on Windows and WSL.

## Open Questions
- Evidence record schema extension for future test coverage metrics embedding? (Defer)
- Sequence persistence beyond daily boundary for long (>24h) sessions? (Edge case; treat as new day)

## Future Extensions
- Append COF dimension completion statuses dynamically.
- Embed quality gate summary (duplication factor, coverage) into end-session record.

---
Version: 0.1.0 (Draft)
Next Review: After adapter tests green and coverage gate warning mode active.
