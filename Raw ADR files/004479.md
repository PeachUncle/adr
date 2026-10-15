# ADR-001: Rendering Approach

**Status**: Accepted
**Date**: 2025-11-26

## Context

Valence requires a canvas-based UI with:
- Spatial positioning of documents and widgets
- Drag-and-drop interactions
- Linking between elements (visual connections)
- Grouping (draw box around elements)
- Zooming and panning
- Multiple widget types with different rendering needs
- Semantic zoom (widgets change detail level based on zoom)

We're building with Tauri, which provides a Rust backend. The question is how to implement the canvas and widget rendering.

## Options

### Option A: Web-based Canvas (Tauri + WebView)

Use Tauri's default architecture: Rust backend with a web frontend rendered in a WebView.

**Sub-options for canvas implementation**:
- **A1: React Flow / xyflow** - Established node-based canvas library
- **A2: Custom on HTML/CSS** - Build canvas interactions from scratch
- **A3: Canvas2D / WebGL** - Lower-level rendering with a library like Konva, PixiJS, or Fabric.js

**Pros**:
- Mature ecosystem for UI components
- Extensive CSS/styling capabilities
- Hot-reload during development
- Familiar web development patterns
- Many canvas libraries to choose from

**Cons**:
- WebView overhead and potential performance limits
- IPC boundary between Rust and frontend
- Two languages/runtimes to manage
- Web canvas libraries may impose assumptions

### Option B: Bevy (Pure Rust)

Use Bevy game engine for rendering, bypassing Tauri's WebView entirely or using Tauri only for system integration.

**Pros**:
- Pure Rust, single language
- ECS architecture aligns conceptually with document/widget relationships
- High performance rendering
- Fine-grained control over all interactions
- Portability (same codebase could target multiple platforms)

**Cons**:
- Steeper learning curve
- Less mature UI ecosystem (no CSS, limited text rendering historically)
- More work to implement standard UI patterns (text input, scrolling, etc.)
- Bevy is still pre-1.0, API changes possible
- May be overkill for a document canvas

### Option C: egui (Rust Immediate-Mode GUI)

Use egui, either standalone or integrated with Tauri via egui-tauri or similar.

**Pros**:
- Pure Rust
- Simpler than Bevy for UI-focused applications
- Immediate-mode is good for rapid iteration
- Good text rendering and standard widgets
- Can integrate with Tauri

**Cons**:
- Immediate-mode may not suit canvas-with-persistent-objects model well
- Less control over visual styling
- Canvas/spatial features would need custom implementation
- Performance with many objects unknown

### Option D: Iced (Rust Elm-like GUI)

Use Iced, a cross-platform GUI library for Rust with an Elm-inspired architecture.

**Pros**:
- Pure Rust
- Retained-mode, better fit for persistent canvas objects
- Clean architecture
- Active development

**Cons**:
- Canvas/node-graph features not built-in
- Would need significant custom work for spatial canvas
- Smaller ecosystem than web

### Option E: Hybrid - Tauri + Bevy WebView

Use Tauri for window management and system features, embed Bevy in a custom protocol or as a separate render target.

**Pros**:
- Best of both: Tauri's system integration, Bevy's rendering
- Could use web UI for some parts, Bevy for canvas

**Cons**:
- Complex integration
- Two rendering systems to maintain
- Unclear how well this works in practice

## Analysis

### Key Considerations

1. **Canvas complexity**: We need spatial positioning, linking, grouping, zoom. This is non-trivial in any approach.

2. **Widget diversity**: Widgets include tables, timelines, cards, JSON viewers. Web has mature solutions for all of these. Rust GUI ecosystem has fewer ready-made components.

3. **Development velocity**: Web allows faster iteration on UI. Rust GUI requires more upfront investment.

4. **ECS alignment**: Bevy's ECS is conceptually interesting for the document/widget/relationship model, but may be architectural overkill.

5. **Long-term maintainability**: Single-language (Rust) is simpler long-term. But web ecosystem is more stable.

### Trade-off Matrix

| Criterion | Web (A) | Bevy (B) | egui (C) | Iced (D) |
|-----------|---------|----------|----------|----------|
| Canvas libraries | Many options | Build custom | Build custom | Build custom |
| UI components | Extensive | Limited | Good basics | Good basics |
| Performance | Good (with care) | Excellent | Good | Good |
| Dev velocity | Fast | Slower | Medium | Medium |
| Single language | No | Yes | Yes | Yes |
| Styling control | Excellent | Full control | Limited | Medium |
| Ecosystem maturity | High | Medium | Medium | Medium |

