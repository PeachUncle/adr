---
title: FCN Version Activation & Promotion Workflow
doc_type: decision-record
adr: 003
status: Accepted
version: 0.2.0
owner: siripong.s@yuanta.co.th
approver: siripong.s@yuanta.co.th
created: 2025-10-09
last_reviewed: 2025-10-17
next_review: 2026-04-09
classification: Internal
tags: [decision, products, governance, versioning]
related:
  - adr-002-product-doc-structure.md
  - ../../../../_policies/document-control-policy.md
  - ../../ba/products/structured-notes/fcn/specs/SUPERSEDED_INDEX.md
---

# FCN Version Activation & Promotion Workflow

## Context
FCN specifications evolve (v1.0 baseline, v1.1 step-down extension). We require a governed path from Proposed → Active → Deprecated to ensure economic, risk, and implementation alignment.

## Version Events Timeline

The following timeline documents key FCN version lifecycle events:

| Date | Version | Event | Description |
|------|---------|-------|-------------|
| 2025-10-09 | v1.0 | Creation | Initial baseline FCN specification created; unconditional par recovery at maturity |
| 2025-10-17 | v1.1.0 | Introduction | Capital-at-risk settlement, autocall/knock-out, issuer governance, and barrier monitoring type added (BR-020–026); new parameters: issuer, put_strike_pct, knock_out_barrier_pct, auto_call_observation_logic, barrier_monitoring_type |
| 2025-10-17 | v1.0 | Superseded | v1.0 marked Superseded by v1.1.0; retained for historical audit; new trades must use v1.1.0 unless explicit governance approval granted |

**Supersession Reference**: See [SUPERSEDED_INDEX.md](../../ba/products/structured-notes/fcn/specs/SUPERSEDED_INDEX.md) for machine-readable supersession metadata and governance enforcement rules.

## Decision
Establish a promotion pipeline:
Concept → Proposed → (Calibration & Review) → Active → Deprecated → Removed

Promotion from Proposed → Active requires a completed Activation Checklist:
1. Parameter table completeness & naming aligned with conventions.
2. Payoff branch taxonomy codes referenced and stable.
3. Step-down or structural extensions documented with backward compatibility notes.
4. Test vectors: minimum normative subset flagged (edge, baseline, KI recovery, physical).
5. Risk calibration review (scenario coverage & stress).
6. Implementation parity confirmation (engine or pricing model).
7. Changelog entry added (with difference summary).
8. Alias / naming conflicts resolved or flagged (deprecation policy integrated).
9. Lifecycle mapping (asset buckets / events) cross-checked.

## Rationale
- Provides gating for correctness & consistency.
- Test vectors ensure reproducible validation.
- Explicit alias auditing reduces semantic drift.

## Alternatives Considered
1. Simple “merge & declare Active” — Rejected (insufficient controls).
2. Heavy-weight change board for every minor revision — Rejected (adds latency, low agility).
3. Tag-based Git semantics only — Rejected (does not capture process artifacts like calibration sign-off).

## Consequences
### Positive
- High confidence in Active specs.
- Clear audit path.
### Negative
- Extra authoring effort early.
- Requires minimal automation to avoid manual drift.

## Activation Checklist Status

The following table tracks completion status of activation checklist items for FCN v1.1.0:

| Checklist Item | Status | Notes | Reference |
|----------------|--------|-------|-----------|
| Parameter table completeness & naming aligned | ✅ Complete | put_strike_pct, issuer, knock_out_barrier_pct, auto_call_observation_logic, barrier_monitoring_type added | [fcn-v1.1.0.md](../../ba/products/structured-notes/fcn/specs/fcn-v1.1.0.md) |
| Test vectors baseline flagged | ✅ Complete | Normative capital-at-risk and autocall test vectors created | [test-vectors/](../../ba/products/structured-notes/fcn/test-vectors/) |
| Issuer whitelist integration | ✅ Complete | BR-022 enforces issuer validation | [issuer_whitelist.md](../../ba/products/structured-notes/fcn/issuer_whitelist.md) |
| Settlement type alignment (canonical values) | ✅ Complete | settlement_type harmonization without alias stage | [schema-diff-v1.0-to-v1.1.md](../../ba/products/structured-notes/fcn/schema-diff-v1.0-to-v1.1.md) |
| Capital-at-risk constraints (put_strike_pct ordering) | ✅ Complete | BR-024, BR-025 define validation and settlement logic | [business-rules.md](../../ba/products/structured-notes/fcn/business-rules.md) BR-024, BR-025 |
| Normative test vector expansion | ⏳ Pending | Additional edge cases and stress scenarios required | Future work |
| Alias linter implementation | ⏳ Pending | Phase 1 alias detection and validation tooling | See ADR-004 |

**Business Rules Coverage**: FCN v1.1.0 introduces BR-020 (autocall barrier range validation), BR-021 (autocall trigger logic), BR-022 (issuer whitelist enforcement), BR-023 (autocall precedence), BR-024 (put strike validation), BR-025 (capital-at-risk settlement), and BR-026 (barrier monitoring type validation). BR-011 (unconditional par recovery) deprecated in favor of capital-at-risk settlement.

**Supersession Statement**: As of 2025-10-17, FCN v1.0 is Superseded. FCN v1.1.0 is the normative Active specification for all new trades. Use of v1.0 for new bookings requires explicit governance approval.

## Metrics
- Average Proposed → Active cycle time.
- % of Active specs with complete normative test vector set.
- Drift incidents (implementation divergence) per quarter.

## Follow-up Tasks
- [ ] Create activation checklist template file.
- [ ] Add validator rule: Proposed spec must reference checklist issue ID.
- [ ] Tag normative test vectors with `normative: true`.

## Change Log
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | 2025-10-09 | siripong.s@yuanta.co.th | Initial draft |
| 0.2.0 | 2025-10-17 | siripong.s@yuanta.co.th | Accepted; added Version Events timeline (v1.0 creation, v1.1.0 introduction, v1.0 superseded); added Activation Checklist Status table with completion tracking; added BR-020–026 references and supersession statement; linked SUPERSEDED_INDEX.md |
