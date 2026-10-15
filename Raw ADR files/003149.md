# ADR-002: Spatial Partitioning with Quadtree for Star Connections

## Status
Proposed

## Date
2025-12-07

## Context

The Starfield visualization draws connection lines between nearby stars to create a "network" effect. The current implementation has **O(n²) complexity** for finding star pairs within connection distance.

### Current Implementation

```typescript
// stars.ts - drawConnections()
for (let i = 0; i < stars.length; i++) {
  for (let j = i + 1; j < stars.length; j++) {
    const dx = stars[i].x - stars[j].x;
    const dy = stars[i].y - stars[j].y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < connectionDistance) {
      // Draw line
    }
  }
}
```

### Performance Analysis

| Star Count | Pair Comparisons | Time (60fps budget: 16.6ms) |
|------------|------------------|----------------------------|
| 100        | 4,950            | ~0.5ms                     |
| 200        | 19,900           | ~2ms                       |
| 500        | 124,750          | ~12ms                      |
| 1000       | 499,500          | ~50ms (OVER BUDGET)        |

With **500+ stars**, connection drawing becomes a bottleneck, especially on lower-end devices.

### Profiling Evidence

- `drawConnections` accounts for ~15-25% of frame time at 300+ stars
- Heavy operations skip every 2 frames as workaround (`frameSkipRef`)
- Connection flickering reported due to frame skipping

## Decision

**Implement a Quadtree for spatial partitioning of stars.**

A quadtree recursively subdivides 2D space into quadrants, allowing O(log n) neighbor queries instead of O(n) linear scans.

### Proposed Architecture

```
┌───────────────────────────────────────┐
│              Canvas Space              │
│  ┌─────────────┬─────────────────────┐ │
│  │     NW      │         NE          │ │
│  │   ┌───┬───┐ │    ┌───────────┐    │ │
│  │   │   │   │ │    │           │    │ │
│  │   ├───┼───┤ │    │  (stars)  │    │ │
│  │   │   │   │ │    │           │    │ │
│  │   └───┴───┘ │    └───────────┘    │ │
│  ├─────────────┼─────────────────────┤ │
│  │     SW      │         SE          │ │
│  │             │                     │ │
│  └─────────────┴─────────────────────┘ │
└───────────────────────────────────────┘
```

### Implementation

#### 1. Quadtree Data Structure (`spatialIndex.ts`)

```typescript
interface Rectangle {
  x: number;      // center x
  y: number;      // center y
  width: number;  // half-width
  height: number; // half-height
}

interface QuadtreeNode<T> {
  boundary: Rectangle;
  capacity: number;
  points: Array<{ x: number; y: number; data: T }>;
  divided: boolean;
  northeast?: QuadtreeNode<T>;
  northwest?: QuadtreeNode<T>;
  southeast?: QuadtreeNode<T>;
  southwest?: QuadtreeNode<T>;
}

class Quadtree<T> {
  insert(point: { x: number; y: number; data: T }): boolean;
  query(range: Rectangle): Array<{ x: number; y: number; data: T }>;
  queryRadius(x: number, y: number, radius: number): Array<T>;
  clear(): void;
}
```

#### 2. Integration with Star System

```typescript
// In animate.ts or stars.ts
const quadtree = new Quadtree<Star>(canvasBounds, capacity: 4);

// Rebuild quadtree each frame (stars move)
quadtree.clear();
for (const star of stars) {
  quadtree.insert({ x: star.x, y: star.y, data: star });
}

// Draw connections using spatial query
for (const star of stars) {
  const nearby = quadtree.queryRadius(star.x, star.y, connectionDistance);
  for (const neighbor of nearby) {
    if (neighbor.id > star.id) { // Avoid duplicate pairs
      drawConnection(star, neighbor);
    }
  }
}
```

#### 3. Optimizations

- **Object pooling**: Reuse quadtree nodes instead of allocating new ones
- **Lazy subdivision**: Only subdivide when capacity exceeded
- **Circular query optimization**: Use squared distances to avoid sqrt
- **Frame coherence**: If stars move slowly, consider incremental updates

### Complexity Analysis

| Operation | Current | With Quadtree |
|-----------|---------|---------------|
| Build index | N/A | O(n log n) |
| Find all pairs | O(n²) | O(n log n) average |
| Total per frame | O(n²) | O(n log n) |

For 500 stars:
- Current: 124,750 comparisons
- Quadtree: ~4,500 comparisons (avg 9 neighbors per star)
- **~27x improvement**

## Consequences

### Positive

- **Better scaling**: Can support 1000+ stars at 60fps
- **Smoother connections**: Remove frame skipping workaround
- **Future features**: Enables efficient collision detection, clustering, etc.
- **Reusable**: Quadtree can be used for planet hover detection, click detection

### Negative

- **Memory overhead**: Quadtree nodes require additional memory (~20-40 bytes per node)
- **Rebuild cost**: Must rebuild tree each frame since stars move
- **Code complexity**: New data structure to maintain and test

### Trade-offs

- **Capacity tuning**: Node capacity affects performance
  - Too small (1-2): Deep trees, more traversal
  - Too large (16+): Linear search within nodes
  - Sweet spot: 4-8 for typical star distributions

## Alternatives Considered

### 1. Grid-based spatial hashing
- Divide space into fixed grid cells
- Pros: Simpler, O(1) cell lookup
- Cons: Poor for non-uniform distributions; connection distance spans multiple cells
- Rejected: Stars cluster around suns; quadtree handles varying density better

### 2. k-d tree
- Binary space partitioning
- Pros: Efficient for static points
- Cons: Expensive rebalancing for moving points
- Rejected: Stars move every frame; rebuild cost too high

### 3. R-tree
- Bounding rectangle tree
- Pros: Good for rectangles/overlapping regions
- Cons: Overkill for point data; complex implementation
- Rejected: Quadtree is simpler and sufficient

### 4. Reduce star count
- Simply use fewer stars
- Pros: No code changes
- Cons: Reduces visual quality; doesn't scale
- Rejected: Want to support high star counts on capable devices

## Implementation Phases

### Phase 1: Core Quadtree
- [ ] Implement `Quadtree` class with insert/query
- [ ] Add unit tests for correctness
- [ ] Benchmark against brute force

### Phase 2: Integration
- [ ] Create `SpatialIndex` wrapper for animation use
- [ ] Modify `drawConnections` to use quadtree
- [ ] Remove frame skipping workaround for connections

### Phase 3: Optimization
- [ ] Add object pooling for nodes
- [ ] Tune capacity parameter
- [ ] Profile and measure improvement

### Phase 4: Extended Use
- [ ] Use for planet hover detection
- [ ] Use for sun click detection
- [ ] Consider for star-sun gravitational influence

## Performance Targets

| Metric | Current | Target |
|--------|---------|--------|
| Frame time (500 stars) | ~12ms connections | <3ms |
| Max stars at 60fps | ~400 | 1000+ |
| Connection quality | Flickering (skip frames) | Smooth (every frame) |

## References

- Wikipedia: Quadtree - https://en.wikipedia.org/wiki/Quadtree
- "Real-Time Collision Detection" by Christer Ericson
- Current drawConnections: `stars.ts` lines ~180-220
- Frame skip workaround: `animate.ts` line ~98
