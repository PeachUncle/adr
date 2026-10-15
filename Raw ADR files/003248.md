# ADR-0006: Database Strategy for PolyShop Microservices

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop uses multiple independent microservices:
- Auth
- Product
- Inventory
- Order
- Payment
- Search
- Notification
- Analytics

Each service deals with different data lifecycles and scaling patterns.

A unified database strategy is required to ensure:
- Independent scaling
- Independent deployments
- Fault isolation
- Correctness of data
- Consistency across distributed workflows (Order Saga)

---

# Decision

PolyShop adopts a **polyglot persistence** model with:
- **One database per service**
- **Private database schema per service**
- **No shared tables**
- **No direct cross-service DB queries**
- **Cross-service communication via Kafka events**

---

# 1. Database Choice Per Service

## 1.1 Auth Service → PostgreSQL
Reasons:
- Strict consistency
- Relational data (users, sessions, roles)
- Strong ACID requirements
- Efficient indexing for login lookup

Schema stored under:

```

infra/db/auth/

```

---

## 1.2 Product Service → PostgreSQL
Reasons:
- Product catalog fits relational structure
- Categories, variants, attributes
- Strong consistency for admin updates
- Supports indexing for search integration

Schema under:

```

infra/db/product/

```

---

## 1.3 Inventory Service → PostgreSQL
Reasons:
- Atomic operations on stock
- Reservation table requires transactions
- Concurrency via row-level locking
- Event-based reconciliation

Schema under:

```

infra/db/inventory/

```

---

## 1.4 Order Service → PostgreSQL
Reasons:
- Order lifecycle is relational
- Strong transactions for order creation
- Uses state machine table (CREATED → PAID → FULFILLED)

Schema under:

```

infra/db/order/

```

---

## 1.5 Payment Service → PostgreSQL + Redis (optional)
PostgreSQL used for:
- Payment intents
- Refunds
- Provider references

Redis optional for:
- Storing ephemeral payment session state
- Improving speed for repeated checks

Schema under:

```

infra/db/payment/

```

---

## 1.6 Search Service → OpenSearch / Elasticsearch
Reasons:
- Full-text search
- Faceting
- Relevance scoring
- Scalable read operations

Index definitions stored under:

```

search-service/indexes/

```

---

## 1.7 Notification Service → MongoDB (optional)
Reasons:
- Flexible templates (email, SMS)
- Schemaless variable structures
- Storing message logs cheaply

Schema design under:

```

infra/db/notification/

```

---

## 1.8 Analytics Service → Data Lake + ClickHouse (future)
Reasons:
- High write throughput
- Analytical queries (daily revenue, funnel metrics)

Stage 1: write raw events to data lake (S3 / MinIO)  
Stage 2: batch load into ClickHouse

Files under:

```

analytics-service/models/

```

---

# 2. Cross-Service Communication Rules

## 2.1 No service can read another service's DB
Strict rule.

Example of forbidden design:
- Order service reads Product DB
- Inventory reads Order DB

All communication must be through:
- Kafka events
- REST API calls (read-only only)

---

# 3. Event Sourcing Boundary

Not full event sourcing, but:
- Order creation emits `Order.Created`
- Payment emits `Payment.Succeeded`
- Inventory emits `Stock.Reserved`

Events stored in each service DB only as an **outbox**, not full event store.

Stored in:

```

common-java/outbox/

```

---

# 4. Transaction Boundaries

- All service-local changes must be **transactional**
- Cross-service workflows use **Saga pattern**
- No distributed SQL transactions

---

# 5. Disaster Recovery

Each DB must implement:
- Point-in-time recovery (PITR)
- Automated daily backups
- Retention policies per service

Stored under:

```

infra/scripts/backup/

```

---

# 6. Alternatives Considered

### 1. Monolithic shared DB
Rejected:
- Deployment coupling
- Scaling issues
- Hard to isolate failures

### 2. Single-type database for all services
Rejected:
- Different services have different needs (search, analytics)

### 3. Full event sourcing & CQRS
Rejected:
- Too heavy for v1
- Requires major operational complexity

---

# Consequences

### Positive
- Clear ownership per service
- Strong isolation
- Independent scaling and failover
- Clean event-driven architecture

### Negative
- Need to maintain multiple databases
- Requires DevOps automation
- Complex local development environment

---

## Final Decision
Each microservice receives its own **isolated** database, with:
- PostgreSQL for transactional services  
- OpenSearch for search  
- MongoDB or PostgreSQL for notifications  
- Data lake + ClickHouse for analytics  

All cross-service communication flows through REST + Kafka events.