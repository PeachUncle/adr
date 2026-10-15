/*!\page adr_0006 ADR-0006: Application Framework Service Management

# ADR-0006: Application Framework Service Management

**Date:** 2025-08-26  
**Status:** Accepted

## Context

The current `sdl::Application` framework requires users to manually create and manage SDL and TTF objects in their application's `init()` method. This leads to boilerplate code and inconsistent initialization patterns across applications:

- In `application_example.cpp:23-24`, users create SDL objects as direct members
- In `font_hello_world.cpp:25-26`, users create SDL and TTF objects as unique_ptr members
- Manual object creation requires users to handle initialization order and error handling
- Optional services like TTF require conditional logic throughout the application

Users need a way to declaratively specify which services (SDL, TTF) they require while maintaining the flexibility to opt out of services they don't need.

## Decision

Implement a **Service Registry Pattern** that allows applications to request services on-demand without creating hard dependencies between `sdl_application` and optional modules like `sdl_ttf`:

```cpp
class BaseApplication {
protected:
  auto requestSDL() -> SDL&;  // Hard dependency acceptable
  
  template<typename T>
  auto requestService() -> T&;  // Generic service request
};

class ServiceRegistry {
public:
  template<typename T>
  static auto registerServiceFactory(std::function<std::unique_ptr<T>()> factory) -> void;
  
  template<typename T>
  static auto createService() -> std::unique_ptr<T>;
};
```

**Key Design Principles:**
1. **SDL Hard Dependency**: `sdl_application` depends directly on `sdl` (acceptable core dependency)
2. **TTF Soft Dependency**: TTF services registered via factory pattern when `sdl_ttf` is linked
3. **Extensibility**: Any service can register itself using the same pattern
4. **Lazy Creation**: Services created only when first requested

The `ApplicationRunner` manages service lifecycle through type-erased storage, with services registering their factory functions at static initialization time.

## Implementation Details

The final implementation uses:

1. **Service Registry Class**: Thread-safe singleton with type-erased factory storage
2. **Application Interface**: `requestSDL()` and `requestService<T>()` methods in BaseApplication
3. **Optional Service Headers**: Services provide registration headers (e.g., `ttf_service.h`) that applications can include for transparent registration
4. **Conditional Registration**: Uses `__has_include` and `constexpr if` to register services only when application framework is available

**Usage Pattern:**
```cpp
#include <ttf_service.h>  // Automatically registers TTF service

class MyApp : public BaseApplication {
  auto init() -> bool override {
    auto& sdl = requestSDL();           // Direct SDL access
    auto& ttf = requestService<TTF>();  // Service registry access
    // Service lifecycle managed automatically
    return true;
  }
};
```

**Key Implementation Files:**
- `src/sdl_application/include/application.h`: Core service management
- `src/sdl_ttf/include/ttf_service.h`: TTF service registration header
- Service registration happens transparently when optional service headers are included

## Consequences

### What becomes easier:
- **Reduced boilerplate**: Applications no longer need manual SDL/TTF object management
- **Consistent initialization**: Framework ensures proper service initialization order
- **Optional dependencies**: Modules like `sdl_ttf` can be linked optionally without breaking builds
- **Error handling**: Framework provides centralized error handling for service initialization
- **Resource management**: Automatic cleanup of services during application shutdown
- **Extensibility**: New services can integrate using the same registration pattern

### What becomes more difficult:
- **Framework complexity**: Type erasure and factory pattern add implementation complexity
- **Debugging**: Service initialization errors may be harder to trace through the registry layer
- **Compile-time safety**: Service availability only known at runtime (when factory is registered)
- **Template instantiation**: Generic service requests may increase compile times

### Risks to mitigate:
- Provide clear error messages when requesting unregistered services
- Document service registration requirements for optional modules
- Ensure factory registration happens before any service requests
- Consider compile-time service detection mechanisms for better error messages

## Alternatives Considered

### 1. Hard Dependency on All Services
```cpp
class BaseApplication {
protected:
  auto requestSDL() -> SDL&;
  auto requestTTF() -> TTF&;  // Creates hard dependency
};
```
**Rejected**: Forces `sdl_application` to depend on `sdl_ttf`, breaking modularity and increasing build requirements.

### 2. Initialization Flags Pattern
```cpp
struct AppConfig {
  bool needsSDL = true;
  bool needsTTF = false;
};
```
**Rejected**: Requires compile-time configuration, less flexible than runtime service discovery.

### 3. CRTP Template Specialization
```cpp
template<bool WithTTF = false>
class Application : public BaseApplication {};
```
**Rejected**: Increases template complexity and still requires compile-time dependency decisions.

### 4. std::optional Return Types
```cpp
auto ApplicationRunner::getTTF() -> std::optional<TTF>&;
```
**Rejected**: Forces applications to handle service availability at every usage point, reducing convenience.

### 5. Status Quo (Manual Management)
**Rejected**: Continues to burden users with boilerplate and inconsistent patterns as shown in current examples.
