# ADR-006 — Database selection: PostgreSQL as primary database

## Status

Accepted

## Context

`stock-management-service` must demonstrate realistic backend engineering patterns around **consistency**, **concurrency**, **transactions**, **replication**, **backup/restore**, and **observability**. The database must support:

* ACID transactions with solid row-level locking (`SELECT FOR UPDATE`) and table lock capabilities.
* Reliable primary + read-replica topology (streaming replication).
* Easy tooling for backup/restore (dev and demonstrable production patterns).
* Good ecosystem support for NodeJS / Prisma, observability (tracing/metrics), and containerized development.
* Rich SQL features (joins, constraints, window functions) to keep business logic expressive in queries when necessary.
* Extensible via proven extensions (pg_stat_statements, pg_trgm, etc.) for realistic operational demonstrations.

We reviewed common alternatives (briefly): MySQL/MariaDB, CockroachDB, YugabyteDB, MongoDB, and various cloud-native distributed SQL databases. Those have tradeoffs (MySQL: less expressive SQL features and more awkward locks semantics; Cockroach/Yugabyte: great for geo-distribution but add operational complexity and different locking/transaction semantics that obscure classic `SELECT FOR UPDATE` demos; MongoDB: non-relational and not suitable for teaching ACID relational transactions in this context). For the training goals of this project, the chosen DB must be familiar, demonstrable in containers, and let you implement canonical relational patterns (transactions, locks, replica lag, WAL, backups).

## Decision

Use **PostgreSQL** (recommended major version: **16**) as the primary database for `stock-management-service`. Use one Postgres primary (write) and one Postgres replica (read) in the local Docker Compose environment. For future/advanced demos you may add more replicas or production-grade backup tooling (pgBackRest, WAL archiving).

## Rationale

* **ACID + Locking semantics**: Postgres provides first-class ACID transactions and explicit `SELECT FOR UPDATE`, transaction isolation level controls, and documented deadlock detection — exactly what the project must demonstrate.
* **Replication tooling**: Streaming replication (primary → replica) is stable, easy to configure in Docker Compose for demos, and exposes replica lag phenomena that are valuable to teach/read-after-write patterns.
* **Operational tools**: `pg_dump`/`pg_restore`, `pg_basebackup`, WAL archiving, and mature tools such as `pgBackRest` and `wal-e` provide easy paths from demo to more advanced backup strategies.
* **Ecosystem & driver support**: Prisma has solid Postgres support; Node.js/Prisma + pg + Prisma transactions work well and are idiomatic for the tech stack chosen (NestJS + Prisma).
* **Extensions & observability**: Extensions like `pg_stat_statements` (query insights), `pg_trgm` (text search), and `pgcrypto` (UUID generation) are useful for realistic datasets and operational observability. Postgres plays well with OpenTelemetry + Prometheus exporters and pg metrics.
* **Developer experience**: Official Postgres Docker images are well-documented, small enough for dev, and widely used in examples, CI, and documentation—minimizes accidental complexity during learning.

## Consequences

* **Positive**

  * Straightforward demonstration of row-level locking and transaction behavior.
  * Easy to reproduce and test replica lag, read-after-write strategies, and backup/restore in Compose.
  * Large amount of educational and operational material available.
* **Negative**

  * Operational complexity (managing replicas, WAL, retention) must be explained and managed even in demos.
  * If later you wanted to demonstrate geo-partitioning or global strong consistency without single-writer, you would need to adopt other databases (not necessary for this project).

## Operational notes & recommendations (practical)

Use these guidelines for Compose and future ops:

### Image

* Recommended image: `postgres:16` (pin to a specific patch once validated, e.g. `postgres:16.3`).
* For compact dev images you may use `postgres:16-alpine` but note compatibility issues with some extensions; prefer the canonical image in CI/dev first.

### Basic Docker Compose service names (use these hostnames in `.env`)

