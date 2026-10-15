---
docid: ADR-055
title: ADR 021 Archunitnet Architecture Testing
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-021: ArchUnitNET for Automated Architecture Testing

**Status:** Accepted  
**Date:** January 2, 2026  
**Context:** B2X architecture enforcement  
**Decision Authors:** @Architect, @TechLead, @Backend, @QA  
**Coordinated by:** @SARAH

---

## Problem

B2X has well-documented architecture decisions (ADRs) but no automated enforcement:

1. **Layer violations go undetected** until code review (human error prone)
2. **Bounded context isolation** depends on developer discipline
3. **ADRs become stale** — documentation without enforcement
4. **Onboarding friction** — new developers learn rules through trial and error
5. **Technical debt accumulates** through "just this once" shortcuts

### Current Architecture (Documented but Not Enforced)

- **Clean/Onion Architecture** per domain (Core → Application → Infrastructure)
- **10 Bounded Contexts** (Catalog, CMS, Identity, Customer, etc.)
- **Wolverine CQRS** patterns (Handlers, Commands, Queries, Events)
- **DDD patterns** (Entities, Value Objects, Aggregates in Core)

---

## Decision

**Adopt ArchUnitNET for automated architecture testing.**

### Why ArchUnitNET

| Criterion | ArchUnitNET | Alternatives |
|-----------|-------------|--------------|
| .NET 10 Support | ✅ Yes (tested) | NetArchTest: Partial |
| xUnit Integration | ✅ Native | NDepend: Separate tool |
| Fluent API | ✅ Readable rules | Manual: N/A |
| License | Apache 2.0 (free) | NDepend: Commercial |
| Community | 1.2k ⭐, active | NetArchTest: Less active |
| CI/CD Ready | ✅ Standard tests | NDepend: Extra setup |

### Package

```xml
<PackageVersion Include="TngTech.ArchUnitNET.xUnit" Version="0.13.1" />
```

---

## Implementation

### Project Structure

```
backend/
└── Tests/
    └── Architecture/
        └── B2X.Architecture.Tests/
            ├── B2X.Architecture.Tests.csproj
            ├── ArchitectureTestBase.cs      ← Shared architecture loading
            ├── LayerDependencyTests.cs      ← Clean architecture rules
            ├── BoundedContextTests.cs       ← BC isolation rules
            ├── NamingConventionTests.cs     ← Handler/Event/Command naming
            └── WolverinePatternTests.cs     ← CQRS pattern rules
```

### Phase 1 Rules (Immediate)

#### 1. Layer Dependencies (Clean Architecture)

```csharp
// Domain Core must not depend on Infrastructure
Types().That().ResideInNamespace("*.Core.*")
    .Should().NotDependOnAny(
        Types().That().ResideInNamespace("*.Infrastructure.*"))
    .Because("Domain must be independent of infrastructure (ADR-002)")
```

#### 2. Bounded Context Isolation

```csharp
// Catalog must not depend on CMS, Identity, etc.
Types().That().ResideInNamespace("B2X.Catalog.*")
    .Should().NotDependOnAny(
        Types().That().ResideInNamespace("B2X.CMS.*")
            .Or().ResideInNamespace("B2X.Identity.*")
            .Or().ResideInNamespace("B2X.Customer.*"))
    .Because("Bounded contexts must be isolated (ADR-001)")
```

#### 3. Handler Naming & Location

```csharp
// All handlers must be in Handlers namespace
Classes().That().HaveNameEndingWith("Handler")
    .Should().ResideInNamespace("*.Handlers.*")
    .Because("Wolverine handlers must be in Handlers namespace")
```

#### 4. Event Naming Convention

```csharp
// Events must end with "Event"
Classes().That().ResideInNamespace("*.Events.*")
    .Should().HaveNameEndingWith("Event")
    .Because("Domain events must follow naming convention")
```

#### 5. No EF Core in Domain

```csharp
// Domain Core must not reference EF Core
Types().That().ResideInNamespace("*.Core.*")
    .Should().NotDependOnAny(
        Types().That().ResideInNamespace("Microsoft.EntityFrameworkCore.*"))
    .Because("Domain must be persistence-ignorant")
```

### Phase 2 Rules (Sprint 2-3)

- Cyclic dependency detection between slices
- Validator naming and location rules
- Controller location rules (API projects only)
- Service registration patterns
- Repository interface rules

### Phase 3 Rules (Ongoing)

- New rule for each ADR created
- Custom rules for Wolverine message patterns
- Performance-critical path rules

---

## Consequences

### Positive

✅ **ADRs become living tests** — violations caught in CI  
✅ **Faster onboarding** — architecture rules are executable documentation  
✅ **Code review efficiency** — automated checks reduce manual burden  
✅ **Refactoring safety net** — architecture preserved during changes  
✅ **Technical debt prevention** — shortcuts blocked at PR level  

### Negative

⚠️ **Initial setup effort** — ~2-4 hours for Phase 1  
⚠️ **Debug build requirement** — ArchUnitNET works best with Debug builds  
⚠️ **Learning curve** — team needs to learn fluent API  
⚠️ **Maintenance** — rules must evolve with architecture  

### Mitigations

- Start with 5 critical rules only (Phase 1)
- Use `.Because()` for clear error messages linking to ADRs
- Document rule-to-ADR mapping
- Include in CI test pipeline (already runs Debug)

---

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| **NetArchTest** | Less active, fewer features than ArchUnitNET |
| **NDepend** | Commercial license, overkill for current needs |
| **Manual Code Reviews** | Doesn't scale, human error prone (current state) |
| **Roslyn Analyzers** | Complex to write, better for code style than architecture |

---

## References

- [ArchUnitNET GitHub](https://github.com/TNG/ArchUnitNET)
- [ArchUnitNET Documentation](https://archunitnet.readthedocs.io/)
- [ADR-001: Event-Driven Architecture](./ADR-001-event-driven-architecture.md)
- [ADR-002: Onion Architecture](./ADR-002-onion-architecture.md) *(to be created)*

---

## Compliance

- **License:** Apache 2.0 — ✅ Compatible with commercial use
- **Security:** No external calls, analyzes local assemblies only
- **Performance:** < 30 seconds for full architecture scan

---

**Approved by:** @Architect, @TechLead  
**Implementation:** @Backend  
**QA Sign-off:** @QA
