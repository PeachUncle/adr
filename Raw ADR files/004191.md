# ADR 0006: Unify FakeAppSettingsManager and Create tasqly_fakes Library

**Date:** 2025-10-05  
**Status:** Accepted ✅  
**Author:** Mohamed Ali  
**Version:** 1.0  
**Layer:** Build System / Test Utilities  

---

## 🧩 Context

During Phase 0 benchmarking and test integration, multiple files (`Bench_LoadUserSettings.cpp`,  
`Bench_SaveUserSettings.cpp`, `Bench_SwitchTheme.cpp`) defined their own local versions  
of `FakeAppSettingsManager`.  

This duplication caused **ODR (One Definition Rule)** violations during MinGW linking,  
leading to build failures like:

```
duplicate section `.rdata$_ZTV22FakeAppSettingsManager[...]` has different size
```

Additionally, there were other local fakes (like `InMemorySettingsStore` and  
`BenchSettingsManager`) defined inline in benchmark files, fragmenting test logic  
and introducing maintenance overhead.

---

## 🎯 Decision

Create a **dedicated static library** named `tasqly_fakes`  
to hold all fake and test-double implementations, shared across  
both **unit tests** and **benchmarks**.

### Library: `tasqly_fakes`

**Purpose:**  
Centralize fake classes for testing and benchmarking.

**Path:**  
`tests/fakes/`

**Contents:**
- `FakeAppSettingsManager.h`  
- `FakeSettingsStore.h`  
- `FakeClock.h`  
- `FakeUuidGen.h`  
- `LogManagerTestAccessor.h`

**CMake Declaration:**
```cmake
add_library(tasqly_fakes STATIC
    tests/fakes/FakeAppSettingsManager.h
    tests/fakes/FakeSettingsStore.h
    tests/fakes/FakeClock.h
    tests/fakes/FakeUuidGen.h
    tests/fakes/LogManagerTestAccessor.h
)

target_include_directories(tasqly_fakes PUBLIC
    ${CMAKE_SOURCE_DIR}/tests/fakes
)

target_link_libraries(tasqly_fakes
    PUBLIC
        tasqly_core
        Qt6::Core
)
```

---

## 🧠 Implementation Summary

- Created new file:  
  `tests/fakes/FakeSettingsStore.h`  
  → Provides an in-memory backend (no disk I/O).

- Updated existing file:  
  `tests/fakes/FakeAppSettingsManager.h`  
  → Unified implementation using `FakeSettingsStore`.

- Cleaned benchmarks:
  - `Bench_SwitchTheme.cpp`: removed `InMemorySettingsStore` and `BenchSettingsManager`
  - `Bench_SaveUserSettings.cpp`: now uses unified fake
  - `Bench_LoadUserSettings.cpp`: unchanged (uses lightweight benchmark-only fake)

- Linked all test and benchmark targets with `tasqly_fakes`.

---

## ✅ Result

| Aspect | Before | After |
|--------|---------|--------|
| Fake Definitions | Duplicated across files | Centralized in `tasqly_fakes` |
| Linker Errors | Present (ODR violation on MinGW) | Fully resolved |
| Maintainability | High overhead | Clean and modular |
| Performance | Same | Stable (no file I/O) |
| Architecture | Implicit fakes per file | Explicit Test Utilities Layer |

---

## 🧱 Architectural Impact

The project now includes a dedicated **Test Utilities Layer**, forming a clean separation:
```
tasqly_core        → Core logic (production)
tasqly_fakes       → Test doubles & utilities
tasqly_tests       → Unit & integration tests
tasqly_benchmarks  → Performance tests
```

This aligns Tasqly with modern Clean Architecture patterns,
improving test reliability, modularity, and maintainability.

---

## 🚀 Future Work

- Extend `tasqly_fakes` with database and repository fakes.
- Integrate `FakeSettingsStore` in future use cases (e.g. FeatureFlagsManager tests).
- Add a quality gate to forbid inline fake definitions in benchmarks.

---

## 🏁 Status

**Decision accepted and implemented successfully.**  
All builds (MSVC + MinGW) verified stable.  
Benchmarks and tests now pass consistently across compilers.

