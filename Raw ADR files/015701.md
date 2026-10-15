# ADR-0015: Manifest-Driven 3D Diagram Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-03
- **Feature:** 004-3d-diagrams
- **Context:** The book contains over 12 diagrams that follow similar patterns (Node Graphs, Coordinate Trees, Point Cloud Visualizations). Hardcoding each diagram as a separate React component would lead to code duplication and make it difficult for non-developer authors to add or modify diagrams.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will adopt a **Manifest-Driven Architecture** using a generic **Builder Pattern**.

- **Data Source**: A single `static/3d/manifest.json` file defines all diagrams.
- **Schema**: Each entry contains `type` (`flow`, `robot`, `pointcloud`) and `config` (nodes, edges, model paths).
- **Builders**: TypeScript classes (`FlowBuilder`, `RobotBuilder`) responsible for interpreting the config and generating 3D objects.
- **Usage**: Markdown files simply reference the diagram ID: `<ThreeDiagram id="chapter-1-node-graph" />`.

## Consequences

### Positive

- **Scalability**: Adding a new "Flow" diagram requires only JSON editing, no code changes.
- **Maintainability**: Logic for rendering "Nodes" or "Edges" is centralized in one Builder. Fixing a bug fixes all diagrams.
- **Decoupling**: Content authors don't need to know TypeScript or Three.js.

### Negative

- **Flexibility Constraints**: If a diagram requires a unique visual feature not supported by the `Builder`, the Builder must be extended (feature creep risk) or a "Custom" type used.
- **Schema Versioning**: Changes to the manifest schema might break existing diagrams if not handled carefully.

## Alternatives Considered

**Alternative A: Individual Components (`<Chapter1Graph />`)**
- **Pros**: Maximum flexibility, easy to hack specific interactions.
- **Cons**: Massive code duplication. Maintenance nightmare if we decide to change the "Node" visual style globally.
- **Why Rejected**: Violates DRY (Don't Repeat Yourself) and makes global styling updates difficult.

**Alternative B: MDX Props (`<ThreeDiagram nodes={...} />`)**
- **Pros**: Keeps data close to the content text.
- **Cons**: Passing complex JSON structures (nested arrays of objects) via MDX props is error-prone and clutters the Markdown file.
- **Why Rejected**: Separation of concerns; we want the "Database" of diagrams to be manageable separately from the prose.

## References

- Feature Spec: specs/004-3d-diagrams/spec.md
- Implementation Plan: specs/004-3d-diagrams/plan.md
- Data Model: specs/004-3d-diagrams/data-model.md
- Related ADRs: 0014-three-js-visualization-engine-strategy.md
- Evaluator Evidence: N/A