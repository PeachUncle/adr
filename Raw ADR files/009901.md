# ADR 002: Silk.NET for 3D Visualization (Not Unity)

**Date:** 2025-11-22  
**Status:** Accepted  
**Deciders:** Architecture Team

## Context

We need a 3D rendering solution for visualizing the solar system and interstellar object trajectories. The original requirement mentioned Unity3D, but we need to evaluate the best option for a .NET microservices architecture.

## Decision

We will use **Silk.NET** with **OpenGL** instead of Unity3D.

### Technology Stack

- **Silk.NET** - Modern .NET bindings for OpenGL, Vulkan, OpenCL
- **OpenGL 4.6** - Widely supported, mature rendering API
- **ImGui.NET** - Immediate mode GUI for controls and debug UI
- **System.Numerics** - Vector and matrix math

## Rationale

### Why NOT Unity3D

❌ **Poor Integration** - Unity doesn't integrate well with ASP.NET Core microservices  
❌ **Licensing** - Unity requires separate runtime/deployment licenses  
❌ **Overhead** - Full game engine is overkill for simple 3D visualization  
❌ **Deployment** - Unity WebGL or standalone builds complicate architecture  
❌ **Team Skills** - Unity development is separate from .NET backend development

### Why Silk.NET

✅ **Native .NET** - First-class .NET 8 library, modern C# features  
✅ **Lightweight** - Only rendering, no game engine overhead  
✅ **Flexible** - Control over rendering pipeline  
✅ **Cross-Platform** - Windows, Linux, macOS support  
✅ **Performance** - Direct OpenGL access, no Unity overhead  
✅ **Integration** - Easy to embed in .NET applications  
✅ **Learning** - Teaches graphics programming fundamentals

## Implementation Details

### Rendering Architecture

```
InterstellarTracker.Web (Console App)
  ├── Silk.NET.OpenGL (Rendering)
  ├── Silk.NET.Windowing (Window management)
  ├── ImGui.NET (UI overlay)
  └── HTTP Client (API communication)
```

### Communication Flow

```
Web Client → Visualization Service API → Calculate positions
          ← JSON (positions, velocities)
          → Render 3D scene
```

### Features

- **Camera Controls** - Orbit, pan, zoom
- **Time Control** - Real-time, accelerated, pause
- **Object Selection** - Click planets/comet for info
- **Trajectory Lines** - Past and predicted paths
- **UI Overlay** - ImGui for date, speed, info panels

## Consequences

### Positive

✅ **Consistency** - Everything in .NET ecosystem  
✅ **Simplicity** - Lighter than full game engine  
✅ **Control** - Full control over rendering  
✅ **Performance** - Direct GPU access  
✅ **Deployment** - Standard .NET application deployment

### Negative

❌ **Development Time** - More manual work than Unity  
❌ **Physics** - Need to implement orbital mechanics ourselves (actually a learning opportunity)  
❌ **Assets** - No built-in asset pipeline  
❌ **Tooling** - No visual editor like Unity

### Mitigations

- Keep graphics simple (spheres, lines, basic textures)
- Use existing orbital mechanics libraries (e.g., AstroSharp)
- Focus on data visualization, not photorealism
- Document rendering code thoroughly for learning

## Alternatives Considered

1. **Unity3D** - Rejected due to integration and licensing issues
2. **Three.js (Web)** - Considered, but want native .NET experience
3. **Godot** - Similar issues to Unity, less .NET integration
4. **OpenTK** - Older, Silk.NET is the modern successor
5. **Vulkan** - Too low-level for this project

## References

- [Silk.NET Documentation](https://github.com/dotnet/Silk.NET)
- [Learn OpenGL](https://learnopengl.com/)
- [ImGui.NET](https://github.com/ImGuiNET/ImGui.NET)
- [OpenGL Specification](https://www.opengl.org/documentation/)
