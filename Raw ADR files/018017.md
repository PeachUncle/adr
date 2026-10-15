# ADR 0002 — Decoupling Database Access from the API Gateway

**Status:** Accepted
**Date:** 2025-10-29
**Context:** Architecture, Backend Design

---

## **Context**

The current architecture places the database inside the **API Gateway** service (`api-gateway/`), where it directly handles persistence for transcriptions and job status.

While this setup is simple and practical for early development, it tightly couples the gateway to the database schema and persistence logic.
If the schema changes, or if a dedicated “Transcription Service” is introduced later, many parts of the gateway would need updates.

---

## **Decision**

To mitigate tight coupling, we’ll introduce a **Repository Pattern** within the API Gateway.
All database access will go through a **repository layer** that abstracts persistence details.

### Example structure

```
api-gateway/
  ├─ src/
  │  ├─ repositories/
  │  │  └─ transcription.repository.ts
  │  ├─ services/
  │  │  └─ transcription.service.ts
  │  └─ controllers/
  │     └─ stt.controller.ts
```

### Example code

```ts
// transcription.repository.ts
export class TranscriptionRepository {
  async create(data) { /* insert into DB */ }
  async findById(id) { /* query by ID */ }
  async updateStatus(id, status) { /* update record */ }
}
```

This layer acts as an **interface between business logic and persistence**, allowing future refactors or service separation without breaking the gateway’s controllers.

---

## **Alternatives Considered**

1. **Keep direct DB access in controllers**

   * ✅ Simpler, fewer files
   * ❌ Strong coupling, hard to refactor later

2. **Move persistence to a dedicated Transcription Service**

   * ✅ Fully decoupled
   * ❌ Adds network hops and infrastructure early on

3. **Use a Message Queue for persistence**

   * ✅ Asynchronous, decoupled, scalable
   * ❌ Too complex for current scope

---

## **Consequences**

**Pros:**

* Easier to migrate to another database or service later
* Gateway logic remains simple and testable
* Enables a smooth evolution toward a microservice or event-driven design

**Cons:**

* Adds one more layer of abstraction
* Slightly more boilerplate in early development

---

## **Tags**

#architecture #adr #backend #repository-pattern #api-gateway #decoupling #database #stt-service