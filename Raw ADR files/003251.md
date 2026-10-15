# ADR-0009: Kafka Topic Naming Convention

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop uses Kafka for:
- Order Saga orchestration
- Event-driven communication across services
- Search indexing updates
- Email/SMS notifications
- Payment workflow triggers

A consistent topic naming format is required to avoid:
- Confusion across environments
- Conflicts between services
- Unclear ownership of topics
- Difficulty applying ACLs and retention policies

A standardized naming convention must also support:
- Multi-environment deployment (local/dev/staging/prod)
- Versioning of event schemas
- Partition strategies
- Future extension to other brokers

---

# Decision

PolyShop adopts the following **Kafka topic naming format**:

```

{domain}.{entity}.{event}.{version}

```

Example:
```

order.payment.failed.v1
inventory.reservation.created.v1
product.updated.v1
notification.email.send.v2

```

---

# 1. Topic Naming Rules

Each topic contains **four parts**:

### 1. **domain**
Represents the service or business area.
Allowed examples:
- `auth`
- `order`
- `inventory`
- `payment`
- `product`
- `search`
- `notification`
- `analytics`

### 2. **entity**
The object the event refers to:
- `user`
- `order`
- `reservation`
- `payment`
- `product`
- `template`

### 3. **event**
Concrete action/state change:
- `created`
- `updated`
- `deleted`
- `reserved`
- `confirmed`
- `cancelled`
- `failed`
- `completed`
- `expired`

### 4. **version**
Schema version of the event payload:
- Format: `v1`, `v2`, …

Version increments when:
- Breaking changes occur
- Field is removed
- Field meaning changes
- Enum values change meaning

Non-breaking additions do **not** require version updates.

---

# 2. Topic Examples (Approved List)

### Order Domain
```

order.created.v1
order.cancelled.v1
order.payment.pending.v1
order.payment.completed.v1
order.payment.failed.v1

```

### Payment Domain
```

payment.intent.created.v1
payment.refund.created.v1
payment.refund.failed.v1

```

### Inventory Domain
```

inventory.reservation.created.v1
inventory.reservation.confirmed.v1
inventory.reservation.released.v1
inventory.stock.changed.v1

```

### Product Domain
```

product.updated.v1
product.created.v1
product.deleted.v1

```

### Notification Domain
```

notification.email.send.v1
notification.sms.send.v1
notification.template.updated.v1

```

### Search Indexing
```

search.product.index.v1
search.product.remove.v1

```

### Analytics Domain
```

analytics.order.aggregated.v1
analytics.sales.daily.v1

```

---

# 3. Environment Prefixing (Mandatory)

Each environment prefixes topics:

```

local.order.created.v1
dev.order.created.v1
staging.order.created.v1
prod.order.created.v1

```

Benefits:
- No accidental cross-environment consumption
- Easier debugging/logging
- Cleaner ACL management

---

# 4. Partitioning Strategy

Default:
- 3 partitions per topic

High-volume topics:
- `order.created.v1` → 6–12 partitions
- `payment.intent.created.v1` → 6 partitions

Low-volume topics:
- `notification.template.updated.v1` → 1 partition

Partition key rule:
```

Use the entity primary identifier.

```

Examples:
- Order events → `orderId`
- Inventory reservation → `reservationId`
- Payments → `paymentId`
- Users → `userId`

---

# 5. Retention Policy

| Topic Group | Retention |
|-------------|-----------|
| Order events | 7 days |
| Payment events | 14 days |
| Inventory reservations | 3 days |
| Search indexing | 1 day |
| Notification events | 1 day |
| DLQs | 14–30 days |

DLQ Topic Format:
```

{topic}.dlq

```

Example:
```

prod.order.created.v1.dlq

```

---

# 6. Alternative Naming Considered

### Option A – `{service}.{event}`
Rejected: too ambiguous, no schema versioning.

### Option B – Snake case
Rejected: inconsistent with industry standards.

### Option C – Event type only
Rejected: same topic used by multiple services, messy.

---

# Consequences

### Positive
- Clear ownership of topics
- Easy maintenance and filtering
- Supports long-term system evolution
- Strong compatibility with schema registries
- Works for local/dev/staging/prod separation

### Negative
- Slightly more verbose topic names

---

# Final Decision

All Kafka topics in PolyShop must follow:

```

{environment}.{domain}.{entity}.{event}.{version}

```

This ensures a uniform, scalable, and future-proof messaging strategy.