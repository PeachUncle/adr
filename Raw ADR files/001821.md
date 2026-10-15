# ADR 0002: Use Microsoft Official Analyzers Only

## Status
Accepted

## Context
Code quality analyzers help maintain consistent code style and catch potential issues. Several options exist in the .NET ecosystem:

1. **Microsoft.CodeAnalysis.NetAnalyzers** - Official Microsoft analyzers
2. **StyleCop.Analyzers** - Community-maintained style analyzer
3. **SonarAnalyzer.CSharp** - Third-party commercial/open source
4. **Roslynator** - Community analyzer collection

### StyleCop.Analyzers Investigation
- ⚠️ Community project, not official Microsoft
- ⚠️ Original StyleCop was discontinued by Microsoft in 2015
- ⚠️ Very opinionated rules (documentation, ordering, spacing)
- ⚠️ Not used by Microsoft's own projects (.NET Runtime, ASP.NET Core, EF Core)
- ✅ ~10M downloads/month - popular but optional
- ✅ Open source and maintained

### Microsoft.CodeAnalysis.NetAnalyzers
- ✅ Official Microsoft analyzers
- ✅ Ships with .NET SDK
- ✅ Used by all Microsoft projects
- ✅ Focuses on correctness, performance, and security
- ✅ Less opinionated about style

## Decision
**We will use only Microsoft official analyzers and avoid third-party analyzers like StyleCop.**

Our code quality stack:
- ✅ **Microsoft.CodeAnalysis.NetAnalyzers** - Code analysis
- ✅ **Microsoft.CodeAnalysis.PublicApiAnalyzers** - API tracking (when stable)
- ✅ **.editorconfig** - Style and formatting rules
- ✅ **dotnet format** - Automatic formatting
- ✅ **TreatWarningsAsErrors** - Enforce quality
- ❌ **StyleCop.Analyzers** - Removed

## Rationale

### Why Remove StyleCop?
1. **Not a standard** - Microsoft doesn't use it in their own projects
2. **Too opinionated** - Forces specific documentation and ordering styles
3. **Generates noise** - Many warnings about documentation that may not add value
4. **Redundant** - Microsoft.CodeAnalysis.NetAnalyzers covers correctness
5. **EditorConfig sufficient** - Handles formatting and style consistently

### What We Keep
- **Microsoft.CodeAnalysis.NetAnalyzers**: Official, essential, focuses on bugs
- **.editorconfig**: Universal standard for formatting
- **TreatWarningsAsErrors**: Enforces quality without extra dependencies

## Consequences

### Positive
- ✅ Cleaner builds without style noise
- ✅ Only official Microsoft tools
- ✅ Less opinionated - more flexibility
- ✅ Aligns with Microsoft's own practices
- ✅ Faster builds (fewer analyzers)

### Negative
- ❌ No automatic enforcement of XML documentation
- ❌ No enforcement of member ordering
- ❌ Team must agree on conventions via code review

### Mitigation
- Use `.editorconfig` for essential formatting rules
- Document coding conventions in CONTRIBUTING.md
- Enforce through code review process
- Can add StyleCop later if team grows and needs it

## Alternatives Considered

### Keep StyleCop
- ❌ Rejected: Too opinionated, not used by Microsoft
- ❌ Creates maintenance burden for documentation

### Add SonarAnalyzer
- ⏸️ Deferred: Good tool but adds complexity
- ⏸️ Can consider for future if needed

### Add Roslynator
- ⏸️ Deferred: Useful refactorings but not essential
- ⏸️ Can add via IDE extension for individual developers

## References
- [Microsoft.CodeAnalysis.NetAnalyzers](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview)
- [StyleCop.Analyzers](https://github.com/DotNetAnalyzers/StyleCopAnalyzers)
- [EditorConfig](https://editorconfig.org/)
- [.NET Runtime](https://github.com/dotnet/runtime) - Does not use StyleCop
- [ASP.NET Core](https://github.com/dotnet/aspnetcore) - Does not use StyleCop

## Review Date
Review this decision at v1.0.0 if team size or requirements change.

## Date
2025-10-01
