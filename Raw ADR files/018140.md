# ADR-0003: Entity Component System Architecture

**Date**: 2025-11-09
**Status**: Accepted

## Context

We need an architecture pattern to organize game entities (player, enemies, projectiles) and their behaviors. Key requirements:

- **Maintainability**: Code should be easy to understand and modify
- **Extensibility**: Adding new entity types or behaviors should be straightforward
- **Performance**: System must support 60 FPS with 20+ entities
- **Educational Value**: Pattern should demonstrate good game architecture practices
- **Testability**: Entities and systems should be unit-testable in isolation

Current entity types:
- 1 Player (movement, shooting, health, camera)
- 5 Enemies (AI, health, shooting, pathfinding)
- 10+ Projectiles (movement, collision, damage, lifetime)
- Map objects (static walls, obstacles - no behavior)

Behavior complexity:
- Player: Input handling, camera control, shooting cooldown
- Enemy: State machine (idle, chase, attack), targeting, pathfinding
- Projectile: Movement, lifetime tracking, collision detection

## Decision

Implement a **lightweight Entity Component System (ECS)** with the following design:

### Core Concepts

**Entity**: Unique ID + component container
```typescript
interface Entity {
  id: string;
  components: Map<string, Component>;
  isActive: boolean;
}
```

**Component**: Pure data, no logic
```typescript
interface Component {
  type: string;
}

// Example components:
interface PositionComponent extends Component {
  type: 'position';
  position: THREE.Vector3;
  rotation: THREE.Euler;
}

interface HealthComponent extends Component {
  type: 'health';
  current: number;
  max: number;
}

interface VelocityComponent extends Component {
  type: 'velocity';
  velocity: THREE.Vector3;
  speed: number;
}

interface MeshComponent extends Component {
  type: 'mesh';
  mesh: THREE.Mesh;
}

interface AIComponent extends Component {
  type: 'ai';
  state: 'idle' | 'chase' | 'attack' | 'dead';
  detectionRadius: number;
  attackRange: number;
  target: Entity | null;
}
```

**System**: Logic that operates on entities with specific components
```typescript
abstract class System {
  abstract requiredComponents: string[];
  abstract update(entities: Entity[], deltaTime: number): void;
}

// Example system:
class MovementSystem extends System {
  requiredComponents = ['position', 'velocity'];

  update(entities: Entity[], deltaTime: number) {
    for (const entity of entities) {
      if (this.hasRequiredComponents(entity)) {
        const pos = entity.components.get('position') as PositionComponent;
        const vel = entity.components.get('velocity') as VelocityComponent;

        pos.position.add(vel.velocity.clone().multiplyScalar(deltaTime));
      }
    }
  }
}
```

### System Order (Update Pipeline)
1. **InputSystem**: Process keyboard/mouse, update player velocity
2. **AISystem**: Update enemy state machines, set target velocities
3. **MovementSystem**: Apply velocities to positions
4. **CollisionSystem**: Detect and resolve collisions
5. **ProjectileSystem**: Update projectile lifetimes, check hits
6. **HealthSystem**: Apply damage, check death conditions
7. **RenderSystem**: Sync Three.js meshes with entity positions

### Entity Manager
```typescript
class EntityManager {
  private entities: Map<string, Entity> = new Map();
  private systems: System[] = [];

  createEntity(components: Component[]): Entity {
    const entity = { id: generateId(), components: new Map(), isActive: true };
    components.forEach(c => entity.components.set(c.type, c));
    this.entities.set(entity.id, entity);
    return entity;
  }

  destroyEntity(id: string): void {
    this.entities.delete(id);
  }

  update(deltaTime: number): void {
    for (const system of this.systems) {
      const relevantEntities = Array.from(this.entities.values())
        .filter(e => e.isActive && system.matchesEntity(e));
      system.update(relevantEntities, deltaTime);
    }
  }
}
```

