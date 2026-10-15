---
status: 'accepted'
date: 2025-01-28
decision-makers: [Product Owner, Development Team]
consulted: [Animation Engineers, UX Designers]
informed: [QA Team, Stakeholders]
---

# Comprehensive Animation System for Scroll-Based Effects

## Context and Problem Statement

The current ad-hoc approach to managing scroll-based animations has led to fragile, hard-to-maintain code with complex state management. We have multiple animation types (scroll-scrubbed, scroll-triggered, time-based) that need to coordinate with each other, but the coordination logic is scattered across individual animators. This has resulted in:

- Difficult-to-debug timing issues
- Complex state management with multiple flags per animation
- Hard-to-test animation coordination
- Frequent bugs when animations need to wait for each other
- No clear pattern for adding new animations

We need a systematic approach to managing scroll-based animations that provides clear patterns, easy coordination, and maintainable code.

## Decision Drivers

- Maintainability: Current approach requires tracking many state flags per animation
- Reliability: Animation timing bugs are frequent and hard to reproduce
- Testability: Coordinated animations are difficult to test in isolation
- Extensibility: Adding new animations requires understanding complex state logic
- User Experience: Animations must coordinate smoothly without glitches

## Considered Options

1. Comprehensive Animation System with queuing and coordination
2. Continue with current ad-hoc per-animation state management
3. Use external animation library (GSAP, Framer Motion)

## Decision Outcome

Chosen option: "Comprehensive Animation System with queuing and coordination", because it provides:

- Clear, consistent patterns for all animation types
- Explicit dependency management between animations
- Centralized state management
- Built specifically for our scroll-based use cases
- Easy to test and maintain

### Consequences

- Good, because animations will have consistent, predictable behavior
- Good, because new animations can be added using established patterns
- Good, because animation coordination is explicit and testable
- Good, because reduces cognitive load when debugging animation issues
- Bad, because requires upfront effort to design and implement system
- Bad, because existing animations need to be refactored to use new system

### Confirmation

The animation system will be confirmed working when:

1. All existing animations (sparkler, magic phase, segment 2) work correctly with new system
2. No timing bugs or double-trigger issues
3. Tests can easily mock animation states and coordination
4. New animations can be added with <50 lines of code
5. Animation dependencies are explicit in code (not implicit through timing)

## Pros and Cons of the Options

### Comprehensive Animation System

**Animation System Features:**

- **Animation Types**: Scroll-scrubbed, scroll-triggered, time-based
- **State Management**: Clear lifecycle (idle, triggered, active, completed, reset)
- **Dependency System**: Animations can declare dependencies on other animations
- **Queuing**: Animations wait for dependencies before triggering
- **Bidirectional Behavior**: Define both forward and reverse scroll behaviors
- **Coordination API**: Query state of any animation
- **Testing Support**: Easy mocking and state inspection

- Good, because provides consistent patterns across all animations
- Good, because makes animation dependencies explicit
- Good, because centralizes state management logic
- Good, because easier to test animation coordination
- Good, because reduces code duplication
- Neutral, because requires learning new API patterns
- Bad, because requires refactoring existing code
- Bad, because adds abstraction layer

### Continue Current Approach

Continue managing animation state individually in each animator class.

- Good, because no refactoring needed
- Good, because no new concepts to learn
- Bad, because state management is complex and error-prone
- Bad, because coordination logic is implicit and scattered
- Bad, because difficult to test interactions
- Bad, because hard to add new animations
- Bad, because frequent timing bugs

### External Animation Library

Use GSAP ScrollTrigger or Framer Motion for scroll-based animations.

- Good, because mature, well-tested libraries
- Good, because comprehensive documentation and examples
- Good, because handles edge cases
- Neutral, because adds external dependency
- Bad, because may not fit exact use cases
- Bad, because learning curve for team
- Bad, because less control over behavior
- Bad, because bundle size impact

## More Information

### Implementation Phases

1. **Phase 1: Core System** (Week 1)
   - Define animation base class/interface
   - Implement state management
   - Create dependency resolution system
   - Build queuing mechanism

2. **Phase 2: Migration** (Week 2)
   - Refactor sparkler animator to use new system
   - Refactor magic phase animator to use new system
   - Refactor segment 2 animator to use new system
   - Update tests

3. **Phase 3: Validation** (Week 3)
   - End-to-end testing of all animations
   - Performance testing
   - Bug fixes and refinements

### Success Criteria

- Zero animation timing bugs after migration
- Test coverage >90% for animation system
- New animation can be added in <1 hour
- Animation dependencies are self-documenting in code

### Related Decisions

- 026.03-BIZ-MAGIC-PHASE-ANIMATION: Will use animation system
- Future animation features will build on this system

### Reassessment Criteria

Review this decision if:

- Animation system becomes too complex (>500 lines)
- Performance issues emerge
- Team finds external library better fits needs
- More than 3 animations need exemptions from system
