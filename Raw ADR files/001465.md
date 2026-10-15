# ADR-004: File Size Enforcement and Modular Refactoring

Status: Accepted  
Date: January 2025  
Deciders: Architecture Team

## Context

During architecture audit, **78 files exceeded the 500-line hard limit**, with some reaching 1748 lines. This violates fundamental project rules:
- Files MUST NOT exceed 500 lines
- Files approaching 400 lines MUST be split immediately
- Each file MUST have a single responsibility
- Classes >200 lines MUST be split into focused helpers

### Critical Violations Found

| File | Lines | Issues |
|------|-------|--------|
| `choice-system-clarity.js` | 1748 | Single massive class, multiple responsibilities |
| `animation-system.js` | 1683 | 6 classes in one file (should be 6 files) |
| `persistence-ui.js` | 1410 | Mixing UI + storage + validation |
| `controls.js` | 1381 | Input handling + UI + state management |
| `wolf-ai-enhanced.js` | 1348 | AI + animation + state + rendering |
| ...and 73 more files | >500 | Various violations |

## Decision

**Enforce strict file size limits with architectural refactoring:**

1. **Immediate Actions (Phase 1 - Critical Files)**
   - Split `animation-system.js` → 6 separate class files
   - Refactor `choice-system-clarity.js` → coordinator + components
   - Break down `persistence-ui.js` → separate concerns
   - Refactor `controls.js` → input mapper + coordinators

2. **Architectural Patterns to Apply**
   - **Manager Pattern**: Business logic (e.g., `ChoiceManager`)
   - **Coordinator Pattern**: Orchestration (e.g., `ChoiceCoordinator`)
   - **ViewModel Pattern**: UI state (e.g., `ChoiceViewModel`)
   - **Renderer Pattern**: Visual only (e.g., `ChoiceRenderer`)
   - **Component Pattern**: Focused UI pieces (e.g., `ChoiceCard`)

3. **File Organization Standards**
   ```
   /feature/
     ├── /manager/          # Business logic (<300 lines each)
     ├── /coordinator/      # Orchestration (<200 lines each)
     ├── /components/       # UI components (<150 lines each)
     ├── /renderer/         # Rendering (<200 lines each)
     └── /utils/            # Helpers (<200 lines each)
   ```

4. **CI Enforcement**
   - Pre-commit hook: Reject files >500 lines
   - Build gate: Fail if any file exceeds limit
   - Lint rule: Warning at 400 lines, error at 500

## Implementation Plan

### Phase 1: Critical Files (Week 1)
1. **Animation System** (1683 → 6 files of ~280 lines each)
   - `AnimationFrame.js` (50 lines)
   - `Animation.js` (170 lines)
   - `AnimationController.js` (140 lines)
   - `ProceduralAnimator.js` (300 lines) → Split to 2 files
   - `CharacterAnimator.js` (400 lines) → Split to 2 files
   - `WolfAnimator.js` (300 lines)

2. **Choice System** (1748 → coordinator pattern)
   - `ChoiceCoordinator.js` (200 lines) - Main orchestration
   - `ChoiceManager.js` (250 lines) - Business logic
   - `ChoiceRenderer.js` (200 lines) - Visual display
   - `/components/` folder:
     - `ChoiceCard.js` (150 lines)
     - `ChoiceComparison.js` (150 lines)
     - `ChoiceTimeline.js` (150 lines)
     - `ChoiceMetrics.js` (150 lines)
   - `/utils/` folder:
     - `choice-utils.js` (150 lines)
     - `choice-metrics.js` (150 lines)

### Phase 2: High-Priority Files (Week 2)
3. **Persistence UI** (1410 → separate concerns)
4. **Controls** (1381 → input mapper pattern)
5. **Wolf AI** (1348 → AI + animation split)

### Phase 3: Remaining Files (Week 3-4)
6. All remaining 73 files >500 lines
7. CI enforcement enabled

## Benefits

✅ **Maintainability**: Each file has single, clear purpose  
✅ **Testability**: Smaller files = focused tests  
✅ **Readability**: Developers can understand files quickly  
✅ **Reusability**: Smaller modules are more composable  
✅ **Scalability**: Easier to extend without bloat  
✅ **Team Productivity**: Less merge conflicts, easier reviews  
✅ **Architecture Compliance**: Enforces coordinator pattern

## Consequences

**Positive:**
- Cleaner architecture with proper separation of concerns
- Easier to navigate codebase
- Better adherence to Single Responsibility Principle
- Improved code review experience
- Easier to identify and fix bugs

**Negative:**
- Requires significant refactoring effort (~2-4 weeks)
- May temporarily break some imports during transition
- Need to update all documentation references
- Team needs training on new file organization

**Neutral:**
- More files to manage (but better organized)
- Need folder structure conventions

## Migration Strategy

For each file being split:

1. **Analyze**: Identify distinct responsibilities/classes
2. **Plan**: Design folder structure and module boundaries
3. **Split**: Extract classes/functions to separate files
4. **Connect**: Use coordinator pattern for orchestration
5. **Test**: Ensure all tests pass
6. **Lint**: Fix ESLint violations
7. **Document**: Update import paths and references

### Example Migration (animation-system.js)

**Before:**
```javascript
// animation-system.js (1683 lines)
export class AnimationFrame { ... }
export class Animation { ... }
export class AnimationController { ... }
export class ProceduralAnimator { ... }
export class CharacterAnimator { ... }
export class WolfAnimator { ... }
```

**After:**
```
/animation/system/
  ├── AnimationFrame.js        (50 lines)
  ├── Animation.js             (170 lines)
  ├── AnimationController.js   (140 lines)
  ├── /procedural/
  │   ├── ProceduralAnimator.js      (280 lines)
  │   └── ProceduralAnimatorUtils.js (150 lines)
  ├── /character/
  │   ├── CharacterAnimator.js       (300 lines)
  │   └── CharacterAnimatorState.js  (150 lines)
  └── /enemy/
      └── WolfAnimator.js            (300 lines)
```

## Validation

**Success Criteria:**
- [ ] Zero files exceed 500 lines
- [ ] All files follow Single Responsibility Principle
- [ ] Coordinator pattern applied consistently
- [ ] All existing tests pass
- [ ] ESLint passes with zero errors
- [ ] CI enforcement enabled and working
- [ ] Documentation updated

## Related

- ADR-001: Remove JavaScript Physics Simulation
- ADR-002: Math.random() Elimination
- ADR-003: State Manager Consolidation
- GUIDELINES/AGENTS.md (Architecture principles)
- User Rule: `<file_length_and_structure>`

## References

- Single Responsibility Principle: https://en.wikipedia.org/wiki/Single-responsibility_principle
- Coordinator Pattern: https://khanlou.com/2015/10/coordinators-redux/
- Manager Pattern: https://www.martinfowler.com/eaaCatalog/serviceLayer.html

---

*This ADR addresses the most critical architectural debt in the codebase and establishes enforcement mechanisms to prevent regression.*
