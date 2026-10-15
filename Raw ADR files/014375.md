# Use Bevy for Visualization and Game Logic

![](https://img.shields.io/badge/status-accepted-brightgreen)

## Date

📅 2024-06-01

## Context

We require a game engine or rendering framework to visualize both prerecorded and live pose data  
for a camera-controlled game. The system should support:

- Real-time 2D/3D rendering of skeletal movement
- Integration with Rust for performance and safety
- A modern architecture that fits the data-driven nature of pose inputs
- Flexibility to build interactive game logic (e.g., scoring, timing, choreography playback)
- Long-term maintainability

Bevy is a modern game engine written in Rust. It provides a powerful ECS (Entity-Component-System)  
architecture, real-time rendering, and excellent modularity.

However, Bevy is still evolving rapidly and introduces breaking changes frequently. The API  
surface is not fully stable yet, and ecosystem maturity is still developing.

Alternatives considered:

- **Godot** (Rust bindings, but complex integration and less idiomatic)
- **Macroquad / ggez** (lightweight but limited in modularity and extensibility)
- **Unity/Unreal** (too heavyweight for this project, with additional language/runtime concerns)

## Decision

We will use **Bevy** as our rendering and game logic engine.

Justifications:
- Seamless integration with our existing Rust-based backend
- Excellent fit for pose-driven, data-centric architecture via ECS
- Strong community and rapidly growing ecosystem
- Declarative, clean syntax and reactive system model align with project goals
- Future-proof for building more sophisticated game mechanics and interactions

We accept the tradeoff of potential breaking changes in exchange for the flexibility and power  
Bevy provides, particularly in early-stage prototyping and real-time motion visualization.

## Consequences

- We will need to track Bevy version updates and adjust code as needed during development
- Dependencies will be locked to specific versions in `Cargo.toml` to ensure reproducibility
- Some experimental features may require unstable Bevy APIs or plugins
- Long-term performance and maintainability are supported by the Rust-native stack

