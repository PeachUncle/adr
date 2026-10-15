# Use visx for Network Visualization

## Purpose
This document records the decision to use visx instead of D3.js directly for network visualization in Phase 3.

## Classification
- **Domain:** Technology Selection
- **Stability:** Semi-stable
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context
The original technology stack specified D3.js for network visualization in Phase 3. While D3.js is powerful and flexible, it requires significant low-level implementation work and can be challenging to integrate cleanly with React's component model and declarative paradigm.

visx is a collection of low-level visualization components for React built on top of D3.js. It provides:
- React-first API that works naturally with React patterns
- Composable primitives that align with React component architecture
- D3.js calculations under the hood (scales, shapes, layouts)
- Better TypeScript support out of the box
- Maintained by Airbnb with active development

### Decision
Use visx (@visx/\* packages) instead of D3.js directly for implementing the network visualization feature in Phase 3.

### Status
Accepted

### Consequences

**Positive consequences:**
- More idiomatic React code with better component composition
- Reduced complexity in managing D3.js lifecycle with React
- Built-in TypeScript definitions improve developer experience
- Easier to maintain and test visualization components
- Better separation of concerns (visx handles rendering, D3 handles calculations)

**Negative consequences:**
- Additional dependency (though visx uses D3.js internally, so not really "more" dependencies)
- Slightly less flexibility than raw D3.js for extremely custom visualizations
- Team needs to learn visx API in addition to D3 concepts

**Risks introduced:**
- visx is less widely adopted than D3.js directly (smaller community)
- Potential visx-specific bugs or limitations
- If visx is abandoned, migration back to D3.js would be needed

**Trade-offs made:**
- Trading ultimate flexibility for better React integration and developer experience
- Accepting a higher-level abstraction that may limit some advanced D3.js techniques

### Alternatives Considered

#### Alternative 1: D3.js Directly
Use D3.js directly as originally specified in the technology stack.

**Pros:**
- Maximum flexibility for custom visualizations
- Largest community and ecosystem
- Most Stack Overflow answers and examples available
- Direct control over all rendering details

**Cons:**
- Requires careful lifecycle management with React (refs, useEffect, cleanup)
- Imperative API clashes with React's declarative model
- More boilerplate code for common patterns
- Harder to compose with other React components
- Manual TypeScript type definitions often needed

#### Alternative 2: React Flow
Use React Flow library specifically designed for node-based UIs.

**Pros:**
- Built specifically for node graphs with React
- Rich feature set (zoom, pan, minimap, edge routing)
- Excellent React integration
- Active development and good documentation

**Cons:**
- Opinionated about graph structure and behavior
- May be overkill for simpler visualizations
- Heavier dependency (larger bundle size)
- Less suitable for force-directed layouts (Bartleby's primary use case)

#### Alternative 3: Recharts
Use Recharts for all visualization needs.

**Pros:**
- Very high-level, quick to implement
- Good for standard charts
- Excellent React integration

**Cons:**
- Not designed for network/graph visualizations
- Not suitable for force-directed layouts
- Limited customization for non-standard viz types

### Implementation Notes

**Package installation for Phase 3:**
```bash
npm install @visx/network @visx/group @visx/scale @visx/zoom @visx/drag @visx/tooltip
npm install --save-dev @types/d3-force  # For force simulation types
```

**Key visx packages for network visualization:**
- `@visx/network` - Core graph/network components
- `@visx/zoom` - Zoom and pan functionality
- `@visx/drag` - Node dragging
- `@visx/tooltip` - Hover tooltips for nodes/edges
- `@visx/group` - SVG group components
- `@visx/scale` - D3 scales wrapped for React

**Integration approach:**
- Use D3's force simulation for layout calculations
- Use visx components for rendering SVG elements
- Manage force simulation in React state/effects
- Use visx's event handlers for interaction

**Note:** D3.js will still be used internally by visx and may be used directly for force simulation calculations that visx doesn't wrap.

## Relationships
- **Parent Nodes:** [decisions/003-technology-stack.md]
- **Child Nodes:** None
- **Related Nodes:**
  - [elements/frontend-app/overview.md] - updates - Changes visualization technology
  - [planning/roadmap.md] - refines - Clarifies Phase 3 implementation approach

## Navigation Guidance
- **Access Context:** Reference when implementing Phase 3 network visualization
- **Common Next Steps:** Review visx documentation and force-directed layout patterns
- **Related Tasks:** Network visualization implementation, component architecture
- **Update Patterns:** Revisit if visx proves insufficient or if React ecosystem shifts

## Metadata
- **Decision Number:** 005
- **Created:** 2025-11-14
- **Last Updated:** 2025-11-14
- **Updated By:** AI Agent (Claude)
- **Deciders:** Project stakeholder, AI Agent

## Change History
- 2025-11-14: Initial decision record created
