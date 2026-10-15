# ADR-0004: AI State Machine Design

**Date**: 2025-11-09
**Status**: Accepted

## Context

We need AI for enemies that provides challenging gameplay while remaining simple to implement and understand. Key requirements:

- **Behavior**: Enemies should detect player, pursue, maintain distance, and shoot
- **Complexity**: Simple enough to implement in 2-3 days
- **Performance**: Must handle 5 concurrent enemies at 60 FPS
- **Predictability**: Players should understand and counter enemy behavior
- **Extensibility**: Foundation for future enemy types (P2/P3: melee enemies, tanks, etc.)

Enemy behaviors needed:
1. **Idle**: Default state, look around, no player detected
2. **Chase**: Player detected, move toward player position
3. **Attack**: In shooting range, stop and fire at player
4. **Dead**: Health depleted, play death animation, remove from game

Challenges:
- Pathfinding with obstacles (3-5 boxes on map)
- Shooting accuracy (should miss sometimes for fairness)
- Multiple enemies coordinating (avoid clumping)
- Performance (5 enemies updating AI every frame)

## Decision

Implement a **Finite State Machine (FSM)** with **four states** and simple behavior rules:

### State Definitions

```typescript
type AIState = 'idle' | 'chase' | 'attack' | 'dead';

interface AIComponent extends Component {
  type: 'ai';
  state: AIState;
  detectionRadius: number;    // 20 units (configurable via JSON)
  attackRange: number;        // 8 units (min distance before shooting)
  fireRate: number;           // 1.0 seconds between shots
  lastShotTime: number;       // Timestamp of last shot
  target: Entity | null;      // Reference to player entity
  accuracy: number;           // 0.7 = 70% chance to shoot in player's direction
  idleTimer: number;          // Time spent in idle (for patrol later)
}
```

### State Transitions

```
     [Spawn]
        ↓
    ┌──[Idle]──┐
    │     ↓     │
    │  Player   │
    │  detected │
    │     ↓     │
    └→ [Chase] ←┘
        ↓   ↑
       In   Out of
      range range
        ↓   ↑
      [Attack]

    [Health ≤ 0] → [Dead] → [Remove]
```

**Transition Logic** (checked every frame):
- **Idle → Chase**: Player distance < detectionRadius (20 units)
- **Chase → Attack**: Player distance < attackRange (8 units)
- **Attack → Chase**: Player distance > attackRange (enemy retreats)
- **Chase → Idle**: Player distance > detectionRadius (lost sight)
- **Any → Dead**: Health ≤ 0

### State Behaviors

**Idle State**:
```typescript
function updateIdleState(enemy: Entity, deltaTime: number) {
  // Look for player
  const player = getPlayerEntity();
  const distance = enemy.position.distanceTo(player.position);

  if (distance < enemy.ai.detectionRadius) {
    enemy.ai.state = 'chase';
    enemy.ai.target = player;
  }

  // Optional: Slow rotation (look around)
  enemy.rotation.y += 0.5 * deltaTime;
}
```

**Chase State**:
```typescript
function updateChaseState(enemy: Entity, deltaTime: number) {
  const player = enemy.ai.target;
  const distance = enemy.position.distanceTo(player.position);

  // Transition checks
  if (distance > enemy.ai.detectionRadius) {
    enemy.ai.state = 'idle';
    enemy.ai.target = null;
    return;
  }

  if (distance < enemy.ai.attackRange) {
    enemy.ai.state = 'attack';
    return;
  }

  // Move toward player (simple pursuit)
  const direction = player.position.clone()
    .sub(enemy.position)
    .normalize();

  // Obstacle avoidance: raycast ahead, if blocked, strafe
  const blocked = checkObstacleInPath(enemy, direction);
  if (blocked) {
    direction.applyAxisAngle(new Vector3(0, 1, 0), Math.PI / 2); // Turn 90 degrees
  }

  enemy.velocity.copy(direction.multiplyScalar(enemy.speed));
}
```

