---
docid: ADR-103
title: ADR_SERVICE_BOUNDARIES
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# Architecture Decision Record: Service Boundaries & Domain Integration

**Date:** December 30, 2025  
**Author:** @Architect  
**Status:** Accepted  
**Scope:** Phase 1 Planning  

---

## Decision

**Establish clear service boundaries** for B2X microservices architecture to prevent coupling, enable independent scaling, and clarify ownership across bounded contexts.

---

## Context

### Current State
B2X is organized around multiple bounded contexts (Catalog, CMS, Customer, Identity, Tenancy, etc.), each with domain logic and APIs. However, inter-service communication patterns and data flow boundaries need explicit documentation.

### Problem
- **Unclear boundaries:** When should services communicate vs. replicate data?
- **Coupling risk:** Synchronous service calls create tight coupling
- **Scaling issues:** Can't scale services independently without clear responsibility boundaries
- **Testing difficulty:** Integration testing complicated by fuzzy service boundaries

### Goals
1. Define which service owns which domain/entity
2. Establish communication patterns (sync vs. async)
3. Prevent duplicate domain logic
4. Enable independent deployment

---

## Decision

### Service Boundary Map

```
┌─────────────────────────────────────────────────────────┐
│                    B2X System                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Catalog     │  │  CMS         │  │  Tenancy     │  │
│  │  Service     │  │  Service     │  │  Service     │  │
│  │              │  │              │  │              │  │
│  │ Owns:        │  │ Owns:        │  │ Owns:        │  │
│  │ - Products   │  │ - Pages      │  │ - Tenants    │  │
│  │ - Categories │  │ - Content    │  │ - Themes     │  │
│  │ - Pricing    │  │ - Assets     │  │ - Settings   │  │
│  │ - Inventory  │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Customer    │  │  Identity    │  │  Localization│  │
│  │  Service     │  │  Service     │  │  Service     │  │
│  │              │  │              │  │              │  │
│  │ Owns:        │  │ Owns:        │  │ Owns:        │  │
│  │ - Orders     │  │ - Users      │  │ - Translations
│  │ - Returns    │  │ - Auth       │  │ - Language   │  │
│  │ - Invoices   │  │ - Roles      │  │ - Locales    │  │
│  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Gateways (API Layer)                            │  │
│  │  - Store Gateway (public)                        │  │
│  │  - Admin Gateway (internal)                      │  │
│  │  - Orchestration Service (coordination)          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Ownership Rules

| Domain | Owner | Responsible For | Can Reference |
|--------|-------|-----------------|----------------|
| Products, Categories, Pricing, Inventory | **Catalog Service** | Complete product lifecycle | Tenancy (tenant context) |
| Pages, Content, Assets | **CMS Service** | Website content management | Localization (translations) |
| Users, Authentication, Authorization | **Identity Service** | User accounts and security | All services (via API) |
| Orders, Returns, Invoices | **Customer Service** | Customer transactions | Catalog (product info), Identity (customer data) |
| Tenants, Themes, Settings | **Tenancy Service** | Multi-tenancy support | All services (configuration) |
| Languages, Translations | **Localization Service** | Localization data | All services |

---

## Communication Patterns

### Rule 1: Database Isolation ✅
- Each service has its **own database**
- No direct database access from other services
- Data sharing only through APIs

### Rule 2: Synchronous Communication (Use Sparingly)
**When:** Reading real-time data, immediate response required  
**Example:** Customer Service → Catalog Service (check product availability)  
**Constraints:** Max 100ms timeout, circuit breaker required

### Rule 3: Asynchronous Communication (Preferred)
**When:** Notifications, eventual consistency, background processing  
**Example:** Order created → Catalog Service decreases inventory (async event)  
**Technology:** Wolverine messaging, event bus

### Rule 4: Data Replication (Acceptable)
**When:** Frequently accessed reference data  
**Example:** Catalog Service caches tenant settings locally  
**Constraints:** Must be read-only replica, periodic sync

### Rule 5: No Cross-Service Transactions
- Distributed transactions not allowed
- Use Saga pattern for multi-service workflows
- Accept eventual consistency

---

## Anti-Patterns (What NOT to do)

❌ **Don't:** Direct database access across services  
❌ **Don't:** Call Service A from Service B synchronously (deep chains)  
❌ **Don't:** Replicate entity ownership (two services own same entity)  
❌ **Don't:** Share domain models across services  
❌ **Don't:** Use distributed transactions (2-phase commit)  

---

## Inter-Service Communication Flows

### Flow 1: Place Order (Customer Service)

```
1. Customer Service receives order
2. Validates customer (Identity Service API call) ✓
3. Publishes OrderCreated event (async)
4. Catalog Service receives event → decreases inventory
5. Tenancy Service receives event → updates usage metrics
6. Localization Service (if needed) → prepares invoices
7. OrderConfirmed event published
8. Customer Service receives confirmation
```

**Pattern:** Async pub/sub with orchestration

### Flow 2: Update Product Price (Catalog Service)

```
1. Catalog Service updates product
2. Publishes ProductPriceUpdated event
3. Customer Service receives event (cache invalidation)
4. CMS Service receives event (if price displayed on site)
5. All services confirm receipt
```

**Pattern:** Async event broadcast

### Flow 3: User Authentication (Identity Service)

```
1. Any service needs user info
2. Calls Identity Service API synchronously
3. Gets user object with roles/permissions
4. Caches response (5 min TTL)
5. Falls back to cache on API failure
```

**Pattern:** Sync API with caching & circuit breaker

---

## Service Dependencies

### Dependency Graph
```
Catalog Service:
  Depends on: Tenancy (config), Localization (translations)
  
