# ADR-005: D3.js for Dependency Graph Visualization

**Status:** Accepted
**Date:** 2025-11-15
**Deciders:** Alice (Architect), Charlie (Developer), Diana (UX Designer)
**Technical Story:** Epic 6 - Story 6-8 (Dependency Graph Visualization Component)

## Context and Problem Statement

The Agent Orchestrator needs to visualize story dependencies as an interactive graph. Users need to see dependency relationships, critical paths, and story status at a glance. The visualization should support pan, zoom, filtering, and export capabilities while handling graphs with 100+ nodes.

## Decision Drivers

* Flexible, customizable visualization (not template-based)
* Support for force-directed layouts
* Interactive features (pan, zoom, click, hover)
* Export capabilities (PNG, SVG)
* Performance with large graphs (100+ nodes)
* Integration with React
* SVG output for crisp rendering at any zoom level

## Considered Options

* **Option 1:** D3.js (Data-Driven Documents)
* **Option 2:** Cytoscape.js
* **Option 3:** Vis.js Network
* **Option 4:** React Flow

## Decision Outcome

**Chosen option:** "D3.js", because it provides maximum flexibility for custom visualizations, excellent force-directed layout algorithms, SVG output for export, and complete control over rendering while being the industry standard for data visualization.

### Positive Consequences

* Force-directed layout creates intuitive graph structure automatically
* SVG output enables crisp rendering at any zoom level
* Export to PNG/SVG/shareable links built-in
* Full control over node/edge rendering
* Excellent performance with virtualization (>100 nodes)
* Pan/zoom/drag interactions work smoothly
* Critical path highlighting easy to implement
* React integration via useRef + useEffect pattern

### Negative Consequences

* D3's imperative API conflicts with React's declarative model (requires careful integration)
* Learning curve for D3.js API
* More code required than template-based libraries
* Need to handle React re-renders carefully

## Pros and Cons of the Options

### Option 1: D3.js

Industry-standard data visualization library with low-level control.

**Pros:**
* Maximum flexibility and customization
* Excellent force-directed layout algorithms
* SVG output (export-friendly)
* Large ecosystem and community
* Industry standard (hiring-friendly)
* Performance optimizations available
* Complete control over rendering
* Rich interaction API

**Cons:**
* Imperative API (conflicts with React)
* Steeper learning curve
* More code than template-based libs
* Requires careful React integration

### Option 2: Cytoscape.js

Specialized graph theory library for network visualization.

**Pros:**
* Built specifically for graphs
* Good layout algorithms
* Strong performance
* Touch-friendly

**Cons:**
* Less flexible than D3
* Canvas rendering (not SVG)
* **Export more difficult** (Canvas to image)
* Smaller community than D3
* Less suitable for custom styling
* Heavier bundle (~400KB vs D3 ~200KB)

### Option 3: Vis.js Network

Complete graph visualization library with built-in UI.

**Pros:**
* Easiest to get started
* Built-in controls
* Physics simulation
* Good documentation

**Cons:**
* **Limited customization**
* Opinionated styling
* Canvas rendering (not SVG)
* Larger bundle size
* Less control over layout
* Export capabilities limited

### Option 4: React Flow

React-first library for node-based UIs.

**Pros:**
* Designed for React (declarative)
* Good for flowcharts
* Built-in controls
* Easy drag and drop

**Cons:**
* **Not optimized for force-directed graphs**
* Layout must be calculated manually
* Less suitable for dependency visualization
* Limited force simulation
* Not designed for our use case

## Links

* [D3.js Documentation](https://d3js.org/)
* [D3 Force Documentation](https://github.com/d3/d3-force)
* [D3 with React Guide](https://2019.wattenberger.com/blog/react-and-d3)
* [Epic 6 Retrospective](../epics/epic-6-retrospective.md)
* Implementation: `dashboard/src/components/graph/DependencyGraph.tsx`

## Implementation Notes

### D3 + React Integration Pattern
```typescript
const DependencyGraph: React.FC<Props> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    // D3 owns this DOM subtree
    const svg = d3.select(svgRef.current);

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges))
      .force('charge', d3.forceManyBody())
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Render nodes/edges...
  }, [data]);

  return <svg ref={svgRef} />;
};
```

### Force Simulation Parameters
- **Link Distance:** 100px (balanced spacing)
- **Charge Strength:** -300 (node repulsion)
- **Collision Radius:** 40px (prevent overlap)
- **Alpha Decay:** 0.02 (smooth stabilization)

### Virtualization for Large Graphs
- Graphs >100 nodes switch to list view automatically
- Force simulation disabled for >200 nodes
- Chunked rendering for smooth performance

### Export Capabilities
- **PNG:** Uses canvas to convert SVG to raster
- **SVG:** Direct download of SVG element
- **Shareable Links:** URL params encode filter state

### Performance Results (Story 6-8)
- **50 nodes/edges:** Smooth 60fps
- **100 nodes/edges:** 45-60fps
- **200+ nodes:** Auto-switches to list view
- **Pan/Zoom:** No lag with 100 nodes
- **Export:** <2 seconds for PNG (100 nodes)

### Accessibility
- ARIA labels on all nodes
- Keyboard navigation (Tab, Enter, Escape)
- Focus indicators
- Screen reader support via tooltips

### Challenge Overcome (3 Review Cycles)
Story 6-8 required 3 code review iterations:
1. Added edge click tooltips and keyboard navigation
2. Fixed TypeScript compilation errors
3. Final approval - all 11 acceptance criteria met

This demonstrates D3's learning curve but also its flexibility to add features incrementally.

## Review and Update History

| Date | Reviewer | Change |
|------|----------|--------|
| 2025-11-15 | Alice, Charlie, Diana | Initial decision (Story 6-8) |
| 2025-11-15 | Charlie | Review cycle 1: Added interactions |
| 2025-11-15 | Charlie | Review cycle 2: Fixed TypeScript errors |
| 2025-11-15 | Charlie | Review cycle 3: APPROVED ✅ |
| 2025-11-16 | Bob | Documented in ADR with performance data |
