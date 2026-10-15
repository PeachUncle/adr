# ADR-0003: Event Contract Design for PolyShop

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop uses Kafka for asynchronous communication between microservices.  
Events must be:
- stable
- versioned
- backwards compatible
- safe to evolve
- domain-driven

Without clear rules, services could publish breaking payloads or inconsistent names, causing consumer failures.

## Decision
Adopt a **centralized event contract specification**, stored in:

```

/docs/events/polyshop-events.md
/libs/common-* (event DTOs)
/kafka/topics/*.md

````

### Rules
1. **Each domain owns its events**
   - Auth → `auth.*`
   - Orders → `order.*`
   - Inventory → `inventory.*`
   - Payment → `payment.*`
   - Product → `product.*`

2. **Event = immutable fact**
   - No updates, no deletes.
   - Corrections published as new events.

3. **Versioning**
   - Every event uses a version suffix:
     ```
     product.created.v1
     order.paid.v2
     ```
   - Additive changes must maintain backward compatibility.

4. **Payload Envelope**
```json
{
  "eventId": "uuid",
  "eventType": "string",
  "version": 1,
  "timestamp": "ISO-8601",
  "data": {}
}
````

5. **Schema storage**

    * All schemas stored in `/docs/events/`
    * Language-specific DTOs in:

        * `libs/common-java/`
        * `libs/common-js/`
        * `libs/common-py/`

6. **Consumer Policies**

    * Must tolerate unknown fields.
    * Must not break when optional fields appear.

7. **Dead Letter Queue Rules**

    * Each topic has a parallel `.DLQ` topic.
    * DLQ events include:

        * raw event
        * error message
        * stack trace (if available)

### Topic Naming

```
polyshop.{service}.{entity}.{event}.{version}
```

Examples:

```
polyshop.order.order.created.v1
polyshop.payment.payment.succeeded.v1
polyshop.inventory.stock.reserved.v1
```

### Event Lifetimes

| Event Category         | Retention |
| ---------------------- | --------- |
| Order events           | 14 days   |
| Payment events         | 30 days   |
| Inventory reservations | 7 days    |
| Product index events   | 3 days    |
| Email/SMS events       | 3 days    |

## Alternatives Considered

### 1. No versioning

Rejected — any change would break old consumers.

### 2. Inline JSON schema with each service

Rejected — duplication and inconsistency risk.

### 3. Avro/Protobuf

Postponed — may adopt in the future.

## Consequences

### Positive

* Predictable event evolution
* Strong domain boundaries
* Safe schema governance
* Easier debugging via consistent envelopes

### Negative

* Requires governance discipline
* Version proliferation possible

## Final Decision

All PolyShop services must publish and consume events strictly following this contract.
All new events must be added to `/docs/events/polyshop-events.md`.