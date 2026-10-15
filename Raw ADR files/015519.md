# ADR-0015: RenderX.Shell.Avalonia Thin-Host Architecture

**Date:** 2025-11-08  
**Status:** Accepted  
**Context:** Shell Upgrade from WebView2 to Native Avalonia  
**Decision Makers:** Architecture Team  

## Problem Statement

The RenderX.Shell.Avalonia currently uses WebView2 to host a TypeScript frontend, creating:
- External runtime dependency (150MB+)
- IPC overhead (5-10ms latency)
- Complex deployment process
- Separate logging streams
- Difficult maintenance and extension

## Decision

Upgrade the shell to a **thin-host architecture** that:
1. Consumes `RenderX.HostSDK.Avalonia` and `MusicalConductor.Avalonia` as dependencies
2. Provides only native Avalonia UI controls (CanvasControl, ControlPanelControl)
3. Delegates ALL business logic to the SDKs
4. Routes user interactions through SDK services via DI

## Rationale

### Why Thin-Host?
- **Single Source of Truth:** Business logic lives in SDKs, not duplicated in shell
- **Consistency:** All shells use the same SDK implementations
- **Testability:** SDKs tested independently from UI
- **Scalability:** Easy to add new shells without code duplication
- **Performance:** Direct method calls (75% faster than IPC)

### Why NOT Monolith?
- Duplicates SDK logic
- Difficult to maintain multiple implementations
- Inconsistent behavior across shells
- Harder to test
- Slower performance

## Architecture

### Shell Responsibilities (ONLY)
- Avalonia UI controls (Canvas, ControlPanel)
- User interaction handling
- Event subscription/publishing (via IEventRouter)
- Conductor execution (via IConductorClient)
- Logging (via Conductor's infrastructure)

### SDK Responsibilities (ALL BUSINESS LOGIC)
- Event routing (IEventRouter)
- Component inventory (IInventoryAPI)
- CSS registry (ICssRegistryAPI)
- Conductor execution (IConductorClient)
- Plugin management
- Sequence execution
- Logging infrastructure

### ThinHostLayer (Facade)
```csharp
public interface IThinHostLayer
{
    IEventRouter EventRouter { get; }
    IInventoryAPI InventoryAPI { get; }
    ICssRegistryAPI CssRegistry { get; }
    IConductorClient Conductor { get; }
    ILogger Logger { get; }
}
```

## Constraints

### REQUIRED:
- All services injected via DI
- No custom SDK interface implementations
- No business logic in shell code
- All logging through Conductor
- ThinHostLayer is a simple facade

### FORBIDDEN:
- Custom IEventRouter implementations
- Custom IConductor implementations
- Imports from `RenderX.Shell.Avalonia.Core.Conductor/**`
- Imports from `RenderX.Shell.Avalonia.Core.Events/**`
- Business logic in UI controls
- Creating SDK service instances with `new`

## Enforcement

### Roslyn Analyzer
- Rule: `SHELL001` - Thin-host architecture violation
- Detects forbidden imports
- Prevents drift from pattern
- Runs on every build

### Code Review Checklist
- [ ] No custom SDK implementations
- [ ] All services from DI
- [ ] No forbidden imports
- [ ] Roslyn analyzer passes

### Tests
- Unit tests for analyzer
- Integration tests for thin-host pattern
- E2E tests for functionality

## Implementation

### Phase 1: Foundation (2-3 hours)
- Add SDK references
- Create ThinHostLayer
- Update DI registration

### Phase 2: UI Components (8-12 hours)
- Create CanvasControl
- Create ControlPanelControl
- Wire events

### Phase 3: Integration (6-8 hours)
- Plugin manager
- Component rendering
- Event routing

### Phase 4: Cleanup (4-6 hours)
- Remove WebView2
- Remove legacy code
- Optimize performance

## Benefits

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Startup | ~3s | <2s | 33% faster |
| Component Load | ~500ms | <100ms | 80% faster |
| Event Latency | ~20ms | <5ms | 75% faster |
| Memory | ~250MB | <200MB | 20% reduction |
| Deployment | ~250MB | <100MB | 60% reduction |

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Jint stability | Medium | Use proven MusicalConductor.Avalonia |
| UI performance | Medium | Profile & optimize hot paths |
| Plugin compatibility | Medium | Comprehensive integration tests |
| Architecture drift | Medium | Roslyn analyzer enforcement |

## Alternatives Considered

### 1. Keep WebView2
- **Pros:** No changes needed
- **Cons:** Maintains all current problems

### 2. Monolith Shell
- **Pros:** Simpler initially
- **Cons:** Duplicates SDK logic, harder to maintain

### 3. Thin-Host (CHOSEN)
- **Pros:** Single source of truth, consistent, testable, performant
- **Cons:** Requires discipline to maintain pattern

## References

- SHELL_UPGRADE_README.md
- SHELL_UPGRADE_IMPLEMENTATION_GUIDE.md
- GitHub Issue #369 (Main Epic)
- GitHub Issues #370-373 (Phase Issues)

## Approval

- [ ] Architecture Team
- [ ] Development Team
- [ ] QA Team