## Questions Resolved

1. **How complex is the canvas interaction model?**
   SvelteFlow provides grouping, linking, custom nodes, and zoom out of the box. Semantic zoom will require custom node components that respond to zoom level, but this is achievable within the framework.

2. **How important is pure-Rust?**
   Less important than development velocity for experimentation. The core domain logic (documents, relationships, queries, LLM integration) will be in Rust. The rendering layer being in Svelte is an acceptable trade-off for access to mature canvas tooling.

3. **What's the tolerance for custom UI work?**
   Low tolerance initially - need to reach experimentation stage quickly. SvelteFlow minimizes custom canvas work, letting focus shift to the domain-specific features sooner.

4. **Is Bevy's ECS actually useful here, or just conceptually appealing?**
   Conceptually appealing but not worth the implementation overhead. The document/relationship model can be cleanly expressed in Rust structs without ECS. Revisit only if performance issues emerge with large investigations.

## Decision

**Option A1: Tauri + Svelte + SvelteFlow**

Use Tauri as the application shell with:
- **Frontend**: Svelte + SvelteFlow for canvas rendering and UI
- **Backend**: Rust for domain logic, persistence, external integrations

### State Ownership Boundary

**Frontend owns (UI state)**:
- Node positions on canvas
- Viewport (pan, zoom level)
- Selection state
- Transient interaction state (dragging, resizing)
- Widget expansion/collapse state

**Backend owns (domain state)**:
- Document content and metadata
- Links and relationships
- Groups and membership
- Query execution and results
- LLM interactions
- All file I/O and persistence
- Investigation lifecycle

**Sync points**:
- Open investigation: Rust → Frontend (hydrate stores)
- Document content edits: Frontend → Rust (immediate)
- Position changes: Frontend-local during editing, sync to Rust on save
- Query/LLM operations: Frontend → Rust → (async) → Frontend
- Save: Frontend positions → Rust → persist all

### Rationale

1. **Fastest path to experimentation** - SvelteFlow provides the canvas primitives needed to test document/widget/relationship concepts without building rendering infrastructure.

2. **Mature ecosystem** - CSS for styling, established patterns for state management, extensive documentation.

3. **Appropriate complexity** - Rust handles what Rust is good at (system integration, data integrity, concurrent operations). Frontend handles what web tech is good at (responsive UI, visual polish).

4. **Portability preserved** - Tauri builds native applications for macOS, Windows, Linux. No browser dependency at runtime.

5. **Extensibility** - If SvelteFlow constrains us later, we can replace the canvas component. The Rust backend and domain model remain stable.

## Alternatives Considered

### Option B: Bevy (Pure Rust)
**Not selected** - ECS architecture is conceptually interesting but implementation overhead is too high. Building drag/drop, text rendering, and canvas interactions from scratch delays reaching the experimentation stage. Could revisit if web rendering proves inadequate for performance at scale.

### Option C: egui
**Not selected** - Immediate-mode paradigm is a poor fit for persistent canvas state. Would require significant custom work for spatial canvas features.

### Option D: Iced
**Not selected** - Less mature ecosystem, no ready-made canvas/node-graph components. Same "build from scratch" problem as Bevy.

### Option E: Hybrid Tauri + Bevy
**Not selected** - Adds complexity without clear benefit. If Bevy's rendering is needed, go full Bevy. Mixing two rendering systems creates integration burden.

## Consequences

### Positive
- Can start building document/widget experiments sooner
- Access to SvelteFlow's mature node/edge/grouping features
- Hot reload during development accelerates iteration
- CSS provides extensive styling control for widgets

### Negative
- Two languages to maintain (Rust + TypeScript/JavaScript)
- IPC boundary adds some architectural complexity
- Must be disciplined about state ownership to avoid sync bugs
- WebView has performance ceiling (likely fine for investigation scale, but unknown)

### Risks
- SvelteFlow may impose constraints that conflict with semantic zoom or custom widget needs
- Learning curve for Svelte if skills are rusty
- IPC overhead could cause lag for rapid interactions (mitigated by frontend-owns-UI-state pattern)

## Follow-up Decisions

This decision enables but does not resolve:
- **ADR-002**: Frontend tooling (TypeScript vs JavaScript, build tooling)
- **ADR-003**: Document storage format (SQLite vs JSON files)
- **ADR-004**: Widget architecture (how custom nodes integrate with SvelteFlow)
