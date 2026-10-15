---
docid: ADR-076
title: ADR 033 Tenant Admin Download Erp Connector Cli
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-033: Tenant-Admin Download for ERP-Connector and Administration-CLI Coupled to CLI

**Status:** Approved  
**Date:** January 5, 2026  
**Context:** B2X multi-tenant SaaS platform  
**Decision Authors:** @Architect, @Backend, @Security, @DevOps, @TechLead, @ProductOwner, @Legal, @Support, @DocMaintainer

---

## Problem

Following the CLI architecture split in ADR-031, where the administration CLI is designed to be distributable to tenant administrators, we need to decide whether to:

1. **Provide downloadable ERP-connector** to tenant-admins for on-premises ERP integration
2. **Couple the administration-CLI** with ERP-connector functionality for unified tenant management

### Current State
- ERP integrations are handled via the ERP-connector (KB-021)
- ERP-connector is a .NET Framework 4.8 console application running on-premises
- Administration CLI (from ADR-031) provides tenant-scoped operations
- No current mechanism for tenant-admins to download or manage ERP components

### Key Concerns
- **Security:** ERP-connector requires access to sensitive ERP data and systems
- **Coupling:** Should administration CLI include ERP management commands?
- **Multi-tenancy:** How to ensure tenant isolation in downloadable components?
- **Technical Feasibility:** Distribution, versioning, and support implications

### Business Context
- Tenant-admins need to integrate their ERP systems with B2X
- Current process requires manual ERP-connector setup and configuration
- Opportunity to simplify onboarding by providing downloadable tools
- Risk of exposing internal infrastructure or compromising security

---

## Decision Drivers

### Security Considerations
- ERP-connector accesses sensitive business data (customers, orders, inventory)
- Must prevent cross-tenant data leakage
- Authentication must be tenant-scoped and auditable
- Distribution must follow security guidelines (security.instructions.md)

### Coupling Analysis
- Administration CLI is tenant-focused (users, catalogs, tenant config)
- ERP-connector is integration-focused (data synchronization, API bridging)
- Coupling could simplify deployment but increase complexity
- Separation maintains clear boundaries but requires separate tooling

### Multi-Tenancy Requirements
- Each tenant's ERP-connector must be isolated
- Configuration must be tenant-specific
- No shared state between tenant deployments
- Audit logging must track tenant-specific operations

### Technical Feasibility
- ERP-connector is .NET Framework 4.8 (Windows-only)
- Administration CLI is .NET 10 cross-platform
- Distribution via NuGet packages
- Version compatibility and update management

### User Experience
- Simplify tenant onboarding process
- Reduce support burden
- Provide unified tooling for tenant administration
- Enable self-service ERP setup

---

## Considered Options

### Option 1: Coupled Administration CLI with ERP-Connector Download
**Provide administration CLI that includes ERP-connector download and management commands**

**Pros:**
- ✅ Unified tooling for tenant administration and ERP integration
- ✅ Simplified deployment (single CLI handles both concerns)
- ✅ Easier user experience (one tool to learn)
- ✅ Consistent authentication and configuration

**Cons:**
- ❌ Increased coupling between administration and integration concerns
- ❌ Larger distribution package with ERP-specific dependencies
- ❌ Potential security risks if ERP commands access sensitive data inappropriately
- ❌ Versioning complexity (CLI and ERP-connector may have different release cycles)

**Technical Feasibility:** Medium - Requires extending administration CLI with ERP commands and download functionality

### Option 2: Separate ERP-Connector Download Only
**Provide standalone ERP-connector download, keep administration CLI separate**

**Pros:**
- ✅ Clear separation of concerns (administration vs. integration)
- ✅ Smaller, focused administration CLI
- ✅ Independent versioning and deployment
- ✅ Reduced security surface for administration CLI

**Cons:**
- ❌ Tenant-admins need multiple tools for complete setup
- ❌ More complex user experience (separate installations)
- ❌ Potential configuration inconsistencies between tools
- ❌ Increased support overhead for tool coordination

**Technical Feasibility:** High - ERP-connector already exists as standalone component

### Option 3: ERP-Connector Remains Internal Only
**Do not provide downloadable ERP-connector, require professional services setup**

