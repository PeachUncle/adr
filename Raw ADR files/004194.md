# ADR 0005: Phase 1 Domain Isolation Policy

- **Status:** Accepted  
- **Date:** 2025-10-06  
- **Owners:** Tasqly Team  
- **Related:** Phase 1 — Slice 1  
- **Tags:** Architecture / Domain / Clean Separation
---

## 🧭 Context

Phase 0 established the full *application infrastructure* (logging, settings, navigation, theme, notifier, persistence),  
but its *domain layer* existed only as a minimal placeholder (`src/domain/core/`).  
This included early definitions of `Task.h`, `Goal.h`, and basic repository interfaces,  
using **Qt types** (`QString`, `QDateTime`) and a *data-struct* approach without validation or separation.

Phase 1 begins the first true **Domain Implementation Phase**, focusing on:
- Clean separation between domain and infrastructure  
- Pure domain entities (`Task`, `Goal`, etc.) using only STL types  
- Explicit validation, Result-based contracts, and typed repositories  

During early analysis of Slice 1, two potential approaches arose for how to evolve from the legacy Phase 0 domain core.

---

## ⚖️ Decision Alternatives

| Option | Description | Pros | Cons |
|--------|--------------|------|------|
| **A — Parallel Domain Layer (Legacy Coexistence)** | Keep old files (`core/Task.h`, `core/ITaskRepository.h`) and build new ones with the same names under `entities/` and `interfaces/`, bridging via mappers. | ✅ Allows gradual migration<br>✅ Keeps benchmarks/tests intact | ❌ Requires mapping layer<br>❌ Adds maintenance overhead<br>❌ Introduces dual-source confusion |
| **B — Full Isolation (Clean Split)** 🟢 **Chosen** | Keep old Phase 0 domain *untouched* but start a **brand-new clean domain** without linking or mapping. No compatibility layer. | ✅ Maximum purity (no Qt leakage)<br>✅ Clear architectural boundary<br>✅ No dependency coupling<br>✅ Easier long-term maintenance | ⚠️ Temporary duplication until new use cases integrate in later phases |

---

## 🧩 Decision

> **Tasqly Phase 1 will implement a fully isolated domain layer.**  
> No legacy bridging or mapping will exist between `domain/core` and `domain/entities`.

The old Phase 0 files remain only for historical references and benchmark reproducibility.  
All new business logic will live in dedicated folders following Clean Architecture standards.

---

## 🧱 Implementation Details

### 📁 New Directory Layout

```
src/
 ├── domain/
 │   ├── core/                  ← Phase 0 legacy utilities (Result, Error, Clock, UuidGen, etc.)
 │   ├── entities/              ← Phase 1 new pure entities
 │   │    ├── Task.h
 │   │    └── Task.cpp
 │   ├── interfaces/            ← New repository contracts
 │   │    └── ITaskRepository.h
 │   ├── validation/            ← Entity validation helpers
 │   │    └── TaskValidator.{h,cpp}
 │   └── mappers/               ← DTO ↔ Entity (optional, no legacy linkage)
 │        └── TaskDtoMapper.{h,cpp}
```

### 🧠 Design Notes
- All new entities use `std::string`, `std::chrono::system_clock::time_point`, and `Result<T,Error>`.
- No inclusion of Qt headers or dependencies.
- All repositories return `Result`-wrapped values.
- Validation rules are explicit (title length, deadline constraints, etc.).
- Legacy code (Phase 0) remains unmodified, residing under `domain/core/`.

---

## 🚫 Legacy Bridging Policy

> **No mapping or adapter layer will be created** between:
> - `tasqly::domain::core::Task`
> - `tasqly::domain::entities::Task`

Each phase’s layer is self-contained.  
Integration between new and old modules will occur only at the **application boundary** (e.g., in later Phases 2–3).

---

## 📊 Impact Analysis

| Aspect | Result |
|--------|---------|
| **Build System** | No conflicts — unique include paths (`core/` vs `entities/`) and distinct namespaces. |
| **Linking** | Safe — separate compilation targets, distinct namespaces (`tasqly::domain::core` vs `tasqly::domain::entities`). |
| **Tests** | Phase 0 tests remain valid and untouched.<br>Phase 1 will introduce new unit/integration test sets. |
| **CI/CD** | No regression impact — CI continues to validate legacy + new separately. |

---

## 🧭 Consequences

- ✅ Clean Domain Foundation ready for all future use cases (Create/Update/Delete/Filter Tasks)
- ✅ No Qt/DB leakage beyond Phase 1
- ✅ Phase 1 entities become the canonical domain model
- ⚠️ Legacy Phase 0 remains for compatibility testing and benchmark comparison only
- 🔜 In Phase 2, repositories and app-layer use cases will adopt this new domain model fully

---

## 📘 References

- `DevelopmentStandards_Index.md` — Section 1.1 “Vertical Slices Discipline”  
- `FilePolicy.md` — “Do not modify previous phase files without explicit ADR.”  
- `Subsystems_Unified.md` — “Legacy Compatibility Layer Pattern”  
- `Project_Quality_Policy.md` — “Clean Architecture enforcement per phase transition.”  
- `Phase 1 Slice 1 Analysis` — docs/adr/phase1/slice1/0001_phase_1_slice_1_analysis.md  

---

## ✅ Status Summary

| Item | Decision |
|------|-----------|
| Legacy `Task.h` | Kept under `/domain/core/` for reference |
| Legacy `ITaskRepository.h` | Kept for Phase 0 only |
| New `Task.h` / `Task.cpp` | Implemented under `/domain/entities/` |
| New `ITaskRepository.h` | Implemented under `/domain/interfaces/` |
| Mapper between old/new | ❌ Not implemented |
| Domain validation layer | ✅ Planned in Slice 1 |
| Integration with App | Deferred to Phase 2 |

---

## ✍️ Author’s Note

This ADR formalizes the architectural boundary between **Phase 0 (infrastructure era)**  
and **Phase 1 (domain-driven foundation)**.  
By fully isolating the new domain, Tasqly ensures long-term maintainability,  
unit test purity, and consistent Clean Architecture layering.

---

**Approved by:**  
🧑💻 Mohamed Ali — Lead Developer  
📅 2025-10-08  
📘 ADR ID: 0005_phase1_domain_isolation_policy.md