* `postgres-primary` — primary (writes)
* `postgres-replica` — replica (reads)

### Important Postgres configuration parameters for replication (set on primary & replica as needed)

* `wal_level = replica`
* `max_wal_senders = 5` (tune as needed)
* `wal_keep_size = 64MB` (or larger if you want to avoid WAL removal while replica is down)
* `archive_mode = on` (if you demonstrate WAL archiving)
* `hot_standby = on` (on replica)
* `synchronous_commit = off` (default) — for demo clarity, you may show impact of `synchronous_commit = on` vs `off`
* `max_connections` should be tuned for your environment; use connection pooling for many app connections.

### Connection & pooling

* Use two distinct connection URLs in `.env` (already in your env example):

  * `DATABASE_URL_PRIMARY=postgresql://postgres:postgres@postgres-primary:5432/stockdb`
  * `DATABASE_URL_REPLICA=postgresql://postgres:postgres@postgres-replica:5432/stockdb`
* For production-like demos, use a connection pooler (pgbouncer) to avoid connection storms. In local dev it is optional but document it in ADRs.

### Backups & restore

* **Dev**: use `pg_dump` + `pg_restore` (simple and sufficient to demonstrate backup/restore).
* **Advanced / production simulation**: document and demonstrate `pgBackRest` or WAL archiving and PITR (Point-in-Time Recovery) — describe migration from pg_dump to pgBackRest in docs.

### Extensions to enable (recommended for project & observability)

* `pg_stat_statements` — query stats, helpful for dashboards.
* `pg_trgm` — faster text search, good for product search demos.
* `pgcrypto` — functions for UUID generation and cryptographic functions.

### Monitoring & metrics

* Add metrics collection:

  * Expose Postgres metrics via `postgres_exporter` (Prometheus exporter) to track replication lag, active connections, locks, slow queries.
  * Scrape `postgres_exporter` from Prometheus and include `pg_replication_lag` and `pg_stat_activity`-based panels in Grafana.

### Testing replica lag

* Simulate replica lag by pausing the replica container (`docker pause`) or by adjusting WAL retention and network delay — use this to validate read-after-write strategies.

## Migration path (future)

* For larger-scale demos, add:

  * `pgBackRest` for more realistic backups and retention policies.
  * A pgbouncer layer for connection pooling.
  * Additional read replicas for scaling reads.
  * Logical replication for partial table replication to other systems (Kafka connectors, etc.).

## Alternatives considered (brief)

* **MySQL / MariaDB** — stable and widely used, but less expressive SQL, different lock semantics; less aligned with Prisma transaction idioms for advanced locking demos.
* **CockroachDB / YugabyteDB** — distributed SQL with strong availability; operational semantics differ (optimistic or serializable transactional models) and complicate simple teaching on `SELECT FOR UPDATE`.
* **MongoDB / NoSQL** — not suitable for relational ACID transaction demos by design.
* **Cloud-managed DBs (RDS, Cloud SQL, etc.)** — great for production, but not necessary for local dev lab; consider later for production-grade demo.

## Implementation checklist (short)

* [ ] Use `postgres:16` in `docker-compose.yml` for primary and replica.
* [ ] Configure primary with `wal_level=replica`, `max_wal_senders` and appropriate `wal_keep_size`.
* [ ] Configure replica to use `primary_conninfo` and `hot_standby=on`.
* [ ] Add `postgres_exporter` service and wire it into Prometheus.
* [ ] Enable `pg_stat_statements` and `pg_trgm` in the image or init script.
* [ ] Provide `pg_dump` backup container and a restore recipe in `infra/`.

---

## References & further reading (suggested)

* Official PostgreSQL docs — transactions, replication, WAL, backup/restore.
* `pg_stat_statements` and `pg_trgm` extension docs.
* `pgBackRest` and `pgbouncer` guides (for advanced ops).
* Prisma docs on multiple database connections and transaction patterns.
