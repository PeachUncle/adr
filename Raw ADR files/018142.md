# ADR-0005: Asset Loading Strategy

**Date**: 2025-11-09
**Status**: Accepted

## Context

We need to load game configuration data (map layout, entity properties, gameplay balance) at runtime. Requirements:

- **Data-Driven Design**: Game balance tunable without code changes
- **Load Time**: All assets loaded in <2 seconds (NFR-006 requirement)
- **Bundle Size**: Keep data files minimal (<50KB total)
- **Maintainability**: Non-programmers should be able to edit balance values
- **Extensibility**: Easy to add new maps, enemy types in future increments
- **No External Dependencies**: All assets local (no CDN, no network requests)

Assets needed:
1. **Map Configuration**: Wall positions, obstacle locations, spawn points
2. **Entity Properties**: Player/enemy health, speed, damage, fire rate
3. **Game Balance**: Detection radius, accuracy, projectile speed
4. **Future (P2/P3)**: Textures, sounds, 3D models

Development constraints:
- No asset pipeline build step (Vite should handle it natively)
- Must work in development (hot reload) and production (bundled)
- Type safety: TypeScript should validate loaded data

## Decision

Use **local JSON files** with the following structure:

### File Structure
```
src/
├── data/
│   ├── game-config.json       # Player, enemy, projectile properties
│   ├── map-arena-01.json      # Map geometry, obstacles, spawn points
│   └── balance.json           # Tweakable values (AI, combat)
├── loaders/
│   ├── ConfigLoader.ts        # JSON loading utilities
│   └── types.ts               # TypeScript interfaces for validation
```

### Configuration Format

**game-config.json**:
```json
{
  "version": "1.0.0",
  "player": {
    "health": 100,
    "speed": 5.0,
    "shootCooldown": 0.2,
    "damage": 25,
    "radius": 0.5
  },
  "enemy": {
    "health": 50,
    "speed": 3.0,
    "shootCooldown": 1.0,
    "damage": 10,
    "radius": 0.4,
    "count": 5
  },
  "projectile": {
    "speed": 20.0,
    "lifetime": 5.0,
    "radius": 0.1
  }
}
```

**map-arena-01.json**:
```json
{
  "name": "Arena 01",
  "size": { "width": 50, "height": 50 },
  "walls": [
    { "type": "box", "position": [0, 0, -25], "size": [50, 5, 1] },
    { "type": "box", "position": [0, 0, 25], "size": [50, 5, 1] },
    { "type": "box", "position": [-25, 0, 0], "size": [1, 5, 50] },
    { "type": "box", "position": [25, 0, 0], "size": [1, 5, 50] }
  ],
  "obstacles": [
    { "type": "box", "position": [10, 0, 10], "size": [3, 3, 3] },
    { "type": "cylinder", "position": [-10, 0, -10], "radius": 2, "height": 4 },
    { "type": "box", "position": [0, 0, 0], "size": [2, 2, 2] }
  ],
  "spawns": {
    "player": { "position": [0, 1, 20] },
    "enemies": [
      { "position": [10, 1, -10] },
      { "position": [-10, 1, -10] },
      { "position": [15, 1, 0] },
      { "position": [-15, 1, 0] },
      { "position": [0, 1, -20] }
    ]
  }
}
```

**balance.json** (for easy iteration):
```json
{
  "ai": {
    "detectionRadius": 20,
    "attackRange": 8,
    "accuracy": 0.7,
    "chaseSpeed": 3.0
  },
  "combat": {
    "playerDamage": 25,
    "enemyDamage": 10,
    "projectileSpeed": 20,
    "fireRatePlayer": 0.2,
    "fireRateEnemy": 1.0
  }
}
```

### TypeScript Validation

