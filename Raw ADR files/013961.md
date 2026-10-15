---
canonical: true
created: '2025-11-20'
doc_id: ADR-00004
doc_type: adr
related: []
status: active
summary: Accepted
supersedes: []
tags:
  - adr
  - agents
  - architecture
  - ecs
  - plugins
  - rendering
  - terminal
title: 'ADR-0004: Mapsui Integration, Zoomable World, and External Map Stacks'
---

# ADR-0004: Mapsui Integration, Zoomable World, and External Map Stacks

## Status

Accepted

## Context

The .NET solution is being reorganized per RFC-005 into tiered areas:

- **app-essential** – entry points, plugin host, UI shells (console, Windows, etc.).
- **game-essential** – shared game domain, ECS, rendering and map/dungeon logic.
- **engine** – reusable ECS + rendering primitives.
- **content-authoring** – tools and pipelines for authoring/previewing game content.

For the world-map side of the game, we want a **zoomable world** experience:

- At high level, world/continent view similar to real-world maps (OpenStreetMap-like).
- At deeper zoom, regional/city views.
- At deepest zoom, transition into dungeon views (driven by `PigeonPea.Dungeon.*`).

The implementation will use external map libraries:

- **Mapsui** – interactive map viewer (pan/zoom, layers, etc.).
- **BruTile** – tile source abstraction for HTTP/WMTS/MBTiles/custom tiles.
- **VectorTile / NTS** – vector geometry and tiled vector data for future real-world overlays.

We already have:

- `engine/core/src/PigeonPea.Shared.Rendering` – engine-level `Viewport`, tiles, renderer abstractions.
- `game-essential/core/src/PigeonPea.Map.*` and `PigeonPea.Dungeon.*` – game map and dungeon domain + rendering.
- `game-essential/core/src/PigeonPea.MapsuiAdapter` – adapter wrapping a Mapsui-like navigator and producing `Viewport`.
- `content-authoring/core/src/PigeonPea.MapsuiHost` – CLI that renders tiles from `FantasyMapGenerator.Core` + map rendering.

We need to clarify how Mapsui, BruTile, and VectorTile fit into these tiers without polluting engine code or creating bad dependency directions.

## Decision

1. **Mapsui is an app/content-layer dependency, not an engine dependency**

- Engine projects (`engine/core/src/*`) **must not reference Mapsui**.
- Mapsui usage is confined to:
  - **App shells** (e.g., a Windows Mapsui-based viewer).
  - **Content-authoring tools** (e.g., `PigeonPea.MapsuiHost` once it embeds Mapsui).
- The bridge between Mapsui navigation and the engine `Viewport` is provided by a small adapter library:
  - **Project:** `game-essential/core/src/PigeonPea.MapsuiAdapter`
  - **Responsibility:**
    - Define a minimal `IMapsuiNavigatorLike` contract.
    - Convert `CenterX/CenterY/ZoomX/ZoomY` into an engine `Viewport`.
    - Be reusable by console, Windows, or other hosts that want to drive the game map using a Mapsui-style navigator.

2. **BruTile-backed tile providers live in content-authoring / app layers**

- BruTile packages are considered **optional infrastructure**; engine and core game logic should not require them.
- Any BruTile usage (e.g., HTTP raster overlays, custom `TileSource` implementations) must live in:
  - `content-authoring` projects (e.g., a BruTile-backed tile generator for world-map tiles), and/or
  - `app-essential` / Windows-specific projects that embed Mapsui.
- Existing BruTile-based overlay code in the rasterizer remains **guarded behind preprocessor symbols** (e.g., `BRUTILE_OVERLAY`) so that BruTile is not required for the default build.

3. **VectorTile / NTS usage is kept in external or content-authoring projects**

- Real-world vector data ingestion (e.g., OSM VectorTile layers) is treated as **content pipeline logic**, not engine logic.
- VectorTile + NTS-based geometry operations live in:
  - The `_lib/fantasy-map-generator-port` projects, and/or
  - Future `content-authoring` projects responsible for:
    - Importing real-world vector data.
    - Converting it into game domain structures (`MapData`, markers, regions).
- Engine-level types (`Viewport`, `Tile`, ECS components) remain independent of VectorTile and NTS packages.

4. **Project placement for Mapsui integration**

