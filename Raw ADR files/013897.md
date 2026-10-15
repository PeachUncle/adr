# ADR-0001: ROS 2 Distribution and Development Environment

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** 003-ros2-nervous-system
- **Context:** The module needs to establish a consistent and stable development environment for ROS 2 humanoid robotics content. This decision impacts all code examples, compatibility requirements, and long-term maintainability of the educational content. The target audience includes engineers, researchers, and students who need reproducible examples that work in real environments.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- ROS 2 Distribution: Jazzy Jalisco (LTS, May 2024 - 2029)
- Operating System: Ubuntu 22.04 LTS
- Python Version: 3.10 (default in Ubuntu 22.04)
- Target Hardware: NVIDIA Jetson Orin Nano (8GB) as minimal edge platform
- Development Environment: RTX 4070 Ti+ workstation or AWS g5.2xlarge (Ubuntu 22.04 AMI)

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- Long-term stability and support through 2029 with Jazzy LTS
- Industrial and educational adoption with NVIDIA Isaac ROS support
- Compatibility with hardware platforms used in humanoid robotics
- Consistent environment for reproducible examples
- Reduced maintenance burden with stable API surface

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

- May miss newer features available in later ROS 2 releases
- Potential for content to appear less cutting-edge than using newest releases
- Lock-in to specific Ubuntu and Python versions
- Possible need for backporting of newer features if required

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

Alternative A: ROS 2 Kilted Kaiju (May 2025) with newer features
- Rejected due to less stability, documentation, and industrial support
- Risk of breaking changes during the module development timeline

Alternative B: ROS 2 Humble Hawksbill (current LTS at time of planning)
- Rejected in favor of Jazzy due to NVIDIA Isaac ROS support and longer support timeline

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: E:/New folder/New folder/physical-ai-humanoid-robotics/specs/003-ros2-nervous-system/spec.md
- Implementation Plan: E:/New folder/New folder/physical-ai-humanoid-robotics/specs/003-ros2-nervous-system/plan.md
- Related ADRs: ADR-0002, ADR-0003
- Evaluator Evidence: Plan analysis showing requirements for stability and industrial adoption <!-- link to eval notes/PHR showing graders and outcomes -->
