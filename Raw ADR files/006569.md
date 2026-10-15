# ADR-001: Registry-Based Architecture for Component Selection

## Status

**Accepted** - Implemented December 2024

## Context

The Algorithm Visualization Platform needed a scalable way to handle multiple algorithms without requiring routing or configuration changes for each new algorithm. The initial implementation had two panels:

- **LEFT Panel (Visualization):** Successfully used a registry pattern (`visualizationRegistry.js`) to dynamically select visualization components based on `visualization_type` metadata
- **RIGHT Panel (Algorithm State):** Originally used hardcoded conditionals in `App.jsx` to select state components

This architectural inconsistency created several problems:

1. **Scalability**: Each new algorithm required modifying `App.jsx` with new conditionals
2. **Maintenance**: Algorithm-specific logic scattered across the main application component
3. **Inconsistency**: Two different patterns for similar problems (component selection)
4. **Developer Experience**: Contributors had to understand two different approaches

## Decision

**Extend the registry pattern to the RIGHT panel (algorithm state components), achieving symmetric architecture across both panels.**

### Implementation

Both panels now use registry-based component selection:

**LEFT Panel (Visualization):**
```javascript
// visualizationRegistry.js
const VISUALIZATION_REGISTRY = {
  'array': ArrayView,
  'timeline': TimelineView,
  'graph': GraphView,
  'tree': TreeView
};

export const getVisualizationComponent = (visualizationType) => {
  return VISUALIZATION_REGISTRY[visualizationType] || DefaultVisualization;
};
```

**RIGHT Panel (Algorithm State):**
```javascript
// stateRegistry.js
const STATE_REGISTRY = {
  'binary-search': BinarySearchState,
  'interval-coverage': IntervalCoverageState,
  'merge-sort': MergeSortState
};

export const getStateComponent = (algorithmName) => {
  return STATE_REGISTRY[algorithmName] || DefaultStateComponent;
};
```

**Usage in App.jsx:**
```javascript
// Before: 100+ lines of conditionals
const isIntervalCoverage = currentAlgorithm === 'interval-coverage';
{isIntervalCoverage ? (
  <IntervalCoverageState step={step} />
) : (
  <BinarySearchState step={step} />
)}

// After: 2 lines, zero algorithm-specific logic
const StateComponent = getStateComponent(currentAlgorithm);
<StateComponent step={step} onIntervalHover={onIntervalHover} />
```

### Key Architectural Principles

1. **Backend Declares, Frontend Selects**
   - Backend metadata specifies what's needed (`visualization_type`, `algorithm` name)
   - Frontend registries automatically select appropriate components

2. **Zero-Config Algorithm Addition**
   - Register backend tracer class → appears in API
   - Register state component → appears in UI
   - No `app.py` changes, no `App.jsx` changes

3. **Graceful Fallback**
   - Unknown algorithms get `DefaultStateComponent`
   - Unknown visualization types get `DefaultVisualization`
   - Console warnings for debugging, no crashes

4. **Prop Forwarding**
   - All potential props passed to dynamic components
   - Unused props ignored (React standard behavior)
   - Enables flexible component interfaces

## Alternatives Considered

### Alternative 1: Keep Conditional Pattern
**Approach:** Continue using `if/else` or ternary conditionals for state components

**Pros:**
- No new abstractions
- Direct, easy to trace in debugger
- Explicit component selection

**Cons:**
- Doesn't scale (100 algorithms = 100 conditionals)
- `App.jsx` grows unbounded
- Violates DRY principle (LEFT panel already uses registry)
- Every algorithm requires `App.jsx` modification

**Rejected Because:** Architectural inconsistency and poor scalability

---

### Alternative 2: Component-per-Route Architecture
**Approach:** Create separate routes/pages for each algorithm

**Pros:**
- Clear separation by algorithm
- Standard React Router pattern
- Easy code splitting

**Cons:**
- Requires routing configuration per algorithm
- Duplicates shared UI logic (control bar, modals, keyboard shortcuts)
- Violates "zero frontend routing changes" principle
- Breaks single-page application model

**Rejected Because:** Goes against core platform philosophy (backend does thinking, frontend reacts)

---

### Alternative 3: Higher-Order Component (HOC) Pattern
**Approach:** Wrap each algorithm state component in HOC that handles registration

**Pros:**
- Declarative registration
- Co-located with component definition
- Standard React pattern

**Cons:**
- More complex than simple object registry
- Requires build-time processing or runtime registration
- Harder to debug (wrapper layers)
- Doesn't provide centralized view of registered components

**Rejected Because:** Over-engineered for the problem; simple object lookup is sufficient

---

### Alternative 4: Dynamic Imports with Naming Convention
**Approach:** Use dynamic `import()` based on algorithm name convention