**types.ts**:
```typescript
export interface GameConfig {
  version: string;
  player: EntityConfig;
  enemy: EntityConfig;
  projectile: ProjectileConfig;
}

export interface EntityConfig {
  health: number;
  speed: number;
  shootCooldown: number;
  damage: number;
  radius: number;
  count?: number;
}

export interface MapConfig {
  name: string;
  size: { width: number; height: number };
  walls: GeometryDefinition[];
  obstacles: GeometryDefinition[];
  spawns: {
    player: { position: [number, number, number] };
    enemies: { position: [number, number, number] }[];
  };
}

export interface GeometryDefinition {
  type: 'box' | 'cylinder' | 'sphere';
  position: [number, number, number];
  size?: [number, number, number];
  radius?: number;
  height?: number;
}
```

### Loading Implementation

**ConfigLoader.ts**:
```typescript
export class ConfigLoader {
  private static cache = new Map<string, any>();

  static async loadGameConfig(): Promise<GameConfig> {
    return this.loadJSON<GameConfig>('/src/data/game-config.json');
  }

  static async loadMap(mapName: string): Promise<MapConfig> {
    return this.loadJSON<MapConfig>(`/src/data/map-${mapName}.json`);
  }

  private static async loadJSON<T>(path: string): Promise<T> {
    // Check cache first
    if (this.cache.has(path)) {
      return this.cache.get(path) as T;
    }

    // Fetch and parse
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`Failed to load ${path}: ${response.statusText}`);
    }

    const data = await response.json() as T;
    this.cache.set(path, data);
    return data;
  }

  static clearCache(): void {
    this.cache.clear();
  }
}
```

### Vite Integration

Vite automatically handles JSON imports with hot reload:
```typescript
// Option 1: Direct import (bundled, no fetch)
import gameConfig from './data/game-config.json';

// Option 2: Dynamic fetch (runtime loading)
const config = await ConfigLoader.loadGameConfig();
```

For production, Vite bundles JSON into the JavaScript bundle (no separate network requests).

## Alternatives Considered

### 1. **Hardcoded Constants in TypeScript**
```typescript
export const PLAYER_HEALTH = 100;
export const ENEMY_SPEED = 3.0;
```

**Pros**:
- No loading time (immediate)
- Type-safe at compile time
- No parsing overhead

**Cons**:
- **Not data-driven**: Must recompile to change balance
- **Not designer-friendly**: Non-programmers can't tweak values
- **Merge conflicts**: Multiple people editing same constants file
- **No runtime flexibility**: Can't A/B test different balance sets

**Why not chosen**: Violates "data-driven design" principle from specification.

### 2. **YAML Configuration**
```yaml
player:
  health: 100
  speed: 5.0
```

**Pros**:
- More human-readable than JSON (no quotes, commas)
- Comments supported

**Cons**:
- Requires YAML parser library (js-yaml ~30KB)
- Slower parsing than native JSON.parse()
- Less familiar to web developers

**Why not chosen**: Bundle size cost not justified, JSON is simpler and native.

### 3. **External API/Database**
Load from server at runtime

**Pros**:
- Can update balance without redeploying
- A/B testing easy (different users get different configs)

**Cons**:
- **Violates NFR-006**: No external network requests allowed
- **Performance**: Network latency delays game start
- **Offline broken**: Game won't work without internet
- **Complexity**: Requires backend server

**Why not chosen**: Specification explicitly requires local-only assets.

### 4. **GLTF/GLB for Map Geometry**
Use 3D model format for map

**Pros**:
- Industry standard for 3D assets
- Visual editors (Blender, Maya)
- Efficient binary format (GLB)

**Cons**:
- **Overkill for simple geometry**: Our map is just boxes and cylinders
- **Requires loader**: THREE.GLTFLoader adds ~50KB to bundle
- **Learning curve**: Artists need to learn 3D modeling
- **MVP scope**: Deferred to P2/P3 when adding complex models

**Why not chosen**: Simple procedural geometry sufficient for MVP, GLTF deferred to future.

### 5. **IndexedDB for Client-Side Storage**
Store config in browser database

**Pros**:
- Persistent across sessions
- Can store large amounts of data

**Cons**:
- **Overkill**: We have <50KB of config data
- **Complexity**: Requires async DB operations
- **Not needed**: No user-generated content to persist

