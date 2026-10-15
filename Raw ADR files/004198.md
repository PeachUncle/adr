# ADR 0006: testing-access-limitation-in-postgrestaskrepository

- **Status**: Draft  
- **Date**: 2025-11-12  
- **Owners**: Tasqly Team  
- **Related**: Phase1 — Slice2  
- **Tags**: testing, access-control, postgres, repository, cmake, macros

---

## Context

During coverage expansion for `P1_S2_PostgresTaskRepository.cpp`,  
the team encountered restricted access to internal class members.  
Specifically, the method `executeQuery()` and the member `m_conn` are declared as `private`.  
These members are essential for unit tests that simulate internal connection recovery logic,  
such as handling of invalid PostgreSQL states and retry mechanisms using `PQreset()`.

Because these elements are not accessible from outside the class,  
unit tests could not properly verify behavior when connections fail or recover.  
The repository class is also declared `final`, which prevents test inheritance for controlled mocking.

To bypass this limitation, a temporary compile-time macro  
`TASQLY_TESTING_BUILD` was introduced through the CMake configuration.  
This macro allows test builds to alter access levels or relax `final` restrictions,  
enabling internal testing without modifying core runtime logic.

---

## Decision

A conditional compilation flag (`TASQLY_TESTING_BUILD`)  
is defined in the CMake test configuration.  
When active, it adjusts access modifiers inside `P1_S2_PostgresTaskRepository`  
to allow test classes to reach internal members for behavior verification.  
This approach was adopted as a practical short-term solution  
to raise coverage and enable deterministic tests for retry and failure paths.

---

## Consequences

- ✅ Enables isolated unit testing of connection handling and retry logic.  
- ✅ Allows coverage improvement without altering functional code behavior.  
- ⚠️ Introduces conditional access modifiers inside production headers.  
- ⚠️ Blurs separation between production and testing concerns.  
- ⚠️ May affect class interface consistency across build contexts.  
- 🔄 Will require future refactoring toward a cleaner, maintainable testing approach  
  (e.g., dedicated Test Access Layer or Dependency Injection for database interfaces).

---

## References

- `src/infra/db/P1_S2_PostgresTaskRepository.h`  
- `tests/unit/persistence/test_P1_S2_PostgresTaskRepository.cpp`  
- `Phase1_Tests.cmake`  
- `ADR 0005 — Conditional Testing Build Configuration`
