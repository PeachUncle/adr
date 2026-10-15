# ADR-001: .NET 9.0 Framework Selection

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Week 1, Day 1 - Project Initialization

## Context

The project needed to select a primary development framework that would support:

- Modern C# language features
- High-performance web APIs
- Blazor for interactive web applications
- Strong typing and compile-time safety
- Cross-platform deployment (Azure Container Apps, Docker)
- Rich ecosystem for AI/ML integration

## Decision

Selected **.NET 9.0** as the target framework for all projects in the solution.

## Rationale

1. **Latest LTS Features**: .NET 9.0 provides the latest language features including C# 13
2. **Performance**: Significant performance improvements in ASP.NET Core and runtime
3. **Blazor Enhancements**: Improved Blazor Server performance and SignalR integration
4. **Native AOT Support**: Better startup time and reduced memory footprint
5. **Aspire Integration**: .NET Aspire 9.5.1 provides excellent cloud-native orchestration
6. **Ecosystem Maturity**: Extensive package ecosystem for Entity Framework Core, Azure SDK, ML.NET
7. **Long-term Support**: Microsoft commitment to enterprise-grade support and security updates

## Consequences

### Positive

- Access to latest C# 13 features (primary constructors, collection expressions, etc.)
- Excellent performance for high-throughput assessment API
- Strong tooling support in VS Code with C# DevKit
- Seamless Azure deployment with Container Apps
- Native support for OpenTelemetry and observability

### Negative

- Requires .NET 9.0 SDK for all developers
- Some third-party packages may lag in .NET 9 support
- Dev containers must include .NET 9 SDK (increased image size)

### Risks Mitigated

- Used global.json to lock SDK version (9.0.100) for consistency
- All CI/CD pipelines use exact SDK version
- Dev container pre-configured with .NET 9.0

## Related Decisions

- ADR-002: Blazor Server for Student App
- ADR-007: .NET Aspire for Local Orchestration
- ADR-028: Upgrade to .NET 9 and Aspire 9.5.1

## References

- `global.json` - SDK version pinning
- Commit: `28044ab` - "feat: Upgrade to .NET 9 and Aspire 9.5.1"
- All `*.csproj` files specify `<TargetFramework>net9.0</TargetFramework>`
