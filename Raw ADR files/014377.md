# Stick to 2D Rendering for Dance Visualization

![Status: Accepted](https://img.shields.io/badge/status-accepted-brightgreen)

## Date

📅 2024-06-01

## Context

The game currently uses Bevy's 2D camera system for rendering. Player and choreography motion is
captured using MediaPipe Pose, which provides x, y, z coordinates for each joint. The Z dimension is
relative (not absolute depth), derived from a monocular camera.

The game's intended presentation style is inspired by dance games like "Just Dance", where dancers
are shown from a fixed front-facing perspective.

## Decision

We will continue using Bevy's 2D rendering system.

Although MediaPipe provides a Z dimension, it is not suitable for absolute 3D rendering due to its
relative nature. Most choreography content is designed around a fixed viewpoint, making 2D a natural
fit.

2D simplifies:

* Pose comparison and scoring
* Visual clarity
* Cross-platform rendering, including WebAssembly

We will retain Z data in pose serialization and optionally use it to enhance 2D rendering (e.g.,
darken or scale limbs based on depth).

## Consequences

* 3D rendering and true camera-space depth are not supported (yet).
* Any depth-aware animations must be simulated in 2D.
* Future features like rotating viewpoints or AR-style projections may require refactoring.

## Alternatives Considered

| Option                   | Pros                                 | Cons                                     |
| ------------------------ | ------------------------------------ | ---------------------------------------- |
| Use 3D view              | Allows richer scene layout, Z-motion | More complex; Z is not fully reliable    |
| Hybrid 2.5D              | Fake depth via layering              | Requires custom rendering hacks          |
| True 3D with calibration | Better posture modeling              | Requires calibration, hardware, redesign |

## Related

* ADR 001: [Use Bevy for Visualization and Game Logic](001-use-bevy.md)
* ADR 002: [Use MediaPipe Pose Landmarker for Pose Detection](002-use-mediapipe.md)

