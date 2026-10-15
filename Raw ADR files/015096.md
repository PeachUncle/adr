# ADR-001: Sprint 1 Technical Decisions

## Status
**Accepted** - 2025-12-30

---

## Context

Sprint 1 requires foundational technical decisions for the Quiz Battle Arena tower defense game:
1. Project setup and structure
2. Asset sourcing (sprites, backgrounds, audio)
3. Quiz UI approach (M2 planning)
4. Game mechanics implementation (GD questions)

---

## Decision 1: Project Setup

### Technology Stack
- **Phaser 3.90.0** - Game framework with arcade physics
- **Vite 7.3.0** - Dev server and build tool (port 3336)
- **Jest 30.2.0** - Testing framework with ES modules
- **JavaScript (ES modules)** - Main language

### Project Structure
```
src/
├── main.js           # Entry point, Phaser config
├── scenes/           # GameScene, MenuScene, etc.
├── utils/            # Game logic modules
└── assets/
    ├── sprites/      # Zombie, plant, pea sprites
    ├── backgrounds/  # Lawn grid
    └── audio/        # SFX
tests/                # Jest tests
```

### Verified Working
- [x] `npm run dev` - Starts on port 3336
- [x] `npm test` - Jest passes
- [x] Phaser initializes with arcade physics

---

## Decision 2: Asset Sources

### Recommended Free Assets

#### Zombies
| Asset Pack | Source | Details |
|------------|--------|---------|
| **Urban Zombie Pixel Art Pack** | [itch.io](https://free-game-assets.itch.io/free-urban-zombie-sprite-sheet-pixel-art-pack) | 4 chars, idle/walk/attack/hurt/dead anims, PNG/PSD |
| **Free 3 Zombies Pixelated Pack** | [itch.io](https://free-game-assets.itch.io/free-zombie-sprite-sheet-pack-pixel-art) | 3 zombies, good for variety |
| **2D Animated Zombie 32x32** | [itch.io](https://tinymuse.itch.io/2d-animated-zombie) | Small size, good for prototype |

#### Tower Defense / Plants
| Asset Pack | Source | Details |
|------------|--------|---------|
| **Tiny Tower Defense Assets** | [itch.io](https://itch.io/game-assets/free/tag-tower-defense) | Complete 16-bit TD pack |
| **Archer Towers Pixel Art** | [itch.io](https://itch.io/game-assets/free/tag-tower-defense) | Tower sprites |
| **Spire Tower Packs 1-4** | itch.io/Foozle | Animated towers with 3 levels each |

#### Grass/Lawn Backgrounds
| Asset Pack | Source | Details |
|------------|--------|---------|
| **Grass Tileset 16x16** | [OpenGameArt](https://opengameart.org/content/grass-tileset-16x16) | Tiled editor compatible |
| **Pixel Art Grass Tileset** | [OpenGameArt](https://opengameart.org/content/pixel-art-grass-tileset) | 112 tiles, CC-BY 4.0 |
| **Free Grasslands Tileset** | [itch.io](https://itch.io/game-assets/free/tag-grass/tag-pixel-art) | Flexible, free |

### Asset Integration
1. Download PNG spritesheets
2. Place in `src/assets/sprites/`
3. Load in Phaser scene with `this.load.spritesheet()`
4. Create animations in scene's `create()` method

---

## Decision 3: Quiz UI (M2 Planning)

### Recommendation: **Phaser UI (not React)**

| Factor | Phaser UI | React Overlay |
|--------|-----------|---------------|
| Integration | Native, seamless | Requires DOM bridge |
| Animations | Game-style, consistent | Web-style, separate |
| Complexity | Single framework | Two frameworks |
| Performance | No context switching | DOM/Canvas sync overhead |
| Game feel | Immersive | Web app feel |

**Decision**: Use Phaser's built-in text and container objects for quiz UI.

**Rationale**: Quiz is a game mechanic (earn sun), not a web form. Keep everything in Phaser for consistent game feel and simpler architecture.

---

## Decision 4: GD Technical Questions

### Q1: Zombie Death Animation
**Answer**: **Fade out with flash**

```javascript
// On zombie death
zombie.setTint(0xffffff);  // White flash
this.tweens.add({
  targets: zombie,
  alpha: 0,
  y: zombie.y + 10,
  duration: 300,
  onComplete: () => zombie.destroy()
});
```

**Rationale**:
- Ragdoll physics adds complexity (Box2D needed)
- Fade out is simple, satisfying, and performant
- White flash gives "hit" feedback

### Q2: Pea Projectile Speed
**Answer**: **Visible travel time - 400 pixels/second**

```javascript
const PEA_SPEED = 400; // pixels per second
```

**Rationale**:
- Instant hit removes visual feedback
- Visible projectile is satisfying (PvZ feel)
- 400 px/sec = crosses screen in ~2.4 sec
- Allows player to see peas hitting zombies

### Q3: Collision Detection
**Answer**: **First zombie in lane (leftmost)**

```javascript
// In update loop
peas.forEach(pea => {
  const zombiesInLane = zombies.filter(z => z.lane === pea.lane);
  const leftmostZombie = zombiesInLane.sort((a, b) => a.x - b.x)[0];
  if (leftmostZombie && checkCollision(pea, leftmostZombie)) {
    handleHit(pea, leftmostZombie);
  }
});
```

**Rationale**:
- Matches PvZ behavior (pea hits first zombie it reaches)
- Prevents peas passing through zombies
- More strategic (kill front zombie first)
- Phaser arcade physics overlap handles this naturally with proper sorting

---

## Consequences

### Positive
- Simple project setup, ready for DEV
- Free assets available, no licensing issues
- Consistent Phaser-only architecture
- Clear technical specs for GD questions

### Negative
- Asset quality varies (may need to find alternatives)
- No ragdoll physics (less "fun" death animation)

---

## Next Steps

1. **TL**: Create asset download script or document exact assets to use
2. **DEV**: Can start S1-002 once assets are integrated
3. **GD**: Balance values confirmed, can assist DEV with tuning

---

**Author**: TL
**Reviewed by**: Pending SM review