**Attack State**:
```typescript
function updateAttackState(enemy: Entity, currentTime: number) {
  const player = enemy.ai.target;
  const distance = enemy.position.distanceTo(player.position);

  // Transition checks
  if (distance > enemy.ai.attackRange) {
    enemy.ai.state = 'chase';
    return;
  }

  // Stop movement (stand still to shoot)
  enemy.velocity.set(0, 0, 0);

  // Face player
  const direction = player.position.clone().sub(enemy.position);
  enemy.rotation.y = Math.atan2(direction.x, direction.z);

  // Shoot at player (with cooldown and accuracy)
  if (currentTime - enemy.ai.lastShotTime > enemy.ai.fireRate) {
    shootAtPlayer(enemy, player, enemy.ai.accuracy);
    enemy.ai.lastShotTime = currentTime;
  }
}
```

**Dead State**:
```typescript
function updateDeadState(enemy: Entity) {
  enemy.isActive = false; // Mark for removal
  enemy.mesh.visible = false; // Hide immediately (or play death animation)
  // Could add: particle effect, sound, score increment
}
```

### Shooting Accuracy
```typescript
function shootAtPlayer(enemy: Entity, player: Entity, accuracy: number) {
  // Perfect aim direction
  const perfectDirection = player.position.clone()
    .sub(enemy.position)
    .normalize();

  // Add random offset based on accuracy (lower = more spread)
  const spread = (1 - accuracy) * Math.PI / 4; // Max 45 degree cone
  const randomOffset = new Vector3(
    (Math.random() - 0.5) * spread,
    0,
    (Math.random() - 0.5) * spread
  );

  const aimDirection = perfectDirection.add(randomOffset).normalize();

  // Spawn projectile
  createProjectile(enemy.position, aimDirection, 'enemy', enemy.damage);
}
```

### Obstacle Avoidance (Simple Raycast)
```typescript
function checkObstacleInPath(enemy: Entity, direction: Vector3): boolean {
  const raycaster = new THREE.Raycaster(enemy.position, direction, 0, 2);
  const obstacles = getObstacles(); // Map walls and boxes
  const intersects = raycaster.intersectObjects(obstacles);

  return intersects.length > 0; // True if obstacle ahead
}
```

## Alternatives Considered

### 1. **Behavior Trees**
Used in AAA games (Halo, Unreal Engine)

**Pros**:
- Very flexible: Easy to add complex behaviors (flanking, cover, retreating)
- Reusable nodes: "FindCover", "FleeFromDanger" can be shared
- Designer-friendly: Visual editors exist (behavior3js)

**Cons**:
- **Overkill**: We only need 4 states, not 50+ behaviors
- **Complexity**: Requires tree evaluation every frame (performance cost)
- **Learning curve**: Unfamiliar to most web developers
- **Implementation time**: 2-3x longer than FSM

**Why not chosen**: Too complex for simple AI needs, violates "simplest solution" principle.

### 2. **Goal-Oriented Action Planning (GOAP)**
Used in F.E.A.R., Tomb Raider

**Pros**:
- Emergent behavior: AI "plans" actions to achieve goals
- Flexible: AI adapts to changing situations (low health → find health pack)

**Cons**:
- **Complex**: Requires action planner, cost evaluation, state preconditions
- **Performance**: A* search every frame is expensive
- **Unpredictable**: Hard to debug when AI does unexpected things
- **Overkill**: We don't have enough actions to justify planner

**Why not chosen**: Way too complex for our needs, not suitable for 2-3 week timeline.

### 3. **Utility AI (Scoring System)**
Used in The Sims, Civilization

**Pros**:
- Smooth behavior: No hard state transitions (blends behaviors)
- Tunable: Each action has utility score (e.g., "attack" = 0.8 if low health)

