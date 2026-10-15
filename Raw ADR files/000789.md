---
docid: ADR-079
title: ADR 036 Shared Erp Project Architecture
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-036: Shared ERP Project Architecture

**Status:** Accepted  
**Date:** January 5, 2026  
**Context:** B2X ERP Connector Architecture  
**Decision Authors:** @Architect, @TechLead

---

## Problem

The B2X ERP connector architecture (ADR-034) had significant code duplication across multiple implementations:

1. **Standalone ERP Connector** (`erp-connector/`) - .NET Framework 4.8 console app for enventa Trade ERP
2. **Backend Shared Library** (`backend/shared/B2X.Shared.ErpConnector/`) - .NET 8.0 interfaces
3. **Backend Connectors** (`backend/Connectors/`) - .NET 10.0 validation implementations
4. **ERP Domain** (`backend/Domain/ERP/`) - .NET 10.0 provider pattern implementations

This resulted in:
- Duplicated interface definitions (`IErpConnector`, `IErpAdapter`)
- Inconsistent DTO models across implementations
- Validation logic scattered across multiple projects
- Maintenance burden when changes required updates in 4+ locations

---

## Decision Drivers

- **Code Reuse**: Eliminate duplication of common ERP interfaces and models
- **Multi-Framework Support**: Must target .NET Framework 4.8 (enventa), .NET 8.0 (modern ERPs), and .NET 10.0 (latest)
- **Maintainability**: Single source of truth for shared contracts
- **ADR-034 Compliance**: Support pluggable ERP connector framework architecture

---

## Decision

Implement shared projects with multi-targeting to consolidate common ERP code:

### New Project Structure

```
backend/shared/
├── B2X.Shared.Erp.Core/           # Core interfaces & DTOs
│   ├── Interfaces/
│   │   ├── IErpConnector.cs             # Unified connector interface
│   │   ├── IErpAdapterFactory.cs        # Factory pattern
│   │   └── IErpConnectorRegistry.cs     # Registry for pluggable connectors
│   └── Models/
│       ├── ErpConfiguration.cs          # Configuration models
│       ├── ErpCapabilities.cs           # Capability flags
│       ├── ErpResults.cs                # Result types
│       └── ErpDtos.cs                   # Data transfer objects
│
└── B2X.Shared.Erp.Validation/     # Shared validation logic
    ├── IErpDataValidator.cs             # Validator interface
    ├── BaseErpDataValidator.cs          # Base implementation
    └── Validators/
        ├── EnventaDataValidator.cs      # enventa-specific validation
        └── SapDataValidator.cs          # SAP-specific validation
```

### Multi-Targeting Configuration

```xml
<TargetFrameworks>netstandard2.1;net48;net8.0;net10.0</TargetFrameworks>
```

This allows:
- **.NET Standard 2.1**: Broad compatibility baseline
- **.NET Framework 4.8**: Legacy ERP connector support (enventa)
- **.NET 8.0**: Modern ERP implementations (SAP, Dynamics)
- **.NET 10.0**: Latest backend services

### Benefits Achieved

| Aspect | Before | After |
|--------|--------|-------|
| Interface Definitions | 4 locations | 1 location |
| DTO Models | 3+ variants | 1 canonical set |
| Validation Logic | Scattered | Centralized |
| Framework Support | Per-project | Multi-target |

---

## Consequences

### Positive

- ✅ Single source of truth for ERP contracts
- ✅ Consistent validation across all ERP implementations
- ✅ Reduced maintenance overhead
- ✅ Easier addition of new ERP connectors (per ADR-034)
- ✅ Automatic propagation of interface changes

### Negative

- ⚠️ Build time increase due to multi-targeting
- ⚠️ Requires NuGet packages for older frameworks (`System.Threading.Tasks.Extensions`)
- ⚠️ Some advanced features unavailable in .NET Standard 2.1/net48

### Neutral

- Build produces multiple assemblies per target framework
- Existing projects need project reference updates

---

## Implementation

### Projects Created

1. **B2X.Shared.Erp.Core** - Core interfaces and models
2. **B2X.Shared.Erp.Validation** - Shared validation logic

### Projects Updated

1. **erp-connector** - Added references to shared projects
2. **B2X.slnx** - Added shared ERP projects to solution
3. **erp-connector solution** - Added shared project references

---

## Related Documents

- [ADR-034] Multi-ERP Connector Architecture
- [ADR-033] Tenant-Admin Download for ERP-Connector
- [KB-021] enventa Trade ERP Integration

---

## Review Dates

- **Accepted**: January 5, 2026
- **Next Review**: Q2 2026 (after additional ERP connector implementations)
