# ADR 0007: Phase0/Phase1 Header Collision in Task.h

- **Status:** Accepted
- **Date:** 2025-10-14
- **Owner:** Core Domain Team
- **Related:** Phase 1 — Slice 1
- **Tags:** Header Collision in Task.h

---

## 🧩 Context

During the refactoring of the core domain layer (Phase1), a new `Task` entity was introduced under:

```
src/domain/core/entities/Task.h
```

The legacy Phase0 implementation, located at:

```
src/domain/core/Task.h
```

remains part of the `tasqly_core` target for backward compatibility with QML-based components.  
Both files define a class/struct named `Task`, but with *different dependencies*:

| Version | Dependency Base | Notes |
|----------|-----------------|--------|
| **Phase0** | Qt (`QString`, `QDateTime`) | Used by QML façade and legacy App layer |
| **Phase1** | STL (`std::string`, `std::chrono`) | Pure C++ domain model for new testing layer |

The coexistence of these two headers caused subtle and dangerous symbol collisions.

---

## ❗ Problem Statement

Unit tests linking against `tasqly_core` accidentally included the *Phase0* `Task.h` (Qt-based) instead of the intended *Phase1* version.

This happened because:

1. The include path for `tasqly_core` exposed the **entire `src/` tree** via:
   ```cmake
   target_include_directories(tasqly_core PUBLIC ${CMAKE_SOURCE_DIR}/src)
   ```
2. Windows file system is **case-insensitive**, so both:
   ```cpp
   #include "domain/core/entities/Task.h"
   #include "domain/core/task.h"
   ```
   can resolve to the same physical file.
3. Incremental builds (Ninja/CMake cache) preserved stale dependency information from older includes.
4. The result was that tests compiled successfully but linked and executed with the **Qt ABI** (`QString`), causing a segmentation fault during `Task` destructor execution.

---

## 🧠 Analysis Summary

- The error trace indicated:
  ```
  QString::~QString
  tasqly::domain::core::Task::~Task
  ```
  confirming that the Qt-based Task was instantiated instead of the STL one.
- Root cause: overly broad include path exposing both `core/` and `core/entities/`.

---

## ✅ Decision

To isolate domain layers **without adding multiple build targets**, we adopted a **Phase-Scoped Include Policy** inside the same `tasqly_core` target.

### Practical Fix

1. Restrict include visibility in `Core.cmake`:

   ```cmake
   # 📂 Include Directories (Phase-aware)
   target_include_directories(tasqly_core PUBLIC
       ${CMAKE_SOURCE_DIR}/src/domain/core/entities
       ${CMAKE_SOURCE_DIR}/src/domain/core/mappers
   )
   ```

   🔒 Removes `src` as a general include path to prevent cross-layer leakage.

2. Enforce correct include in `TaskMapper` and tests:
   ```cpp
   #include "domain/core/entities/Task.h"
   ```

3. Perform a **clean rebuild** after changes:
   ```bash
   rd /s /q build
   cmake --preset=mingw-debug
   ```

4. Add a build-time guard in legacy header:

   ```cpp
   #ifdef TASQLY_PHASE_MODE_PHASE1
   #error "🚫 Legacy Task.h (Phase0) must not be included in Phase1 or tests."
   #endif
   ```

5. Introduce a diagnostic flag in root `CMakeLists.txt`:
   ```cmake
   set(TASQLY_PHASE_MODE "phase1" CACHE STRING "Active domain phase (phase0 or phase1)")
   ```

---

## 🧰 Technical Outcome

| Area | Before | After |
|-------|---------|--------|
| Include paths | `${SRC_ROOT}` (global) | Only domain core Phase1 paths |
| Header collision | Possible | Impossible |
| Qt dependency in tests | ❌ Incorrectly linked | ✅ Isolated |
| ABI mismatch | Frequent | Eliminated |

---

## ⚡ Consequences

**Positive:**
- Domain core code can evolve independently from QML.
- Test suite now builds against STL-only model.
- No change in number of CMake targets (simpler build system).

**Negative:**
- App phase still depends on Phase0 include layout until full migration.

---

## 🧭 Future Work

- Migrate all QML-facing models to Phase1 equivalents gradually.
- Eventually deprecate `src/domain/core/Task.h` entirely once QML layer uses a DTO boundary instead of direct entities.

---

## 📜 References

- Commit: `fix(TaskMapper): isolate Phase1 domain includes`
- Stack trace evidence: `QString::~QString` segmentation fault in test run.
- Related File: `tests/unit/domain/mappers/test_TaskMapper_Single.cpp`

---

**Reviewed by:**  
- @mohamedali (Domain Architecture Lead)  
- @olavenko (Core Maintainer)  
- @tasqly-qml (QML Integration Engineer)

---
