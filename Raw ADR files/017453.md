# ADR-009: Medieval Theme Obstacle Fragmentation Logic

## Status

**Accepted** - 2025-12-06

## Context

The Medieval Fantasy Theme (ADR-008) introduces **type-based obstacle rendering** where obstacles of different sizes represent different entities:

- **Large obstacles (radius ≥ 30)**: Wyverns (hostile dragons)
- **Medium obstacles (radius ≥ 15)**: Giant Bats
- **Small obstacles (radius < 15)**: Magical Crystals

This creates a **thematic challenge** with the existing fragmentation system.

### Current Fragmentation Behavior

When an asteroid is destroyed in the space/underwater themes:

1. If size level > 0, spawn 2-3 smaller fragments
2. Fragments inherit parent velocity + random angle offset
3. Fragments have same visual type as parent (just smaller)
4. Process repeats until smallest size reached

**Example (Space Theme)**:

```
Large Asteroid → 2-3 Medium Asteroids → 2-3 Small Asteroids → 0 fragments
```

### The Problem

With type-based rendering, **visual type changes with size**:

```
Large obstacle (wyvern) → Medium obstacle (bat) → Small obstacle (crystal)
```

**Question**: Does it make thematic sense for a destroyed wyvern to spawn bats, and destroyed bats to spawn crystals?

**Initial concern**: This feels arbitrary unless there's a narrative explanation.

## Decision

Implement a **Magical Transformation Chain** where obstacle fragmentation follows a thematic progression:

```
Wyvern (cursed creature) → Bats (released from curse) → Crystals (residual magic) → Sparkles (no fragments)
```

### Narrative Justification

The game world operates under these magical rules:

1. **Wyverns are cursed creatures** - Evil sorcerer's minions, magically bound servants
2. **Destroying a wyvern breaks the curse** - Releases 2-3 giant bats that were trapped inside
3. **Bats are semi-corporeal magical constructs** - Not fully physical, partially made of arcane energy
4. **Destroying a bat shatters its arcane form** - Releases 2-3 pure magical crystals (concentrated energy)
5. **Crystals are concentrated magic shards** - When destroyed, they explode into sparkles/dust (no further fragments)

### Implementation Approach

**Option 1: Size-Based Implicit Typing (Chosen)**

Use existing size-based logic, let renderer determine type:

```typescript
// Existing fragmentation logic (unchanged)
function fragmentAsteroid(asteroid: Asteroid): Asteroid[] {
  if (asteroid.sizeLevel === 0) return []; // Smallest size, no fragments

  const fragments: Asteroid[] = [];
  const fragmentCount = 2 + Math.floor(Math.random() * 2); // 2-3 fragments

  for (let i = 0; i < fragmentCount; i++) {
    fragments.push({
      ...createSmallerAsteroid(asteroid),
      sizeLevel: asteroid.sizeLevel - 1, // Smaller size level
    });
  }

  return fragments;
}

// Renderer determines type based on size (in medieval theme only)
function getObstacleTypeBySize(radius: number): MedievalObstacleType {
  if (radius >= 30) return 'wyvern'; // Large
  if (radius >= 15) return 'bat'; // Medium
  return 'crystal'; // Small
}
```

**Benefits**:

- ✅ **Zero changes to core game logic** - Fragmentation system untouched
- ✅ **Theme-agnostic data layer** - `Asteroid` doesn't know it's a wyvern/bat/crystal
- ✅ **Automatic progression** - Size decrease automatically changes visual type
- ✅ **Backward compatible** - Space/underwater themes unaffected

**Trade-off**:

- ⚠️ Type transitions are implicit (size determines type, not explicit property)
- **Mitigation**: Document clearly in renderer JSDoc, narrative explains progression

**Option 2: Explicit `debrisType` Property (Rejected)**

Add `debrisType` to `Asteroid` interface:

```typescript
type Asteroid = {
  // ... existing properties
  debrisType?: 'wyvern' | 'bat' | 'crystal'; // Medieval theme only
};

function fragmentAsteroid(asteroid: Asteroid): Asteroid[] {
  // ... fragment creation
  const fragmentType = getFragmentType(asteroid.debrisType);
  fragments.forEach((f) => (f.debrisType = fragmentType));
  return fragments;
}
```

**Rejected because**:

- ❌ Requires modifying core `Asteroid` type
- ❌ Theme-specific property leaks into theme-agnostic entity
- ❌ Fragmentation logic becomes theme-aware (violates separation of concerns)
- ❌ All themes must handle/ignore this property

### Fragmentation Chain Details

| Parent Type | Parent Size  | Fragments    | Fragment Type | Fragment Size | Narrative                             |
| ----------- | ------------ | ------------ | ------------- | ------------- | ------------------------------------- |
| **Wyvern**  | radius ≥ 30  | 2-3 bats     | Bat           | radius 15-29  | Curse broken, trapped bats released   |
| **Bat**     | radius 15-29 | 2-3 crystals | Crystal       | radius < 15   | Arcane form shattered into pure magic |
| **Crystal** | radius < 15  | 0 (sparkles) | None          | N/A           | Magic disperses as sparkle particles  |

