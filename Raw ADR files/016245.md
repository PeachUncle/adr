/*!\page adr_0002 ADR-0002: Pimpl Pattern for SDL Dependencies

# ADR-0002: Pimpl Pattern for SDL Dependencies

**Date:** 2024-08-25  
**Status:** Accepted

## Context

SDL3 is a large C library with extensive headers that include platform-specific code, macro definitions, and complex type declarations. Direct inclusion of SDL headers in our public API would create several problems:

- **Compilation Dependencies**: Users would be forced to have SDL3 headers installed and properly configured
- **Header Bloat**: Large SDL headers would slow compilation of user code significantly  
- **ABI Instability**: Changes in SDL headers would require recompilation of all user code
- **Namespace Pollution**: SDL macros and definitions would leak into user code
- **Platform Coupling**: Platform-specific SDL code would expose implementation details

We needed a way to provide a clean C++ API while completely isolating SDL dependencies from our public headers.

## Decision

We implemented the **Pimpl (Pointer to Implementation) idiom** consistently across all SDL resource wrapper classes:

### Public Header Structure
- Public headers contain only forward declarations and `std::unique_ptr<ClassImpl>`
- No SDL includes in any public header file
- Clean, dependency-free API surface

**Example (`src/sdl/include/surface.h`):**
```cpp
#include <memory>
#include <filesystem>
// NO SDL includes!

class SurfaceImpl;  // Forward declaration

class Surface {
public:
  Surface(const std::filesystem::path& filePath);
  // ... public interface
  [[nodiscard]] auto getImpl() const -> const SurfaceImpl&;
private:
  std::unique_ptr<SurfaceImpl> _impl;  // Standardized pimpl naming
};
```

### Implementation Header Structure  
- Implementation details isolated in `src/sdl/src/include/*_impl.h` files
- SDL dependencies contained within implementation
- Friend relationships contained at impl level only - no coupling exposed in public API

**Example (`src/sdl/src/include/surface_impl.h`):**
```cpp
#include "surface.h"
#include <SDL3/SDL.h>  // SDL dependency isolated here

class SurfaceImpl {
  friend class Surface;
  friend class TextureImpl;  // Friend at impl level only
public:
  static auto createSurface(SDL_Surface* sdlSurface) -> Surface;
  SDL_Surface* getSdlSurface() const; // Controlled access for other impls
private:
  SDL_Surface* _sdlSurface = nullptr;  // Raw SDL resource
};
```

### Implementation Pattern
All classes follow the same pattern:
1. **Public constructor**: Creates `std::make_unique<ClassImpl>()`
2. **Public methods**: Delegate to `_impl->method()` calls
3. **Resource management**: RAII cleanup in destructors
4. **Move semantics**: Proper transfer of `unique_ptr` ownership
5. **Inter-class access**: Public classes expose `getImpl()` methods for controlled access to impl data
6. **Friend relationships**: Contained entirely at impl level (e.g., `SpriteImpl` friends `SpriteRendererImpl`)
7. **Naming convention**: All pimpl members use standardized `_impl` naming (not `_classNameImpl`)

## Consequences

### Positive Outcomes

**Zero Public Dependencies**: Users can use SDL++ without any SDL headers, includes, or build configuration. The public API is completely self-contained.

**Fast Compilation**: User code compiles quickly since it doesn't process large SDL headers. Our TicTacToe example builds in seconds rather than minutes.

**ABI Stability**: Internal implementation changes don't require user code recompilation. We can upgrade SDL versions without breaking user builds.

**Clean API Surface**: Public headers are readable and focused. No SDL-specific types, macros, platform dependencies, or implementation coupling leak through.

**Implementation Flexibility**: We can change internal SDL usage patterns, add caching, or even switch SDL versions without affecting the public API.

**Consistent Naming**: Standardized `_impl` naming across all classes improves code maintainability and reduces cognitive load when working with pimpl patterns.

### Negative Consequences

**Runtime Indirection**: One extra pointer dereference per method call. In practice, this is negligible for SDL operations which are already heavyweight.

**Memory Overhead**: Additional heap allocation per object (8 bytes per `unique_ptr`). Minimal impact for typical SDL resource counts.

**Implementation Complexity**: Each class requires both public and private headers. More files to maintain and keep synchronized.

**Debugging Difficulty**: Debugger must follow pointer to reach actual SDL resources. Modern debuggers handle this well with proper debug symbols.

**Friend Relationships**: Implementation classes use `friend` access for internal operations, but these relationships are contained entirely within the impl layer, keeping public headers clean.

## Alternatives Considered

### Direct SDL Exposure
**Approach**: Include SDL headers directly in public API.

**Rejected because:**
- Forces SDL dependency on all users
- Compilation would be 5-10x slower
- Platform-specific SDL code would leak into user builds
- ABI would be unstable across SDL versions

### Template-Based Abstraction
**Approach**: Heavy template usage to avoid virtual calls and pimpl overhead.

**Rejected because:**
- Would still require SDL headers in public templates
- Template error messages would expose SDL implementation details
- Longer compilation times due to template instantiation
- More complex for users to understand and debug

### Opaque Handle Pattern  
**Approach**: Return opaque handles/IDs rather than objects.

**Rejected because:**
- Not idiomatic C++ - users expect object-oriented interface
- Would require global resource management tables
- Lose automatic cleanup benefits of RAII
- Type safety issues with handle mix-ups

### Interface/Implementation Split
**Approach**: Pure virtual base classes with concrete implementations.

**Rejected because:**
- Virtual function call overhead for every operation
- More complex inheritance hierarchies
- Still need pimpl or headers for concrete classes
- Doesn't solve the SDL dependency problem

## Implementation Evidence

The pattern's effectiveness is visible throughout our codebase:

**Consistent Application**: All 14 major wrapper classes (`Window`, `Renderer`, `Surface`, `Texture`, `EventBus`, `Sprite`, `Button`, etc.) follow identical pimpl structure with standardized `_impl` naming.

**Clean Public Headers**: Zero SDL includes in `src/sdl/include/` - only standard library and our own headers. No friend statements exposing internal coupling.

**Isolated Dependencies**: All SDL includes and friend relationships contained within `src/sdl/src/include/*_impl.h` files.

**User Experience**: TicTacToe example includes only `#include <sdl.h>` and compiles without any SDL configuration.

**Performance**: Event system handles thousands of events per second with negligible pimpl overhead compared to SDL processing costs.

**Maintainability**: Recently upgraded from SDL3 preview to newer version by changing only implementation files - zero public API changes required.

The pimpl pattern successfully provides complete dependency isolation while maintaining excellent performance and usability characteristics essential for real-time applications.

---

*This ADR addresses implementation hiding. Related decisions about resource management (ADR-0004) and overall architecture (ADR-0001) provide additional context.*
