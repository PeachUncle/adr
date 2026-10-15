---
title: "ADR-001: Migration to .NET 10"
date: 2025-11-13
status: Accepted
tags: [dotnet, migration, framework, policy]
---

# ADR-001: Migration to .NET 10

## Status

Accepted

## Date

2025-11-13

## Context

The .NET ecosystem continues to evolve rapidly, with Microsoft releasing new versions that provide performance improvements, new language features, security updates, and long-term support. As of November 2025, .NET 10 is available and represents the current standard for .NET development.

Our organization currently has projects running on various .NET versions:
- .NET 8 and earlier (legacy projects)
- .NET 9 (recently created projects)
- .NET 10 (new development)

We need to establish a clear policy regarding .NET version adoption to:
- Maintain security and receive critical updates
- Leverage modern C# language features and performance improvements
- Ensure consistency across our codebase
- Reduce technical debt
- Align with Microsoft's support lifecycle

## Decision

We have decided to adopt the following .NET version policy:

### General Recommendation: .NET 10
**All new projects and active development SHOULD use .NET 10** as the target framework. This is the recommended standard for all Wigo4it development.

### Acceptable: .NET 9
**.NET 9 projects are ALLOWED to remain on .NET 9** without immediate migration requirements. However:
- New projects SHOULD NOT be created with .NET 9
- Teams are ENCOURAGED to upgrade to .NET 10 during regular maintenance cycles
- .NET 9 projects MUST be upgraded to .NET 10 before .NET 9 reaches end of support

### Required: Upgrade from .NET 8 and Earlier
**All projects running .NET 8 or earlier versions MUST be updated** to the latest version (.NET 10):
- This is a MANDATORY requirement, not a recommendation
- Migration plans must be created for all affected projects
- Timeline: All .NET 8 and earlier projects must be migrated within 6 months of this ADR's acceptance
- Priority should be given to customer-facing applications and critical services

## Rationale

### Why .NET 10 is Recommended

1. **Performance Improvements**: .NET 10 includes significant runtime and compiler optimizations
2. **C# 14 Features**: Access to the latest language features including:
   - Primary constructors improvements
   - Collection expressions enhancements
   - Enhanced pattern matching
   - Improved nullable reference types
3. **Security Updates**: Latest security patches and improvements
4. **Long-term Support**: .NET 10 will be supported by Microsoft through its lifecycle
5. **Ecosystem Alignment**: Latest libraries and frameworks target .NET 10
6. **Developer Productivity**: Modern tooling and IDE support optimized for .NET 10

### Why .NET 9 is Still Acceptable

1. **Recent Investment**: Projects recently built on .NET 9 represent recent development effort
2. **Stability**: .NET 9 is still a supported and stable platform
3. **Migration Cost**: Forcing immediate migration would create unnecessary overhead
4. **Risk Management**: Allows teams to plan migrations during appropriate maintenance windows

### Why .NET 8 and Earlier Must Be Updated

1. **Support Lifecycle**: .NET 8 and earlier versions are approaching or past end-of-life
2. **Security Risks**: Older versions no longer receive security updates
3. **Technical Debt**: Maintaining multiple old versions increases complexity
4. **Performance Gap**: Significant performance improvements in newer versions
5. **Recruitment**: Difficult to attract talent when working on outdated technology
6. **Dependency Issues**: Third-party libraries dropping support for older versions

## Consequences

### Positive Consequences

- **Improved Security**: All projects will be on supported versions with active security updates
- **Better Performance**: Applications will benefit from runtime and compiler optimizations
- **Modern Features**: Developers can use latest C# language features across all projects
- **Reduced Complexity**: Fewer .NET versions to support and maintain
- **Better Tooling**: Consistent developer experience with latest tooling
- **Future-Proof**: Easier to adopt future .NET versions with smaller version gaps

### Negative Consequences

- **Migration Effort**: Teams must invest time to upgrade .NET 8 and earlier projects
- **Testing Requirements**: Upgraded applications require thorough testing
- **Potential Breaking Changes**: Some APIs may have breaking changes between versions
- **Learning Curve**: Developers need to learn new features and changed behaviors
- **Third-party Dependencies**: Some libraries may need updates or replacements

### Migration Guidance

For projects requiring migration from .NET 8 or earlier to .NET 10:

1. **Assessment Phase**:
   - Inventory all dependencies and verify .NET 10 compatibility
   - Identify deprecated APIs and breaking changes
   - Estimate effort and create migration plan

2. **Preparation Phase**:
   - Update all NuGet packages to versions compatible with .NET 10
   - Review Microsoft's migration guides for breaking changes
   - Set up test environment with .NET 10

3. **Migration Phase**:
   - Update project files (`.csproj`) to target `net10.0`
   - Address compiler warnings and errors
   - Update deprecated API usage
   - Apply code fixes for breaking changes

4. **Testing Phase**:
   - Run full regression test suite
   - Perform integration testing
   - Validate performance metrics
   - Conduct user acceptance testing

5. **Deployment Phase**:
   - Deploy to non-production environments first
   - Monitor application behavior
   - Roll out to production with rollback plan ready

### Exceptions

Exceptions to this policy may be granted in the following circumstances:
- **Legacy Systems**: Systems scheduled for decommissioning within 6 months
- **Third-party Constraints**: Systems constrained by third-party platform requirements
- **Customer Requirements**: Customer-mandated platform requirements

All exceptions must be:
- Documented with justification
- Approved by technical leadership
- Reviewed quarterly for continued validity

## Implementation

1. **Immediate Actions**:
   - Communicate this ADR to all development teams
   - Update project templates to use .NET 10
   - Update CI/CD pipelines to support .NET 10 builds
   - Update developer workstation setup guides

2. **Within 1 Month**:
   - Create inventory of all .NET projects and their versions
   - Identify projects requiring mandatory migration
   - Create migration timeline for .NET 8 and earlier projects

3. **Within 3 Months**:
   - Begin migration of .NET 8 and earlier projects
   - Provide migration support and guidance
   - Track migration progress

4. **Within 6 Months**:
   - Complete all mandatory migrations from .NET 8 and earlier
   - Review and update this ADR if needed

## Monitoring and Review

- **Quarterly Reviews**: Track progress on migrations and policy compliance
- **Annual Review**: Reassess this policy when new .NET versions are released
- **Update Trigger**: This ADR should be reviewed when .NET 11 is released

## References

- [.NET Support Policy](https://dotnet.microsoft.com/platform/support/policy/dotnet-core)
- [What's new in .NET 10](https://learn.microsoft.com/dotnet/core/whats-new/dotnet-10)
- [C# 14 Language Features](https://learn.microsoft.com/dotnet/csharp/whats-new/csharp-14)
- [Migrate from .NET Framework to .NET 10](https://learn.microsoft.com/dotnet/core/porting/)

## Related Documents

- ADR-002: C# Language Version Policy (if it exists)
- Coding Standards: .NET Project Structure
- DevOps Guidelines: CI/CD Pipeline Configuration