Customer Service:
  Depends on: Catalog (product data), Identity (user auth), Tenancy (config)
  
CMS Service:
  Depends on: Tenancy (config), Localization (translations)
  
Identity Service:
  Depends on: Tenancy (config)
  
Tenancy Service:
  Depends on: None (core service)
  
Localization Service:
  Depends on: None (utility service)
```

### Deployment Order
1. Tenancy Service (no dependencies)
2. Localization Service (no dependencies)
3. Identity Service (depends on Tenancy)
4. Catalog Service (depends on Tenancy, Localization)
5. CMS Service (depends on Tenancy, Localization)
6. Customer Service (depends on all)

---

## Data Governance

### Customer Data Ownership
- Identity Service: User accounts, authentication
- Customer Service: Orders, returns, transactions
- Tenancy Service: Tenant settings for users
- **Rule:** Only Customer Service can modify order data

### Product Data Ownership
- Catalog Service: All product information
- **Rule:** Only Catalog Service can modify product prices/inventory

### Content Data Ownership
- CMS Service: All website content
- **Rule:** Only CMS Service can modify content/pages

---

## Consistency Models

### Immediate Consistency (Sync APIs)
- Authentication checks (Identity Service)
- Configuration reads (Tenancy Service)
- Response time: < 100ms

### Eventual Consistency (Async Events)
- Inventory updates (when order placed)
- Usage metrics (when actions taken)
- Consistency target: < 5 seconds

### Strong Consistency (Not Used)
- Distributed transactions avoided
- If needed, redesign to single service

---

## Testing Strategy

### Unit Testing
Each service tests its own domain logic in isolation.

### Integration Testing
Services test against other services' APIs (Docker compose environment).

### Contract Testing
Services publish/subscribe contracts for async communication.

### End-to-End Testing
Full workflow testing through gateways.

---

## Implementation Roadmap

### Phase 1 (Current)
✅ Define service boundaries (this ADR)  
✅ Document data ownership  
✅ Establish communication patterns  

### Phase 2
⏳ Implement circuit breakers for sync calls  
⏳ Create Saga orchestration for complex workflows  
⏳ Setup event store for audit trail  

### Phase 3
⏳ Distributed tracing (correlation IDs)  
⏳ Service mesh (Istio/Linkerd)  
⏳ Advanced load balancing  

---

## Consequences

### Positive ✅
- Clear service ownership
- Independent scaling
- Reduced coupling
- Easier testing
- Technology flexibility per service

### Negative ⚠️
- Operational complexity (multiple databases)
- Network latency (API calls)
- Eventual consistency (complex workflows)
- Monitoring overhead

### Mitigation
- Use API gateways for simplified communication
- Implement robust error handling
- Monitor service health continuously
- Document all service contracts

---

## Related Decisions

- ADR: Event-Driven Architecture (published)
- ADR: DDD for Bounded Contexts (published)
- ADR: CQRS Pattern Usage (published)

---

## References

- Domain-Driven Design (Eric Evans)
- Building Microservices (Sam Newman)
- Patterns of Enterprise Application Architecture

---

## Approval

| Role | Decision | Date |
|------|----------|------|
| @Architect | ✅ Approved | Dec 30, 2025 |
| @Backend | ✅ Acknowledged | Dec 30, 2025 |
| @TechLead | ✅ Reviewed | Dec 30, 2025 |

---

**Decision Recorded By:** @Architect  
**Date:** December 30, 2025  
**Status:** Accepted & Implemented  
**Next Review:** Phase 2 (after 2 weeks of execution)
