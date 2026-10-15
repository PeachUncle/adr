# ADR-0002: Simulation Toolchain Selection

- **Status:** Accepted
- **Date:** 2025-12-08
- **Feature:** 1-robotics-book-spec
- **Context:** The book requires a robust and flexible simulation strategy to cover a range of robotics concepts, from basic mechanics to advanced AI-driven perception. The choice of simulation tools directly impacts the realism, performance, and educational value of the examples.

## Decision

The project will adopt a multi-tool simulation strategy, leveraging:

- **Gazebo:** For foundational ROS 2 integration and basic robotics simulations.
- **Unity:** For high-quality visualizations and scenarios where game engine features are beneficial.
- **NVIDIA Isaac Sim:** For high-fidelity physics simulation, advanced sensor modeling, and perception-based AI training.

## Consequences

### Positive

- **Comprehensive Coverage:** The combination of tools covers the full spectrum from classic robotics simulation to cutting-edge, GPU-accelerated digital twins.
- **Industry Relevance:** Exposes readers to multiple industry-standard tools, enhancing the practical value of their skills.
- **Best Tool for the Job:** Allows each concept to be demonstrated in the most appropriate environment (e.g., Isaac Sim for realistic sensor data, Unity for compelling visuals).

### Negative

- **High Learning Curve:** Readers will need to install and learn the basics of three separate, complex software packages.
- **Increased Asset Maintenance:** Simulation assets (worlds, models) may need to be adapted or recreated for different platforms, increasing the maintenance overhead.
- **System Requirements:** The hardware requirements, especially for NVIDIA Isaac Sim, are significant.

## Alternatives Considered

### Single-Tool Strategy (e.g., Gazebo only)

- **Description:** Standardize on a single simulation tool, like Gazebo, for all examples to simplify the learning path.
- **Reason for Rejection:** While simpler, a single tool cannot adequately cover the project's ambitious scope. Gazebo is excellent for many ROS 2 tasks but lacks the high-fidelity rendering of Unity or the GPU-accelerated physics and perception capabilities of Isaac Sim, which are critical for the book's later chapters.

## References

- **Implementation Plan:** D:\Quarter 4\ai-book\humanoid-robotic-book\specs\1-robotics-book-spec\plan.md
- **Related ADRs:** None
