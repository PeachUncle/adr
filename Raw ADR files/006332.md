# ADR-005: Search & Indexing (SQLite)

Status: Accepted
Date: 2025-08-21
Owners: Archon Core

## Context

Projects can reach 10k–50k nodes. Pure in-memory scans are slow; we need fast search/filter without external services.

## Decision

- Use a **local, rebuildable SQLite index** at `.archon/index/archon.db`.
- Schema (initial):
  - `nodes(id TEXT PRIMARY KEY, name TEXT, parent_id TEXT)`
  - `properties(node_id TEXT, key TEXT, type TEXT,
     value_text TEXT, value_num REAL, value_bool INTEGER, value_date TEXT)`
  - `fts_properties` (FTS5) over `name`, `key`, `value_text`
- **Incremental updates** on node/property changes; **full rebuild** on clone/import.
- The index is **not authoritative**; it can be deleted and rebuilt at any time.
- Query API exposes: by name, by path prefix, property key/value filters, full-text search.

## Rationale

SQLite is ubiquitous, lightweight, and fast. Keeping the index rebuildable avoids complex migrations and correctness pitfalls.

## Alternatives Considered

- **No index (scan):** Too slow for large projects.
- **Embedded search engines (e.g., Bleve):** Adds dependencies; SQLite is sufficient and simpler to ship.

## Consequences

- Positive: Instant search/filter at scale; no external services.
- Negative: Extra file and update path; need to handle index corruption gracefully.
- Operational: Uses modernc.org/sqlite which guarantees FTS5 support across all platforms.
- Follow-ups: Tokenization for non-Latin scripts; collation tuning; property-specific indexes by domain if needed.

## Implementation Notes

- Indexer: `internal/index/sqlite/` (writer queue to avoid contention).
- Driver: Uses modernc.org/sqlite which guarantees FTS5 support; no fallback needed.
- Rebuild: `archon index rebuild` CLI and background task on clone/import.
- Backup: Exclude `.archon/index/` from backups; it’s a cache.
- Tests: Consistency (node save → index updated), FTS queries, rebuild-from-scratch.

## Review / Revisit

- Revisit for multi-project global search or if perf at >100k nodes degrades.
