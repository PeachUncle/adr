# ADR-0020 — Control Panel UI Sequence Orchestration

**Status:** Accepted  
**Date:** 2025-08-25  
**Related Issue:** [#33 - Design shift: Orchestrate Control Panel UI via sequences](https://github.com/BPMSoftwareSolutions/renderx-plugins-demo/issues/33)

## Context

The Control Panel UI was previously orchestrated through local React-only flows using hooks, reducers, and direct component interactions. While functional, this approach had several limitations:

1. **Limited Observability**: UI lifecycles were hidden within React hooks and reducers, making it difficult to trace and debug UI behavior
2. **Tight Coupling**: Implicit effects and hidden dependencies between components made the system harder to maintain and test
3. **Inconsistent Architecture**: UI interactions didn't follow the symphony pattern used throughout the rest of the platform
4. **Testing Challenges**: Complex UI flows were difficult to test at the sequence level due to their implicit nature

## Decision

We have decided to shift Control Panel UI orchestration from local React-only flows to explicit symphonies (JSON sequences + handlers). This change introduces the following new UI sequences:

### New UI Sequences

1. **control.panel.ui.init**
   - Beats: `ui:config:load → ui:resolver:init → ui:schemas:load → ui:observers:register → ui:ready:notify`
   - Purpose: Initialize Control Panel UI components and services

2. **control.panel.ui.render**
   - Beats: `ui:fields:generate → ui:sections:generate → ui:view:render`
   - Purpose: Generate and render Control Panel UI fields and sections

3. **control.panel.ui.field.change**
   - Beats: `ui:field:prepare → ui:field:dispatch → ui:dirty:set → ui:await:refresh`
   - Purpose: Handle field value changes with forwarding to canvas.component.update

4. **control.panel.ui.field.validate**
   - Beats: `ui:field:validate → ui:errors:merge → ui:view:update`
   - Purpose: Validate field values using SchemaResolverService

5. **control.panel.ui.section.toggle**
   - Beats: `ui:section:toggle → ui:view:update`
   - Purpose: Handle section expand/collapse state changes

### Implementation Approach

The implementation follows a **thin adapter layer** approach:

- **Existing UI logic is preserved**: All existing hooks, services, and components continue to work
- **Sequences wrap existing behavior**: New sequences call into existing hooks/services rather than replacing them
- **Graceful fallback**: If sequences fail to initialize, the UI falls back to the original React-only flows
- **Incremental adoption**: Components can opt into sequence-driven behavior gradually

## Architecture

### File Structure
```
plugins/control-panel/
├── symphonies/ui/
│   ├── ui.symphony.ts          # Handler exports
│   └── ui.stage-crew.ts        # Stage-crew implementations
├── hooks/
│   └── useControlPanelSequences.ts  # Sequence orchestration hook
└── ...existing structure...

public/json-sequences/control-panel/
├── ui.init.json
├── ui.render.json
├── ui.field.change.json
├── ui.field.validate.json
└── ui.section.toggle.json
```

### Integration Points

1. **useControlPanelSequences**: New hook that orchestrates UI sequences
2. **useControlPanelActions**: Modified to use sequence-driven field changes when available
3. **ControlPanel component**: Triggers ui.render sequence on state changes
4. **PropertyFieldRenderer**: Uses sequence-driven validation when available

### Sequence Flow Example

```
User changes field value
    ↓
ui.field.change sequence triggered
    ↓
ui:field:prepare (validate input)
    ↓
ui:field:dispatch (forward to canvas.component.update)
    ↓
ui:dirty:set (mark UI as dirty)
    ↓
ui:await:refresh (wait for canvas update)
    ↓
control.panel.update sequence (existing)
    ↓
UI refreshes with new data
```

## Benefits

1. **Improved Traceability**: UI lifecycles become first-class sequences that can be observed, logged, and debugged
2. **Reduced Coupling**: Explicit sequence definitions make dependencies and effects visible
3. **Better Testability**: Sequence-level unit tests can verify UI flows independently of React components
4. **Architectural Consistency**: UI interactions now align with the symphony pattern used across the platform
5. **Enhanced Observability**: All UI operations can be traced through the conductor's logging and monitoring systems

## Consequences

### Positive
- UI behavior is now observable and replayable through sequences
- Testing becomes more granular and reliable
- Architecture is consistent across the entire platform
- Future UI enhancements can leverage the sequence infrastructure

### Negative
- Slight increase in complexity due to the additional orchestration layer
- Potential performance overhead from sequence execution (mitigated by fallback mechanisms)
- Learning curve for developers unfamiliar with the symphony pattern

### Neutral
- User-visible behavior remains identical
- Existing tests continue to pass without modification
- Migration is incremental and non-breaking

## Implementation Status

- ✅ **Phase 1**: Created UI sequence scaffolding (JSON sequences and handlers)
- ✅ **Phase 2**: Integrated sequences with existing UI components
- ✅ **Phase 3**: Added comprehensive tests and documentation

### Test Coverage
- 17 new unit tests for UI sequence handlers
- All existing Control Panel tests continue to pass (43 tests)
- Sequence integration tests verify proper forwarding to canvas updates

## Future Considerations

1. **Performance Monitoring**: Monitor sequence execution overhead in production
2. **Enhanced Logging**: Consider adding more detailed logging for UI sequence execution
3. **Sequence Composition**: Explore opportunities to compose UI sequences for complex workflows
4. **Developer Tools**: Consider building developer tools to visualize UI sequence execution

## References

- [Issue #33](https://github.com/BPMSoftwareSolutions/renderx-plugins-demo/issues/33)
- [ADR-0014 — JSON-defined default sequences per plugin](./ADR-0014%20—%20JSON-defined%20default%20sequences%20per%20plugin.md)
- [Control Panel Scalable Architecture](../control-panel-scalable-architecture.md)
