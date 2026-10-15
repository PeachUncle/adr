# ADR 0025: db-abstraction-layer-and-repo-refactor

- **Status**: Draft  
- **Date**: 2025-11-15  
- **Owners**: Tasqly Core Team  
- **Related**: Phase 1 — Slice 2.5  
- **Tags**: db, abstraction, repository, refactor, postgres, infra

---

## Context

The previous Postgres repository (`P1_S2_PostgresTaskRepository`) relied directly on **libpq** types (`PGconn`, `PGresult`) and imperative SQL execution, tightly coupling the persistence layer to the DB driver and making testing extremely hard.

As part of **Slice 2.5**, the architecture requires:

- Full DB abstraction  
- Deterministic fakes for testing  
- Repository refactor to remove all libpq code  
- Clean separation between **Infra Errors** and **Domain Errors**

To achieve this, we needed to build a DB-access layer that sits *under* repositories and hides all driver-specific logic.

This ADR documents:
- What has been completed so far  
- What remains to finish Slice 2.5 cleanly  

---

## Decision

### ✅ Completed

#### 1. **Result Abstraction Layer**
- Added `P1_S2_Result` (DbResult + DbQueryResult).
- Bridges infra runtime errors (`P1_Error`) with DB operations.
- Central to all new DB-facing APIs.

#### 2. **DB Interface Abstraction**
- Added `IDbConnection` with:
  - `execute(sql)`
  - `reset()`
  - `isValid()`
- Decoupled completely from libpq and connection drivers.

#### 3. **Concrete Implementations**
- Implemented `P1_S2_PostgresConnection`:
  - Wraps libpq internally
  - Retry logic (exec → fail → reset → retry)
  - Masks sensitive data
  - Converts PGresult → DbQueryResult

- Implemented `P1_S2_FakeDbConnection`:
  - Fully deterministic
  - Supports failure injection
  - Will be used by tasqly_fakes target

#### 4. **Repository Refactor Begin**
- Created new location:
src/infra/db/P1_S2_DbTaskRepository.h/.cpp

markdown
Copy code
- Removed old Postgres-repo entirely.
- Connected repo to:
- `IDbConnection`
- `DbResult`
- `P1_Logger`
- DomainResult/DomainError mapping
- Implemented:
- Correct interface alignment with `P1_ITaskRepository`
- Valid error conversions (Infra → Domain)

#### 5. **Supporting Fixes**
- Aligned namespaces between infra/runtime and domain/core.
- Fixed error mapping in `mapDbError`.
- Fixed Postgres connection forward declaration + casting in `.cpp`.

---

### ⏳ Remaining Work (required to complete Slice 2.5)

#### 1. **SQL Layer (Repository Implementation)**
We must now implement all SQL statements inside `P1_S2_DbTaskRepository`:

- [ ] INSERT (create)
- [ ] SELECT (getById)
- [ ] UPDATE
- [ ] DELETE
- [ ] LIST + filters + paging

#### 2. **Mapping Layer**
Implement:
- [ ] `mapSingleRow(qr)`
- [ ] `mapRows(qr)`

That convert `DbQueryResult` → `Task`.

#### 3. **Error Handling**
Complete mapping:
- InfraError → DomainError (already scaffolded)
- Ensure consistent behavior across all CRUD operations

#### 4. **Repository Factory Update**
- [ ] Update existing Repo factory to start injecting:
- `PostgresConnection`  
- OR `FakeDbConnection` (fallback/testing)

#### 5. **Migration Integration**
SQL files created earlier:
- `P1_S2_create_tasks.sql`
- `P1_S2_drop_tasks.sql`

Need to be used:
- [ ] Inside a migration runner or setup step
- [ ] Ensuring tasks table schema matches repo expectations

---

## Consequences

### ✅ Benefits
- Fully testable DB layer (thanks to deterministic fakes)
- Completely decoupled repository logic
- Clean separation between infra & domain
- Isolation from libpq → easier future swap (e.g., SQLite)
- More maintainable SQL layer

### ⚠️ Drawbacks / Risks
- Additional upfront code for SQL building
- Mapping layer needs careful, schema-synchronized implementation
- Repo now depends on a fully correct `DbQueryResult` format

### 🔄 Trade-offs
- Chose an IDbConnection abstraction instead of a higher-level ORM-like helper; more manual but far more predictable and stable.
- Kept SQL as raw strings for Slice 2.5; builders may be introduced later in Slice 3 for more structure.

---

## References

- `P1_S2_IDbConnection.h/.cpp`
- `P1_S2_PostgresConnection.h/.cpp`
- `P1_S2_FakeDbConnection.h/.cpp`
- `P1_S2_DbTaskRepository.h/.cpp`
- `P1_S2_Result.h`
- `P1_Error.h`
- `P1_DomainResult.h`
- `P1_ITaskRepository.h`
- SQL files:
- `P1_S2_create_tasks.sql`
- `P1_S2_drop_tasks.sql`