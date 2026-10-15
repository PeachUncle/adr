# 📑 ADR 0004: Refactor AppSettingsManager with ISettingsStore Abstraction

**ADR ID:** ADR-2025-10-02-01  
**Title:** Refactor AppSettingsManager to use ISettingsStore abstraction  
**Date:** 2025-10-02  
**Status:** Accepted  
**Deciders:** Tasqly Core Team  
**Technical Story:** Improve testability and reliability of AppSettingsManager persistence layer  
**Tags:** [refactor], [settings], [persistence], [testability], [benchmarks]

---

## 🧠 Context
The original `AppSettingsManager` implementation directly depended on `QSettings` (INI backend).  
Problems identified:
- **Testability Issues:** Could not inject fake or mock stores → difficult to simulate errors (exceptions, corrupt files, status errors).  
- **Limited Coverage:** Unit tests only covered "happy path" (70% coverage).  
- **Error Handling Duplication:** Multiple repeated code paths for error emission.  
- **Benchmarking Noise:** I/O-heavy QSettings backend makes benchmarks less reliable.  

---

## ✅ Decision
Introduce a **lightweight abstraction layer** `ISettingsStore` to decouple `AppSettingsManager` from `QSettings`.  

- Implemented **QSettingsStore** (default backend).  
- Updated `AppSettingsManager` to depend on `std::unique_ptr<ISettingsStore>`.  
- Added **helpers**:
  - `triggerPersistenceError()` → debounced error signal emission.  
  - `handleStatusError()` → centralized QSettings::Status checks.  
- **Unit tests updated**:
  - Added `ThrowingSettingsStore`, `StatusSequenceSettingsStore`, `TestIniSettingsStore`.  
  - Coverage increased to ~100% of `AppSettingsManager`.  
- **Benchmarks**:
  - Baseline benchmarks added (using real QSettings backend).  
  - Planned: complementary in-memory benchmarks (using InMemoryStore).  

---

## 🔄 Alternatives Considered
1. **Keep direct QSettings dependency**  
   - ❌ Not testable.  
   - ❌ Error cases remain hard to reproduce.  

2. **Use Qt’s QSaveFile/QSettings subclasses**  
   - ❌ Still tied to I/O, no better test isolation.  
   - ❌ Higher coupling with Qt internals.  

3. **Abstract store with ISettingsStore (Chosen)**  
   - ✅ Enables dependency injection.  
   - ✅ Unit tests can simulate all error conditions.  
   - ✅ Clean separation of concerns.  

---

## 🎯 Consequences
- **Positive:**  
  - Unit test coverage for AppSettingsManager rose from 69.9% → ~100%.  
  - Error handling unified, less code duplication.  
  - Benchmarks possible with both real QSettings and in-memory mock stores.  
- **Neutral:**  
  - Slight increase in complexity (new interface).  
- **Negative:**  
  - Requires adapting existing tests.  
  - Slight overhead of indirection (but negligible).  

---

## 📌 Actions
- [x] Implement `ISettingsStore` and `QSettingsStore`.  
- [x] Refactor `AppSettingsManager` constructors to accept injected store.  
- [x] Add new unit tests (Throwing/StatusSequence/TestIni stores).  
- [x] Add error handling helpers.  
- [x] Add `Bench_AppSettingsManager.cpp` with QSettings.  
- [ ] Add `Bench_AppSettingsManager_Mock.cpp` with in-memory store.  

---

## 🔗 Related
- `AppSettingsManager.h/.cpp`  
- `test_app_settings_manager.cpp`  
- `Bench_AppSettingsManager.cpp`  
- Planned: `Bench_AppSettingsManager_Mock.cpp`  
