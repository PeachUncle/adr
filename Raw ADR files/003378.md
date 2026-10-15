# ADR-002: Flow System Over Wizard Pattern

**Status**: Accepted and Implemented  
**Date**: October 2025  
**Decision Makers**: Development Team  
**Related Documents**: 
- `docs/archive/WIZARD_TO_FLOW_MIGRATION.md`
- `docs/archive/WIZARD_FLOW_FEATURE_PARITY.md`

---

## Context

Protogen required a system for multi-step guided workflows to handle complex user interactions such as scene creation, deck management, and other CRUD operations. The initial implementation used a traditional Wizard pattern, but limitations became apparent as requirements grew more sophisticated.

### Problems with Traditional Wizard Pattern

1. **Limited Flexibility**: Linear step progression without conditional logic
2. **No Branching**: Unable to create different paths based on user choices
3. **Tight Coupling**: Wizard-specific components not reusable in other contexts
4. **No Template System**: Duplication of similar workflows across the application
5. **Single Use Case**: Optimized only for form-based workflows

### Requirements

- Support for multi-step form workflows (existing wizard functionality)
- Conditional step visibility based on collected data
- Multi-path branching for different user choices
- Mixed content types (forms, navigation, content display)
- Reusable flow templates
- Integration with Dialog System for display
- Unified architecture for all guided experiences

---

## Decision

**We will implement a Flow System that replaces the Wizard pattern**, with the wizard functionality preserved as a "Form Flow" sub-module.

### Flow System Architecture

```
Flow System
├── Core Flow Engine (Template & Instance Management)
├── Form Flow Sub-Module (Wizard Replacement)
│   ├── FormStep, SelectionStep, ReviewStep
│   ├── Validation Service
│   └── Form-specific hooks
├── Navigation Flow (Future)
└── Content Flow (Future)
```

### Key Design Principles

1. **Template-Based**: Flows are registered as reusable templates
2. **Instance Management**: Multiple flow instances can run simultaneously
3. **Step Types**: Explicit step types (form, selection, review, navigation, content)
4. **Conditional Logic**: Steps can have conditions for visibility
5. **Branching Support**: Multiple paths from any step based on conditions
6. **Event-Driven**: Flow lifecycle events for integration with other systems
7. **Dialog Integration**: Seamless rendering in modal, drawer, or fullscreen dialogs

---

## Consequences

### Positive

✅ **Backwards Compatible**: Wizard functionality preserved in Form Flow sub-module  
✅ **More Powerful**: Conditional steps, branching, and mixed content types  
✅ **Reusable**: Template system reduces code duplication  
✅ **Extensible**: New flow types can be added without changing core  
✅ **Unified**: Single system for all guided experiences  
✅ **Production Proven**: Successfully used in Scene Management dialogs  
✅ **Better DX**: Clearer API with explicit step configuration

### Negative

⚠️ **Migration Required**: Existing wizard implementations need updating  
⚠️ **More Complex**: Additional configuration (order, step_type) required  
⚠️ **Learning Curve**: Team needs to understand new architecture

### Neutral

ℹ️ **API Changes**: Import paths changed from `wizard` to `flow` and `flow/form`  
ℹ️ **Type Renames**: `WizardConfig` → `FormFlow`, `WizardStep` → `FlowStep`  
ℹ️ **Registration Required**: Flows must be registered before use

---

## Implementation Status

### Completed

- ✅ Core Flow System engine with template management
- ✅ Form Flow sub-module with all wizard capabilities
- ✅ Validation service integrated
- ✅ Step components (FormStep, SelectionStep, ReviewStep) migrated
- ✅ Dialog System integration
- ✅ Production usage in Scene Management (Create/Edit/Manage dialogs)
- ✅ Migration guide documentation

### Deferred

- ⏳ Navigation Flow sub-module
- ⏳ Content Flow sub-module  
- ⏳ Advanced flow analytics
- ⏳ Flow export/import capabilities

---

## Alternatives Considered

### Alternative 1: Enhance Wizard Pattern

**Approach**: Add conditional logic and branching to existing Wizard system

**Rejected Because**:
- Would create a complex, monolithic wizard system
- Difficult to extend for non-form use cases
- Naming would become confusing ("wizard" for navigation flows)

### Alternative 2: Multiple Independent Systems

**Approach**: Separate systems for forms, navigation, content

**Rejected Because**:
- Code duplication across systems
- Inconsistent user experience
- Harder to maintain and evolve
- Missed opportunity for unified architecture

### Alternative 3: Third-Party Flow Library

**Approach**: Integrate existing flow/wizard library

**Rejected Because**:
- None met our specific requirements
- Integration overhead with existing systems
- Less control over future development
- Added dependency and bundle size

---

## References

- **Migration Guide**: `docs/archive/WIZARD_TO_FLOW_MIGRATION.md`
- **Feature Parity**: `docs/archive/WIZARD_FLOW_FEATURE_PARITY.md`
- **Implementation**: `shared/src/systems/flow/`
- **Production Example**: `portal/src/features/scene-management/`

---

## Notes

The Flow System has proven highly successful in production, powering the Scene Management interface with a 4-step creation flow, full-screen management dialog, and edit flow. The decision to preserve wizard functionality as a sub-module made migration straightforward while enabling future enhancements.

**Next Evolution**: Consider adding Navigation Flow and Content Flow sub-modules for guided tours, onboarding, and content presentation flows.