- **`game-essential/core/src/PigeonPea.MapsuiAdapter`**
  - Depends on:
    - `engine/core/src/PigeonPea.Shared.Rendering` (for `Viewport`).
    - External Mapsui packages (for concrete navigator wrappers, if needed).
  - Does **not** depend on content-authoring projects.
  - Used by:
    - Game map control logic in `PigeonPea.Map.Control`.
    - App shells (console, Windows) and tools that want to express pan/zoom in engine terms.

- **`content-authoring/core/src/PigeonPea.MapsuiHost`**
  - Depends on:
    - `game-essential/core/src/PigeonPea.Shared`.
    - `game-essential/core/src/PigeonPea.Map.Rendering`.
    - `_lib/fantasy-map-generator-port/src/FantasyMapGenerator.Core`.
  - Currently a CLI that:
    - Generates a `MapData` via FantasyMapGenerator.
    - Uses map rendering to emit raster tiles (PNG) to disk.
  - In future, can host a Mapsui `MapControl` that:
    - Uses a BruTile provider backed by these generated tiles.
    - Uses `PigeonPea.MapsuiAdapter` to translate pan/zoom into `Viewport` for on-demand rendering.

5. **Zoomable world → dungeon transition is orchestrated in game-essential**

- The **zoom logic** (when to show world/region/city/dungeon) is expressed in game-essential projects:
  - `PigeonPea.Map.Core` / `PigeonPea.Map.Control` manage world-scale map state.
  - `PigeonPea.Dungeon.*` manage dungeon-scale state.
- External map stacks (Mapsui/BruTile/VectorTile) only influence **how** views are presented and which data is supplied, not the core rules of the game world.

## Rationale

- **Keep the engine reusable**
  - Engine-level ECS and rendering primitives should be reusable in non-Mapsui environments (console, server-side simulations, other UIs).
  - Avoiding Mapsui/BruTile/VectorTile in the engine keeps dependencies light and reduces coupling to UI frameworks and GIS libraries.

- **Make external map stacks optional**
  - Console and tests must not require Mapsui/BruTile/VectorTile to compile or run.
  - Developers can work on dungeon / gameplay features without pulling in heavy GIS dependencies.

- **Align with tiered architecture**
  - External viewers (Mapsui) and tile-fetch infrastructure (BruTile) are naturally app/content concerns.
  - Game-essential projects abstract the world in terms of `MapData`, ECS components, and `Viewport`, which app layers can visualize using various stacks (Mapsui, terminal rendering, etc.).

- **Support future real-world overlays**
  - Keeping VectorTile/NTS integration in content-authoring or `_lib` projects lets us experiment with real-world map overlays and data conversion without polluting core game logic.

## Consequences

- `PigeonPea.MapsuiAdapter` and `PigeonPea.MapsuiHost` are now **placed and referenced according to the tier model**:
  - Adapter in **game-essential** as a bridge to engine viewports.
  - Host in **content-authoring** as a tool that renders world-map tiles and, eventually, hosts a Mapsui viewer.

- Mapsui/BruTile/VectorTile remain **entirely optional** from the point of view of engine and most game-essential code.

- Console and Windows apps can:
  - Continue to use terminal/GUI rendering pipelines without understanding Mapsui.
  - Optionally add Mapsui-based views by depending on `PigeonPea.MapsuiAdapter` and appropriate content-authoring pipelines.

- Future work to integrate Mapsui/BruTile/VectorTile more deeply (e.g., real-world overlays, live tile services) should:
  - Add new projects under `content-authoring` or app tiers.
  - Avoid introducing references from engine → content-authoring.

## Implementation Notes

- Completed so far:
  - `dotnet/game-essential/core/src/PigeonPea.MapsuiAdapter/` created by moving the old `mapsui-adapter` project and pointing it at `engine/core/src/PigeonPea.Shared.Rendering`.
  - `dotnet/content-authoring/core/src/PigeonPea.MapsuiHost/` created by moving the old `mapsui-host` project and wiring it to `PigeonPea.Shared`, `PigeonPea.Map.Rendering`, and `FantasyMapGenerator.Core`.

- Near-term follow-ups (separate tasks):
  - Add these projects to `PigeonPea.sln` under appropriate solution folders.
  - Optionally introduce a Mapsui-based Windows viewer using `PigeonPea.MapsuiAdapter`.
  - Ensure console and Windows apps continue to build after the tier reorg, relying only on engine/game/content tiers as intended.