**Cons**:
- **Balancing nightmare**: Requires tuning many score curves
- **Less predictable**: Hard to understand why AI chose action
- **Overkill**: Works best with 10+ actions, we have 3-4

**Why not chosen**: FSM is more predictable and easier to balance for arcade shooter.

### 4. **Scripted Sequences**
Predefined behavior scripts

**Pros**:
- Total control: Designer specifies exact behavior
- Predictable: Always does the same thing

**Cons**:
- **Inflexible**: Can't adapt to player behavior
- **Boring**: Feels robotic, players can exploit patterns
- **High maintenance**: Every scenario needs custom script

**Why not chosen**: We want reactive AI that responds to player, not scripted encounters.

## Consequences

### Positive
- ✅ **Simple to implement**: ~150 lines of code for entire AI system
- ✅ **Understandable**: Anyone can read the state transitions and know what AI does
- ✅ **Debuggable**: Easy to add logging ("Enemy transitioned Idle → Chase")
- ✅ **Predictable**: Players can learn and counter enemy patterns
- ✅ **Performant**: O(1) state update per enemy (no pathfinding, planning, etc.)
- ✅ **Extensible**: Adding new states (e.g., "Flee") is straightforward
- ✅ **Testable**: Each state behavior can be unit tested in isolation

### Negative
- ❌ **No advanced tactics**: Enemies don't take cover, flank, or coordinate
- ❌ **Repetitive behavior**: All enemies act the same way (until P2 adds enemy types)
- ❌ **Obstacle handling simplistic**: 90-degree turns look unnatural
- ❌ **No memory**: Enemy doesn't remember last known player position

### Trade-offs
- **Simplicity vs Realism**: FSM is simple but enemies won't feel "smart"
- **Performance vs Features**: No A* pathfinding means poor obstacle navigation
- **Predictability vs Variety**: Fixed states mean limited behavior diversity

## Implementation Notes

### Configuration (JSON)
```json
{
  "enemy": {
    "ai": {
      "detectionRadius": 20,
      "attackRange": 8,
      "fireRate": 1.0,
      "accuracy": 0.7,
      "speed": 3
    }
  }
}
```

### Performance Budget
- **State update**: <0.01ms per enemy (simple distance checks)
- **Obstacle raycast**: <0.05ms per enemy (only in chase state)
- **Total AI budget**: 5 enemies * 0.06ms = 0.3ms/frame (1.8% of 16.67ms budget)

### Future Enhancements (P2/P3)
- **Patrol State**: Enemies walk predefined waypoints when idle
- **Flee State**: Enemies retreat when low health
- **Cover System**: Enemies hide behind obstacles when reloading
- **Squad Coordination**: Enemies avoid clumping, flank player

## Validation Criteria

This ADR is successful if:
- [ ] Enemies detect player from 20 units away (100% of tests)
- [ ] Enemies pursue player when detected (visual inspection)
- [ ] Enemies stop at 8 units and shoot (100% of tests)
- [ ] Enemies miss ~30% of shots (accuracy = 0.7)
- [ ] AI system uses <1ms per frame for 5 enemies (profiler check)
- [ ] State transitions are bug-free (no stuck enemies)

## Related Decisions
- [ADR-0003: Entity Component System](./0003-entity-component-system.md) - AIComponent defined here
- [ADR-0002: Collision Detection](./0002-collision-detection-strategy.md) - Obstacle raycasting uses collision system
- [ADR-0005: Asset Loading Strategy](./0005-asset-loading-strategy.md) - AI parameters loaded from JSON

## References
- Game Programming Patterns - State: http://gameprogrammingpatterns.com/state.html
- AI Game Programming Wisdom (book series)
- GDC Talk: "Building a Better Centaur: AI at Massive Scale" (HALO)
- Three.js Raycaster: https://threejs.org/docs/#api/en/core/Raycaster
- Finite State Machines in Games: https://www.gamedev.net/tutorials/programming/artificial-intelligence/finite-state-machines-and-ai-r2907/
