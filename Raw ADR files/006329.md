# ADR-002: On-Disk Layout & Attachments

Status: Accepted

Date: 2025-08-21

Owners: Archon Core

## Context

We need a storage format that works well with Git, scales to tens of thousands of nodes, and keeps merges understandable. A single monolithic JSON risks constant conflicts and large diffs. Binary assets must not bloat Git history.

## Decision

Use a **sharded layout** with one file per node, attachment hashing, and a local rebuildable index:

/project.json                  # { rootId, schemaVersion, settings }
/nodes/.json               # one file per node (see shape below)
/index/archon.db               # SQLite cache (rebuildable, not required)
/attachments/.      # binaries; Git LFS for > 1MB

**Node file shape** (`/nodes/<id>.json`):

```json
{
  "id": "01J9…",
  "name": "Microscope",
  "description": "…",
  "properties": { "vendor.serialNumber": "ABC123" },
  "children": ["01J9CHILD1", "01J9CHILD2"]  // child IDs (order preserved)
}
```

Attachments:

- Store binaries in /attachments/ via content-addressed names.
- Track files > 1 MB in Git LFS.
- Nodes reference attachments in properties, e.g.:
  - "manualPDF": { "type": "attachment", "hash": "sha256:…", "filename": "manual.pdf" }

Rationale

- Sharded nodes drastically reduce merge conflicts; diffs are smaller and more readable.
- Child IDs (not embedded subtrees) allow loading/saving only the files that changed.
- LFS prevents repository bloat and keeps clones fast.

Alternatives Considered

- Single monolithic JSON: simplest to start, but does not scale for collaboration.
- Embedded children in parent files: simplifies reads, but any subtree edit touches the parent file and increases conflicts.
- No index: workable but slow search at 10k+ nodes.

Consequences

- Positive: Clean merges; partial I/O; scalable to 50k nodes with virtualization.
- Negative: More filesystem entries; slightly higher loader complexity.
- Follow-ups: Rebuild index on clone/import; background incremental index updates on change.

Implementation Notes

- Git/LFS: .gitattributes entries for /attachments/**and a JSON diff driver for /nodes/**.
- SQLite index at .archon/index/archon.db with FTS5 tables for fast search.
- Loader/saver at internal/store/loader.go; indexer at internal/index/sqlite/….

Review / Revisit

- Revisit thresholds (1 MB LFS; performance at 50k nodes) after telemetry and real projects.

---
