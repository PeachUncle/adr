---
docid: ADR-097
title: ADR 051 Rename B2X To B2xgate
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-051: Rename B2X to B2X

**Status**: Proposed  
**Date**: 2026-01-07  
**Decision Makers**: @Architect, @TechLead, @SARAH  
**Technical Story**: Product rebranding initiative

---

## Context

The B2X platform requires a name change to **B2X** as part of a product rebranding initiative. This affects all aspects of the codebase including:

- .NET namespaces and assemblies
- Solution and project files
- Frontend packages
- Docker containers and Kubernetes resources
- Documentation and scripts
- MCP server configurations

The rename must be executed comprehensively to avoid partial states and maintain codebase consistency.

---

## Decision

We will rename **B2X** to **B2X** across the entire codebase using an **incremental phased approach** over 8-10 working days.

### Rename Mapping

| Old Name | New Name |
|----------|----------|
| `B2X` | `B2X` |
| `B2X` | `b2x` |
| `B2X` | `B2X` |

### Scope

| Category | Estimated Files |
|----------|-----------------|
| C# Projects (`.csproj`) | ~82 |
| C# Namespaces | ~500+ |
| MCP Servers | 12+ packages |
| Frontend packages | 3 projects |
| Docker/K8s configs | ~20+ |
| Documentation | ~100+ |
| Scripts | ~30+ |
| **Total** | **~800+** |

---

## Execution Strategy

### Chosen Approach: Incremental (Option B)

**Rationale**: 
- Lower risk than big-bang approach
- Easier rollback per phase
- Allows verification between phases
- Team can address issues incrementally

### 10-Phase Plan

| Phase | Focus | Duration | Owner |
|-------|-------|----------|-------|
| 1 | Preparation & Backup | 1 day | @SARAH |
| 2 | Backend Core (solution, projects, namespaces) | 2 days | @Backend |
| 3 | Shared & Infrastructure | 2 days | @Backend, @DevOps |
| 4 | MCP Servers | 1 day | @CopilotExpert |
| 5 | Frontend | 1 day | @Frontend |
| 6 | Docker & Kubernetes | 1 day | @DevOps |
| 7 | Scripts & Config | 0.5 days | @DevOps |
| 8 | Documentation | 1 day | @DocMaintainer |
| 9 | Verification & Testing | 1 day | @QA |
| 10 | Repository Migration | 0.5 days | @SARAH, @DevOps |

### Feature Freeze Policy

- **Full freeze** on affected areas during active rename phase
- Other development can continue on unaffected areas
- Clear communication before each phase begins

---

## Consequences

### Positive

- **Clean branding**: Consistent B2X identity throughout
- **No technical debt**: Complete rename eliminates confusion
- **Future-proof**: New name established from the start

### Negative

- **Development disruption**: 8-10 days of focused work
- **Risk of breakage**: Comprehensive changes can introduce bugs
- **Git history**: Harder to trace pre-rename history

### Mitigations

- Incremental approach with verification between phases
- Comprehensive test suite execution after each phase
- Rollback capability via git branches
- Automated scripts to reduce human error

---

## Alternatives Considered

### Option A: Big Bang (Rejected)

- Complete rename in single sprint
- **Rejected because**: Too high risk, requires full team freeze

### Option C: Parallel Codebase (Rejected)

- Create B2X as new repository, migrate incrementally
- **Rejected because**: Double maintenance overhead, complexity

---

## Technical Implementation

### Automated Tooling

1. **PowerShell/Bash scripts** for bulk find-replace
2. **Roslyn-based refactoring** for C# namespaces (using Roslyn MCP)
3. **IDE refactoring tools** (Rider/VS) for namespace updates
4. **Verification scripts** to find remaining references

### Verification Checklist

- [ ] `dotnet build B2X.slnx` succeeds
- [ ] `dotnet test B2X.slnx` all tests pass
- [ ] All frontend projects build (`npm run build`)
- [ ] Docker compose builds and runs
- [ ] No remaining `B2X` references in code
- [ ] All documentation updated
- [ ] CI/CD pipelines functional

---

## References

- [BS-RENAME-001] Brainstorm: Rename B2X to B2X
- [GL-004] Branch Naming Strategy
- [WF-003] Dependency Upgrade Workflow

---

## Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| @Architect | | ⏳ Pending | |
| @TechLead | | ⏳ Pending | |
| @SARAH | | ⏳ Pending | |

---

**Next Steps** (upon approval):
1. Create GitHub Issues for each phase
2. Create feature branch `feature/rename-B2X-to-b2x`
3. Schedule execution window with team
4. Begin Phase 1: Preparation
