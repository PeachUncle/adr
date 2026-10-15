---
title: Parameter Alias & Deprecation Policy (Structured Notes)
doc_type: decision-record
adr: 004
status: Accepted
version: 0.2.0
owner: siripong.s@yuanta.co.th
approver: siripong.s@yuanta.co.th
created: 2025-10-09
last_reviewed: 2025-10-17
next_review: 2026-04-09
classification: Internal
tags: [decision, naming, products, governance]
related:
  - ../../../../_policies/tagging-schema.md
  - ../../../../_policies/document-control-policy.md
  - adr-002-product-doc-structure.md
---

# Parameter Alias & Deprecation Policy (Structured Notes)

## Context
Legacy parameter `min_upside_guarantee_pct` no longer semantically accurate (symmetric absolute guarantee). Replacement: `min_abs_move_guarantee_pct`. Need controlled phased alias management synchronized with spec versions (v1.0 baseline vs v1.1+).

## Decision
Adopt a 4-stage alias life cycle:
1. Introduce: Both fields permitted; canonical = new name; legacy flagged with banner.
2. Stable Dual: At least one minor version cycle; tooling warns on new usage of legacy.
3. Deprecation Notice: Legacy marked “Deprecated – removal next major”.
4. Removal: Legacy eliminated in next major spec; changelog & schema updated.

Documentation Requirements:
- Conventions file lists alias mapping.
- Each spec containing alias includes “Alias Table” with: legacy_name, new_name, stage, first_version, removal_target.
- Test vectors stop referencing legacy once stage 3 begins.

## Rationale
- Prevents sudden breaking changes.
- Provides clarity for implementation / data migrations.
- Aligns with economic semantics clarity.

## Alternatives Considered
1. Immediate rename – risk of breaking downstream dependencies.
2. Permanent alias retention – increases cognitive & validation overhead.

## Enforcement
Automation phases:
- Phase 1: Lint warns if legacy appears without alias banner.
- Phase 2: Fails PR if legacy used past deprecation stage.
- Phase 3: Removal verified (no occurrences) before tagging new major.

## Follow-up Tasks
- [ ] Add alias mapping section to conventions file.
- [ ] Implement alias linter (Phase 1) — TODO: CI validation to detect legacy parameter usage without deprecation notice banner.
- [ ] Add spec checklist item “Alias Table present if any alias active.”


## Current Alias Inventory

**Status as of 2025-10-17**: No active parameter aliases currently deployed in FCN specifications.

**Historical Context**:
- The `settlement_type` parameter underwent harmonization from v1.0 to v1.1.0 with canonical value alignment (e.g., `physical-settlement`, `cash-settlement`) but did NOT require an intermediate alias stage. The change was backward-compatible through value normalization.

**Future Candidates**:
The following parameter scenarios may require alias management in future versions:
1. **Mixed settlement semantics**: If v1.2+ introduces hybrid settlement modes that blend physical and cash mechanics, a transitional alias may be needed.
2. **Barrier monitoring type activation**: When `barrier_monitoring_type='continuous'` becomes normative (currently reserved in v1.1.0), documentation may require an alias phase to differentiate from implicit discrete-only behavior in v1.0.
3. **Coupon memory logic variants**: If memory accumulation logic diversifies (e.g., partial memory, capped memory), legacy `is_memory_coupon` boolean may need alias to structured enum.

These candidates will be evaluated under the 4-stage lifecycle defined in this ADR if/when introduced.

## Change Log
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | 2025-10-09 | siripong.s@yuanta.co.th | Initial draft |
| 0.1.1 | 2025-10-17 | siripong.s@yuanta.co.th | Added Current Alias Inventory section documenting no active aliases; noted settlement_type harmonization without alias stage; identified future alias candidates (mixed settlement, barrier monitoring continuous mode, coupon memory variants); clarified Phase 1 linter task |
| 0.2.0 | 2025-10-17 | siripong.s@yuanta.co.th | Accepted; policy framework established with 4-stage lifecycle, enforcement phases, and future candidate identification |
