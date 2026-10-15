# ADR-0013: Kafka Topic Structure for PolyShop

## Status
Accepted

## Date
2025-11-17

## Context

PolyShop uses Kafka for all inter-service asynchronous communication.  
Topic structure must support:

- Clear separation by domain
- Event versioning
- Multiple consumers per event
- Replay capability
- Schema evolution
- Dead-letter handling
- Reduced cross-service coupling

A consistent naming structure is required so all teams (Auth, Product, Order, Inventory, Payment, Notification, Search, Analytics) follow the same rules.

---

# Decision

We adopt a **standardized, versioned Kafka topic naming convention**:

```

polyshop.<service>.<entity>.<action>.v<version>

```

This ensures readability, predictable patterns, and version control.

---

# Topic Categories

## 1. Auth Topics
```

polyshop.auth.user.registered.v1
polyshop.auth.user.verified.v1
polyshop.auth.user.password-reset-requested.v1
polyshop.auth.user.password-changed.v1

```

## 2. Product Topics
```

polyshop.product.product.created.v1
polyshop.product.product.updated.v1
polyshop.product.product.archived.v1
polyshop.product.category.created.v1
polyshop.product.category.updated.v1

```

## 3. Inventory Topics
```

polyshop.inventory.stock.reserved.v1
polyshop.inventory.stock.released.v1
polyshop.inventory.stock.confirmed.v1
polyshop.inventory.stock.movement-recorded.v1

```

## 4. Order Topics
```

polyshop.order.order.created.v1
polyshop.order.order.paid.v1
polyshop.order.order.cancelled.v1
polyshop.order.order.fulfilled.v1
polyshop.order.order.failed.v1

```

## 5. Payment Topics
```

polyshop.payment.payment.initiated.v1
polyshop.payment.payment.success.v1
polyshop.payment.payment.failed.v1
polyshop.payment.refund.created.v1
polyshop.payment.refund.success.v1

```

## 6. Notification Topics
```

polyshop.notification.email.sent.v1
polyshop.notification.sms.sent.v1

```

## 7. Search Topics
```

polyshop.search.product.index-requested.v1
polyshop.search.product.index-updated.v1

```

## 8. Analytics Topics
```

polyshop.analytics.event.ingested.v1
polyshop.analytics.daily-stats-computed.v1
polyshop.analytics.sales-aggregated.v1

```

---

# Partition Strategy

**Rule 1 — Order-sensitive events**  
Key = entityId (e.g., orderId)

Example:
```

polyshop.order.order.created.v1
key → orderId

```
Guarantees correct ordering for Sagas.

**Rule 2 — High throughput (analytics/log-like)**  
Multiple partitions (8–32 recommended).

**Rule 3 — User-specific events**  
Key = userId

Example:
```

polyshop.auth.user.registered.v1

```

---

# Replication Factor

All topics use:
```

replication.factor = 3
min.insync.replicas = 2

```

Production-safe defaults.

---

# Retention Strategy

### Business critical events  
```

retention.ms = 7 days

```

### High frequency analytics events  
```

retention.ms = 24 hours

```

### Audit-compliant events (Auth, Order, Payment)  
```

retention.ms = 90 days

```

### DLQ topics  
```

retention.ms = 14 days

```

---

# DLQ Topic Naming

```

polyshop.dlq.<original_topic_name>

```

Example:
```

polyshop.dlq.polyshop.order.order.created.v1

```

When a consumer fails 5 times consecutively, message is pushed to DLQ.

---

# Schema Storage & Validation

All event schemas are stored in:

```

/docs/events/

```

Each event type must include:

- JSON Schema
- Example payload
- Version number
- Backward compatibility notes

A producer **must validate** the event before publishing.

---

# Alternatives Considered

### A — Single-topic design  
Rejected: impossible to scale, no domain separation.

### B — Per-service but no versioning  
Rejected: evolution breaks consumers.

### C — Use Avro + Schema Registry only  
Not chosen for now to avoid complexity. Optional future upgrade.

Kafka topic naming must remain stable regardless of serialization format.

---

# Consequences

### Benefits
- Predictable naming  
- Supports evolution through versioning  
- Strong domain boundaries  
- Easier monitoring, metrics, alerting  
- Robust DLQ/trace workflows

### Drawbacks
- Many topics (30+)  
- Requires management automation  
- Versioning introduces maintenance overhead

---

# Final Decision

PolyShop adopts a **fully versioned, domain-structured Kafka topic layout** to support stable, scalable, event-driven workflows across all services.