# ADR 0004: Mapper Strategy — Manual vs Codegen

- **Status:** Draft  
- **Date:** 2025-10-06  
- **Owners:** Tasqly Team  
- **Related:** Phase 1 — Slice 1  
- **Tags:** mapping, dto, automation, codegen, maintainability

---

## Context
Tasqly’s architecture defines a strict separation between the **domain layer** and the **infrastructure layer**. Data conversion between `Task` (domain entity) and `TaskDto` (persistence structure) is required for all CRUD operations.

The project must decide whether these mappings should be:
1. **Manual:** Hand-written conversion code (explicit field-by-field translation).  
2. **Generated (Codegen):** Auto-generated mappers using templates, macros, or reflection.

This ADR determines which approach is adopted for Phase 1 and establishes evaluation criteria for future automation.

---

## Decision
Tasqly will use a **Manual Mapper Strategy** for Phase 1 and 2, with the option to introduce **code generation** once infrastructure complexity grows.

### ✅ Rationale
- Phase 1 aims for clarity, correctness, and explicit boundaries — automation would obscure mapping logic.
- Manual mapping simplifies debugging and logging integration.
- Codegen introduces additional dependencies (Python, reflection libs, meta-DSL) which are not yet stabilized in the current CI pipeline.

Future phases (≥ Phase 3) may revisit this decision if repetitive DTO structures accumulate across multiple entities.

---

## Implementation Outline
**File:** `domain/mappers/TaskMapper.cpp`

### Example — Manual Mapper Implementation
```cpp
#include "domain/mappers/TaskMapper.h"

using namespace tasqly::domain::core;
using namespace tasqly::domain::mappers;

TaskDto TaskMapper::toDto(const Task& t) {
    TaskDto dto;
    dto.id = t.id.toString();
    dto.title = t.title;
    dto.notes = t.notes;
    dto.status = to_string(t.status);
    dto.priority = to_string(t.priority);
    dto.deadline = t.deadline ? toIsoString(*t.deadline) : std::nullopt;
    dto.createdAt = toIsoString(t.createdAt);
    dto.updatedAt = toIsoString(t.updatedAt);
    return dto;
}

Task TaskMapper::fromDto(const TaskDto& dto) {
    Task t;
    t.id = Uuid(dto.id);
    t.title = dto.title;
    t.notes = dto.notes;
    t.status = parseStatus(dto.status);
    t.priority = parsePriority(dto.priority);
    t.deadline = dto.deadline ? fromIsoString(*dto.deadline) : std::nullopt;
    t.createdAt = fromIsoString(dto.createdAt);
    t.updatedAt = fromIsoString(dto.updatedAt);
    return t;
}
```

---

## Comparison Table
| Criterion | Manual Mapping | Codegen Mapping |
|------------|----------------|-----------------|
| Transparency | ✅ Explicit and readable | ⚠️ Hidden behind templates |
| Debugging | ✅ Easy to trace | ⚠️ Requires generator inspection |
| CI/CD Integration | ✅ Simple | ⚠️ Requires prebuild step |
| Flexibility | ✅ Custom logic possible | ❌ Hard to insert custom rules |
| Scalability | ⚠️ Repetitive for many entities | ✅ Excellent for large schemas |
| Tooling Needs | ✅ None | ⚠️ Requires reflection or templates |

---

## Future Work (Phase ≥ 3)
- Evaluate C++20 Reflection / `magic_enum` / `rttr` for mapper generation.
- Prototype a Python-based mapper generator (`scripts/gen_mapper.py`).
- Create ADR once prototype reaches maturity.

---

## Consequences
### ✅ Benefits
- Immediate control over business logic.
- Simplifies testing (`TaskMapperTests.cpp`).
- Consistent with current CI and phase goals.

### ⚠️ Drawbacks
- Manual updates required for every new field.
- Repetitive boilerplate across entities.

### 🔄 Trade-offs
- **Pro:** Stability, clarity, and minimal build impact.
- **Con:** Less scalable as the domain expands.

---

## Testing & Quality
| Test Type | Description | Result |
|------------|-------------|---------|
| Unit | DTO roundtrip validation | ✅ |
| Integration | Repository + Mapper consistency | ✅ |
| Regression | Schema version mismatch detection | ✅ |

---

## References
- [ADR 0002 — DTO Mappers vs Direct Entity Exposure](./0002-dto-vs-direct-entity.md)
- [ADR-template.md](../../../../docs/ADR-template.md)
- [Subsystems_Unified.md](../../../../Development%20Standards/Subsystems_Unified.md)
- [C++_Standards_Combined.md](../../../../Development%20Standards/Standards/C++_Standards_Combined.md)
- [FilePolicy.md](../../../../Development%20Standards/Policies/FilePolicy.md)
- [Project_Quality_Policy.md](../../../../Development%20Standards/Project_Quality_Policy.md)
- [Testing_Standards_Combined.md](../../../../Development%20Standards/Standards/Testing_Standards_Combined.md)

---

**Next Step:** Integrate `TaskMapper` unit tests under `tests/domain/mappers/TaskMapperTests.cpp`.