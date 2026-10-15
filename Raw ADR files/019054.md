# ADR-0011: External Database Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-24
- **Feature:** 001-k8s-local-deploy
- **Context:** Phase 4 requires deploying application to Kubernetes. The existing Phase 3 application uses Neon PostgreSQL (serverless, externally hosted). A decision is required: deploy database in-cluster (StatefulSet with PVC) or continue using external Neon. In-cluster database adds Kubernetes complexity (PVCs, StatefulSets) while external database simplifies cluster but requires internet connectivity.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines persistence layer strategy
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - In-cluster PostgreSQL, SQLite evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all services, scaling, backups, and operations
-->

## Decision

We will continue using Neon PostgreSQL as the external database for all services:

**Database Integration Pattern:**
- Provider: Neon Serverless PostgreSQL
- Connection: Backend and MCP server connect directly to Neon via `DATABASE_URL` environment variable
- Kubernetes Integration: `DATABASE_URL` stored in Kubernetes Secret (`app-secrets`)
- No StatefulSet or PVC required in cluster
- No in-cluster database deployment

**Connection Configuration:**
```
Kubernetes Secret (app-secrets):
  DATABASE_URL: postgresql://user:password@ep-neon-host.aws.neon.tech/neondb?sslmode=require

Backend Deployment:
  envFrom:
    - secretRef:
        name: app-secrets
  (injects DATABASE_URL into container)

MCP Server Deployment:
  envFrom:
    - secretRef:
        name: app-secrets
  (injects DATABASE_URL into container)
```

### Architecture Diagram

```
┌───────────────────────────────────────────────────────────┐
│                   Minikube Cluster                     │
│                                                           │
│  ┌──────────────┐    ┌──────────────┐               │
│  │   Frontend   │    │   Backend    │               │
│  │  Port: 3000  │───▶│  Port: 8000  │               │
│  └──────────────┘    └──────┬───────┘               │
│                            │ DATABASE_URL             │
│                            │ (from Secret)          │
│                            ▼                         │
│                      ┌──────────────┐              │
│                      │  MCP Server  │              │
│                      │  Port: 8001  │              │
│                      └──────┬───────┘              │
│                             │ DATABASE_URL            │
└─────────────────────────────┼───────────────────────┘
                              │
                              ▼ SSL Connection
                    ┌─────────────────┐
                    │ Neon PostgreSQL │
                    │  Serverless     │
                    │  (External)     │
                    │  AWS/Azure Region│
                    └─────────────────┘
```

### Rationale

Neon PostgreSQL is already configured and working from Phase 3. As a serverless database, Neon provides automatic scaling, built-in backups, and serverless scaling without infrastructure management. Continuing with external Neon eliminates StatefulSet, PVC, and in-cluster database complexity. The cluster becomes stateless, simplifying deployment and rollback. Network overhead is minimal (<10ms to Neon) and is well within 500ms response time target.

## Consequences

### Positive

- **Simplified Cluster:** No StatefulSet or PVC resources required; cluster is stateless
- **Built-in Scalability:** Neon auto-scales based on load; no manual intervention needed
- **Automatic Backups:** Neon provides point-in-time recovery and automated backups
- **Reduced Blast Radius:** Database failures don't affect cluster; cluster failures don't affect database
- **Faster Cluster Startup:** No waiting for database pod initialization
- **Zero Infrastructure Management:** No PostgreSQL server administration required
- **Connection Pooling:** Neon handles connection pooling efficiently
- **Production Path:** Neon is suitable for Phase 5 cloud deployment (same pattern)

### Negative

- **Network Dependency:** Cluster must have internet access to database
  - *Mitigation:* All modern cloud environments have internet; Minikube uses host networking which has internet
- **Network Latency:** ~5-20ms latency to Neon vs <1ms for in-cluster
  - *Mitigation:* Latency is well within 500ms p95 target; database operations are not the bottleneck
- **Cost for Production:** Neon charges for storage and compute (generous free tier available)
  - *Mitigation:* Evaluate cost at Phase 5; free tier sufficient for development and likely early production
- **Vendor Lock-in:** Migrating from Neon requires data export/import
  - *Mitigation:* PostgreSQL is standard; export is straightforward; no vendor-specific features used

## Alternatives Considered

### Alternative A: In-Cluster PostgreSQL (StatefulSet + PVC)
- **Pros:** Network latency <1ms, no internet dependency, data in cluster, no vendor cost
- **Cons:** Requires StatefulSet, PVC, persistent storage, manual backups, cluster must have storage class
- **Why Rejected:** In-cluster database significantly increases Kubernetes complexity. Requires managing PVCs, storage classes, StatefulSets (more complex than Deployments), and manual backup setup. Neon provides all this automatically.

### Alternative B: SQLite Embedded
- **Pros:** No external dependency, zero network latency, file-based (simple)
- **Cons:** Single writer only, no concurrent access, no serverless scaling, not production-ready
- **Why Rejected:** SQLite doesn't support concurrent writes, which would break MCP server and backend scaling. SQLite is excellent for embedded use cases but not for multi-service web applications.

### Alternative C: Cloud SQL (GCP) / RDS (AWS)
- **Pros:** Cloud-managed, high reliability, well-integrated with respective cloud providers
- **Cons:** Higher cost, more complex setup, region coupling, may exceed free tier
- **Why Rejected:** Neon provides similar serverless PostgreSQL capabilities at lower cost with simpler setup. Cloud SQL/RDS are appropriate for large-scale production but overkill for current needs.

### Alternative D: CockroachDB
- **Pros:** Distributed SQL, automatic failover, cloud-native
- **Cons:** Different SQL dialect, higher cost, less mature PostgreSQL compatibility
- **Why Rejected:** Our application uses PostgreSQL-specific features (SQLModel, Alembic migrations). CockroachDB's partial PostgreSQL compatibility adds risk without clear benefit over Neon.

## References

- Feature Spec: [specs/001-k8s-local-deploy/spec.md](../../specs/001-k8s-local-deploy/spec.md)
- Implementation Plan: [specs/001-k8s-local-deploy/plan.md](../../specs/001-k8s-local-deploy/plan.md) AD-03
- Research Notes: [specs/001-k8s-local-deploy/research.md](../../specs/001-k8s-local-deploy/research.md) §7
- Related ADRs: ADR-0002 (Backend Stack - PostgreSQL foundation), ADR-0009 (Three-Container Architecture)
- Neon Documentation: https://neon.tech/docs
- Kubernetes StatefulSets: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
