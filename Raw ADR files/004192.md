# ADR 0003: DTO Mappers vs Direct Entity Exposure

- **Status:** Draft  
- **Date:** 2025-10-06  
- **Owners:** Tasqly Team  
- **Related:** Phase 1 — Slice 1  
- **Tags:** domain, dto, mapper, architecture, data-isolation

---

## Context
In Tasqly’s architecture, the domain layer must remain **free of infrastructure dependencies** (Qt, DB, API). However, as data flows between layers, objects from the domain (`Task`) must be converted into external representations suitable for storage or transport.

There are two primary strategies to achieve this:

1. **Direct Entity Exposure:** Using domain objects (`Task`) directly in infrastructure (e.g., Postgres repos or QML bindings).
2. **DTO Mapping:** Introducing a **Data Transfer Object (DTO)** layer that isolates domain models from persistence and UI schemas.

We need to determine which strategy to adopt for Phase 1 to ensure maintainability and clean separation.

---

## Decision
Tasqly will adopt the **DTO Mapping Strategy** for all cross-layer interactions between **Domain ↔ Infrastructure** and **Domain ↔ App/QML**.

Each layer will define clear mapping contracts:
- `TaskDto` — used for persistence and serialization.
- `TaskMapper` — responsible for converting between domain and DTO representations.

### ✅ Reasons for DTO Approach
- Preserves **domain purity** (no DB/Qt dependencies).
- Supports **multiple storage backends** (InMemory, Postgres) without changing domain logic.
- Enables **validation isolation** and **versioning** of data schemas.
- Improves **testability**: DTOs can be mocked without touching domain rules.

---

## Rejected Alternative — Direct Entity Exposure
While simpler to implement initially, this approach creates tight coupling:
- Domain classes would require knowledge of database fields or Qt types.
- Refactoring DB schema would propagate to domain layer.
- Testing infrastructure would require full DB mocks.

Thus, direct exposure violates **Clean Architecture** and **Separation of Concerns**.

---

## Implementation Outline

### Domain Layer (`domain/core`)
Pure entities (`Task`, `Result`, `Error`, `Uuid`, `TimePoint`)

### Infrastructure Layer (`infra/persistence`)
```cpp
struct TaskDto {
    std::string id;
    std::string title;
    std::string notes;
    std::string status;
    std::string priority;
    std::optional<std::string> deadline;
    std::string createdAt;
    std::string updatedAt;
};
```

### Mapper Interface (`domain/mappers/TaskMapper.h`)
```cpp
#pragma once
#include "domain/core/Task.h"
#include "infra/persistence/TaskDto.h"

namespace tasqly::domain::mappers {

struct TaskMapper {
    static TaskDto toDto(const domain::core::Task& task);
    static domain::core::Task fromDto(const TaskDto& dto);
};

} // namespace tasqly::domain::mappers
```

---

## Consequences
### ✅ Benefits
- Maintains **Clean Architecture boundaries**.
- Reduces regression risk when modifying DB schema.
- DTOs act as a stable external contract for persistence or APIs.

### ⚠️ Drawbacks
- Requires additional boilerplate for mapping logic.
- Must maintain synchronization between DTOs and entities.

### 🔄 Trade-offs
- **Pro:** Isolation, flexibility, testability.
- **Con:** Slightly higher maintenance cost and mapping complexity.

---

## Testing & Quality
| Test Type | Scope | Expected |
|------------|--------|-----------|
| Unit | `TaskMapper` roundtrip | DTO → Entity → DTO equality ✅ |
| Integration | Repo + Mapper | CRUD mapping integrity ✅ |
| Regression | Mapper validation | Detects missing fields or type mismatches ✅ |

---

## References
- [ADR 0001 — Task Entity & Contracts](./0001-task-entity-contracts.md)
- [ADR-template.md](../../../../docs/ADR-template.md)
- [Subsystems_Unified.md](../../../../Development%20Standards/Subsystems_Unified.md)
- [C++_Standards_Combined.md](../../../../Development%20Standards/Standards/C++_Standards_Combined.md)
- [FilePolicy.md](../../../../Development%20Standards/Policies/FilePolicy.md)
- [Project_Quality_Policy.md](../../../../Development%20Standards/Project_Quality_Policy.md)
- [Testing_Standards_Combined.md](../../../../Development%20Standards/Standards/Testing_Standards_Combined.md)

---

**Next Step:** Create ADR 0003 — “Mapper Strategy — Manual vs Codegen.”