---
layout: default
title: Architecture Decision Records
parent: Architecture
nav_order: 2
---

# Architecture Decision Records (ADRs)
{: .no_toc }

Key architectural decisions documented for future reference.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## What are ADRs?

Architecture Decision Records (ADRs) document important architectural decisions made during the project. Each ADR captures:

- **Context:** What is the issue we're facing?
- **Decision:** What did we decide?
- **Consequences:** What are the trade-offs?

---

## Decision Records

### ADR-0001: SQLite First Strategy

**Status:** ✅ Accepted

**Context:**  
Need a simple database for MVP without complex setup.

**Decision:**  
Use SQLite for initial development, with clean repository interfaces to allow PostgreSQL migration later.

**Consequences:**
- ✅ Zero configuration for developers
- ✅ Easy local testing
- ⚠️ Limited concurrency (acceptable for MVP)

📄 [Full Document](https://github.com/deniswm/petwise-mvp/blob/master/docs/architecture/decisions/adr-0001-database-sqlite-first.md)

---

### ADR-0002: Appointment Status Lifecycle Model

**Status:** ✅ Accepted

**Context:**  
Appointments need a clear state machine with valid transitions.

**Decision:**  
Implement explicit status enum with transition validation in the aggregate:
- `SCHEDULED` → `CONFIRMED` → `IN_PROGRESS` → `COMPLETED`
- `SCHEDULED` → `CANCELLED`

**Consequences:**
- ✅ Business rules enforced at domain level
- ✅ Clear lifecycle prevents invalid states
- ℹ️ Status transitions must be explicit

📄 [Full Document](https://github.com/deniswm/petwise-mvp/blob/master/docs/architecture/decisions/adr-0002-appointment-status-model.md)

---

### ADR-0003: Domain Modeling with DDD Basics

**Status:** ✅ Accepted

**Context:**  
Need clear separation between entities, value objects, and aggregates.

**Decision:**  
Apply DDD tactical patterns:
- **Entities:** Objects with identity (Tutor, Pet, Appointment)
- **Value Objects:** Immutable, identity-less (Email, Phone, DateRange)
- **Aggregates:** Consistency boundaries (Appointment manages AppointmentStatus)

**Consequences:**
- ✅ Clear business logic encapsulation
- ✅ Testable domain model
- ℹ️ Requires discipline to maintain boundaries

📄 [Full Document](https://github.com/deniswm/petwise-mvp/blob/master/docs/architecture/decisions/adr-0003-domain-modeling-ddd-basics.md)

---

### ADR-0004: Repository and Gateway Strategy

**Status:** ✅ Accepted

**Context:**  
Need persistence abstraction without coupling to JPA.

**Decision:**  
Use repository pattern with domain-level interfaces (gateways):
- Domain defines contracts (e.g., `TutorGateway`)
- Infrastructure implements with JPA or other tech

**Consequences:**
- ✅ Domain independent of persistence tech
- ✅ Easy to test with in-memory implementations
- ✅ Can swap JPA for other solutions

📄 [Full Document](https://github.com/deniswm/petwise-mvp/blob/master/docs/architecture/decisions/adr-0004-repository-and-gateway-strategy.md)

---

### ADR-0005: Use Case Pattern

**Status:** ✅ Accepted

**Context:**  
Need consistent structure for application layer operations.

**Decision:**  
Every use case follows single responsibility:
```java
public interface UseCase<INPUT, OUTPUT> {
    OUTPUT execute(INPUT input);
}
```

**Consequences:**
- ✅ Clear, testable, single-purpose operations
- ✅ Easy to compose and orchestrate
- ℹ️ One class per use case (can grow file count)

📄 [Full Document](https://github.com/deniswm/petwise-mvp/blob/master/docs/architecture/decisions/adr-0005-usecase-pattern.md)

---

## ADR Template

Want to create a new ADR? Use our template:

📄 [ADR Template](https://github.com/deniswm/petwise-mvp/blob/master/docs/architecture/decisions/adr-template.md)

---

## Full ADR Documents

All ADRs are available in the repository:

📁 [`docs/architecture/decisions/`](https://github.com/deniswm/petwise-mvp/tree/master/docs/architecture/decisions)

