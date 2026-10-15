# ADR-0004: Hardware Considerations: Unitree G1/Go2 Robot Specifications

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

-   **Status:** Proposed
-   **Date:** 2025-11-30
-   **Feature:** 001-physical-ai-robotics-book
-   **Context:** The textbook aims to provide practical knowledge relevant to real-world robotics. Discussing specific, industry-relevant hardware allows for concrete examples of sim-to-real transfer and addressing hardware constraints, grounding theoretical concepts in tangible applications. The Unitree G1/Go2 robots are prominent humanoid/quadrupedal platforms suitable for illustrating these concepts.

## Decision

Unitree G1/Go2 robot specifications will be referenced for discussions on hardware implications, sim-to-real transfer, and deployment challenges.
    -   Reference Hardware: Unitree G1/Go2 robots

## Consequences

### Positive

Provides tangible, real-world examples for students, grounding theoretical concepts in practical applications. Facilitates detailed discussions on real-world challenges such as hardware limitations, sensor noise, actuator constraints, and safety protocols. Makes the content more appealing and relevant to those interested in real robot deployment and hands-on robotics.

### Negative

Specific hardware references can become outdated as robot technology rapidly evolves, necessitating periodic updates to the textbook content. While Unitree robots are relatively accessible, they still represent a significant investment, and referencing them might create an expectation that students need these specific robots for practical learning, which might not be feasible for all readers.

## Alternatives Considered

-   **General Robotics Hardware**: Discussing generic robot hardware without specific models would be less concrete and harder for students to visualize and connect with. It would lack the specificity needed for detailed discussions on real-world constraints and sim-to-real challenges.
-   **Other Humanoid/Quadrupedal Platforms**: While other advanced platforms exist (e.g., Boston Dynamics Spot, Agility Robotics Digit), Unitree robots currently offer a good balance of capability, research adoption, and relative accessibility for academic and educational purposes, making them a suitable choice for discussion in a textbook.

## References

-   Feature Spec: specs/001-physical-ai-robotics-book/spec.md
-   Implementation Plan: specs/001-physical-ai-robotics-book/plan.md
-   Related ADRs: null
-   Evaluator Evidence: null
