# ADR-0001: ROS 2 Distribution Choice

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-08
- **Feature:** 001-beginner-humanoid-textbook
- **Context:** The textbook targets undergraduate and graduate students new to physical AI, assuming only basic Python knowledge. A stable and well-documented ROS 2 distribution is crucial for a beginner-friendly learning experience, minimizing setup issues and unexpected breakages. The decision involves choosing between a long-term support (LTS) release with established documentation and community support, and a more recent, potentially less stable, distribution.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

The ROS 2 distribution chosen is Jazzy Jalisco (stable LTS, May 2024–2029).

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

Better beginner tutorials and documentation. Avoids unexpected breaking changes, providing a more stable and predictable learning environment for students.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

Misses the absolute latest features and potentially cutting-edge advancements available in rolling releases. However, for a beginner textbook, stability and well-documented features are prioritized over bleeding-edge functionality.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

ROS 2 Rolling Ridley: This is the bleeding-edge distribution of ROS 2. It offers the latest features and bug fixes but has a shorter support cycle and less stable API. Rejected because its rapidly changing nature and potential for breakage are not suitable for a beginner-focused textbook where stability and well-established documentation are paramount.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: /specs/001-beginner-humanoid-textbook/spec.md
- Implementation Plan: /specs/001-beginner-humanoid-textbook/plan.md
- Related ADRs: {{RELATED_ADRS}}
- Evaluator Evidence: {{EVAL_NOTES_LINK}} <!-- link to eval notes/PHR showing graders and outcomes -->
