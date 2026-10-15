# ADR-0002: Core Content Technologies: Python 3.11+ and ROS 2 Humble

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

-   **Status:** Proposed
-   **Date:** 2025-11-30
-   **Feature:** 001-physical-ai-robotics-book
-   **Context:** The textbook focuses on Physical AI and Humanoid Robotics. Python is a widely used language in robotics, and ROS 2 is the leading framework for robot application development. The content needs to be current and align with industry standards to provide relevant and practical knowledge.

## Decision

Python 3.11+ and ROS 2 Humble are selected as the core content technologies. All code examples and lab exercises will adhere to these standards.
    -   Programming Language: Python 3.11+
    -   Robotics Framework: ROS 2 Humble

## Consequences

### Positive

Aligns with current industry practices and academic trends, provides a strong foundation for practical robotics, offers access to a vast ecosystem of tools and libraries, ensures the content is relevant and future-proof for students, and allows for easier integration with simulation platforms.

### Negative

Requires students to have a basic understanding of Python. The rapid evolution of ROS 2 might necessitate periodic content updates to maintain currency.

## Alternatives Considered

-   **C++ for ROS**: While C++ is integral to ROS 2 for performance-critical components, Python is generally more accessible for beginners and allows for quicker prototyping and clearer code examples in a textbook context.
-   **Older ROS versions (e.g., ROS 1)**: ROS 1 is nearing end-of-life and lacks many of the new features and improvements found in ROS 2, making it less future-proof for a new textbook.
-   **Other robotics frameworks (e.g., Robot Operating System (ROS) alternatives)**: While alternatives exist, ROS has the largest community, comprehensive tooling, and widespread adoption in both academia and industry, making it the most beneficial choice for a foundational textbook.

## References

-   Feature Spec: specs/001-physical-ai-robotics-book/spec.md
-   Implementation Plan: specs/001-physical-ai-robotics-book/plan.md
-   Related ADRs: null
-   Evaluator Evidence: null
