# ADR-006 — Observability Cardinality Policy

> **File:** docs/adr/ADR-006-observability-cardinality-policy.md  
> **Purpose:** Bound metric and trace label cardinality to ensure reliable, cost‑effective observability.

---

id: ADR-006
title: "Observability Cardinality Policy"
status: "Accepted"
date: "2025-10-14"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- PRD: "docs/1. Product Requirements Document.md#operability-and-observability"
- TDD: "docs/2. Technical Design Document v2.md#observability-logging-metrics-tracing"
- QA: "docs/3. Testing and Quality Assurance Plan.md#non-functional-acceptance-criteria"

---

## Context

Unbounded label cardinality (e.g., per‑user IDs, UUIDs, raw paths) in metrics and traces causes high memory usage, query timeouts, and budget overrun. We need clear limits compatible with our SLOs and dashboards.

## Decision

Adopt an **allow‑list** of metric labels and enforce **cardinality budgets** per metric family. Use **route templates** and **ID hashing** where necessary; reject or drop labels at ingestion when limits are exceeded.

### Policy

- **Allowed HTTP labels**: `method`, `route_template`, `status`, `api_version`, `service`. _Disallowed:_ `user_id`, raw `path`, `jti`, `sid`.
- **Metric families**:
  - Requests: `http_request_duration_ms`, `http_requests_total` — **max 200** label combinations per service.
  - DB: `db_query_duration_ms` — labels `operation`, `table`, `success`.
  - Auth: `auth_login_success_total`, `auth_rt_reuse_total` — no user/device labels.
- **Route templating**: `/api/v1/sessions/:id` not `/api/v1/sessions/123`.
- **ID hashing** (only when essential): hash → **first 8 chars** to cap cardinality (still use sparingly).
- **Traces**: Span attributes follow same allow‑list; **sampling** set to 1–5% for high‑volume endpoints with exemplar links to metrics.

### Enforcement

- Middleware validates label sets against allow‑list.
- Prometheus relabel/drop rules remove disallowed labels.
- Periodic audit job flags metrics breaching budget; CI check parses metrics registry for new labels.

### Dashboards & SLOs

- Standard dashboards per service with allowed labels only.
- SLO alerts based on RED metrics; no alerts tied to disallowed labels.

## Consequences

- Predictable memory and storage footprint.
- Slightly reduced ad‑hoc drill‑down (no per‑user metrics), but privacy and cost are improved.

## Alternatives Considered

- **Unlimited labels** with high sampling: Still expensive and unstable.
- **Per‑user metrics**: Privacy and cost concerns; move such needs to logs with retention controls.

## QA & Acceptance

- Unit tests for label allow‑list middleware.
- Load test ensures metrics remain below budget under peak traffic.
- CI fails when new labels are introduced without ADR update.

## Backout Plan

If troubleshooting requires temporary high‑cardinality labels, enable a **debug window** feature flag that adds ephemeral labels for ≤ 24h and auto‑removes them.

## Change Log

- **1.0 (2025-10-14)** Initial acceptance.
