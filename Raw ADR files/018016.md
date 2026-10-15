# ADR 0001 – Database Location

**Date:** 2025-10-29  
**Status:** Accepted  
**Context:** Architecture Decision Record  

---

## Context

The `stt-service` project consists of multiple components:
- **api-gateway** (Node/TypeScript): orchestrates requests, queueing, and communication with the transcription backend.
- **whisper-service** (Python/FastAPI): handles audio transcription using Whisper models.
- **shared/**: holds files shared across services (e.g., uploads, transcripts).

We need to store transcription metadata and text in a **durable** and **queryable** way (for example, to retrieve past transcriptions, job statuses, or audit logs). The decision concerns **where** the database should live in this architecture.

---

## Decision

The database will **live within the `api-gateway/` service**.

Specifically:
- A `db/` folder will be added under `api-gateway/src/` (e.g. `api-gateway/src/db/`).
- The API Gateway will manage **all persistence** (job status, transcription metadata, results, etc.).
- The `whisper-service` will remain **stateless**, performing only audio processing and returning results to the gateway.
- The database engine can start with **SQLite** for local development and later migrate to **PostgreSQL** without changing higher-level architecture.

---

## Rationale

- Keeps data ownership clear: the API Gateway orchestrates all requests and owns their lifecycle.
- The whisper-service remains isolated, easier to scale and swap (or replace with another transcription engine).
- Simplifies authentication, migration, and access control by keeping persistence in one service.
- Aligns with 12-factor app principles: stateless workers, stateful orchestrators.

---

## Consequences

**Pros:**
- Clear responsibility boundaries.
- Easier debugging and testing (mock Whisper responses, persist test data locally).
- Portable database strategy (SQLite → PostgreSQL).

**Cons:**
- Slightly increases the complexity of the API Gateway.
- Adds coupling between the gateway and the database schema.

---

## Alternatives Considered

1. **Shared database service (central DB folder at root)**
   - Rejected because it couples services too tightly.
2. **Database inside whisper-service**
   - Rejected because Whisper should remain a stateless worker, not a data owner.

---

## Future Evolution

- A separate ADR will describe **database schema design**.
- Another ADR will handle **migration strategy** and **multi-environment configuration** (local, staging, production).

---

## References

- `PROJECT_STRUCTURE.md`
- `ARCHITECTURE.md`