### Simplified ECS (Pragmatic Approach)
We use a **lightweight ECS**, not strict ECS (like Unity DOTS or Bevy):
- **Entities CAN reference other entities** (e.g., AI target, projectile owner)
- **Components MAY have methods** (not pure data) for helper functions
- **Systems CAN access global state** (e.g., scene, camera) when needed
- **No archetypes or memory optimization** (our scale doesn't require it)

This balances ECS benefits (modularity, testability) with pragmatism (ease of implementation).

## Alternatives Considered

### 1. **Object-Oriented Hierarchy (Inheritance)**
```typescript
abstract class GameObject {
  position: Vector3;
  abstract update(deltaTime: number): void;
}

class Player extends GameObject { ... }
class Enemy extends GameObject { ... }
class Projectile extends GameObject { ... }
```

**Pros**:
- Familiar to most developers (OOP is well-known)
- Simple for small hierarchies
- TypeScript type safety with class hierarchies

**Cons**:
- **Deep inheritance fragility**: Changes to base class affect all subclasses
- **Code duplication**: Shared behaviors (health, movement) require mixins or copy-paste
- **Inflexible**: Hard to add new combinations (e.g., "Enemy that doesn't shoot")
- **Testing complexity**: Must mock entire class hierarchy

**Why not chosen**: Becomes brittle as entity types grow (P2/P3 features like power-ups, different enemy types).

### 2. **Pure Component Pattern (No Systems)**
```typescript
interface Entity {
  components: Component[];
  update(deltaTime: number): void; // Each component updates itself
}
```

**Pros**:
- Simple: No separate system layer
- Components self-contained

**Cons**:
- **No centralized logic**: Collision checks scattered across components
- **Component coupling**: HealthComponent needs to know about DamageComponent
- **Hard to test**: Components depend on each other's state

**Why not chosen**: Collision and physics require centralized systems (can't be done per-component).

### 3. **Strict ECS (Data-Oriented Design)**
Examples: Unity DOTS, Bevy, EnTT

**Pros**:
- Maximum performance: Cache-friendly memory layout
- Scales to 100,000+ entities
- Parallelizable systems

**Cons**:
- **Complex implementation**: Requires archetypes, component arrays, memory management
- **Development overhead**: 3-5x more code than needed for our scale
- **Learning curve**: Unfamiliar to most web developers
- **Overkill**: We have 20 entities, not 20,000

**Why not chosen**: Premature optimization - our scale doesn't justify the complexity.

### 4. **No Architecture (Spaghetti Code)**
All logic in game loop:
```typescript
function gameLoop() {
  updatePlayer();
  updateEnemies();
  updateProjectiles();
  checkCollisions();
  renderEverything();
}
```

**Pros**:
- Fast to write initially
- No abstraction overhead

**Cons**:
- **Unmaintainable**: All code in one giant file
- **Untestable**: Can't unit test individual behaviors
- **No reusability**: Copy-paste for similar entities
- **Fragile**: Changing one thing breaks others

**Why not chosen**: Violates NFR-004 (maintainability), not educational.

## Consequences

### Positive
- ✅ **Modularity**: New behaviors = new components/systems (no hierarchy changes)
- ✅ **Testability**: Systems can be unit tested with mock entities
- ✅ **Clarity**: Clear separation of data (components) and logic (systems)
- ✅ **Reusability**: Health component works for player, enemies, and future entities
- ✅ **Flexibility**: Entity types defined by component composition, not inheritance
- ✅ **Educational**: Demonstrates industry-standard game architecture pattern
- ✅ **Performance**: System-based updates are cache-friendly (iterate over same component types)

### Negative
- ❌ **Indirection**: Must look up components by type (extra Map lookup vs direct property)
- ❌ **Boilerplate**: More code than simple OOP (entity factory, component definitions)
- ❌ **Learning curve**: Developers unfamiliar with ECS may find it confusing initially
- ❌ **TypeScript friction**: Component lookups lose type safety (need type assertions)

### Trade-offs
- **Complexity vs Flexibility**: More upfront complexity, but easier to extend later
- **Performance**: Slightly slower than direct property access, but faster than deep inheritance
- **Type Safety**: Less compile-time safety (component lookups), more runtime flexibility

## Implementation Notes

### Entity Creation Example
```typescript
// Player entity
const player = entityManager.createEntity([
  { type: 'position', position: new Vector3(0, 0, 0), rotation: new Euler() },
  { type: 'velocity', velocity: new Vector3(), speed: 5 },
  { type: 'health', current: 100, max: 100 },
  { type: 'mesh', mesh: createPlayerMesh() },
  { type: 'input', keys: {}, mouse: {} },
  { type: 'shooter', cooldown: 0.2, lastShot: 0 }
]);

// Enemy entity
const enemy = entityManager.createEntity([
  { type: 'position', position: new Vector3(10, 0, 10), rotation: new Euler() },
  { type: 'velocity', velocity: new Vector3(), speed: 3 },
  { type: 'health', current: 50, max: 50 },
  { type: 'mesh', mesh: createEnemyMesh() },
  { type: 'ai', state: 'idle', detectionRadius: 20, attackRange: 8, target: null },
  { type: 'shooter', cooldown: 1.0, lastShot: 0 }
]);
```

### System Registration
```typescript
const entityManager = new EntityManager();

// Register systems in execution order
entityManager.addSystem(new InputSystem());
entityManager.addSystem(new AISystem());
entityManager.addSystem(new MovementSystem());
entityManager.addSystem(new CollisionSystem());
entityManager.addSystem(new ProjectileSystem());
entityManager.addSystem(new HealthSystem());
entityManager.addSystem(new RenderSystem(scene)); // Needs Three.js scene reference

// Game loop
function animate(currentTime: number) {
  const deltaTime = (currentTime - lastTime) / 1000;
  entityManager.update(deltaTime);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

### Component Query Helper
```typescript
// Type-safe component retrieval
function getComponent<T extends Component>(entity: Entity, type: string): T | undefined {
  return entity.components.get(type) as T | undefined;
}

// Usage in system:
const health = getComponent<HealthComponent>(entity, 'health');
if (health && health.current <= 0) {
  entity.isActive = false; // Mark for removal
}
```

## Performance Considerations

**Memory Layout**:
- Components stored in Map (O(1) lookup)
- Systems iterate over filtered entity arrays
- No memory pooling initially (add if profiling shows GC pressure)

**Optimization Opportunities** (if needed):
- Component array packing (all PositionComponents in contiguous array)
- Entity archetypes (group entities with same component sets)
- System multithreading (Web Workers for AI system)

**Current Performance Target**:
- Entity update: <2ms per frame for 20 entities
- Component lookup: <0.001ms (Map access is fast)
- System overhead: <0.5ms total (system dispatch)

## Validation Criteria

This ADR is successful if:
- [ ] New entity type can be added in <50 lines of code
- [ ] Systems can be unit tested without full game setup
- [ ] Adding new behavior (e.g., "poison damage") requires only new system, no entity changes
- [ ] Code review confirms architecture is understandable to team
- [ ] Performance target met: 60 FPS with 20+ entities

## Related Decisions
- [ADR-0001: Three.js Rendering](./0001-threejs-rendering-approach.md) - MeshComponent wraps Three.js objects
- [ADR-0002: Collision Detection](./0002-collision-detection-strategy.md) - CollisionSystem operates on Position/Velocity components
- [ADR-0004: AI State Machine](./0004-ai-state-machine.md) - AISystem updates AIComponent state

## References
- Game Programming Patterns - Component: http://gameprogrammingpatterns.com/component.html
- Overwatch Gameplay Architecture: https://www.youtube.com/watch?v=W3aieHjyNvw
- Unity ECS Documentation: https://docs.unity3d.com/Packages/com.unity.entities@latest
- Bevy Engine Book: https://bevyengine.org/learn/book/
- Bob Nystrom's ECS Article: http://gameprogrammingpatterns.com/component.html
