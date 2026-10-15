# ADR-007: Theme-Based Rendering via Strategy Pattern

## Status

**Accepted** - Implemented 2025-12-05

## Context

The game initially supported color-only themes (ADR-006), but we needed to extend theming to support **fundamentally different visual representations** while maintaining a single codebase. Specifically, we wanted to create an "underwater" theme that renders:

- Spaceship → Submarine
- Asteroids → Jellyfish
- Laser bullets → Torpedoes
- Powerups → Ocean creatures (octopus, starfish)
- Starfield → Plankton particles

### Challenges

1. **Code Duplication Risk**: Naively duplicating game logic for each theme would double/triple the codebase size
2. **Maintenance Burden**: Bug fixes and feature additions would need to be applied to multiple versions
3. **Type Safety**: Custom renderers need compile-time validation
4. **Performance**: Theme switching must be instant (no loading/restart)
5. **Backward Compatibility**: Existing themes (Default, Monochrome) must continue working unchanged

### Key Insight

**Entity data structures are theme-agnostic**. An `Asteroid` is just position, velocity, size, and rotation data. Whether it's rendered as a rocky asteroid or a pulsing jellyfish is purely a visual concern.

## Decision

Implement a **Render Strategy Pattern** that separates entity data from visual representation:

1. **Extract Default Renderers**: Refactor existing rendering code into reusable single-entity functions
2. **Define Renderer Types**: Create type-safe interfaces for custom renderers
3. **Extend Theme System**: Add optional `renderers` field to `Theme` type
4. **Update Render Manager**: Check for custom renderers, fall back to defaults
5. **Zero Duplication**: Reuse ALL game logic (physics, collision, spawning, scoring)

### Architecture

```typescript
// Theme definition with custom renderers
type Theme = {
  id: ThemeId;
  colors: ColorPalette;
  renderers?: {
    player?: EntityRenderer<Player>;
    obstacle?: EntityRenderer<Asteroid>;
    bullet?: EntityRenderer<Bullet>;
    powerups?: {
      shield?: EntityRenderer<ActivePowerup>;
      doubleBlaster?: EntityRenderer<ActivePowerup>;
    };
  };
};

// Render manager uses strategy pattern
function renderAll(ctx: CanvasRenderingContext2D) {
  const theme = getCurrentTheme();
  const obstacles = entityState.getMutableObstacles();

  if (theme.renderers?.obstacle) {
    // Custom renderer (e.g., jellyfish)
    obstacles.forEach((o) => theme.renderers.obstacle!(ctx, o));
  } else {
    // Default renderer (asteroid)
    obstacles.forEach((o) => drawAsteroid(ctx, o));
  }
}
```

### Implementation Details

**Type System** (`src/types/index.ts`):

- `EntityRenderer<T>` - Generic renderer type
- `ThemeRenderers` - Complete strategy set
- `ActivePowerup` - Shared powerup type

**Entity Modules** (backward compatible):

- `drawAsteroid(ctx, asteroid)` - Single-entity renderer (new)
- `drawObstacles(ctx)` - Loops and calls drawAsteroid (refactored)
- Same pattern for bullets, powerups

**Render Manager** (`src/systems/renderManager.ts`):

- Checks `theme.renderers` for custom functions
- Falls back to defaults if not provided
- Type-safe with comprehensive JSDoc

## Rationale

### Why Strategy Pattern over Alternatives?

#### Alternative 1: Conditional Logic in Renderers ❌

```typescript
function drawAsteroid(ctx, asteroid, theme) {
  if (theme.id === 'underwater') {
    // Draw jellyfish
  } else if (theme.id === 'space') {
    // Draw asteroid
  } else if (theme.id === 'cyberpunk') {
    // Draw data fragment
  }
}
```

**Rejected because**:

- Violates Open/Closed Principle (modify existing code for new themes)
- Creates bloated functions with complex branching
- All theme logic coupled in one place
- Hard to test individual renderers

#### Alternative 2: Separate Game Loops per Theme ❌

```typescript
if (theme.id === 'underwater') {
  underwaterGameLoop();
} else {
  spaceGameLoop();
}
```

**Rejected because**:

- Duplicates all game logic (physics, collision, spawning)
- Bug fixes must be applied to multiple loops
- Massive codebase growth (3 themes = 3x code)
- Testing nightmare

#### Alternative 3: Inheritance Hierarchy ❌

```typescript
class SpaceRenderer extends BaseRenderer {}
class UnderwaterRenderer extends BaseRenderer {}
```

**Rejected because**:

- JavaScript/TypeScript doesn't favor deep inheritance
- Inflexible (can't mix renderer types)
- More boilerplate than functional approach
- Harder to tree-shake unused code

### Why Strategy Pattern Works ✅

1. **Separation of Concerns**: Data (Asteroid) vs Presentation (drawJellyfish)
2. **Open/Closed Principle**: Open for extension (new themes), closed for modification (core logic)
3. **Composition over Inheritance**: Mix and match renderers freely
4. **Type Safety**: TypeScript enforces `EntityRenderer<T>` signatures
5. **Zero Overhead**: Direct function calls, no runtime penalty
6. **Testability**: Mock renderers easily, test strategies independently

## Consequences

### Positive ✅

1. **Zero Code Duplication**
   - Game logic: 100% reused (physics, collision, spawning, scoring)
   - Entity data: 100% reused (Asteroid, Bullet, Player types)
   - UI/HUD: 100% reused (scores, timers, overlays)
   - State management: 100% reused (reactive state, event bus)

2. **Infinite Themes Without Core Changes**
   - New themes are just renderer functions
   - No modifications to game loop, physics, or collision
   - Add 10 themes = +10 renderer files, 0 core changes

3. **Type Safety**
   - Compiler enforces `EntityRenderer<Asteroid>` signature
   - Custom renderers get autocomplete for entity properties
   - Impossible to pass wrong entity type

4. **Performance**
   - Direct function calls (no polymorphic dispatch)
   - Theme switching is instant (just swap function references)
   - No sprite loading or asset management needed

5. **Backward Compatibility**
   - Existing themes work unchanged (no `renderers` field = use defaults)
   - Gradual migration (can add custom renderers one at a time)
   - Old code continues to work: `drawObstacles(ctx)` still valid

6. **Developer Experience**
   - Clear separation: "What data?" (entities) vs "How to draw?" (renderers)
   - Easy to add new themes (just write renderer functions)
   - Visual changes don't touch game logic
   - Comprehensive JSDoc examples

### Negative ⚠️

1. **Slight Complexity Increase**
   - Render manager now has conditional logic (check for custom renderer)
   - Developers must understand strategy pattern
   - **Mitigation**: Comprehensive documentation, clear examples

2. **Indirection for Simple Cases**
   - Default rendering now goes through `drawAsteroid()` instead of inline
   - **Impact**: Negligible (function call overhead ~1ns)
   - **Benefit**: Consistent API for themes to override

3. **Potential for Renderer Duplication**
   - Theme authors might copy-paste similar renderers
   - **Mitigation**: Provide shared utility functions, clear examples

4. **Testing Complexity**
   - Need to test both default and custom renderer paths
   - **Mitigation**: Render manager tests cover both paths

### Neutral 🔶

1. **No Entity Renaming**
   - `Asteroid` stays `Asteroid` (not renamed to `Obstacle`)
   - **Rationale**: Internal implementation detail, themes provide visual metaphor
   - **Trade-off**: Slight semantic mismatch for underwater theme (jellyfish is an Asteroid)

2. **Player Renderer Accesses Global State**
   - `drawPlayer(ctx)` reads from `playerState.player` and `powerUps`
   - **Rationale**: Shield, position, etc. are global concerns
   - **Alternative**: Custom renderers can also access globals if needed

## Alternatives Considered

### 1. Sprite Sheet System

Replace vector graphics with image-based sprites for each theme.

**Pros**:

- Artists can create detailed visuals
- Potentially higher visual fidelity

**Cons**:

- Large asset downloads (multiple sprite sheets)
- Loading time on theme switch
- Memory overhead (multiple sheets in memory)
- Lost resolution independence
- More complex build pipeline

**Decision**: Rejected for Phase 1, may revisit for Phase 3 (asset-based themes)

### 2. Canvas Layers

Use multiple canvases, one per theme, composite them.

**Pros**:

- Complete visual isolation
- Could pre-render themes

**Cons**:

- Memory intensive (multiple canvases)
- Compositing performance cost
- More complex render pipeline
- Harder to manage z-ordering

**Decision**: Rejected - unnecessary complexity for pure visual changes

### 3. WebGL Shaders

Use fragment shaders to transform visuals.

**Pros**:

- GPU-accelerated
- Powerful visual effects
- Could support real-time theme interpolation

**Cons**:

- Complete rewrite of render pipeline
- Steeper learning curve
- Browser compatibility concerns
- Overkill for 2D vector graphics

**Decision**: Rejected - not appropriate for this game's style

## Related

### ADRs

- [ADR-006: Theme System Architecture](./ADR-006-theme-system.md) - Color-only themes (Phase 1)
- This ADR extends ADR-006 with rendering strategies (Phase 2)

### Documentation

- [Underwater Theme Specification](../../UNDERWATER_THEME_SPEC.md) - Detailed implementation guide
- [Phase 1 Complete](../../PHASE_1_COMPLETE.md) - Implementation summary
- [Developer Guide - Theme System](../../DEVELOPER_GUIDE.md#theme-system)

### Code References

- `src/types/index.ts` - `EntityRenderer<T>`, `ThemeRenderers` types
- `src/systems/renderManager.ts` - Strategy pattern implementation
- `src/entities/asteroid.ts` - `drawAsteroid()` extracted renderer
- `src/entities/bullet.ts` - `drawBullet()` extracted renderer
- `src/entities/powerup.ts` - `drawShieldPowerup()`, `drawDoubleBlasterPowerup()`

### Future Work

- Phase 2: Implement Underwater Theme renderers
- Phase 3: Asset-based themes (sprite sheets, custom fonts)
- Phase 4: Background particle systems (plankton, stars, etc.)

## Implementation Notes

### Code Metrics

- Files Modified: 5
- Lines Added: ~519
- Lines Removed: ~246
- Net Change: +273 lines
- Code Duplication: **ZERO**

### Quality Gates

- ✅ TypeScript: No errors
- ✅ Tests: 152/152 passing (94.23% coverage)
- ✅ ESLint: No errors
- ✅ Backward Compatible: All existing code works unchanged

### Migration Path

1. ✅ **Phase 1** (Complete): Refactor to strategy pattern
2. 🔜 **Phase 2** (Next): Implement underwater theme renderers
3. 🔜 **Phase 3** (Future): Add background/particle system strategies
4. 🔜 **Phase 4** (Future): Asset-based theme support

## Conclusion

The **Render Strategy Pattern** achieves our goal of supporting fundamentally different visual themes with **zero code duplication**. By separating entity data from visual representation, we maintain a single codebase while enabling infinite visual variations.

The pattern is **extensible** (new themes are just renderer functions), **type-safe** (compiler-enforced), **performant** (direct function calls), and **backward compatible** (existing code works unchanged).

This architectural decision enables the underwater theme and any future themes (cyberpunk, medieval, etc.) without ever touching game logic again. Visual creativity is now decoupled from game mechanics.

**Status**: Production-ready, implemented 2025-12-05