```javascript
const StateComponent = React.lazy(() => 
  import(`./components/algorithm-states/${algorithmName}State.jsx`)
);
```

**Pros:**
- No explicit registration needed
- Automatic discovery via file system
- Built-in code splitting

**Cons:**
- Relies on file naming convention (fragile)
- Harder to validate at build time
- Poor error messages when component missing
- Can't easily list all registered algorithms
- Build tools may not support dynamic imports well

**Rejected Because:** Too magical; explicit registration is clearer and more maintainable

## Consequences

### Positive

1. **Scalability Achieved**
   - Can support 100+ algorithms without modifying `App.jsx`
   - Adding algorithm = register in two places (backend registry + state registry)
   - Linear complexity instead of multiplicative

2. **Architectural Consistency**
   - Both panels use identical patterns
   - Single mental model for contributors
   - Easier onboarding for new developers

3. **Maintainability Improved**
   - `App.jsx` reduced by 80+ lines
   - Algorithm-specific logic isolated in components
   - Changes to one algorithm don't affect others

4. **Developer Experience Enhanced**
   - Clear process: "Create component → Register → Done"
   - Centralized registry shows all available options
   - Helper functions (`isStateComponentRegistered()`) for validation

5. **Testing Simplified**
   - Registry functions are pure, easy to test
   - Mock registries for component testing
   - No need to test App.jsx for each algorithm

### Negative

1. **Indirection Added**
   - One extra lookup per render (negligible performance impact)
   - Debugging requires checking registry mapping
   - Less obvious which component renders for which algorithm

2. **Registration Required**
   - Must remember to register both backend and frontend
   - Forgetting registration = silent fallback to default component
   - No compile-time enforcement (could add build validation)

3. **Props Must Be Generic**
   - All potential props passed to all components
   - Some components receive unused props
   - Requires documentation of prop contracts

### Mitigation Strategies

For indirection concerns:
- Add comprehensive JSDoc comments to registry functions
- Include examples in README
- Use TypeScript in future for type safety

For registration concerns:
- Add compliance checklist item: "State component registered in `stateRegistry.js`"
- Consider build-time validation script
- Console warnings when algorithm has no registered component

For prop contract concerns:
- Document expected props in each component's PropTypes
- Create interface documentation in component files
- Consider TypeScript interfaces in future

## Related Decisions

- **ADR-002**: Component Organization Principles (explains where registered components live)
- **Backend Registry Pattern**: This decision mirrors the existing backend algorithm registry architecture

## Validation

The registry pattern was validated through:

1. **Successful Phase 3-4 Implementation** (December 2024)
   - Created `stateRegistry.js` with complete test coverage
   - Refactored `App.jsx` from 100+ lines of conditionals to 2 lines
   - Zero functional regressions

2. **Both Algorithms Work Identically**
   - Binary Search: Pointers display correctly
   - Interval Coverage: Call stack displays correctly
   - Algorithm switching: No errors
   - Keyboard shortcuts: All functional

3. **Code Metrics**
   - `App.jsx`: Reduced by 80+ lines
   - Test coverage: 80%+ on registry functions
   - Zero breaking changes

## Implementation Notes

**File Locations:**
- `frontend/src/utils/stateRegistry.js` - State component registry
- `frontend/src/utils/visualizationRegistry.js` - Visualization component registry
- `frontend/src/App.jsx` - Uses both registries (lines 16, 173)
- `docs/ADR/FRONTEND/ADR-001-registry-based-architecture.md` - This document

**Registry Functions:**
- `getStateComponent(algorithmName)` - Get state component for algorithm
- `isStateComponentRegistered(algorithmName)` - Check if component registered
- `getRegisteredAlgorithms()` - List all registered algorithms

**Current Registrations:**
- `binary-search` → `BinarySearchState`
- `interval-coverage` → `IntervalCoverageState`

## Future Considerations

1. **TypeScript Migration**
   - Add type safety to registry lookups
   - Enforce prop contracts with interfaces
   - Build-time validation of registrations

2. **Build-Time Validation**
   - Script to verify all backend algorithms have frontend registrations
   - Warn if component files exist but not registered
   - CI/CD integration

3. **Auto-Registration via File System**
   - Explore webpack/vite plugins for automatic registration
   - Maintain explicit registry as source of truth
   - Use file system as validation, not source

4. **Registry Extensions**
   - Add metadata to registrations (description, author, version)
   - Support algorithm variants (same algorithm, different visualizations)
   - Plugin system for third-party algorithms

## References

- Implementation: Session 39-41 (December 2024)
- Refactoring Plan: `docs/REFACTORING_FE_PHASED_PLAN.md`
- Test Coverage: `frontend/src/utils/stateRegistry.test.js`

---

**Author:** Development Team  
**Date:** December 14, 2024  
**Last Updated:** December 14, 2024