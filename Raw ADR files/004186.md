# ADR 0004: Tracking-Of-Newly-Introduced-Files

- **Status**: Accepted
- **Date**: 2025-09-07
- **Owners**: Tasqly Team
- **Related**: Phase0 — Slice4
- **Tags**: files, tracking, architecture

---

## Context
During Slice 4 implementation, several new files were introduced to support persistence abstraction, deterministic Id/Time providers, and application service coordination.  
To maintain project clarity, this ADR documents all newly created files, their layer, and purpose.

## Decision
The following files have been added:

### 1. Application Layer
- `src/app/loading/AppLoadingManager.h`  
- `src/app/loading/AppLoadingManager.cpp`  
  - Purpose: Manage application-wide loading state and expose readiness to UI/QML.

- `src/app/core/AppContext.h`  
- `src/app/core/AppContext.cpp`  
  - Purpose: Central registry holding repositories and utilities (`ITaskRepository`, `IGoalRepository`, `IUuidGen`, `IClock`).

- `src/app/usecases/InitRepositories.h`  
- `src/app/usecases/InitRepositories.cpp`  
  - Purpose: Initialize repositories, register them into `AppContext`, update `AppLoadingManager`, and log initialization result.

- `src/app/usecases/ListTasks.h`  
- `src/app/usecases/ListTasks.cpp`  
  - Purpose: Use case for listing tasks with pagination.

### 2. Infrastructure Layer
- `src/infra/utils/SystemUuidGen.h`  
  - Purpose: Production UUID generator using Qt's `QUuid`.

- `src/infra/utils/SystemClock.h`  
  - Purpose: Production clock returning current system time with `QDateTime`.

### 3. Test Utilities
- `tests/fakes/FakeUuidGen.h`  
  - Purpose: Deterministic fake UUID generator.

- `tests/fakes/FakeClock.h`  
  - Purpose: Deterministic fake clock for manual time control in tests.

## Consequences
- ✅ Application layer has explicit managers (`AppLoadingManager`, `AppContext`).  
- ✅ Infrastructure and test fakes separate production and test implementations.  
- ⚠️ Requires ongoing CI/code review checks to enforce conventions.  
- 🔄 QML demo and seeding toggle ADR still pending.

## References
- `src/app/loading/AppLoadingManager.h`  
- `src/app/core/AppContext.h`  
- `src/app/usecases/ListTasks.h`