**Pros:**
- ✅ Maximum security (no external distribution of ERP access)
- ✅ Controlled deployment and configuration
- ✅ Professional services revenue opportunity
- ✅ Simplified support (internal team handles all setups)

**Cons:**
- ❌ Poor user experience (manual setup required)
- ❌ Higher barrier to entry for tenants
- ❌ Increased operational overhead
- ❌ Limits scalability and self-service capabilities

**Technical Feasibility:** High - No additional development required

---

## Decision

**Provide downloadable ERP-connector coupled with administration CLI for tenant-admins**

### Rationale
- **Security:** Tenant-scoped authentication and isolation can be enforced
- **User Experience:** Unified tooling significantly simplifies tenant onboarding
- **Business Value:** Enables self-service ERP integration, reducing support costs
- **Technical Feasibility:** Building on existing ADR-031 split, coupling is manageable

### Implementation Approach
1. **Extend Administration CLI** with ERP-connector download commands
2. **Tenant-Scoped Distribution** - CLI downloads tenant-specific ERP-connector builds
3. **Secure Download Mechanism** - Authenticated, version-controlled downloads
4. **Configuration Coupling** - Administration CLI can configure downloaded ERP-connector

### Key Requirements
- ERP-connector downloads are authenticated with tenant API keys
- Downloaded ERP-connector is pre-configured for the tenant
- Administration CLI includes commands for ERP-connector lifecycle management
- All operations are audited and tenant-isolated

---

## Proposed Architecture

```
Administration CLI (Downloadable to Tenants)
├── Core Commands (from ADR-031)
│   ├── tenant create/update
│   ├── user management
│   └── catalog operations
│
├── ERP Integration Commands (New)
│   ├── erp download-connector
│   ├── erp configure-connector
│   ├── erp start-connector
│   ├── erp status-connector
│   └── erp update-connector
│
└── Download Service (Internal)
    ├── Tenant-Authenticated Downloads
    ├── Version Management
    └── Configuration Injection
```

### Download Flow
```bash
# Tenant admin downloads and configures ERP-connector
B2X erp download-connector --version latest
B2X erp configure-connector --erp-type enventa --connection-string "..."
B2X erp start-connector --background
```

### Security Model
- Downloads require valid tenant API key
- ERP-connector is signed and version-controlled
- Configuration includes tenant-specific isolation parameters
- All operations logged for audit compliance

---

## Security Considerations

### Authentication & Authorization
- ✅ Tenant API key required for all ERP operations
- ✅ Downloads authenticated against tenant identity
- ✅ No cross-tenant access possible
- ✅ Audit logging for all download and configuration operations

### Data Protection
- ✅ ERP-connector configuration encrypted at rest and in transit
- ✅ HTTPS required for all download communications
- ✅ No sensitive data in logs (masking applied)
- ✅ Certificate pinning for production downloads

### Distribution Security
- ✅ Signed NuGet packages for CLI distribution
- ✅ Signed ERP-connector binaries
- ✅ Version verification before download
- ✅ Tamper detection and integrity checks

### Multi-Tenancy Isolation
- ✅ Each downloaded ERP-connector configured for single tenant
- ✅ Tenant ID embedded in configuration
- ✅ No shared state between tenant deployments
- ✅ Rate limiting per tenant for downloads

---

## Consequences

### Positive ✅

1. **Improved User Experience**
   - Single CLI for all tenant administration tasks
   - Self-service ERP integration setup
   - Reduced onboarding time for new tenants
   - Consistent tooling across administration and integration

2. **Business Benefits**
   - Lower support costs (self-service capabilities)
   - Faster tenant time-to-value
   - Competitive advantage in ERP integration ease
   - Revenue opportunity through premium ERP features

3. **Technical Benefits**
   - Unified authentication and configuration
   - Easier maintenance (single CLI to update)
   - Consistent versioning and release cycles
   - Better monitoring and troubleshooting

4. **Security Benefits**
   - Controlled distribution with tenant isolation
   - Audit trail for all tenant operations
   - Professional security review for downloadable components

### Challenges ⚠️

