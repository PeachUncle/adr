# ADR-003: Offline-First Sync with PowerSync and Supabase

**Date:** 2025-10-27  
**Related ADRs:**  
- [ADR-001: Offline-First Architecture](./adr-001-offline-first-decision.md)
- [ADR-002: Tech Stack Decision – React Native](./adr-001-offline-first-decision.md)


---

## 1. Context

We want our React Native app to:

- Work fully offline with local persistence.  
- Synchronize with a central authoritative backend.  
- Handle conflicts and merge changes reliably.  
- Support real-time updates when multiple clients modify data.  

We have selected **Supabase (self-hosted)** as our backend (PostgreSQL + PostgREST + Auth + Realtime) and **PowerSync** as the client-side sync engine to manage offline-first operation queues and conflict resolution.

---

## 2. Decision

Use **PowerSync** to handle the offline-first data synchronization between **local DB** and **Supabase**, combined with **Supabase Auth** for authentication and **Supabase Realtime** for near-instant updates.

---

## 3. Rationale

- **Offline-first support:** PowerSync handles queuing, retries, and merges.  
- **Central authority:** Supabase Postgres is the authoritative store.  
- **Authentication & security:** Supabase Auth + RLS simplifies access control.  
- **Realtime collaboration:** Supabase Realtime pushes changes to other clients.  
- **Maintainable & scalable:** This combination separates local and server concerns cleanly, and can scale as needed.

---

## 4. Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User
    participant UI as React Native UI
    participant LocalDB as Local DB (SQLite/WatermelonDB)
    participant PowerSync as PowerSync Engine
    participant Auth as Supabase Auth
    participant API as Supabase PostgREST API
    participant DB as PostgreSQL (Authoritative)
    participant Realtime as Supabase Realtime

    Note over User,UI: User edits a note while offline
    User->>UI: Edit note
    UI->>LocalDB: Save change locally
    LocalDB->>PowerSync: Queue operation (insert/update/delete)
    Note over LocalDB,PowerSync: Operation stored for later sync

    Note over PowerSync,Net: User goes online
    PowerSync->>Auth: Check access token
    Auth-->>PowerSync: Token valid

    PowerSync->>API: Push queued operation
    API->>DB: Apply change (RLS enforced)
    DB-->>API: Return authoritative state
    API-->>PowerSync: Update with server-confirmed record
    PowerSync->>LocalDB: Merge server response / resolve conflicts
    LocalDB-->>UI: Update UI with final state

    Note over DB,Realtime: Other clients also updated
    DB->>Realtime: Broadcast changes
    Realtime-->>PowerSync: Receive event
    PowerSync->>LocalDB: Apply remote update
    LocalDB-->>UI: Reflect changes in UI
