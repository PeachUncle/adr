# ADR 0004: Barnes-Hut Algorithm for Force-Directed Layout

## Status
Accepted

## Context
The Business Universe visualization uses force-directed graph layout to position department entities. The naive O(n²) algorithm calculates forces between all pairs of nodes, which becomes prohibitively slow with 100+ entities.

Requirements:
- Support 200+ department/KPI entities
- Maintain 60 FPS during layout animations
- Allow real-time interaction during layout

## Decision
We implemented the Barnes-Hut algorithm using an octree spatial partitioning structure:

1. **Octree Construction**: Recursively subdivide 3D space into octants
2. **Center of Mass**: Each octree node stores aggregate mass and center
3. **Force Approximation**: For distant node groups, treat as single point mass
4. **Theta Parameter**: Controls accuracy vs. performance tradeoff (default: 0.5)

### Implementation:
```swift
final class OctreeNode {
    var totalMass: Float = 0
    var centerOfMass: SIMD3<Float> = .zero
    var children: [OctreeNode?] = Array(repeating: nil, count: 8)

    func calculateForce(
        on position: SIMD3<Float>,
        repulsionStrength: Float,
        theta: Float = 0.5
    ) -> SIMD3<Float> {
        // Barnes-Hut criterion: nodeSize / distance < theta
        let distance = simd_length(centerOfMass - position)
        let ratio = halfSize * 2 / distance

        if ratio < theta || isLeaf {
            // Use approximation
            return calculatePointForce(to: position)
        } else {
            // Recurse into children
            return children.compactMap { $0 }
                .reduce(.zero) { $0 + $1.calculateForce(on: position, ...) }
        }
    }
}
```

### Algorithm Selection:
```swift
// Automatic selection based on entity count
if nodes.count <= config.barnesHutThreshold {
    applyRepulsionForcesNaive()  // O(n²) - faster for small n
} else {
    applyRepulsionForcesBarnesHut()  // O(n log n)
}
```

## Consequences

### Positive
- O(n log n) complexity vs O(n²) for naive approach
- 200 nodes: ~10x faster than naive
- 500 nodes: ~25x faster than naive
- Maintains smooth 60 FPS layout animations

### Negative
- More complex implementation
- Small overhead for octree construction
- Approximation introduces minor layout differences

### Configuration:
- `theta = 0.5`: Good balance (default)
- `theta = 0.3`: More accurate, slower
- `theta = 0.8`: Less accurate, faster
- `barnesHutThreshold = 100`: Switch point

## Supplementary: Spatial Hash Grid
For collision detection, we also implemented a `SpatialHashGrid`:
- O(1) average neighbor queries
- Used for overlap detection during layout
- Cell size based on average entity radius

## Related Decisions
- ADR 0003: Entity Pooling
