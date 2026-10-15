# ADR-001: Consolidated RequestAnimationFrame Loop

## Status
Proposed

## Date
2025-12-07

## Context

The Starfield visualization currently uses **multiple separate `requestAnimationFrame` (RAF) loops**:

1. **Main animation loop** (`animate.ts`) - Handles star rendering, sun drawing, particle effects, connections
2. **Camera animation loop** (`useCosmicNavigation.ts` or similar) - Handles smooth camera lerp/transitions when zooming to suns

### Current Architecture Problems

1. **Race conditions**: Camera state updated in one RAF loop may not be visible to the main animation loop until the next frame, causing 1-frame lag in zoom effects.

2. **Synchronization issues**: We had to add `cameraRef` as a workaround to share camera state synchronously between loops. This is a symptom of architectural debt.

3. **Performance overhead**: Multiple RAF callbacks have scheduling overhead. Each RAF callback is queued separately by the browser.

4. **Inconsistent timing**: `deltaTime` calculations may drift between loops if they're not perfectly synchronized.

5. **Debugging difficulty**: Animation bugs require tracing through multiple loops to understand state flow.

### Evidence of Problems

The zoom-to-sun feature was broken because:
- Camera animation ran in a separate RAF updating React state (async)
- Main animation read camera from props (potentially stale)
- Fix required adding `cameraRef` for synchronous access

## Decision

**Merge all animation into a single RAF loop.**

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Single RAF Loop                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Camera     │  │   Physics   │  │  Rendering  │         │
│  │  Update     │→ │   Update    │→ │   Pass      │         │
│  │  (lerp)     │  │  (stars,    │  │  (draw all) │         │
│  │             │  │   suns)     │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Plan

1. **Create animation orchestrator** (`animationOrchestrator.ts`):
   ```typescript
   interface AnimationPhase {
     name: string;
     update: (deltaTime: number, state: AnimationState) => void;
     render?: (ctx: CanvasRenderingContext2D, state: AnimationState) => void;
   }

   const phases: AnimationPhase[] = [
     { name: 'camera', update: updateCamera },
     { name: 'physics', update: updatePhysics },
     { name: 'particles', update: updateParticles },
     { name: 'render', render: renderAll }
   ];
   ```

2. **Move camera lerp into main loop**:
   - Remove separate camera RAF from `useCosmicNavigation`
   - Add camera phase at start of main animation
   - Camera updates happen before rendering in same frame

3. **Consolidate state management**:
   - Single source of truth for all animation state
   - No more refs vs props confusion
   - Clear data flow: update → render

4. **Add phase timing** (optional, for performance monitoring):
   ```typescript
   const phaseTiming = {
     camera: 0,
     physics: 0,
     render: 0
   };
   ```

## Consequences

### Positive

- **No synchronization bugs**: All updates happen in deterministic order
- **Simpler debugging**: Single call stack for entire frame
- **Better performance**: Single RAF callback, better CPU cache locality
- **Cleaner architecture**: Remove `cameraRef` workaround
- **Consistent deltaTime**: Single time source for all calculations

### Negative

- **Larger single function**: Main loop becomes more complex (mitigate with phases)
- **Migration effort**: Need to refactor camera animation hooks
- **Testing changes**: Unit tests for camera need updating

### Risks

- **Breaking changes**: Camera animation behavior might change slightly during migration
- **Performance regression**: If done poorly, could increase frame time (mitigate with profiling)

## Alternatives Considered

### 1. Keep separate loops with message passing
- Use `postMessage` or shared state for synchronization
- Rejected: Adds complexity without solving root cause

### 2. Use Web Workers for physics
- Move physics calculations to worker thread
- Rejected: Overkill for current complexity; adds serialization overhead

### 3. SharedArrayBuffer between loops
- Share camera state via typed arrays
- Rejected: Browser support issues; security restrictions

## Implementation Phases

### Phase 1: Preparation
- [ ] Audit all RAF usages in codebase
- [ ] Document current data flow
- [ ] Add performance baseline measurements

### Phase 2: Consolidation
- [ ] Create `animationOrchestrator.ts`
- [ ] Move camera lerp into main loop
- [ ] Remove separate camera RAF
- [ ] Update `useCosmicNavigation` hook

### Phase 3: Cleanup
- [ ] Remove `cameraRef` workaround
- [ ] Simplify `AnimationProps` interface
- [ ] Update tests

### Phase 4: Optimization
- [ ] Add phase timing metrics
- [ ] Profile and optimize if needed
- [ ] Document new architecture

## References

- Current animate.ts: ~500 lines of main loop logic
- Camera lerp location: `cosmos/camera.ts` + hook usage
- Related fix: Commit `7d9b4ba` (added cameraRef workaround)