1. **Increased Complexity**
   - Administration CLI now handles both admin and integration concerns
   - Larger codebase with ERP-specific logic
   - **Mitigation:** Clear module separation, shared libraries

2. **Security Risks**
   - ERP-connector distribution increases attack surface
   - Potential for misconfiguration by tenant-admins
   - **Mitigation:** Comprehensive security review, automated validation

3. **Version Management**
   - Coordinating CLI and ERP-connector versions
   - Backward compatibility requirements
   - **Mitigation:** Semantic versioning, automated testing

4. **Support Overhead**
   - Tenant-admins may need help with ERP setup
   - Debugging distributed components
   - **Mitigation:** Enhanced documentation, remote diagnostics

---

## Implementation Plan

### Phase 1: Core Download Functionality (Week 1-2)
- Implement `DownloadCommand` with authenticated HTTP client
- Add binary signature verification
- Unit tests for download logic
- Integration with existing CLI authentication

### Phase 2: Service Management Commands (Week 3)
- Implement install/start/stop/status commands
- Cross-platform service abstraction
- Error handling and user feedback
- Integration tests with mock ERP connector

### Phase 3: Advanced Features & Security (Week 4)
- Version management and compatibility checks
- Secure distribution pipeline setup
- Audit logging integration
- End-to-end testing across platforms

### Phase 4: Documentation and Testing (Week 5)
- Customer-facing documentation
- Integration tests with real ERP-connector
- Migration guide for existing tenants
- Support team training

### Phase 5: Controlled Rollout (Week 6-7)
- Beta release to select tenants
- Monitor usage and support tickets
- Iterate based on feedback
- Full production release

---

## Success Metrics

### Technical Metrics
- ✅ 100% tenant isolation in downloaded components
- ✅ <30 second download and configuration time
- ✅ Zero security incidents from downloadable components
- ✅ 95% automated test coverage for ERP commands

### User Experience Metrics
- ✅ 80% reduction in ERP setup support tickets
- ✅ 50% faster tenant onboarding time
- ✅ 90% tenant satisfaction with self-service tools
- ✅ <5% configuration errors by tenants

### Operational Metrics
- ✅ ERP-connector downloads operational within 6 weeks
- ✅ Documentation complete and accurate
- ✅ Support team trained on new functionality
- ✅ Audit compliance verified

---

## Documentation Requirements

### Customer-Facing Documentation
- ERP-connector download and setup guide
- Administration CLI ERP commands reference
- Troubleshooting common ERP integration issues
- Security best practices for on-premises deployment

### Internal Documentation
- Download service API documentation
- Security review procedures for downloadable components
- Audit logging and monitoring setup
- Incident response procedures

---

## Related Decisions

- **ADR-031:** CLI Architecture Split - Administration CLI design
- **KB-021:** enventa Trade ERP - ERP integration details
- **ADR-026:** ERP Startup Performance Optimization
- **ADR-029:** Multi-Format Punchout Integration

---

## Stakeholder Approval

### Required Approvals
- [x] @Architect - Architecture design and coupling analysis
- [x] @Security - Security model and distribution risks
- [x] @Backend - Implementation feasibility
- [x] @DevOps - Deployment and monitoring strategy
- [x] @TechLead - Code quality and testing standards
- [x] @ProductOwner - User experience and business value
- [x] @Legal - Distribution licensing and compliance
- [x] @Support - Support implications and training needs
- [x] @DocMaintainer - Documentation completeness

### Reviewed By
- [x] @SARAH - Quality-gate coordination

### Implementation Status
- **Phase:** Planning
- **Owner:** @Backend
- **Target Date:** End of Q1 2026

---

## References

### External
- [NuGet Package Signing](https://docs.microsoft.com/en-us/nuget/reference/signed-packages)
- [.NET Global Tools Security](https://docs.microsoft.com/en-us/dotnet/core/tools/global-tools)
- [OWASP Secure Distribution Guidelines](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

### Internal
- [ADR-031] CLI Architecture Split
- [KB-021] enventa Trade ERP Integration Guide
- [security.instructions.md] Security Guidelines
- ERP-Connector README: 
- Administration CLI: 

---

**Status:** ✅ Approved  
**Next Review:** January 12, 2026  
**Implementation Target:** Q1 2026