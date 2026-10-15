---
post_title: "ADR: cf_core Test Import Strategy (Stub vs Skip vs Remove)"
author1: "James Hardy"
post_slug: "adr-cf-core-test-stub-strategy"
microsoft_alias: "jameshardy"
featured_image: ""
categories: ["Architecture", "Testing", "Quality"]
tags: ["ADR", "cf_core", "pytest", "stubs", "skip"]
ai_note: "Drafted with AI assistance; reviewed by engineer"
summary: "Decide and document a pragmatic strategy to resolve missing cf_core imports in tests while preserving test stability and evidence generation: stubbing active modules, skipping deprecated tests, and removing obsolete ones with sign-off."
post_date: "2025-11-28"
---

## Status

Proposed (Phase 1.6) — Immediate implementation recommended to reduce pytest collection errors.

## Context

Pytest collection reports multiple `ModuleNotFoundError` failures for modules under `cf_core` that either:
- Were renamed or relocated,
- Are not yet implemented,
- Or represent deprecated/obsolete components.

Affected test paths (examples):
- `tests/cf_core/config/test_models.py` → imports `cf_core.config`
- `tests/cf_core/models/test_task.py` → imports `cf_core.models`
- `tests/cf_core/unit/models/test_context.py` → imports `cf_core.unit.models`

These errors block smoke/quick lanes and hinder stabilizing the suite.

## Decision

Adopt a tiered strategy optimized for fast stabilization, evidence-first operation, and clear rollback:

1. **Stub (Preferred for active features)**
   - Create minimal stub packages for `cf_core/config` and `cf_core/models` that satisfy imports and expose lightweight, type-safe placeholders.
   - Purpose: Unblock collection rapidly; enable unit tests to execute where possible; avoid `sys.exit` patterns.

2. **Skip (For deprecated or pending redesign)**
   - Mark tests with `@pytest.mark.skip(reason="Module deprecated or relocated")` where functionality is not intended to return.
   - Purpose: Maintain signal while preventing false failures; document rationale in-line and in this ADR.

3. **Remove (With architecture sign-off only)**
   - Delete truly obsolete tests when replacement coverage exists or feature is retired.
   - Purpose: Reduce noise; ensure clarity of system intent; preserve lineage via PR and ADR references.

## Rationale

- **Logs First / Trust Nothing, Verify Everything**: Stubs/skip allow tests to run and generate artifacts; removal requires governance.
- **Workspace First**: Minimal changes to satisfy imports without speculative re-implementation.
- **Golden Ratio**: Focus effort where it yields the largest reduction in collection errors quickly.

## Implementation Plan

### A. Create Minimal Stubs

- `cf_core/config/__init__.py`
- `cf_core/models/__init__.py`

Each stub should:
- Provide simple dataclasses/types expected by tests (if discoverable), or no-op placeholders.
- Avoid side effects; be import-safe under pytest.
- Include clear TODOs and ADR reference in docstring for transparency.

### B. Introduce Targeted Skips

- Update affected tests to use `@pytest.mark.skip` with explicit reason if a module is deprecated.
- Document the mapping in this ADR (Appendix A) for traceability.

### C. Governance for Removals

- When removal is necessary, link PR to this ADR and add a brief AAR note explaining replacement coverage.

### D. Rollback & Verification

- After stubs/skips applied, run:

```powershell
pytest --collect-only -q 2>&1 | Select-Object -Last 10
```

- Track error reduction in `docs/ACTIVE-WORK-CHECKLIST.md`.
- Incrementally lift temporary `--ignore` globs in VS Code tasks and CI once error count is acceptable.

## Consequences

- **Positive**: Rapid decrease in collection errors; smoke/quick lanes can proceed; coverage baseline work unblocked.
- **Neutral**: Some tests will exercise placeholders; assertions may need refinement once real implementations land.
- **Negative**: Risk of masking gaps if stubs persist too long; mitigated via TODOs, ADR linkage, and follow-up tasks.

## Alternatives Considered

- Full re-implementation before stabilization — rejected (time cost high, blocks immediate recovery).
- Global ignore of `tests/cf_core/*` — temporary only; lacks evidence and reduces signal.

## References

- `docs/TEST-HARNESS-REFORM-TEMPLATE.md` — pytest conversion template
- `docs/ACTIVE-WORK-CHECKLIST.md` — tracking and validation commands
- AAR artifacts listed in the checklist

## Appendix A — Affected Tests & Proposed Path

| Test Path | Import | Proposed Action |
|-----------|--------|-----------------|
| tests/cf_core/config/test_models.py | cf_core.config | Stub `cf_core/config` now |
| tests/cf_core/models/test_task.py | cf_core.models | Stub `cf_core/models` now |
| tests/cf_core/unit/models/test_context.py | cf_core.unit.models | Skip (pending redesign) |

Note: Final actions may adjust based on deeper inspection; track updates here.
