# ADR-0007: API Versioning Strategy

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop exposes multiple APIs:
- Public Gateway API
- Internal service-to-service APIs
- Event payload schemas (Kafka)

As the system evolves, backward compatibility must:
- Support mobile and web clients
- Avoid breaking integrations
- Permit safe internal refactoring
- Allow parallel version adoption

A versioning strategy must be consistent across all services.

---

# Decision

PolyShop uses **semantic API versioning**, with:

- **Major versions** breaking (v1, v2…)
- **Minor versions** additive only
- **Patch versions** non-breaking fixes

Versioning applies to:

1. REST endpoints
2. OpenAPI definitions
3. Event payloads
4. Client SDKs

---

# 1. REST API Versioning

### Format  
All REST endpoints use:

```

/v1/<resource>...

```

Examples:
```

GET /v1/auth/login
GET /v1/products
POST /v1/orders

```

### Rules

- **Major version in URL path**
- **Backward compatible changes**:
  - Adding optional fields
  - Adding new endpoints
  - Extending enums (with fallback)
- **Breaking changes require new major version**

### Deprecation Process
1. Announce end-of-life in `/.well-known/polyshop/deprecations.json`.
2. Keep old version supported for 6–12 months.
3. Remove endpoint only after all clients migrate.

---

# 2. Internal Service-to-Service API Versioning

Services communicate using:
- REST
- Kafka events

Internal REST APIs also follow `/v1/` rules.

Services interacting with multiple versions must:
- Support **dual readers** temporarily
- Reject unsupported versions with `426 Upgrade Required`

---

# 3. Event Versioning Strategy

Event format:

```

{
"eventType": "Order.Created",
"version": 1,
"data": { ... },
"timestamp": "...",
"metadata": { ... }
}

```

Rules:
- Each event type includes a **version** field
- New version = breaking change
- Consumers must handle older versions until deprecated

### Non-breaking event changes:
✔ adding fields  
✔ adding optional subobjects  
✔ adding metadata  

### Breaking event changes:
✘ renaming fields  
✘ removing fields  
✘ changing field types  
✘ modifying required structure  

In case of breaking change:
- Publish events using **both v1 and v2** for a migration window
- Deprecated versions removed only after all consumers migrate

---

# 4. OpenAPI Versioning

OpenAPI filename must match service version:

```

product-service.v1.yaml
inventory-service.v1.yaml
order-service.v1.yaml

```

Each spec contains:

```

info:
version: "1.0.0"

```

Major bumps require:
- New YAML file
- Gateway mapping for each version

---

# 5. Client SDKs

Client packages use semantic versions:
- Java SDK: `com.polyshop.sdk:1.3.0`
- Node SDK: `@polyshop/sdk@1.3.0`
- Python SDK: `polyshop-sdk==1.3.0`

Breaking API updates → major version bump.

---

# 6. Alternatives Considered

### 1. No versioning (always backward compatible)
Rejected:
- Unrealistic for long-term evolution
- Would force fragile compatibility hacks

### 2. Header-based versioning
Rejected:
- Harder for debugging
- Hard to document
- Harder to route in API Gateway

### 3. Query-parameter versioning (`?version=1`)
Rejected:
- Incorrect semantics
- Poor API design

---

# Consequences

### Positive
- Safe long-term evolution of APIs
- Predictable upgrade paths
- Simple version routing
- Easy generation of client SDKs

### Negative
- Duplicate OpenAPI files for major versions
- Additional maintenance during transitions

---

## Final Decision

PolyShop adopts **semantic versioning** across REST APIs, events, and OpenAPI files.  
Major versions appear directly in the URL path.  
Breaking changes require publishing a new major version and providing a migration period.