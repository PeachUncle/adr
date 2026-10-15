# ADR-001: Node Identity & Hierarchy

Status: Accepted
Date: 2025-08-21
Owners: Archon Core

## Context

Archon models physical configurations as a hierarchy. We need stable identifiers for nodes to support Git-based history, semantic diff/merge, and reliable move detection. Path-based IDs break under reorganization; global name uniqueness is too restrictive for real installations.

## Decision

- Each node has an immutable **UUID v7** `id` (lexicographically time-sortable).
- Names must be **unique among siblings** (case-insensitive). Global uniqueness is not required.
- **Child order is meaningful** and must be preserved in storage and UI.
- Model is a **strict tree** for v1 (no DAG/cross-links). Moves are tracked by change of parent for the same `id`.
- On import, if an incoming `id` collides, generate a new UUID v7 and record a one-time mapping in `import-map.json`.

## Rationale

- Stable IDs are essential for semantic changes (edit/rename/move vs. delete+add) and merge correctness.
- Sibling-only name uniqueness matches user expectations (e.g., many “Temperature Sensor” nodes).
- Tree-only v1 reduces complexity for diff/merge and navigation while covering the majority of real-world use.

## Alternatives Considered

- **Path-derived IDs:** fragile on reorg; destroys diff/merge semantics.
- **Sequential ints:** race-prone in distributed edits; harder to guarantee uniqueness at scale.
- **Immediate DAG:** adds UI and merge complexity; defer until use cases demand it.

## Consequences

- **Positive:** Robust diffs/merges; intuitive move detection; scalable collaboration.
- **Risks:** Future DAG support requires an extension (likely `links[]` by `id`).
- **Follow-ups:** Import mapping; tests for move detection and sibling name validation.

## Implementation Notes

- ID helper at `internal/id/uuid.go` (UUID v7).
- Validation on create/rename (backend + UI).
- Import mapping file: `project/.archon/import-map.json`.
- Example node (storage shape is defined in ADR-002).

## Review / Revisit

- Revisit when introducing DAG/cross-links or if we adopt server-backed realtime sync.
