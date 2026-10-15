# ADR-0001: Three.js Rendering Approach

**Date**: 2025-11-09
**Status**: Accepted

## Context

We need to render a 3D first-person shooter game in the browser. Key requirements:
- 60 FPS performance target with 5 enemies and 10 active projectiles
- Browser compatibility (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Bundle size < 500 KB gzipped
- Development timeline: 2-3 weeks
- Educational value: code should be readable and maintainable
- Target hardware: Mid-tier devices (2019 MacBook Pro equivalent)

We need to choose a rendering approach that balances performance, ease of development, and educational clarity.

## Decision

Use **Three.js r150+** with the following rendering configuration:

**Renderer Setup**:
- `WebGLRenderer` with `antialias: true` for visual quality
- `setPixelRatio(window.devicePixelRatio)` for sharp rendering on retina displays
- `setClearColor(0x000000)` for black background
- `shadowMap.enabled = true` with `PCFSoftShadowMap` type

**Scene Structure**:
- Single `Scene` instance
- `PerspectiveCamera` attached to player (first-person view)
- `AmbientLight` (0x404040) + `DirectionalLight` (0xffffff, intensity 0.8) for lighting
- Frustum culling enabled by default (automatic in Three.js)

**Material Strategy**:
- `MeshStandardMaterial` for most objects (PBR for visual quality)
- `MeshBasicMaterial` for HUD/UI elements (unaffected by lighting)
- Simple textures or solid colors (minimize texture memory)

**Geometry Approach**:
- Use built-in Three.js geometries (`BoxGeometry`, `SphereGeometry`, `CylinderGeometry`)
- Keep polygon count low: <10,000 total triangles in scene
- No external model loading (GLTF/OBJ) in MVP - simplifies asset pipeline

**Optimization Techniques**:
- Object pooling for projectiles (reuse geometries and materials)
- Single draw call per entity type where possible
- Manual frustum culling for off-screen projectiles
- `renderer.render()` called once per frame in `requestAnimationFrame` loop

## Alternatives Considered

### 1. **Babylon.js**
**Pros**:
- More game-focused features out of the box (collision helpers, scene optimizer)
- Better TypeScript support (written in TypeScript)
- Built-in physics engine integration

**Cons**:
- Larger bundle size (~800KB vs Three.js ~600KB)
- Smaller community and learning resources
- Less familiar to web developers (Three.js more common)

**Why not chosen**: Bundle size exceeds target, Three.js has better educational resources and community support.

### 2. **PlayCanvas Engine**
**Pros**:
- Full game engine with editor
- Excellent performance (used in commercial games)
- Built-in entity system and scripting

**Cons**:
- Requires cloud-based editor (not pure code approach)
- Steeper learning curve for developers unfamiliar with game engines
- Less control over architecture (engine-opinionated)

**Why not chosen**: We want code-first approach for educational value, not editor-based workflow.

### 3. **Raw WebGL (No Framework)**
**Pros**:
- Maximum control over rendering
- Smallest possible bundle size
- Educational for low-level graphics concepts

**Cons**:
- 10x more development time (matrix math, shader management, etc.)
- Error-prone (manual state management)
- Not practical for 2-3 week timeline

**Why not chosen**: Development timeline too short, Three.js abstractions save significant time without sacrificing performance.

### 4. **Unity WebGL Export**
**Pros**:
- Professional game engine with full tooling
- Drag-and-drop development
- Advanced features (physics, animation, etc.)

**Cons**:
- Massive bundle size (5-10 MB minimum)
- Long load times (20-30 seconds typical)
- Not web-native (awkward browser integration)

**Why not chosen**: Bundle size and load time violate NFR-001 requirements.

## Consequences

### Positive
- ✅ Proven performance: Three.js handles our scale easily (many projects with >60 FPS)
- ✅ Bundle size target achievable: Three.js core ~150KB gzipped
- ✅ Excellent documentation and community support (StackOverflow, Discord, examples)
- ✅ Familiar to web developers (JavaScript-first API, no new IDE)
- ✅ Educational: Clear API, readable source code, many learning resources
- ✅ Future-proof: Active development, regular releases, WebGPU support planned

### Negative
- ❌ Game-specific features require manual implementation (entity system, physics, AI)
- ❌ No visual editor (all code-based) - longer initial setup
- ❌ Shader debugging can be painful (WebGL error messages are cryptic)
- ❌ Must manually manage performance optimizations (no auto-optimizer)

### Neutral
- Performance profiling needed: Must use browser DevTools + stats.js to monitor FPS
- Abstraction level: High enough for productivity, low enough for control
- Versioning: Pinning to r150+ ensures API stability but requires manual upgrades

## Implementation Notes

**Setup Code** (initialization):
```typescript
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x000000, 10, 50); // Optional: depth cueing

const camera = new THREE.PerspectiveCamera(
  75, // FOV
  window.innerWidth / window.innerHeight, // Aspect
  0.1, // Near plane
  100 // Far plane
);
```

**Performance Monitoring**:
```typescript
import Stats from 'three/examples/jsm/libs/stats.module';

const stats = new Stats();
document.body.appendChild(stats.dom);

function animate() {
  stats.begin();
  // ... game update logic ...
  renderer.render(scene, camera);
  stats.end();
  requestAnimationFrame(animate);
}
```

## Validation Criteria

Before this ADR is considered successful in production:
- [ ] Achieve 60 FPS with 5 enemies, 10 projectiles (Chrome DevTools Performance tab)
- [ ] Bundle size < 500KB gzipped (Vite build output)
- [ ] No visual artifacts or z-fighting (manual testing)
- [ ] Renders correctly on all target browsers (manual cross-browser testing)

## Related Decisions
- [ADR-0002: Collision Detection Strategy](./0002-collision-detection-strategy.md) - Collision relies on Three.js raycasting
- [ADR-0003: Entity Component System Architecture](./0003-entity-component-system.md) - Entities reference Three.js Mesh objects
- [ADR-0005: Asset Loading Strategy](./0005-asset-loading-strategy.md) - Three.js loaders not used in MVP

## References
- Three.js Documentation: https://threejs.org/docs/
- Three.js Examples: https://threejs.org/examples/
- Three.js Fundamentals: https://threejs.org/manual/
- WebGL Performance Best Practices: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices
