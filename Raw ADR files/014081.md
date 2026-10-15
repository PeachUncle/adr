# ADR: Ideas Workflow Deprecation

**Date:** 2025-11-03  
**Status:** Accepted  
**Deciders:** Lane D (Program Operations), Lane C (DevOps & Automation), Lane B (Narrative & Enablement)

## Context

The Plaincraft repository implemented an ideas-based workflow where markdown files in `/ideas/` served as the source of truth for feature planning, with tight integration to GitHub Projects v2 for lifecycle management. This system included:

- 86 idea files tracking units, compositions, architecture items, and playbook entries
- Scripts for idea intake, validation, and synchronization with GitHub Issues
- GitHub Projects v2 schema with custom fields (ID, Type, Lane, Status, Owner, Priority, Release)
- Reconciliation scripts to maintain status synchronization between idea files and project boards
- Backlog pilot procedures for drift detection and audit

## Decision

We have decided to **deprecate and remove the entire ideas workflow** effective November 3, 2025, including:

1. **Ideas folder structure** - Archived to `/_archive/ideas-2025-11-03-deprecated/`
2. **Lifecycle scripts** - `idea-intake.mjs`, `ideas-to-issues.mjs`, `validate-ideas.mjs`, `sync-ideas-checklists.mjs`
3. **GitHub Projects integration** - Project schema, status reconciliation, audit procedures
4. **Lane D responsibilities** - Lifecycle governance, backlog management, project stewardship removed from scope

## Rationale

### Why Remove Ideas Workflow

1. **Scope Reduction**: Lane D responsibilities have been redefined to exclude project-based lifecycle governance
2. **Complexity vs Value**: The bidirectional sync between idea files and GitHub Projects added maintenance overhead without sufficient ROI
3. **Simplification**: Reducing workflow complexity allows teams to focus on direct GitHub issue/PR workflows
4. **Documentation Shift**: GitHub Pages, Storybook, and Playbook now serve as primary documentation sources

### Why Now

- Lane D role evolution required immediate clarity on deprecated responsibilities
- Active maintenance burden (reconciliation scripts, drift detection) outweighed benefits
- No active blockers - all in-flight work can continue via standard GitHub workflows

## Consequences

### Positive

- **Reduced Complexity**: Eliminates dual status management (files + Projects)
- **Lower Maintenance**: No reconciliation scripts, drift audits, or intake automation to maintain
- **Clearer Lane D Scope**: Lane D can focus on redefined responsibilities
- **Simplified Onboarding**: New contributors learn standard GitHub workflows only

### Negative

- **Historical Reference Loss**: 86 ideas archived, requiring archive searches for context
- **Documentation Gap**: Lane D's new scope needs definition and documentation
- **Workflow Transition**: Teams must adapt to working without the ideas structure

### Neutral

- **Archive Preservation**: All 86 idea files preserved in `/_archive/ideas-2025-11-03-deprecated/`
- **Script Deprecation**: Deprecated scripts remain but exit immediately with error messages
- **CI/CD Impact**: None - pipeline fully cleaned by Lane C

## Implementation

### Completed (Lane C - DevOps & Automation)

- [x] Archived `/ideas/` folder to `/_archive/ideas-2025-11-03-deprecated/` (86 files)
- [x] Updated deprecated scripts to exit with clear error messages
- [x] Removed `ideas` alias from guardrails configuration
- [x] Updated policy allowlist to ignore deprecated scripts
- [x] Verified no CI/CD dependencies on ideas workflow
- [x] Created Lane C technical report

### Completed (Lane B - Narrative & Enablement)

- [x] Created this ADR documenting the decision
- [x] Updated root README.md with deprecation notice
- [x] Updated template documentation with deprecation notices
- [x] Updated playbook patterns index with deprecation
- [x] Created stub `/ideas/README.md` explaining deprecation

### Required (Lane D - Program Operations)

- [ ] Document current Lane D responsibilities (without lifecycle governance)
- [ ] Update Lane D runbook/documentation
- [ ] Update training materials
- [ ] Revise onboarding guides

## Migration Path

### For Historical Research

1. Check `/_archive/ideas-2025-11-03-deprecated/` for archived idea files
2. Review git history for context on deprecated ideas
3. Consult deprecation summary at `/_archive/IDEAS-DEPRECATION-2025-11-03.md`

### For New Work

1. Use standard GitHub Issues for feature tracking
2. Reference templates in `/templates/` for scaffolding
3. Consult GitHub Pages, Storybook, and Playbook for documentation
4. Follow updated workflows (to be documented by Lane D)

### For Scripts

1. Remove any local references to `idea-intake`, `validate-ideas`, or similar
2. Update CI/CD to not call deprecated idea scripts
3. Use direct GitHub CLI or Octokit for issue management

## Related Documents

- Lane C Technical Report: `/_archive/LANE-C-REPORT-IDEAS-SUNSET-2025-11-03.md`
- Deprecation Summary: `/_archive/IDEAS-DEPRECATION-2025-11-03.md`
- Archived Ideas: `/_archive/ideas-2025-11-03-deprecated/`
- Deprecated Scripts: `scripts/ideas-to-issues.mjs`, `scripts/validate-ideas.mjs`, `scripts/sync-ideas-checklists.mjs`

## Review Schedule

- **30 days** (2025-12-03): Lane D documentation update checkpoint
- **90 days** (2026-02-01): Consider removing deprecated script stubs
- **180 days** (2026-05-02): Final review and potential archive cleanup

---

**Approved by:** Lane D, Lane C, Lane B  
**Document Owner:** Lane B (Narrative & Enablement)  
**Last Updated:** 2025-11-03
