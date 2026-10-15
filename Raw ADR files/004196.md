# ADR 0001: runtime-error-layer-adoption

- **Status**: Accepted  
- **Date**: 2025-10-21  
- **Owners**: Tasqly Core Team  
- **Related**: Phase1 — Slice2  
- **Tags**: runtime, error, infra, logger, notifier, persistence  

---

## Context

During Phase 1 Slice 2, the infrastructure layer (Postgres repository + fallback system) required  
a unified way to represent **runtime-level errors** such as:

- Database initialization or authentication failures  
- SSL or networking library issues  
- I/O errors and credential masking  
- Runtime fallback switching (Postgres → InMemory)

The **existing `P1_DomainError`** and **`DomainResult<T>`** already provide domain-level semantics  
for validation and storage failures but are **not suited for runtime-level or system errors**.

Without a distinct runtime abstraction, infrastructure subsystems like the **Logger**, **Notifier**,  
and **TaskRepositoryFactory** cannot consistently handle or classify operational failures.

---

## Decision

Introduce a new **pure C++ runtime error abstraction** named `P1_Error`,  
defined under the namespace `tasqly::p1::infra::runtime`.

### ✅ Key Design Points

- Independent from Qt and domain layers  
- Enum-based error classification:
  - `DB_INIT`, `DB_AUTH`, `TIMEOUT`, `NETWORK`, `IO`, `CONFIG`, `UNKNOWN`
- Contains message + optional key-value context  
- Conversion helpers between:
  - `P1_Error → P1_DomainError`
  - `P1_DomainError → P1_Error`
- Usable directly by:
  - `P1_Logger` (to log runtime failures)
  - `P1_Notifier` (to display fallback warnings)
  - `P1_S2_TaskRepositoryFactory` (to report DB fallback cause)

### 📂 File Structure
infra/runtime/
├── P1_Error.h
└── P1_Error.cpp
domain/core/
├── P1_DomainError.h
└── P1_DomainResult.h

pgsql
Copy code

---

## Consequences

### ✅ Benefits
- Unified runtime-level error system across infra subsystems  
- Simplifies error propagation to Logger and Notifier  
- Enables consistent masking of sensitive credentials in logs  
- Supports future conversion to domain-safe errors for repositories  

### ⚠️ Drawbacks
- Slight duplication of semantic error fields (code/message/context)  
- Requires synchronization if domain error enums evolve  

### 🔄 Trade-offs
- Chose standalone `P1_Error` instead of merging with DomainError for better layering isolation  
- Simplifies migration of infra subsystems to pure C++ without Qt dependencies  

---

## References
- [ADR-template.md](../../phase0/ADR-template.md)
- [Subsystems_Unified.md](../../../../Development Standards/Subsystems_Unified.md)
- [P1_DomainError.h](../../../../domain/core/P1_DomainError.h)
- [P1_DomainResult.h](../../../../domain/core/P1_DomainResult.h)