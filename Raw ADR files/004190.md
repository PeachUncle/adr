# 🧩 ADR 0005: FakeAppSettingsManager Link Conflict on MinGW

**Date:** 2025-10-05  
**Status:** Accepted  
**Author:** Mohamed Ali  
**Context:** Phase 0 — Benchmark Stability  
**Impacted Modules:** Benchmarks / Fakes / Build System  

---

## 🧠 Context

During Phase 0 performance benchmarks, running under **MinGW** caused a linker crash:

```
duplicate section `.rdata$_ZTV22FakeAppSettingsManager' has different size
```

This issue did **not** appear under **MSVC**, due to more lenient handling of duplicate vtables.

The error originates from **ODR (One Definition Rule)** violation —  
multiple translation units define `FakeAppSettingsManager` with slightly different layouts.

---

## 🔍 Root Cause

| File | Definition | Description |
|------|-------------|--------------|
| `Bench_LoadUserSettings.cpp` | Local class `FakeAppSettingsManager` | Simple fake with only `themeMode()` |
| `Bench_SaveUserSettings.cpp` | Uses `tests/fakes/FakeAppSettingsManager.h` | Full-featured fake with counters |
| `Bench_SwitchTheme.cpp` | Defines `BenchSettingsManager` (custom) | Unrelated |

Thus, **two different classes** with the same name existed during linking:
- One lightweight inline definition
- One complex fake from the header file  

MinGW (GCC) treats both as distinct vtables with different memory layouts → **link conflict**.

---

## ⚙️ Options Considered

| Option | Description | Pros | Cons |
|---------|--------------|------|------|
| **A. Full Refactor (TasqlyFakes library)** | Move all fakes into a static lib with `.cpp` files and link via CMake | Clean, scalable, production-grade | Risky now (many dependent files), would break CI during Phase 1 |
| **B. Local Rename Fix (temporary)** | Rename the local fake class in `Bench_LoadUserSettings.cpp` to avoid ODR collision | Safe, zero side effects, instant fix | Doesn’t address root cause long-term |

---

## ✅ Decision

For **Phase 0–1**, we will apply **Option B (Local Rename)**:  
Rename the inline fake class in `Bench_LoadUserSettings.cpp`  
from `FakeAppSettingsManager` → `SimpleFakeAppSettingsManager`.

This isolates the vtable and avoids duplication under MinGW.

**No further changes to fakes or CMake** at this stage.

---

## 🚀 Future Plan (Phase 2)

After UI integration and real managers are implemented:

- Create `tests/fakes/CMakeLists.txt`  
  defining `TasqlyFakes` static library:
  ```cmake
  add_library(TasqlyFakes STATIC
      FakeAppSettingsManager.cpp
      FakeThemeManager.cpp
      ...
  )
  target_include_directories(TasqlyFakes PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
  ```
- Move all fake implementations into corresponding `.cpp` files.
- Link benchmarks/tests via:
  ```cmake
  target_link_libraries(TasqlyBenchmarksRunner PRIVATE TasqlyFakes)
  target_link_libraries(TasqlyTestsRunner PRIVATE TasqlyFakes)
  ```

This ensures consistent behavior across MSVC, MinGW, and Clang toolchains.

---

## 🧩 Summary

| Aspect | Temporary Fix | Long-term Solution |
|---------|----------------|--------------------|
| ODR conflict | Rename local class | Consolidate fakes into `TasqlyFakes` library |
| Risk | None | Medium (needs coordination) |
| Duration | Phase 0–1 | Phase 2 onward |
| Benefit | Unblocks MinGW benchmarks | Permanent cross-platform stability |

---

## ✅ Final Decision

**Rename only in `Bench_LoadUserSettings.cpp` (Phase 0–1).**  
Defer full fake refactor until Phase 2.  

Benchmarks remain fully functional on both compilers.

---

**Signed-off-by:**  
Mohamed Ali  
Lead Developer — Tasqly Project