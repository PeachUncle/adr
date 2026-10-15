# ADR-0014: Three.js Visualization Engine Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-03
- **Feature:** 004-3d-diagrams
- **Context:** The project requires replacing static 2D Mermaid diagrams with interactive 3D visualizations to illustrate robotics concepts (nodes, transforms, point clouds). The environment is a Docusaurus site (React-based). We need a solution that is performant, lightweight, and allows for precise control over procedural generation of diagrams (node graphs).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use **Vanilla `three.js` wrapped in a generic React component** (`ThreeDiagram/Engine.ts`).

- **Core Library**: `three` (v0.160+)
- **Integration**: Custom `useEffect` hook managing the `WebGLRenderer` lifecycle.
- **Helpers**: `OrbitControls` for navigation, `GLTFLoader` for models.
- **UI Overlays**: Standard HTML/CSS overlay for labels (instead of 3D text) for accessibility and readability.

## Consequences

### Positive

- **Performance**: Direct control over the render loop allows us to optimize for static graphs (render on demand vs continuous loop).
- **Standardization**: Standard Three.js API is widely documented and stable; no "React-wrapper" abstraction leaks.
- **Simplicity**: Avoids the learning curve and abstraction overhead of `@react-three/fiber` for simple procedural graphs.
- **Accessibility**: Using HTML overlays for text ensures screen readers can still access labels.

### Negative

- **Boilerplate**: Requires manual handling of resize events, clean-up (dispose geometries/materials), and mount/unmount logic.
- **Imperative Code**: The scene construction logic will be imperative (e.g., `scene.add(mesh)`), which contrasts with React's declarative nature.

## Alternatives Considered

**Alternative A: `@react-three/fiber` (R3F)**
- **Pros**: Declarative, "React-way" of doing 3D, vast ecosystem (`@react-three/drei`).
- **Cons**: Introduces significant abstraction. For procedurally generated node graphs defined by JSON, the declarative model can sometimes be more verbose or require complex memoization to avoid re-renders.
- **Why Rejected**: We prefer a "Builder" pattern (imperative generation from JSON) which maps cleaner to vanilla Three.js for this specific use case.

**Alternative B: Babylon.js**
- **Pros**: Extremely feature-rich, great WebXR support out of the box.
- **Cons**: Larger bundle size, different API paradigm than the more common Three.js examples found in the robotics community (e.g., `ros3djs`).
- **Why Rejected**: Bundle size concerns for a documentation site.

## References

- Feature Spec: specs/004-3d-diagrams/spec.md
- Implementation Plan: specs/004-3d-diagrams/plan.md
- Related ADRs: 0001-textbook-frontend-framework-docusaurus.md
- Evaluator Evidence: N/A