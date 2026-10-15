# Choose Postgres as the Durable Write Data Store for Cart Service Carts

* Status: proposed
* Deciders: platform-core + cart squad
* Date: 2025-12-03

## Context and Problem Statement

Granular cart CRUD (products, customer, discounts, fulfillments) is being added to cart-service (see 008_CART_SERVICE.md). The write store for the cart aggregate must be durable, support reactive APIs, and deliver predictable consistency across horizontally scaled pods. Carts are short-lived (default seven-day retention) but must survive node restarts and avoid loss during bursts or maintenance. Queries include fetch-by-id and list-by-store, with atomic updates to nested collections. The prior cache-oriented Redis approach lacks the durability guarantees required for carts that represent user intent; we need a durable store decision before implementation begins.

## Decision Drivers

1. Durability and consistency for cart mutations; no loss on pod or cache restarts.
2. Reactive, low-latency access that does not block event loops.
3. Cross-instance visibility without coordination overhead when scaling cart-service.
4. Simple, atomic updates for cart sub-resources and totals with transactional integrity.
5. Operational fit with existing platform skills and observability.

## Considered Options

1. Postgres (R2DBC) as the cart write store (chosen).
2. Redis as the cart write store (JSON + TTL + sets).
3. In-memory node-local store (Caffeine/Guava) with optional snapshotting.

## Decision Outcome

Chosen option: **Postgres as the durable write data store for carts**.

Postgres provides durability, transactional updates, and strong consistency for cart mutations while still supporting reactive access through R2DBC. It avoids data loss during cache evictions or Redis restarts and simplifies multi-step updates (e.g., add product + recalc totals) with ACID semantics. Store and cart indexes map naturally to relational keys, and retention can be enforced via TTL columns and scheduled pruning. Redis remains useful for caching, but not as the source of truth for carts that must persist through operational events.

### Positive Consequences

- Durable storage survives pod/cluster restarts and maintenance without cart loss.
- ACID transactions simplify concurrent updates to products/discounts/totals, reducing race conditions.
- Relational indexes support efficient fetch-by-id and store-number queries without bespoke key gymnastics.
- Well-understood operational model with backups, replication, and observability already supported by platform teams.

### Negative Consequences

- Higher latency than in-memory Redis; requires careful connection pooling and R2DBC tuning to keep P99 acceptable.
- Operational overhead for schema migrations, vacuum/auto-analyze, and managing retention jobs.
- Additional work to ensure non-blocking drivers (R2DBC) are used end-to-end; JDBC on event loops would be unsafe.

## Pros and Cons of the Options

### 1. Postgres (R2DBC) as the cart write store (chosen)

**Good**
- Durable by default with WAL, backups, and replication; carts are not lost on cache eviction or process restart.
- Transactional integrity allows atomic multi-step cart changes without custom Lua/locking logic.
- Familiar tooling (SQL, indexes, migrations) and existing SRE playbooks.

**Bad**
- Needs R2DBC tuning and pool sizing to keep reactive paths fast.
- Requires schema evolution discipline and migration testing.

### 2. Redis as the cart write store

**Good**
- Extremely low-latency reads/writes with simple key patterns and TTLs.
- Fits the existing cache footprint already provisioned for other services.

**Bad**
- Durability is weaker: snapshot or AOF settings can still lose recent writes on crash/eviction; persistence must be custom-hardened.
- Lacks rich transactional semantics; concurrent updates need Lua scripts or optimistic locking to avoid lost updates.
- Operationally tuned for cache use; treating it as the system of record increases risk and recovery complexity.

### 3. In-memory node-local store (Caffeine/Guava)

**Good**
- Simplest to embed; fastest access and no external dependency.
- Speeds up local development.

**Bad**
- No cross-instance consistency or durability; pods lose carts on restart.
- Fragmented store-level queries across nodes; unsuitable for production carts.

## Implementation Notes and Next Steps

- Model carts with a primary table keyed by `cart_id` (UUID) and indexed by `store_number`; use child tables for products, discounts, fulfillments, and totals to enable transactional updates.
- Use R2DBC for reactive access; configure connection pooling and backpressure-aware timeouts to avoid blocking event loops.
- Enforce retention with an `expires_at` column and a scheduled pruning job (or Postgres TTL via partitioning), default seven days with overrides for known customers.
- Add observability for query latency, deadlocks, and connection pool saturation; alert on failed retention jobs.
- Reevaluate schema once checkout/order flows require additional guarantees (e.g., locking or foreign key relationships to orders).

## References

- 008_CART_SERVICE.md
- MADR template (000-use-markdown-architectural-decision-records.md)