**Why not chosen**: JSON files are simpler and sufficient.

## Consequences

### Positive
- ✅ **Data-driven**: Balance tweaks don't require code changes
- ✅ **Designer-friendly**: JSON is editable in any text editor
- ✅ **Fast loading**: JSON.parse() is native and very fast (<5ms for our files)
- ✅ **Type-safe**: TypeScript interfaces validate loaded data at runtime
- ✅ **Vite integration**: Hot reload works in development, bundled in production
- ✅ **Version control friendly**: JSON diffs clearly in Git
- ✅ **No dependencies**: Uses native browser APIs (fetch, JSON.parse)

### Negative
- ❌ **No schema validation**: Must manually validate JSON structure (or add Zod/Joi)
- ❌ **Not binary**: JSON is less efficient than binary formats (but our data is small)
- ❌ **No comments**: JSON doesn't support comments (could add JSON5 if needed)
- ❌ **Runtime errors**: Typos in JSON only caught at load time, not compile time

### Trade-offs
- **Simplicity vs Validation**: JSON is simple but lacks built-in schema validation
- **Flexibility vs Safety**: Runtime loading is flexible but loses compile-time checks
- **Load Time vs Bundle Size**: Separate JSON files = faster first paint, but multiple requests in dev

## Implementation Notes

### Loading Flow
```typescript
async function initGame() {
  try {
    // Load all configs in parallel
    const [gameConfig, mapConfig, balance] = await Promise.all([
      ConfigLoader.loadGameConfig(),
      ConfigLoader.loadMap('arena-01'),
      ConfigLoader.loadBalance()
    ]);

    // Validate configs (basic checks)
    validateConfig(gameConfig);
    validateMap(mapConfig);

    // Initialize game with loaded data
    const game = new Game(gameConfig, mapConfig, balance);
    game.start();
  } catch (error) {
    console.error('Failed to load game assets:', error);
    showErrorScreen('Failed to load game. Please refresh.');
  }
}
```

### Runtime Validation Example
```typescript
function validateConfig(config: GameConfig): void {
  if (config.player.health <= 0) {
    throw new Error('Player health must be positive');
  }
  if (config.enemy.speed < 0) {
    throw new Error('Enemy speed cannot be negative');
  }
  // ... more validation
}
```

### Performance Metrics
- **JSON parsing**: <5ms for all config files
- **Fetch time**: <10ms (local files in dev, bundled in prod)
- **Total load overhead**: <20ms (well within 2 second budget)

## Validation Criteria

This ADR is successful if:
- [ ] All config files load in <20ms (Chrome DevTools Network tab)
- [ ] Balance changes work without recompiling (change JSON, refresh browser)
- [ ] TypeScript catches type mismatches in config interfaces
- [ ] New maps can be added by creating new JSON files (no code changes)
- [ ] Bundle size increase <10KB (JSON is small)

## Future Enhancements (P2/P3)

- **Audio files**: MP3/OGG loaded via Three.js AudioLoader
- **Textures**: PNG/JPG loaded via Three.js TextureLoader
- **3D Models**: GLTF/GLB for complex geometry (enemies, weapons)
- **Schema validation**: Add Zod or JSON Schema for runtime validation
- **Asset compression**: Use gzip/brotli for production (Vite handles this)

## Related Decisions
- [ADR-0003: Entity Component System](./0003-entity-component-system.md) - Entities initialized from config data
- [ADR-0004: AI State Machine](./0004-ai-state-machine.md) - AI parameters loaded from balance.json
- [ADR-0001: Three.js Rendering](./0001-threejs-rendering-approach.md) - Map geometry created from JSON definitions

## References
- Vite Static Asset Handling: https://vitejs.dev/guide/assets.html
- JSON Schema: https://json-schema.org/
- Three.js Loaders: https://threejs.org/docs/#manual/en/introduction/Loading-3D-models
- Data-Driven Game Design: https://www.gamedeveloper.com/programming/data-driven-game-design
