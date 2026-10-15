---
canonical: true
created: '2025-11-20'
doc_id: ADR-00001
doc_type: adr
related: []
status: active
summary: '- Status: Accepted - Date: 2025-11-14'
supersedes: []
tags:
  - adr
  - architecture
  - documentation
  - terminal
  - testing
title: 'ADR-0001: Historical vs Canonical Documentation for .NET Project Structure'
---

# ADR-0001: Historical vs Canonical Documentation for .NET Project Structure

- **Status:** Accepted
- **Date:** 2025-11-14
- **Related Docs:**
  - `docs/rfcs/005-project-structure-reorganization.md`
  - `dotnet/README.md`
  - `docs/rfcs/IMPLEMENTATION_PLAN.md`
  - `docs/architecture/RFC_IMPLEMENTATION_REVIEW.md`
  - `docs/dev-notes/PR_DESCRIPTION.md`

## Context

The .NET project structure for PigeonPea has evolved over time. Earlier work and reviews describe an intermediate layout (e.g. `game-essential/core/PigeonPea.Shared/`, `console-app/core/PigeonPea.Console/`, `windows-app/core/PigeonPea.Windows/`).

Subsequent refactoring introduced a more structured layout with `core/src` and `core/tests` per tier, and moved test projects under their respective `core/tests` folders. Some documents now describe:

- The **current** structure (RFC-005, `dotnet/README.md`)
- A **historical snapshot** of the structure at the time of a large PR (RFC implementation reviews, PR descriptions)

Without a clear policy, it is easy to be unsure whether older review docs must be kept in sync with every subsequent structural change.

## Decision

We distinguish between **canonical** documentation (the source of truth) and **historical** documentation (snapshots tied to specific PRs or review moments):

1. **Canonical structure documentation**

   The following are considered canonical for the current .NET project layout and should be kept in sync with the codebase:
   - `docs/rfcs/005-project-structure-reorganization.md` (RFC-005)
   - `dotnet/README.md` (developer-facing structure and run commands)
   - Planning/checklist docs that describe _desired_ or _current_ state, such as `docs/rfcs/IMPLEMENTATION_PLAN.md` and `docs/rfcs/issues/issue-001-migrate-structure.md`.

   When the structure changes (e.g. moving projects into `core/src` and `core/tests`), these docs should be updated to reflect the new reality.

2. **Historical review documentation**

   The following are treated as historical artifacts that describe what was true at the time of a specific PR or review:
   - `docs/architecture/RFC_IMPLEMENTATION_REVIEW.md`
   - `docs/dev-notes/PR_DESCRIPTION.md`

   These documents are _not_ required to track every subsequent structural change. They may refer to paths like `game-essential/core/PigeonPea.Shared/` and `console-app/core/PigeonPea.Console/` even if the current codebase uses `core/src` and `core/tests`.

   If needed, a brief note can be added to clarify that the structure has evolved since the review, but the detailed content remains a snapshot.

## Consequences

- When reorganizing the .NET folders (e.g. introducing `core/src` and `core/tests` or moving test projects), we:
  - **Must** update RFC-005 and `dotnet/README.md`.
  - **Should** update planning/checklist docs that describe the current target structure.
  - **Do not** attempt to fully rewrite historical review documents.

- Readers should treat RFC-005 and `dotnet/README.md` as the authoritative description of the current structure.
- Historical docs can still be used to understand past decisions and implementations, but path details in those documents may be outdated relative to the current tree.

## Future Work

- Optionally add a short note to `RFC_IMPLEMENTATION_REVIEW.md` and `PR_DESCRIPTION.md` indicating that the project structure has since been refined to use `core/src` and `core/tests`, and that RFC-005 + `dotnet/README.md` are the canonical references.
- If additional major structural changes are made in future, consider adding follow-up ADRs that record those decisions while keeping this canonical vs historical policy intact.
