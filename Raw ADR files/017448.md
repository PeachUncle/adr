# ADR-004: Fixed Timestep Game Loop with Accumulator Pattern

## Status

Accepted (Sprint 1)

## Context

Game loop must handle:

- Variable frame rates (60 FPS desktop, 30 FPS mobile, unpredictable with lag)
- Deterministic physics (same inputs → same outputs)
- Smooth rendering across devices
- Mobile performance constraints

**Problem with variable timestep:**

````typescript
// BAD: Physics depend on frame rate
function update(deltaTime) {
  player.x += player.velocity * deltaTime;
  asteroid.x += asteroid.velocity * deltaTime;
}

// On slow frame (33ms): entities move 2x distance
// On fast frame (8ms): entities move 0.5x distance
// Result: Non-deterministic gameplay, hard to balance, different on each device
```typescript

## Decision
Use **fixed timestep game loop with accumulator pattern** (16.67ms = 60 FPS on desktop, 33.33ms = 30 FPS on mobile).

## Rationale

**Fixed timestep solves:**
1. **Determinism:** Physics always use same delta (16.67ms), guarantees repeatable behavior
2. **Balancing:** Can tune game difficulty without worrying about frame rate
3. **Testing:** Reproducible physics for automated tests
4. **Cross-device:** Same gameplay speed on all devices

**Accumulator pattern solves:**
- Handles variable frame rates without compromising determinism
- Can "catch up" if game lags (runs multiple updates in one frame)
- Prevents "spiral of death" (caps max catch-up updates)

## Implementation

```typescript
const TIME_STEP = isMobile ? 1000 / 30 : 1000 / 60; // Fixed timestep
let accumulator = 0; // Tracks leftover time
let lastTime = performance.now();

function gameLoop(currentTime) {
  const deltaTime = currentTime - lastTime;
  lastTime = currentTime;

  // Cap delta to prevent spiral of death
  const cappedDelta = Math.min(deltaTime, TIME_STEP * 5);
  accumulator += cappedDelta;

  // Run fixed timestep updates until accumulator depleted
  let updates = 0;
  const MAX_UPDATES = 5; // Prevent infinite loop
  while (accumulator >= TIME_STEP && updates < MAX_UPDATES) {
    updateGameState(TIME_STEP); // Always use TIME_STEP
    accumulator -= TIME_STEP;
    updates++;
  }

  // Render (potentially at different rate than updates)
  renderAll(ctx, accumulator / TIME_STEP); // Interpolation factor

  requestAnimationFrame(gameLoop);
}
```typescript

**Example scenario:**
```text
Frame 1: deltaTime = 20ms
  accumulator = 20ms
  update(16.67ms) runs once
  accumulator = 3.33ms (leftover)

Frame 2: deltaTime = 15ms
  accumulator = 3.33ms + 15ms = 18.33ms
  update(16.67ms) runs once
  accumulator = 1.66ms (leftover)

Frame 3: deltaTime = 25ms (lag spike!)
  accumulator = 1.66ms + 25ms = 26.66ms
  update(16.67ms) runs TWICE (catches up)
  accumulator = 3.32ms (small positive leftover, never negative)
````

## Mobile Optimization

**30 FPS update rate (TIME_STEP = 33.33ms):**

- Reduces CPU load by 50% vs 60 FPS
- Still feels responsive (< 34ms input latency)
- Allows budget devices to maintain stable frame rate

**Render skipping (every 2nd frame):**

- Saves GPU bandwidth (render is expensive on mobile)
- Visual frame rate = 30 FPS (update rate = 30 FPS)
- Trade-off: Slightly less smooth visuals, but maintains playable FPS

## Performance Characteristics

**Desktop (60 FPS updates):**

- Update time: ~2-4ms/frame (leaves 12ms for rendering)
- Render time: ~6-8ms/frame
- Total: ~10-12ms/frame (under 16.67ms budget)

**Mobile (30 FPS updates):**

- Update time: ~3-5ms/frame (leaves 28ms for rendering)
- Render time: ~12-15ms/frame (heavier due to lower GPU)
- Total: ~18-20ms/frame (under 33.33ms budget)

## Consequences

**Positive:**

- **Deterministic physics:** Same inputs always produce same outputs
- **Easier balancing:** Tune once, works everywhere
- **Testable:** Automated tests with predictable physics
- **Smooth rendering:** Independent of update rate (can interpolate)
- **Mobile performance:** 30 FPS update + render skip maintains playable FPS

**Negative:**

- **Complexity:** Accumulator pattern is harder to understand than naive loop
  - _Mitigation:_ Inline documentation explains algorithm
- **Input latency:** 30 FPS on mobile = 33ms worst-case latency
  - _Mitigation:_ Acceptable for arcade game (fighting games use 16ms)
- **Catch-up logic:** Lagged frames run multiple updates (can cause stutter)
  - _Mitigation:_ Cap max updates at 5 (spiral of death prevention)

## Alternatives Considered

### 1. Variable Timestep (Rejected)

```typescript
function update(deltaTime) {
  player.x += player.velocity * deltaTime;
}
```

// Pros: Simple
// Cons: Non-deterministic, different on each device, hard to balance

````

### 2. Fixed Timestep without Accumulator (Rejected)
```typescript
function gameLoop() {
  update(16.67); // Always use fixed delta
  render();
}
````

// Pros: Simple, deterministic
// Cons: Can't catch up if lagged, rendering tied to update rate

```

### 3. ECS with Parallel Updates (Considered but overkill)
Entity-Component-System with parallel update scheduling
**Pros:** Maximum performance on multi-core
**Cons:** Massive complexity, overkill for 100-entity game

## Related
- Implementation: `src/game/gameLoop.ts`
- Tests: `tests/game/gameLoop.logic.test.ts`
- Reference: [Fix Your Timestep by Glenn Fiedler](https://gafferongames.com/post/fix_your_timestep/)
- Reference: [Game Programming Patterns - Game Loop](https://gameprogrammingpatterns.com/game-loop.html)
```
