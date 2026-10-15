# ADR 0003: handle-postgresql-tests-on-windows-ci

- **Status**: Accepted  
- **Date**: 2025-11-03  
- **Owners**: Tasqly Infrastructure Team  
- **Related**: Phase1 — Slice2  
- **Tags**: CI, Testing, PostgreSQL, Cross-Platform  

---

## Context

During continuous integration (CI) execution, PostgreSQL-based integration tests failed to build and run on **Windows** (both MSVC and MinGW) environments.  
The cause was the missing PostgreSQL client development headers and libraries (`libpq-fe.h`, `libpq.lib`, etc.) which are not available on default GitHub Windows runners.

Tests affected:
- `MigrationIntegrationTest`
- `PostgresTaskRepoTest`

These tests compile successfully on Linux where `libpq-dev` is available.

This led to the need for a unified strategy ensuring that:
- Windows CI builds remain stable without PostgreSQL dependencies.
- Linux CI continues to fully validate database integration logic.
- Local Windows builds can skip or exclude those tests gracefully.

---

## Decision

We adopted an **environment-aware exclusion strategy** that separates PostgreSQL integration tests from Windows builds.

1. **Windows (Local + CI)**
   - PostgreSQL integration tests are **skipped or excluded** to prevent missing header errors.
   - `DatabaseIntegrationFixture` uses runtime detection:
     ```cpp
     const char* ci = std::getenv("CI");
     if (ci && std::string(ci) == "true") {
         GTEST_SKIP() << "Skipping PostgreSQL integration tests on Windows CI (GitHub Actions).";
         return;
     } else {
         GTEST_SKIP() << "Skipping PostgreSQL integration tests on local Windows environment.";
         return;
     }
     ```
   - This ensures tests compile but do not attempt database operations.

2. **Linux CI**
   - Full PostgreSQL integration is enabled.
   - The CI pipeline includes a PostgreSQL service container (`postgres:17`) for testing.
   - All migrations and repository tests execute normally against the test DB.

3. **Future Enhancement**
   - A planned CMake refinement (Option A) will **exclude** PostgreSQL test files entirely on Windows builds for cleaner CI runs.

---

## Consequences

### ✅ Benefits
- CI builds on Windows no longer fail due to missing PostgreSQL dependencies.  
- Local Windows developers can build and run tests without installing PostgreSQL.  
- Linux CI retains full end-to-end integration test coverage.  
- Clean, maintainable design — no complex `#ifdef` directives scattered across test files.  
- Improved CI reliability and reduced runtime for Windows jobs.

### ⚠️ Drawbacks
- PostgreSQL integration tests are not executed on Windows at all.  
- Requires Linux CI to remain the single source of truth for DB-related test coverage.

### 🔄 Trade-offs
- Prioritized CI stability and portability over full platform parity in test execution.

---

## References
- [DatabaseIntegrationFixture.h](../tests/integration/common/DatabaseIntegrationFixture.h)  
- [ci.yml](../.github/workflows/ci.yml)  
- [PostgresTaskRepoTest](../tests/integration/domain/repos/test_P1_S2_PostgresTaskRepository.cpp)  
- Related ADRs: *None (first DB-integration related ADR)*  
