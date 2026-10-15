---
title: Documentation Governance Approach
doc_type: decision-record
adr: 001
status: Accepted
version: 0.2.0
owner: siripong.s@yuanta.co.th
approver: siripong.s@yuanta.co.th
created: 2025-10-09
last_reviewed: 2025-10-17
next_review: 2026-10-09
classification: Internal
tags: [architecture, decision, governance]
related:
  - ../../../../_policies/document-control-policy.md
---

# Documentation Governance Approach

## Context
Need for structured, trustworthy documentation base.

## Decision
Adopt structured taxonomy, mandatory metadata, role-specific lifecycles, ADR transparency.

## Rationale
Reduces fragmentation; enables automation; provides auditability.

## Alternatives Considered
1. Ad-hoc docs (rejected: inconsistency risk)
2. External wiki (rejected: drift risk)

## Consequences
### Positive
- Higher trust
- Easier onboarding
### Negative
- Authoring overhead
- Automation maintenance

## Current Governance Artifacts

The following governance artifacts implement this decision:

1. **Supersession Index**: [SUPERSEDED_INDEX.md](../../ba/products/structured-notes/fcn/specs/SUPERSEDED_INDEX.md)
   - Tracks superseded FCN specification versions
   - Provides machine-readable format for CI/CD enforcement
   - Status: Active (v1.0 → Superseded as of 2025-10-17)

2. **Schema Diff Documents**: [schema-diff-v1.0-to-v1.1.md](../../ba/products/structured-notes/fcn/schema-diff-v1.0-to-v1.1.md)
   - Documents parameter changes between versions
   - Provides migration guidance
   - Status: Active

3. **Normative Specifications**:
   - [fcn-v1.1.0.md](../../ba/products/structured-notes/fcn/specs/fcn-v1.1.0.md) (Active, normative)
   - [fcn-v1.0.md](../../ba/products/structured-notes/fcn/specs/fcn-v1.0.md) (Superseded)

These artifacts ensure version governance transparency and enable automated validation of specification usage compliance.

## Follow-up Tasks
- [ ] Implement metadata validator (TODO: pending)
- [ ] Implement stale review checker (TODO: pending)

## Change Log
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | 2025-10-09 | siripong.s@yuanta.co.th | Initial draft |
| 0.2.0 | 2025-10-17 | siripong.s@yuanta.co.th | Accepted; added Current Governance Artifacts section referencing SUPERSEDED_INDEX.md, schema-diff, and normative specs; clarified follow-up task status |
