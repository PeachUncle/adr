---
canonical: true
created: '2025-11-20'
doc_id: ADR-00003
doc_type: adr
related: []
status: active
summary: Accepted
supersedes: []
tags:
  - adr
  - ecs
  - plugins
  - rendering
  - testing
title: 'ADR-0003: ECS Split Between Shared.ECS and Content.ECS'
---

# ADR-0003: ECS Split Between Shared.ECS and Content.ECS

## Status

Accepted

## Context

Per RFC-005 the .NET solution is being reorganized into tiers:

- **app-essential** – shells, plugin host, UI entry points
- **game-essential** – shared game domain, reusable ECS and rendering primitives
- **content-authoring** – game/content-specific ECS, rendering, data assets

Originally, ECS concepts in the project were mixed between reusable engine-like pieces and content/game-specific components and systems. As part of the "heavy" content split we want:

- A small, reusable **engine-level ECS** layer that can support multiple games.
- A separate **content ECS** layer that holds game-specific components and systems.
- A clear dependency direction where engine-level ECS does **not** depend on content.

## Decision

We split ECS into two layers/projects:

1. **Engine-level ECS primitives**
   - **Project:** `dotnet/Shared/PigeonPea.Shared.ECS`
   - **Responsibility:**
     - Provide the core ECS building blocks used across games.
     - Wrap/compose the `Arch` ECS library in a way that is idiomatic for PigeonPea.
     - Define base component and system patterns that are not tied to a specific game domain.
   - **Dependencies:**
     - Only `Arch` and the .NET base class library.
   - **Consumers:**
     - Game-essential projects (shared game logic, map/dungeon logic, rendering).
     - Content-authoring ECS and systems via composition, not the other way around.

2. **Content / game-specific ECS**
   - **Project:** `dotnet/content-authoring/core/src/PigeonPea.Content.ECS`
   - **Responsibility:**
     - House ECS components and systems that are specific to a particular game or content pack.
     - Coordinate with game domain models (e.g., world/dungeon/map models) defined in game-essential projects.
   - **Dependencies:**
     - May depend on game-essential domain projects as needed (e.g., map/dungeon domain models).
   - **Consumers:**
     - Game-specific control/rendering layers (e.g., dungeon control/rendering, map rendering).
     - App shells that host content through the plugin system.

## Rationale

- **Reusability:**
  - Keeping `PigeonPea.Shared.ECS` minimal and generic allows multiple games or content packs to share the same ECS foundation.

- **Separation of concerns:**
  - Content-specific behavior (components and systems that only make sense for a given game) lives in `PigeonPea.Content.ECS` instead of polluting the engine-level ECS layer.

- **Dependency direction:**
  - Engine-tier ECS must not depend on content-authoring projects.
  - Content ECS is allowed to depend on engine-tier ECS and game-essential domain models.
  - This makes it possible to ship engine assemblies independently of content.

- **Future plugin system alignment:**
  - Content ECS can align with the plugin system so that content packs provide ECS components/systems via pluggable assemblies, while consumers only require the engine-level ECS contracts.

## Consequences

### Positive

- **Cleaner layering:**
  - `PigeonPea.Shared.ECS` is clearly identified as the canonical ECS foundation.
  - `PigeonPea.Content.ECS` is the place for game/content-specific ECS behavior.

- **Easier evolution:**
  - Engine ECS can evolve with a strong focus on stability and backwards compatibility.
  - Content ECS can iterate more quickly with fewer constraints, since it is not depended on by engine-tier projects.

- **Better test boundaries:**
  - Tests targeting ECS primitives can be written against `PigeonPea.Shared.ECS`.
  - Higher-level behavior tests that involve specific components/systems can be associated with `PigeonPea.Content.ECS` and game-essential projects.

### Negative / Trade-offs

- **More projects and references:**
  - The solution has an extra ECS project and additional `ProjectReference` edges to manage.

- **Boundary discipline required:**
  - Contributors must take care to place new ECS types in the correct project:
    - Engine-wide utilities and patterns go to `PigeonPea.Shared.ECS`.
    - Game/content-specific components and systems go to `PigeonPea.Content.ECS`.

## Implementation Notes

- **Project files today:**
  - `PigeonPea.Shared.ECS.csproj` targets `net9.0` and references the `Arch` package; it has no project references to game/content projects.
  - `PigeonPea.Content.ECS.csproj` targets `net9.0` and currently has no additional references; game-specific dependencies should be added here rather than to the engine-tier ECS project.

- **Guidelines for new ECS code:**
  - When adding a new component or system:
    - If it is generic and reusable across games, add it to `PigeonPea.Shared.ECS`.
    - If it is specific to a particular game, scenario, or content pack, add it to `PigeonPea.Content.ECS` (or a future content ECS project in the content-authoring tier).
  - Keep engine-level ECS independent from map/dungeon/content-specific domain models.

## Future Work

- Introduce more explicit engine-level ECS abstractions (e.g., base systems or pipelines) where appropriate in `PigeonPea.Shared.ECS`.
- Flesh out `PigeonPea.Content.ECS` with clearly named namespaces for different content areas (e.g., dungeon, overworld, UI state) while keeping domain models in game-essential projects.
- Align content ECS with the plugin system so content packs can be loaded/unloaded via plugins without changing engine-tier ECS assemblies.
