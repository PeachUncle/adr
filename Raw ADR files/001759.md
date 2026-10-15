# ADR-007 — Idempotency Policy for Writes

> **File:** docs/adr/ADR-007-idempotency-policy-for-writes.md  
> **Purpose:** Prevent duplicate side‑effects on retried client requests and provide deterministic, safe replays.

---

id: ADR-007
title: "Idempotency Policy for Writes"
status: "Proposed"
date: "2025-10-13"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- TDD §5.7: "Command handling & retries"
- TDD §7.14: "HTTP conventions"

---

## Context

The SPA and future mobile clients perform retries on network failures. Without idempotency, duplicate POST/PUT/PATCH requests can create extra resources or apply the same mutation multiple times. We need a consistent policy and server storage model to deduplicate safely across instances and after restarts.

## Decision

Adopt the **`Idempotency-Key`** header for all **unsafe** endpoints (POST/PUT/PATCH/DELETE) that create or mutate resources. Keys are **opaque**, **client‑generated**, and **unique per logical operation**. The server stores request **fingerprints** for **24h**, enforces **payload match**, and **replays deterministic responses**.

### Rules

- Clients send `Idempotency-Key: <uuid>` per operation; keys are **single‑use** for that route and principal.
- Server stores `{ key, route, method, principal, body_hash, response_code, response_body, created_at, ttl }`.
- On duplicate with **same** `body_hash`: **return stored response** (status + body); do **not** re‑execute side‑effects.
- On duplicate with **different** `body_hash`: return **409 Conflict** with machine‑readable error.
- TTL: **24 hours** by default; configurable. After expiry, key is forgotten; new request executes.
- **Scoping**: Key is scoped to `{principal, method, route_template}`; different routes require different keys.

### Storage & Concurrency

- Storage backend: **Redis** (primary) with TTL; fallback to Postgres table `system.idempotency_keys` when Redis unavailable (best‑effort).
- Atomic write: `SETNX` or Lua script for **first‑write wins**; store provisional record before executing the command.
- On success/failure: fill stored **final response** to enable deterministic replay.

### Responses

- Include header: `Idempotency-Key: <key>` in responses (original and replayed).
- Include `Idempotent-Replayed: true` on replayed responses.

## Consequences

- Prevents duplicate resource creation and repeated charges/side‑effects.
- Requires additional infra (Redis) and careful atomicity.

## Alternatives Considered

- **No idempotency**: Simpler but unsafe.
- **Request signatures without storage**: Cannot protect across restarts or multi‑node.

## QA & Acceptance

- Unit tests for same‑payload replay and mismatched 409 behavior.
- Race tests ensure first writer wins and others replay.
- TTL expiry tests: after 24h, request executes again.

## Backout Plan

Disable enforcement per route via feature flag; clients may continue to send keys but server ignores them.

## Change Log

- **1.0 (2025-10-13):** Initial proposal.
