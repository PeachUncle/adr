# ADR-001: Vision-Language-Action (VLA) System Architecture for Humanoid Robots

## Status
Accepted

## Date
2025-12-18

## Context
The Physical AI & Humanoid Robotics Book requires a comprehensive Module 4 covering Vision-Language-Action (VLA) systems. The architecture must enable humanoid robots to understand natural language commands and execute complex tasks by integrating perception, reasoning, and action in a unified framework.

The system needs to process voice commands through a complete pipeline from speech recognition to physical manipulation while maintaining safety, reliability, and educational value for the target audience of senior undergraduate and graduate students, AI/Robotics researchers, and engineers.

## Decision
We will implement a layered VLA architecture with three distinct components:

1. **Perception Layer**: Computer vision systems for object detection, scene understanding, and environment mapping
2. **Reasoning Layer**: Large Language Models (LLMs) for cognitive planning and task decomposition
3. **Execution Layer**: ROS 2 action servers for low-level robot control and manipulation

Additionally, we will:
- Use LLMs as cognitive planners rather than direct controllers
- Implement a simulation-first validation approach using Isaac Sim
- Integrate with ROS 2 Actions for robot control
- Maintain clear architectural boundaries between perception, reasoning, and execution layers

## Rationale
The layered architecture provides several benefits:
- **Modularity**: Each layer can be developed, tested, and updated independently
- **Safety**: Clear separation between high-level planning and low-level control
- **Maintainability**: Well-defined interfaces between components
- **Scalability**: Individual components can be enhanced without affecting others

Using LLMs as planners rather than controllers ensures safety by maintaining ROS 2's proven control systems while leveraging LLMs' reasoning capabilities for task decomposition.

The simulation-first approach allows for safe testing and validation before real-world deployment, reducing risk and development costs.

## Alternatives Considered
- **End-to-end monolithic system**: Would have provided better performance but reduced safety and maintainability
- **Direct LLM control**: Would have been more responsive but significantly less safe
- **Hardware-in-the-loop first**: Would have been more realistic but higher risk and cost

## Consequences
### Positive
- Improved safety through separation of planning and control
- Better maintainability with modular architecture
- Reduced development risk through simulation-first approach
- Clear educational value through well-defined system boundaries

### Negative
- Potential performance overhead from inter-layer communication
- Increased system complexity
- Additional coordination requirements between layers

## Implementation
The architecture is implemented in Module 4 with:
- Chapter 1 covering VLA foundations and architectural patterns
- Chapter 2 detailing voice processing and cognitive planning
- Chapter 3 presenting the complete integrated system
- All content following academic textbook standards with APA citations

## References
- Module 4 specification: specs/module-4-vla-robotics/spec.md
- Module 4 architecture plan: specs/module-4-vla-robotics/plan.md
- RT-1, RT-2, and VIMA research papers referenced in educational content