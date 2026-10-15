/*!\page adr_0001 ADR-0001: Three-Layer Architecture for SDL3 C++ Wrapper

# ADR-0001: Three-Layer Architecture for SDL3 C++ Wrapper

**Date:** 2024-08-25  
**Status:** Accepted

## Context

SDL3 is a powerful but low-level C library for multimedia applications and games. While SDL3 provides excellent cross-platform capabilities, its C API presents several challenges for modern C++ development:

- **Manual resource management** - SDL resources require explicit cleanup calls
- **C-style error handling** - Functions return error codes rather than using exceptions
- **Verbose API** - Simple operations require multiple function calls
- **Type safety concerns** - Heavy use of void pointers and manual casting
- **No RAII** - Resources can easily leak if cleanup is forgotten

We needed to decide how to structure a C++ wrapper that addresses these issues while remaining maintainable and allowing users to choose their level of abstraction.

## Decision

We implemented a **three-layer architecture** with clear separation of concerns:

### Layer 1: Core SDL Wrapper (`sdl` namespace)
- **Purpose**: Thin RAII wrappers around SDL3 C API
- **Scope**: Window, Renderer, Surface, Texture, Event system
- **Characteristics**:
  - Direct 1:1 mapping to SDL concepts
  - Exception-based error handling via `sdl::Exception`
  - Automatic resource cleanup through destructors
  - Move-only semantics (no copying of expensive resources)
  - Pimpl pattern to hide SDL dependencies

**Example:**
```cpp
// Raw SDL3 requires manual cleanup
SDL_Window* window = SDL_CreateWindow("Title", 800, 600, 0);
SDL_Renderer* renderer = SDL_CreateRenderer(window, nullptr);
// ... manual cleanup required

// sdl provides RAII
sdl::Window window("Title", 800, 600, 0);
sdl::Renderer renderer(window);
// Automatic cleanup on destruction
```

### Layer 2: Game Development Tools (`sdl::tools` namespace)
- **Purpose**: Higher-level utilities built on Layer 1
- **Scope**: EventRouter, Button, Sprite, SpriteRenderer
- **Characteristics**:
  - Game-specific abstractions
  - Event routing and management systems
  - UI components with built-in event handling
  - Composition over inheritance

**Example:**
```cpp
auto eventRouter = std::make_shared<EventRouter>(eventBus);
Button button(eventRouter, FloatRectangle(10, 10, 100, 50));
button.registerEventHandler([](const MouseButtonEvent& e) {
    std::cout << "Button clicked!\n";
});
```

### Layer 3: Applications and Examples
- **Purpose**: Demonstrate real-world usage
- **Scope**: TicTacToe game, diagnostic tools, pattern demonstrations
- **Characteristics**:
  - Complete applications showing best practices
  - Integration examples across all layers
  - Performance and debugging utilities

## Consequences

### Positive Outcomes

**Clear Mental Model**: Each layer has a distinct purpose, making it easy for developers to understand where functionality belongs.

**Flexible Adoption**: Users can:
- Use only Layer 1 for lightweight SDL wrapping
- Add Layer 2 for game development utilities  
- Reference Layer 3 for implementation patterns

**Testability**: Each layer can be unit tested independently:
- Layer 1: Mock SDL calls, test RAII behavior
- Layer 2: Mock Layer 1 objects, test game logic
- Layer 3: Integration tests with real scenarios

**Maintainability**: Changes in one layer have minimal impact on others:
- SDL3 API changes affect only Layer 1 implementations
- Game utility improvements happen in Layer 2
- Examples evolve independently in Layer 3

**Performance**: No unnecessary abstraction overhead - users pay only for what they use.

### Negative Consequences

**Initial Complexity**: Three layers require more upfront design than a single monolithic wrapper.

**API Coordination**: Must maintain consistency between layers, especially ensuring Layer 2 doesn't expose Layer 1 implementation details.

**Documentation Overhead**: Need to explain the layer concept to users and when to use each layer.

**Build Complexity**: CMake configuration must handle dependencies between layers correctly.

## Alternatives Considered

### Single Monolithic Wrapper
**Approach**: One large namespace with all SDL functionality wrapped at various abstraction levels.

**Rejected because:**
- Unclear where to add new features
- Difficult to test individual components
- Users forced to adopt all abstraction levels
- High coupling between different concerns

### Header-Only Template Library  
**Approach**: Template-heavy approach with everything in headers.

**Rejected because:**
- Long compilation times due to SDL header includes
- Difficult to provide stable ABI
- Template error messages would expose SDL details
- Harder to debug compiled code

### Inheritance-Based Hierarchy
**Approach**: Deep inheritance trees like `SDLWindow -> GameWindow -> UIWindow`.

**Rejected because:**
- Rigid hierarchy doesn't match real usage patterns  
- Difficult to compose features (button + sprite rendering)
- Performance overhead from virtual dispatch
- Hard to extend without modifying base classes

## Implementation Evidence

The architecture's effectiveness is demonstrated in our codebase:

**Layer Separation**: source files cleanly organized:
- `src/sdl/`: core SDL wrappers
- `src/sdl_tools/`: game utilities  
- `src/examples/`: real applications

**Independent Testing**: Each layer has comprehensive test coverage:
- 454 lines of sophisticated button tests using mocks
- Zero dependencies between layer test suites
- Clear test boundaries matching architectural layers

**Usage Validation**: The TicTacToe example demonstrates natural API usage across all three layers without forced abstractions.

**Performance**: Event system benchmarks show zero-cost abstraction when using templates, with polymorphic fallback available when needed.

This architecture successfully delivers both the safety of modern C++ and the performance characteristics needed for real-time applications.

---

*This ADR documents a foundational architectural decision. Related decisions about specific patterns (Pimpl, RAII, Event System) are documented in separate ADRs.*
