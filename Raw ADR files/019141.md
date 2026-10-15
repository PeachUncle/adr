# Architectural Design Requirements — Trade‑Mart Core Persistence and Messaging

## Context and Goals

Trade‑Mart requires durable, low‑latency persistence and messaging for trade ingestion, processing, and history.

**Core components**
- **Kafka** – buffering and event‑driven pipelines  
- **PostgreSQL** – transactional trade state  
- **MongoDB** – trade history and audit documents  

**Non‑functional targets**
- P95 ingest ≤ 2 s  
- Durability and HA (99.9% uptime)  
- Full observability (Prometheus/Grafana + OpenTelemetry)  
- Secure communication (TLS + OAuth2/JWT + RBAC/ACLs)  
- Minimized operational overhead and preference for managed services  

---

## Decision Summary

| Component | Choice | Mode | Key Rationale |
|------------|--------|------|----------------|
| **Kafka** | Apache Kafka | Managed (Confluent / MSK) or Strimzi operator on K8s | Durable buffering, ordered ingestion, scalable consumers |
| **Schema Registry** | Confluent / Apicurio | Managed or self‑hosted | Enforces backward/forward schema compatibility |
| **PostgreSQL** | PostgreSQL 13+ | Managed (RDS / Azure DB) or Patroni + PgBouncer | ACID trade state, strong consistency |
| **MongoDB** | MongoDB 6+ | Managed (Atlas) or Percona operator | Flexible schema for trade history/audits |

---

## Component Architecture

### Kafka
- **Topics**: `trade.ingested`, `trade.processed`, `trade.expired`, `trade.repaired`, `trade.audit`
- **Config**: partitions (6–12 initial), replication.factor = 3, `min.insync.replicas = 2`
- **Retention**: 7–30 days; compact audit topics where needed
- **Security**: TLS + SASL/SCRAM or OAuth; topic‑level ACLs
- **Ops**: Managed (preferred) / Strimzi on Kubernetes. Use MirrorMaker 2 for DR.
- **Monitoring**: Prometheus JMX exporter; alerts on under‑replication, consumer lag, disk usage.

---

### PostgreSQL
- **Schema**: `trades` table – indexed by trade_id, maturityDate, status
- **HA/Replication**: Managed HA / Patroni synchronous replication
- **Pooling**: PgBouncer to control connection spikes
- **Backups**: Automated snapshots / pgBackRest + WAL archiving
- **Security**: TLS‑only, strict roles, VPC/network policy isolation
- **Monitoring**: Postgres exporter → Prometheus; watch connections, replication lag, autovacuum.

---

### MongoDB
- **Collections**: `trade_history`, `audit`; TTL indexes for ephemeral retention (∼ 90 days)
- **Topology**: 3‑node replica set ; enable sharding only as scale demands
- **Backups**: Managed snapshots / mongodump tested restores
- **Security**: TLS, SCRAM or x.509 auth, restricted network access
- **Monitoring**: Mongo exporter → Prometheus; alerts on replication lag and memory pressure.

---

## Cross‑Cutting Concerns

- **Schema Governance**: CI‑enforced Schema Registry compatibility checks  
- **Observability**: Unified metrics (Prometheus) + distributed traces (OpenTelemetry → Jaeger)  
- **Scaling**: KEDA for Kafka‑based autoscaling; HPA for application pods  
- **Backups & DR**: Kafka MirrorMaker 2, Postgres pgBackRest, MongoDB snapshots  
- **Security Model**: TLS everywhere, credential rotation via Secrets Manager / K8s Secrets  
