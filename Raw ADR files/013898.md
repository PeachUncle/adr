# ADR-0002: Simulation Boundary and Visualization Approach

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** 003-ros2-nervous-system
- **Context:** The module needs to define clear boundaries between what content belongs in Module 1 versus Module 2 to avoid overlap and maintain focused learning objectives. This decision affects how URDF visualization and simulation content is structured.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- Allowed: URDF/SDF creation, RViz visualization, joint state publishers, robot state publishers
- Not allowed: Physics simulation, sensor noise modeling, or environment interaction (reserved for Module 2)
- Validation method: URDF loads correctly in rviz2 with robot_state_publisher and displays all links/joints

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- Clear separation of concerns between Module 1 and Module 2
- Focused learning objectives without content overlap
- Proper scoping for each module's specific purpose
- Maintains educational coherence

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

- May limit comprehensive examples that would show full integration
- Readers may expect more complete simulation examples
- Potential confusion about where to find complete solutions

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

Alternative A: Full Gazebo physics simulation in Module 1
- Rejected due to violation of Module 2 scope and potential content overlap

Alternative B: No visualization at all
- Rejected as it would limit the ability to verify URDF correctness

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: E:/New folder/New folder/physical-ai-humanoid-robotics/specs/003-ros2-nervous-system/spec.md
- Implementation Plan: E:/New folder/New folder/physical-ai-humanoid-robotics/specs/003-ros2-nervous-system/plan.md
- Related ADRs: ADR-0001, ADR-0003
- Evaluator Evidence: Plan analysis showing requirements for clear Module 1/2 boundaries <!-- link to eval notes/PHR showing graders and outcomes -->
