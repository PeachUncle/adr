# ADR-002: 3D Rendering Approach

## Status

**Accepted** - 2026-01-01

## Context

The game requires a visual representation of a Mahjong table with 136 tiles. The interface must:
- Display tiles clearly (own hand face-up, opponents face-down)
- Support hover, click, and drag interactions
- Animate tile movements (draw, discard, meld reveals)
- Maintain 60fps on mid-range devices
- Integrate with React component architecture

## Decision Drivers

- **Visual Appeal**: Immersive 3D experience requested
- **Performance**: 60fps on mid-range hardware
- **Developer Experience**: Integrate with React patterns
- **Maintainability**: Code should be declarative and testable
- **Bundle Size**: Reasonable initial load time
- **Interaction Model**: Support complex tile interactions

## Considered Options

### Option 1: React Three Fiber + Drei (Selected)

**Pros**:
- Declarative 3D with React component model
- Excellent ecosystem (drei helpers, postprocessing)
- Good TypeScript support
- Integrates naturally with Next.js
- Large community, well-documented
- Supports instanced meshes for performance

**Cons**:
- Learning curve for Three.js concepts
- Larger bundle than 2D solutions
- WebGL required (no fallback in library)

### Option 2: Vanilla Three.js

**Pros**:
- Maximum control over rendering
- Smaller bundle (no React overhead)
- Direct Three.js documentation applies

**Cons**:
- Imperative code style
- Harder to integrate with React state
- More boilerplate for interactions
- Manual lifecycle management

### Option 3: Babylon.js

**Pros**:
- Powerful engine with physics
- Good TypeScript support
- Built-in GUI system

**Cons**:
- Larger bundle size
- Different paradigm than React
- Smaller community for React integration
- Overkill for static Mahjong table

### Option 4: 2D Canvas (Pixi.js or HTML5 Canvas)

**Pros**:
- Simpler implementation
- Better performance on low-end devices
- Smaller bundle size
- Wider browser support

**Cons**:
- Less immersive experience
- User explicitly requested 3D
- Limited visual effects

## Decision

**We will use React Three Fiber with @react-three/drei helpers.**

### Implementation Approach

```tsx
// Scene structure
<Canvas>
  <Suspense fallback={<LoadingFallback />}>
    <TableScene>
      <Table />
      <TileWall count={wallRemaining} />
      <PlayerHand tiles={hand} onSelect={handleSelect} />
      <OpponentHands players={opponents} />
      <DiscardPile tiles={discards} />
      <MeldDisplay melds={allMelds} />
    </TableScene>
  </Suspense>
  <OrbitControls enableZoom={false} />
  <ambientLight intensity={0.5} />
  <spotLight position={[0, 10, 0]} />
</Canvas>
```

### Performance Optimizations

1. **Instanced Meshes**: Single geometry for all 136 tiles
2. **Texture Atlas**: Single texture with all tile faces
3. **Lazy Loading**: 3D assets load progressively
4. **2D Fallback**: Loading state shows 2D representation
5. **Frustum Culling**: Automatic via Three.js
6. **Level of Detail**: Simplified geometry when zoomed out

## Rationale

1. **React Integration**: R3F's declarative model allows tiles to be React components, simplifying state management and interactions.

2. **Ecosystem**: Drei provides ready-made helpers (OrbitControls, Html for overlays, useGLTF for models).

3. **Performance**: Instanced meshes render 136 tiles efficiently. Tested pattern used in similar card/board games.

4. **User Request**: Explicit requirement for 3D WebGL experience.

5. **Maintainability**: Component-based 3D code is easier to test and maintain than imperative alternatives.

## Consequences

### Positive
- Immersive, modern game feel
- React patterns apply to 3D code
- Rich interaction possibilities
- Community support for common patterns

### Negative
- WebGL required (excludes very old browsers)
- Initial bundle ~200KB for three.js
- Learning curve for 3D concepts
- GPU usage on mobile devices

### Mitigations
- Feature detection for WebGL, show warning if unsupported
- Code splitting for 3D components
- Loading states during asset fetch
- Target mid-range devices, not low-end

## Technical Notes

### Tile Model
- GLTF format (compressed)
- Single mesh, ~500 polygons
- UV mapped for texture atlas

### Texture Atlas
- 1024x1024 PNG
- All 42 unique tile faces
- Mipmap enabled

### Interaction
- Raycasting for hover/click detection
- Drei's `useHover` and `onClick` props
- Spring animations via `@react-spring/three`

## Related Decisions

- ADR-001: Real-time Architecture (state sync)
- ADR-005: Asset Delivery (CDN for 3D models)