**Visual Transition**:

```
Player shoots wyvern with fireball
  ↓
Wyvern death animation (smoke puff)
  ↓
2-3 bats spawn at wyvern location (smaller, faster)
  ↓
Player shoots bat with fireball
  ↓
Bat shatters (crystal-like break effect)
  ↓
2-3 crystals spawn at bat location (smallest, fastest)
  ↓
Player shoots crystal with fireball
  ↓
Crystal explodes into sparkle particles (no new obstacles)
```

## Rationale

### Why Magical Transformation Over Alternatives?

#### Alternative 1: Biological Fragmentation ❌

Each creature type spawns smaller versions of itself:

```
Large Wyvern → Medium Wyverns → Small Wyverns
Large Bat → Medium Bats → Small Bats
Large Crystal → Medium Crystals → Small Crystals
```

**Rejected because**:

- Loses visual variety (all obstacles same type throughout encounter)
- Doesn't use the mixed creature/magical obstacle aesthetic
- Requires explicit type tracking (can't use size-based implicit typing)

#### Alternative 2: All-Crystal Transformation ❌

Everything becomes crystals when hit (petrification):

```
Wyvern → Large Crystals → Medium Crystals → Small Crystals
Bat → Medium Crystals → Small Crystals → Tiny Crystal Shards
```

**Rejected because**:

- Creatures only appear briefly (first hit petrifies)
- Loses creature variety after initial spawn
- Doesn't feel as "alive" or dynamic

#### Alternative 3: No Fragmentation for Creatures ❌

Only crystals fragment, creatures die completely:

```
Wyvern → Death (no fragments)
Bat → Death (no fragments)
Crystal → Smaller Crystals → Crystal Shards
```

**Rejected because**:

- Changes game difficulty significantly (fewer obstacles)
- Requires explicit type tracking to control fragmentation
- Inconsistent with established game mechanics

### Why Magical Transformation Works ✅

1. **Maintains Game Balance**
   - Same fragmentation count (2-3 fragments)
   - Same difficulty progression (large → medium → small)
   - No changes to scoring, collision, physics

2. **Adds Narrative Depth**
   - Thematic explanation feels intentional, not arbitrary
   - "Cursed wyverns" story hook
   - Players understand "magic creatures = magic fragments"

3. **Visual Variety**
   - Encounter progresses through all three visual types
   - More interesting than uniform obstacles
   - Reinforces "breaking the curse" fantasy

4. **Zero Core Changes**
   - Size-based typing automatic (renderer decides based on radius)
   - Fragmentation logic untouched
   - No new entity properties
   - Theme-agnostic data layer preserved

5. **Extensibility**
   - Pattern works for future themes (cyberpunk: ships → drones → data fragments)
   - Establishes precedent for themed fragmentation
   - Documents approach for future developers

## Consequences

### Positive ✅

1. **Thematic Consistency**
   - Fragmentation chain makes narrative sense
   - "Cursed wyverns" story enriches game world
   - Players intuitively understand magical transformation
   - Visual progression (creature → creature → magic) feels natural

2. **Zero Core Changes**
   - **Fragmentation logic untouched** - No changes to `asteroid.ts` spawn logic
   - **Entity types unchanged** - `Asteroid` remains theme-agnostic
   - **Game balance preserved** - Same difficulty curve, scoring, collision
   - **Backward compatible** - Space/underwater themes unaffected

3. **Implementation Simplicity**
   - **Size-based implicit typing** - Renderer determines type from radius
   - **No conditional fragmentation** - Core system doesn't know about types
   - **Single source of truth** - `getObstacleTypeBySize()` function defines mapping

4. **Future Extensibility**
   - **Pattern for themed fragmentation** - Future themes can use similar approach
   - **Documented precedent** - ADR explains rationale for next theme
   - **Cyberpunk example**: Mothership → Scout Drones → Data Fragments → Glitch Particles

### Negative ⚠️

1. **Implicit Type Transitions**
   - Type changes based on size, not explicit property
   - Could be confusing for future developers
   - **Mitigation**: Comprehensive JSDoc in renderer, this ADR documents design

2. **Theme-Specific Narrative Dependency**
   - Magical transformation only makes sense in medieval fantasy context
   - Other themes need different narrative justifications
   - **Mitigation**: Each theme documents its fragmentation story (e.g., underwater: jellyfish → baby jellyfish → plankton)

3. **Testing Complexity**
   - Need to verify visual transitions at size boundaries
   - Ensure correct type assignment across all size ranges
   - **Mitigation**: Unit tests for `getObstacleTypeBySize()`, visual regression tests

### Neutral 🔶

1. **No Visual Continuity Enforcement**
   - Wyvern → bats transition is instant (no morph animation)
   - **Rationale**: Fragmentation is explosive event (destruction), not gradual transformation
   - **Consistency**: Same as space theme (asteroid → smaller asteroids, instant spawn)

2. **Narrative Exposure**
   - Players may not understand "cursed wyverns" story without explanation
   - **Future enhancement**: Theme selector page with narrative descriptions (see ADR-008)
   - **Current state**: Visual progression speaks for itself (creature → creature → crystal progression is intuitive)

## Related

### ADRs

- [ADR-007: Theme Rendering Strategy Pattern](./ADR-007-theme-rendering-strategy-pattern.md) - Establishes renderer separation
- [ADR-008: Medieval Fantasy Theme](./ADR-008-medieval-fantasy-theme.md) - Overall theme implementation

### Documentation

- [Medieval Fantasy Theme Specification](../../MEDIEVAL_FANTASY_THEME_SPEC.md) - Detailed implementation guide
- [Game Design Document](../../GAME_DESIGN.md) - Fragmentation mechanics

### Code References

- `src/entities/asteroid.ts` - Fragmentation logic (unchanged)
- `src/core/themes/renderers/medieval/obstacleRenderer.ts` - `getObstacleTypeBySize()` function
- `src/types/index.ts` - `Asteroid` type (unchanged)

## Implementation Notes

### Size-to-Type Mapping

```typescript
/**
 * Determines medieval obstacle type based on size
 *
 * Fragmentation chain:
 * - Wyvern (large, radius ≥ 30) → Bats (medium, radius 15-29)
 * - Bat (medium) → Crystals (small, radius < 15)
 * - Crystal (small) → Sparkles (no fragments, sizeLevel = 0)
 *
 * @param radius - Obstacle radius in pixels
 * @returns Obstacle type for rendering
 */
function getObstacleTypeBySize(radius: number): MedievalObstacleType {
  if (radius >= 30) return 'wyvern'; // Large obstacles
  if (radius >= 15) return 'bat'; // Medium obstacles
  return 'crystal'; // Small obstacles
}
```

### Renderer Implementation

```typescript
/**
 * Renders medieval obstacles with type-based variety
 *
 * Obstacle type determined by size:
 * - Large (radius ≥ 30): Wyvern (hostile dragon)
 * - Medium (radius 15-29): Giant Bat
 * - Small (radius < 15): Magical Crystal
 *
 * Fragmentation narrative: Cursed wyverns release trapped bats,
 * bats shatter into pure magical crystals, crystals explode into sparkles.
 */
export function drawMedievalObstacle(ctx: CanvasRenderingContext2D, obstacle: Asteroid): void {
  const type = getObstacleTypeBySize(obstacle.radius);

  switch (type) {
    case 'wyvern':
      drawWyvern(ctx, obstacle);
      break;
    case 'bat':
      drawBat(ctx, obstacle);
      break;
    case 'crystal':
      drawCrystal(ctx, obstacle);
      break;
  }
}
```

### Testing Strategy

**Unit Tests**:

```typescript
describe('getObstacleTypeBySize', () => {
  it('returns wyvern for large obstacles', () => {
    expect(getObstacleTypeBySize(45)).toBe('wyvern');
    expect(getObstacleTypeBySize(30)).toBe('wyvern');
  });

  it('returns bat for medium obstacles', () => {
    expect(getObstacleTypeBySize(29)).toBe('bat');
    expect(getObstacleTypeBySize(15)).toBe('bat');
  });

  it('returns crystal for small obstacles', () => {
    expect(getObstacleTypeBySize(14)).toBe('crystal');
    expect(getObstacleTypeBySize(5)).toBe('crystal');
  });
});
```

**Visual Regression Tests**:

- Spawn large wyvern, destroy, verify bat fragments appear
- Spawn medium bat, destroy, verify crystal fragments appear
- Spawn small crystal, destroy, verify no fragments (sparkle effect only)

## Future Considerations

### Theme-Specific Fragmentation Patterns

Future themes can use similar size-based implicit typing:

**Cyberpunk Theme**:

```
Mothership (large) → Scout Drones (medium) → Data Fragments (small) → Glitch Particles
```

**Steampunk Theme**:

```
Airship (large) → Gear Clusters (medium) → Cog Shards (small) → Steam Puffs
```

**Post-Apocalyptic Theme**:

```
Scrap Hulk (large) → Metal Debris (medium) → Rust Fragments (small) → Dust Clouds
```

### Explicit Type Tracking (If Needed)

If future themes require **non-size-based fragmentation** (e.g., crystal spawns different crystal color), we could:

1. Add optional `themeData?: Record<string, any>` to `Asteroid`
2. Themes populate this with custom properties
3. Core logic ignores it (theme-specific)

**Decision**: Defer until actually needed, current size-based approach sufficient.

## Conclusion

The **Magical Transformation Chain** (wyvern → bat → crystal) provides thematic consistency for medieval fantasy obstacle fragmentation while maintaining **zero core changes** to the game's entity system. By using size-based implicit typing, we achieve rich visual variety without compromising the theme-agnostic data layer.

This pattern establishes a precedent for future themes: creative narrative justifications can explain visual transformations during fragmentation, allowing diverse obstacle aesthetics while preserving game mechanics.

**Status**: Ready for implementation - 2025-12-06
