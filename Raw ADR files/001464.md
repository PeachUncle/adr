# ADR-001: Remove JavaScript Physics Simulation

**Status**: Accepted  
**Date**: January 2025  
**Deciders**: Architecture Team  

## Context

During the WASM-JS conflict audit, we discovered that both JavaScript and WASM were running physics independently, causing:

- Desynchronization between WASM and JS state
- Non-deterministic behavior in multiplayer
- Performance overhead (double calculation)
- Impossible to debug (which system owns truth?)
- Violation of WASM-first architecture principles

### Files Affected
- `public/src/animation/player/physics/index.js` - Full JS physics solver
- `public/src/gameentity/wolf/behavior.js` - Fallback JS physics
- `public/src/wasm/initializer/fallback-exports.js` - Math.random() usage

## Decision

Remove all JavaScript physics simulation. WASM PhysicsManager is the single source of truth.

### Changes Made

1. **PlayerPhysicsAnimator Refactored**
   - Removed `MinimalPhysicsSolver` class (175 lines)
   - Replaced with WASM-first visual interpolator
   - Reads position/velocity from WASM only
   - Handles smooth visual transitions

2. **Wolf Behavior Fixed**
   - Removed fallback JS physics (lines 68-81)
   - Reads position from WASM only
   - Fails fast if WASM unavailable

3. **Fallback Exports Cleaned**
   - Removed Math.random() usage
   - Deterministic fallback behavior
   - No random movement in fallback mode

## Consequences

### Positive
- ✅ No desyncs between WASM and JS
- ✅ Deterministic simulation
- ✅ Clear ownership (WASM owns physics)
- ✅ Better performance (single calculation)
- ✅ Easier debugging
- ✅ WASM-first compliance

### Negative
- ❌ Must rebuild WASM for physics changes
- ❌ JavaScript can't modify physics directly
- ❌ Requires WASM module for physics

### Neutral
- JavaScript handles only visual interpolation
- Physics debugging must be done in WASM
- Network sync relies on WASM determinism

## Implementation Details

### Before (Wrong)
```javascript
// PlayerPhysicsAnimator - Full physics simulation
class MinimalPhysicsSolver {
  step(dt, context) {
    // Full physics simulation duplicating WASM
    this.pd2D(s.leftLeg.foot, this.key('ll.foot'), footTargets.left, dt);
    this.applyGroundContact(s.leftLeg);
    this.solveLegChain(s.leftLeg, -1);
  }
}

// Wolf behavior - Fallback JS physics
this.velocity.x += this.acceleration.x * deltaTime;
this.position.x += this.velocity.x * deltaTime;
```

### After (Correct)
```javascript
// PlayerPhysicsAnimator - Visual interpolation only
update(deltaTime, context) {
  // Read physics state from WASM
  const wasmPosition = {
    x: this.wasmModule.get_physics_player_x?.() ?? 0,
    y: this.wasmModule.get_physics_player_y?.() ?? 0
  };
  
  // Update target skeleton based on WASM physics
  this.updateSkeletonFromPhysics(wasmPosition, wasmVelocity, context);
  
  // Smooth visual interpolation
  this.interpolateSkeleton(deltaTime);
}

// Wolf behavior - WASM only
if (!this.wasmModule) {
  console.error('Wolf requires WASM module for physics');
  return;
}

this.position.x = this.wasmModule.get_enemy_x(wasmIndex);
this.position.y = this.wasmModule.get_enemy_y(wasmIndex);
```

## Validation

- ✅ WASM build succeeds (195.9 KB)
- ✅ All tests pass
- ✅ No linter errors
- ✅ Physics demo works correctly
- ✅ Multiplayer determinism restored

## Related ADRs

- [ADR-002: Math.random() Elimination](./ADR-002-MATH-RANDOM-ELIMINATION.md)
- [ADR-003: State Manager Consolidation](./ADR-003-STATE-MANAGER-CONSOLIDATION.md)

## References

- See `GUIDELINES/UTILS/MIGRATION_GUIDE.md` for migration steps
- See `GUIDELINES/AGENTS.md` for architecture rules
- [AGENTS.md](../AGENTS.md) - WASM-first architecture
