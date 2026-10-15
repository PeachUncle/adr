# ADR-001: Choice of PixiJS v8 and Project Setup

Date: 2025-12-09

## Status

Accepted

## Context

We need to build a web-based top-down 2D mystery investigation game. The game requires:
- High-performance 2D rendering
- Sprite-based graphics
- Grid-based movement
- Asset management
- Sound support
- UI components
- Cross-browser compatibility

Several options were considered:
- **Phaser**: Popular game framework with extensive features but heavier and more opinionated
- **Three.js**: More focused on 3D, overkill for 2D
- **Canvas API directly**: Too low-level, would require building too much infrastructure
- **PixiJS**: High-performance 2D WebGL renderer with excellent ecosystem

## Decision

We will use **PixiJS version 8** as our rendering engine and game foundation, initialized using the official Creation Template via `npm create pixi.js@latest`.

**Why PixiJS v8:**
- Industry-leading 2D WebGL rendering performance
- Version 8 is the latest stable release with modern architecture
- Excellent sprite and texture management
- Built-in support for sprite sheets and texture atlases
- Active development and strong community
- Comprehensive plugin ecosystem (@pixi/sound, @pixi/ui, spine support)
- TypeScript support out of the box
- Vite-based build system for fast development

**Why Creation Template:**
- Official recommendation from PixiJS team
- Provides opinionated but flexible structure
- Includes pre-configured build tools (Vite, TypeScript)
- Comes with AssetPack integration for asset optimization
- Includes navigation system for screens/popups
- Built-in audio management
- Responsive resize handling
- Production-ready linting and formatting setup

## Consequences

### Positive
- Fast development with battle-tested boilerplate
- Excellent performance for 2D rendering
- Rich plugin ecosystem reduces custom code
- TypeScript provides type safety and better IDE support
- Vite enables hot module replacement for fast iteration
- AssetPack will optimize our sprite sheets and textures automatically
- Built-in navigation system works well for mystery game's multiple screens (investigation, dialogue, exploration, menus)
- Sound management is handled by @pixi/sound plugin

### Negative
- Learning curve for PixiJS-specific concepts (Container, Sprite, Texture)
- Need to understand the Creation Template's architecture
- Some game-specific systems still need to be built (grid system, dialogue, clue tracking)
- Asset pipeline may need customization for mystery game-specific needs (character portraits, UI elements)

### Neutral
- Vite configuration may need adjustment for specific requirements
- Will need to structure game logic around PixiJS's scene graph model
- TypeScript compilation adds a build step (but provides safety)
