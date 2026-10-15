# ADR-004: State Machine Refactoring Strategy

**Status:** Accepted
**Date:** 2025-10-13
**Deciders:** Development Team
**Related:** Style Guide Audit M1, S2 Violations

---

## Context

The style guide audit identified scattered state management across multiple components:

1. **AnimationCard**: 7 separate useState calls managing playback, UI, and configuration state
2. **App**: 5 state variables + 1 unused variable managing navigation, drawer, and refs
3. **TimerEffectsPillCountdownStrong**: 47-line useEffect mixing countdown, color transitions, and animations

**Problems:**
- No clear state relationships or transition rules
- Difficult to test state changes in isolation
- Cannot guarantee state consistency
- Hard to reason about valid state combinations
- Significant maintenance burden

---

## Decision

We will **progressively refactor scattered state into typed state machines** using React's useReducer hook and custom hooks for effect composition.

### Approach

#### 1. State Machines (useReducer)
For complex UI state with clear transitions:
- **AnimationCard**: idle → visible → playing state machine
- **App**: navigation + drawer state machine with atomic transitions

#### 2. Custom Hook Composition
For complex effects with multiple concerns:
- **Timer Components**: Separate hooks for countdown, color transitions, and snap animations

### Rationale

**Why useReducer over useState?**
- Enforces valid state transitions via reducer logic
- Centralizes state update logic (easier to test)
- TypeScript discriminated unions provide type safety
- Explicit actions make state changes auditable

**Why Custom Hooks over Monolithic useEffect?**
- Single Responsibility Principle (each hook one concern)
- Easier to test with focused test cases
- Reusable across similar components
- Simpler cleanup logic per hook

---

## Implementation Strategy

### Phase 1: Design (COMPLETE ✅)
- [x] Create state machine designs with state diagrams
- [x] Define TypeScript interfaces for state and actions
- [x] Document state transitions and invariants
- [x] Create comprehensive test plans
- [x] Write implementation guides

**Artifacts:**
- `docs/state-machines/animationcard-state-machine.md`
- `docs/state-machines/app-state-machine.md`
- `docs/state-machines/timer-hooks-design.md`

### Phase 2: Implementation (DEFERRED)
To be tackled in dedicated sprint with following order:

1. **Timer Hooks** (Lowest Risk)
   - Create useCountdownTimer, useColorTransition, useSnapAnimation
   - Add tests with vi.useFakeTimers()
   - Refactor TimerEffectsPillCountdownStrong
   - Verify no visual regressions

2. **AnimationCard State Machine** (Medium Risk)
   - Create useAnimationCardState hook
   - Add comprehensive tests
   - Refactor AnimationCard component
   - Run full regression suite

3. **App State Machine** (Highest Risk)
   - Create useAppStateMachine hook
   - Update App.tsx navigation
   - Update custom hooks (useGroupInitialization)
   - Extensive integration testing

### Phase 3: Validation
- Full test suite passes (105+ tests)
- Type-check passes (0 errors)
- Visual regression tests pass
- Performance profiling shows no degradation
- Code review approval

---

## Consequences

### Positive

✅ **Type Safety**: Discriminated unions prevent invalid state combinations
✅ **Testability**: Reducers are pure functions, easy to unit test
✅ **Maintainability**: Clear state transitions and single responsibility hooks
✅ **Debuggability**: Explicit actions make state changes auditable
✅ **Reusability**: Custom hooks can be used across similar components
✅ **Documentation**: State diagrams provide clear mental models

### Negative

⚠️ **Learning Curve**: Team needs to understand useReducer patterns
⚠️ **Initial Overhead**: More boilerplate than simple useState
⚠️ **Migration Risk**: Refactoring heavily-used components requires careful testing

### Mitigation

- Comprehensive design documentation (already created)
- Implementation guides with examples
- Test-first approach with coverage goals
- Incremental rollout (timer → AnimationCard → App)
- Pair programming for complex refactoring

---

## Alternatives Considered

### Alternative 1: Keep useState, Add Helper Functions
**Rejected Reason:** Doesn't solve state consistency issues, still scattered

### Alternative 2: Use XState Library
**Rejected Reason:** Heavy dependency for simple state machines, overkill for our needs

### Alternative 3: Context + useReducer
**Rejected Reason:** No need for global state, component-level is sufficient

### Alternative 4: Zustand/Redux
**Rejected Reason:** Overkill for component-level state, adds unnecessary complexity

---

## Design Principles

### 1. Explicit State Transitions
```typescript
// Bad: Implicit state changes
setIsVisible(true)
setReplayKey(prev => prev + 1)

// Good: Explicit actions
dispatch({ type: 'REPLAY' })
```

### 2. Type-Safe States
```typescript
// Bad: Separate booleans (4 possible combinations, only 3 valid)
const [isVisible, setIsVisible] = useState(false)
const [isPlaying, setIsPlaying] = useState(false)

// Good: Discriminated union (only valid states possible)
type State =
  | { status: 'idle' }
  | { status: 'visible' }
  | { status: 'playing' }
```

### 3. Single Responsibility Hooks
```typescript
// Bad: One hook doing everything
useEffect(() => {
  // 47 lines of countdown + color + animation logic
}, [many, dependencies])

// Good: Composed hooks with single concerns
const timer = useCountdownTimer({ ... })
const { color } = useColorTransition({ ... })
const { scale } = useSnapAnimation({ ... })
```

---

## Testing Strategy

### Unit Tests
- Test reducers as pure functions
- Test custom hooks with renderHook
- Use vi.useFakeTimers() for time-based logic
- Verify state transitions and invariants

### Integration Tests
- Test component behavior with state machine
- Verify user interactions trigger correct actions
- Test edge cases (rapid clicks, animations interrupting, etc.)

### Visual Regression Tests
- Playwright screenshots before/after refactoring
- Verify animations still look correct
- Check mobile drawer behavior

---

## Success Metrics

- ✅ Test coverage maintained or improved (105+ tests)
- ✅ Zero TypeScript errors
- ✅ No visual regressions
- ✅ Reduced cyclomatic complexity (measurable via ESLint)
- ✅ Improved maintainability (team feedback)
- ✅ Performance unchanged (no slowdown)

---

## References

- [React useReducer Documentation](https://react.dev/reference/react/useReducer)
- [TypeScript Discriminated Unions](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes-func.html#discriminated-unions)
- [Kent C. Dodds: State Machines](https://kentcdodds.com/blog/implementing-a-simple-state-machine-library-in-javascript)
- [React Testing Library: Testing Hooks](https://react-hooks-testing-library.com/)

---

## Related ADRs

- ADR-001: Framer Motion Selection (animation state management)
- ADR-003: Test Infrastructure (testing strategy for refactoring)

---

## Revision History

- **2025-10-13**: Initial version - Design phase complete
- **Future**: Implementation phase updates
- **Future**: Validation and rollout notes

---

*This ADR documents our approach to state machine refactoring. Implementation will be tracked in separate PRs with detailed testing.*
