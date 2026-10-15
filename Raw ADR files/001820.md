# ADR 0001: Defer Public API Tracking Until API Stabilization

## Status
Accepted

## Context
The `Microsoft.CodeAnalysis.PublicApiAnalyzers` package enforces tracking of all public APIs in `PublicAPI.txt` files. This is an excellent practice for stable libraries to prevent breaking changes, but presents challenges during early development:

1. APIs are changing frequently as we design the workflow orchestration abstractions
2. No automated tool exists to generate the complex PublicAPI.txt signatures
3. Manual maintenance of PublicAPI.txt during rapid iteration is time-consuming
4. The nullability annotations (`!`, `?`) must be precisely correct

## Decision
**We will temporarily disable PublicAPI analyzers (RS0016, RS0017, RS0027, RS0036) for the `Flowrex.Abstractions` project until the API design stabilizes.**

This is a common and accepted practice for libraries in early development, including Microsoft's own projects.

## Consequences

### Positive
- ✅ Faster iteration during API design phase
- ✅ No manual maintenance overhead for changing APIs
- ✅ Clean builds without false positives
- ✅ Focus on API design rather than tracking mechanics

### Negative  
- ❌ No automatic detection of breaking changes during development
- ❌ Risk of accidental API changes (mitigated by code review)
- ❌ Must manually generate PublicAPI.txt files before v1.0.0

## When to Re-enable
Enable PublicAPI tracking when:
1. API design is stable (target: v1.0.0-beta)
2. No major API changes expected
3. Ready to commit to semantic versioning

## How to Re-enable
1. Remove `<NoWarn>` entries from `Flowrex.Abstractions.csproj`
2. Build project to see RS0016 errors listing missing APIs
3. Create `PublicAPI.Unshipped.txt` with exact signatures including nullability
4. Verify build succeeds
5. Document in CHANGELOG.md that API tracking is now enabled

## References
- [PublicApiAnalyzers Documentation](https://github.com/dotnet/roslyn-analyzers/tree/main/src/PublicApiAnalyzers)
- [Semantic Versioning](https://semver.org/)
- Compliance Rule 6.3: Document architecture decisions as ADRs

## Date
2025-10-01
