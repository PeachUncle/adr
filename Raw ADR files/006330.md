# ADR-003: Diff/Merge Semantics & Snapshots

Status: Accepted
Date: 2025-08-21
Owners: Archon Core

## Context

Archon is Git-backed. Non-technical users need meaningful change views and predictable merges. Text diffs on JSON are insufficient; we need semantic diffs, stable move detection, and a simple “Snapshot” concept that maps cleanly to Git.

## Decision

- **Semantic diff is primary**; text diff is auxiliary.
- **Move detection:** A node is “moved” when its parent ID differs across two refs for the same node `id`. Present as "Moved '`<name>`' under '`<new parent>`'".
- **Rename detection:** Compare `name` across refs for the same `id`, present as a rename.
- **Property diff:** Field-wise comparison with types (`string|number|boolean|null`).
- **Three-way merge (IDs as ground truth):**
  - Auto-merge non-overlapping edits.
  - Conflict when both branches change the same property key on the same node from the common base.
  - Delete vs edit/move ⇒ conflict.
  - Sibling order: preserve order; conflicting reorders prompt a reorder UI.
- **Conflict UX:** Side-by-side per-field chooser; record selections into the merge commit.
- **Snapshots:** A user-visible Snapshot is a **commit + immutable tag** with unique name. Optional human-friendly manifest (description, labels) is written as a separate file; history is never rewritten.

## Rationale

Semantic diff/merge maps to how domain experts think (“moved this module”, “changed resolution”), enabling collaboration without Git fluency. Tags formalize the “checkpoint” concept without altering history.

## Alternatives Considered

- **Text-only diff:** Low effort but not understandable to most users.
- **CRDT/realtime first:** Higher complexity; beyond MVP scope.
- **Blocking locks:** Reduce conflicts but impede collaboration; we prefer resolve-over-prevent.

## Consequences

- Positive: Clear changes, predictable merges, approachable UX.
- Negative: Requires robust merge engine and thorough tests.
- Follow-ups: Heuristics (e.g., auto-choose latest) as optional; batch conflict tools.

## Implementation Notes

- Go merge engine: `internal/merge/semantic.go` (diff), `internal/merge/three_way.go` (3-way), `internal/merge/types.go`.
- UI: `src/lib/diff/DiffViewer.svelte`, `src/lib/diff/MergePanel.svelte`.
- Snapshot/tag: Hybrid implementation — tag and commit creation via Git CLI; tag enumeration via go-git for speed. Manager in `internal/snapshot/` writes metadata to `.archon/snapshots/<name>.json` and restores by commit hash.
- Tests: property/structure/move/rename/reorder/delete-edge cases; golden tests.

## Review / Revisit

- Revisit if/when DAG/cross-links are added or if realtime sync is introduced.
