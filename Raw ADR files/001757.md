# ADR-005 — Partitioning Strategy for `sessions` and `audit_log`

> **File:** docs/adr/ADR-005-partitioning-sessions-and-audit-log.md  
> **Purpose:** Ensure scalable storage and performant queries for write‑heavy time‑series tables.

---

id: ADR-005
title: "Partitioning Strategy for sessions & audit_log"
status: "Accepted"
date: "2025-10-14"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- PRD: "docs/1. Product Requirements Document.md#non-functional-requirements-performance"
- TDD: "docs/2. Technical Design Document v2.md#database-schema--modules"
- QA: "docs/3. Testing and Quality Assurance Plan.md#performance-tests"

---

## Context

`core.sessions` (workout logs) and `system.audit_trails` grow linearly with time and are primarily queried by **date ranges** and **user filters**. We need predictable maintenance (vacuum, index bloat control) and fast drop of expired data per retention windows.

## Decision

Use **PostgreSQL declarative partitioning** by **month** on `created_at` for both tables. Co‑locate secondary indexes per partition; automate **attach/detach** and retention drops.

### Layout

- Parent tables: `core.sessions`, `system.audit_trails`.
- Partitions: **monthly**, named `..._pYYYYMM`.
- Indexes: per partition for `(user_id, created_at)` and GIN/partial where needed.
- Constraints: CHECK constraints on time bounds for pruning.

### Maintenance

- **Autocreate** next 3 months of partitions.
- **Detach & drop** partitions older than retention (see ADR‑003).
- Use `CREATE INDEX CONCURRENTLY` during backfills/reindex.
- Run `ANALYZE` after heavy loads; monitor `dead_tuples` and bloat.
- Avoid cross‑partition FKs; keep FK to `auth.users` at parent or enforce via app logic.

### Query Patterns

- Always filter by time (`created_at BETWEEN ...`) and optionally `user_id`.
- Ensure the ORM/query layer injects time predicates to trigger pruning.
- Provide views `v_sessions_recent` and `v_audit_recent` spanning last N months for convenience.

## Consequences

- Large, old data can be dropped quickly (partition drop).
- Better cache locality and planner performance via pruning.
- Slight complexity in migrations and index management.

## Alternatives Considered

- **No partitioning**: Degradation over time; slow deletes.
- **Hash partitioning by user**: Hot‑spot risk and poor date pruning.

## QA & Acceptance

- Tests verify automatic creation and timely drop of partitions.
- Benchmark: range queries (90 days) remain p95 < 200 ms under nominal load.
- Migration scripts verified on CI with a seeded dataset.

## Backout Plan

If monthly partitions prove too granular or too coarse, migrate to **quarterly** by creating new parents/partitions and swapping views with minimal downtime.

## Change Log

- **1.0 (2025-10-14)** Initial acceptance.
