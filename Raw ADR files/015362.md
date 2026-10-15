# Adopt Queue-First Ingestion with Cassandra/Scylla Audit Store

* Status: proposed
* Deciders: platform-core + audit squad
* Date: 2025-12-03

## Context and Problem Statement

Services (starting with cart-service) must emit audit events that are durable, queryable by entity/user/store, and resistant to backpressure. The ingestion path must absorb bursts without slowing write APIs and provide clear developer experience for ad hoc testing or backfills. We need to pick the primary ingestion mechanism and backing store before building audit-service.

## Decision Drivers

1. Durable, append-only storage optimized for time-ordered queries.
2. Backpressure-safe ingestion that decouples publishers from the audit database.
3. Simple DX/DUX for developers and operators to validate, replay, or backfill events.
4. Predictable latency and cost at scale (many small events, occasional bursts).
5. Clear routing for failure handling (retries, dead letters) without blocking business flows.

## Considered Options

1. Queue-first ingestion (Redis Streams/Kafka) with Cassandra/Scylla store; HTTP endpoints as a secondary DX path (chosen).
2. Direct HTTP ingestion writing synchronously to the audit store (no queue).
3. Services writing directly to the database via SDK/R2DBC without HTTP or queue.

## Decision Outcome

Chosen option: **Queue-first ingestion with Cassandra/Scylla as the audit store; HTTP endpoints remain available for DUX (dev/testing/backfill) but are not the primary path.**

Queue-first keeps publishers non-blocking and resilient to downstream pressure, while Cassandra/Scylla provides durable, ordered, and partitionable storage for time-series audit queries. HTTP endpoints stay for great developer UX: quick local testing, controlled backfills, and operational spot checks without needing queue producers.

### Positive Consequences

- Publishers decouple from storage; queue absorbs bursts and supports retries/ordering without slowing business APIs.
- Durable wide-column store handles time-range queries by entity/user/store with tunable TTLs and compaction.
- HTTP endpoints improve DUX: easy curl/Postman/WebTestClient flows for debugging, smoke tests, and manual backfill when queues are unavailable.
- Clear failure isolation: queue retries/ DLQ prevent audit loss while keeping primary flows fast.

### Negative Consequences

- Operating both queue and HTTP adds surface area; need auth/rate limits to prevent bypassing ingestion rules.
- Queue-first adds consumer lag risk; must monitor lag and DLQ size.
- Cassandra/Scylla requires schema and capacity planning; mis-tuned partitions can hurt query latency.

## Pros and Cons of the Options

### 1. Queue-first + Cassandra/Scylla + HTTP (chosen)

**Good**
- Backpressure-safe ingestion with retries and dead letters; publishers stay reactive.
- Append-only wide-column store aligns with audit query patterns and durability needs.
- HTTP endpoints boost DUX for local dev, contract tests, and controlled backfills.

**Bad**
- More components to run locally/CI (queue + DB + API).
- Requires ingestion rules so HTTP is used only for DX/backfill, not as a production firehose.

### 2. HTTP-only to audit store

**Good**
- Simple architecture; fewer moving parts.
- Easy to test with standard tools.

**Bad**
- Publishers block on store latency/outages; harder to handle bursts and retries.
- No built-in buffering; failures risk dropping or double-writing events.

### 3. Direct DB writes from services

**Good**
- Removes an extra hop and service; lowest latency when DB is healthy.
- Simplifies ingestion code in audit-service.

**Bad**
- Tight coupling to DB topology and schema; harder to evolve.
- Each service must handle retries/idempotency; no shared DLQ or backpressure control.

## Implementation Notes and Next Steps

- Use Redis Streams or Kafka as the primary `audit-events` queue; define consumer groups, retries, and DLQ behavior.
- Store events in Cassandra/Scylla with partitioning by store/entity and clustering by timestamp; apply TTL (e.g., 1 year) and time-window compaction.
- Keep HTTP `/audit/events` endpoints enabled but rate-limited and scoped for DX/backfill; document when to use them.
- Ensure idempotency keys (eventId) across queue and HTTP paths to avoid duplicates on retries.
- Add observability: queue lag, consumer throughput, DLQ depth, store write/read latency, and HTTP usage patterns.

## References

- 009_AUDIT_DATA.md
- 000-use-markdown-architectural-decision-records.md
