# ADR-A001: CGO Memory Management Architecture

Date: 2025-07-29

## Status

Proposed

## Context

The Seshat UE5 integration successfully loads all toolkit subsystems using the Swiss Army Knife standard (1:1 mapping of UE subsystems to toolkit modules). However, Blueprint testing revealed a fundamental issue with object lifecycle management across the Go-C++-UE boundary.

### The Problem Chain
1. **Go toolkit functions** like `dice.D20(1)` return `*Roll` objects (Go pointers)
2. **CGO bindings** export these as `unsafe.Pointer(roll)` to C++
3. **UE subsystems** store pointers in handle maps for later Blueprint access
4. **Go garbage collector** deallocates Roll objects (unaware of C++ references)
5. **Blueprint calls** like `RollGetValue(handle)` access deallocated memory → **CRASH**

### Current State
- **Primitive returns work perfectly**: `RollerRoll(20)` returns `int32` directly - no crashes
- **Object returns crash consistently**: `D20(1)` → `RollGetValue(handle)` crashes every time
- **All subsystems load correctly**: Swiss Army Knife integration is architecturally sound

### Scope of Impact
This affects all future rich RPG functionality:
- **Character Creation**: D&D 5e character objects with validation metadata
- **Room Generation**: Complex spatial objects with pathfinding data
- **Spell Systems**: Effect objects with duration and targeting information
- **Combat Systems**: Action objects with complex state management
- **Entity Management**: Any toolkit object with lifecycle beyond immediate return

### Industry Context
This is a **standard CGO pattern requirement** when Go objects cross language boundaries. It's not optional - it's fundamental infrastructure for any C/C++ integration that returns Go objects.

## Decision

We will implement a **CGO Memory Registry Pattern** in the toolkit bindings to manage object lifecycle across the Go-C++-UE boundary.

### Core Components

#### 1. Global Object Registry
```go
// In dice_bindings.go (and all future *_bindings.go files)
var (
    objectRegistry = make(map[uintptr]interface{})
    registryMutex  sync.RWMutex
    nextID         uintptr = 1
)
```

#### 2. Object Registration Functions
```go
// RegisterObject stores a Go object and returns a handle for C++ use
func registerObject(obj interface{}) uintptr {
    registryMutex.Lock()
    defer registryMutex.Unlock()
    
    id := nextID
    nextID++
    objectRegistry[id] = obj
    return id
}

// GetObject retrieves a Go object by its handle
func getObject(handle uintptr) (interface{}, bool) {
    registryMutex.RLock()
    defer registryMutex.RUnlock()
    
    obj, exists := objectRegistry[handle]
    return obj, exists
}
```

#### 3. Explicit Cleanup Pattern
```go
//export RollCleanup
func RollCleanup(handle C.uintptr_t) {
    registryMutex.Lock()
    defer registryMutex.Unlock()
    delete(objectRegistry, uintptr(handle))
}
```

#### 4. Updated Object Return Pattern
```go
//export D20
func D20(count C.int) C.uintptr_t {
    roll := dice.D20(int(count))
    handle := registerObject(roll)
    return C.uintptr_t(handle)
}

//export RollGetValue
func RollGetValue(handle C.uintptr_t) C.int {
    obj, exists := getObject(uintptr(handle))
    if !exists {
        return -1 // Error indicator
    }
    
    roll, ok := obj.(*dice.Roll)
    if !ok {
        return -1 // Type assertion error
    }
    
    return C.int(roll.GetValue())
}
```

### Template Pattern for All Modules
This pattern becomes the standard template for:
- **dice_bindings.go**: Roll object management
- **entity_bindings.go**: Character/Entity object management  
- **spatial_bindings.go**: Room/Position object management
- **spell_bindings.go**: Spell/Effect object management

### UE Integration Requirements
UE subsystems must implement cleanup in their destructors:
```cpp
// In URPGDiceSubsystem destructor
for (auto& HandlePair : ActiveRollHandles) {
    RollCleanupFuncPtr(HandlePair.first);
}
```

## Consequences

### Positive
- **Memory safety**: Go objects protected from garbage collection while C++ holds references
- **Rich object returns**: Enables complex RPG objects with full metadata and functionality
- **Scalable pattern**: Template applies to all future toolkit integrations
- **Industry standard**: Follows established CGO patterns for production systems
- **Blueprint developer friendly**: Objects work as expected without memory management concerns

### Negative  
- **Increased complexity**: Two-step pattern (create object → use handle) required for all objects
- **Manual memory management**: UE subsystems must implement proper cleanup
- **Performance overhead**: Registry lookups and synchronization for each object access
- **Developer education**: Blueprint developers need to understand handle-based patterns

### Neutral
- **Memory registry overhead**: Acceptable for rich RPG object functionality
- **Thread safety requirements**: Standard for any multi-threaded UE integration
- **Handle-based API**: Common pattern in game engines and graphics APIs

## Implementation Plan

### Phase 1: Dice Module Foundation
1. Implement CGO memory registry in `dice_bindings.go`
2. Update `URPGDiceSubsystem` with cleanup patterns
3. Validate Blueprint workflow: `D20(1)` → `RollGetValue(handle)` → cleanup

### Phase 2: Template Standardization
1. Extract common registry functions to shared utility
2. Document handle-based API patterns for Blueprint developers
3. Create testing patterns for memory lifecycle validation

### Phase 3: Module Expansion
1. Apply pattern to `entity_bindings.go` for character creation
2. Apply pattern to spatial modules for room generation
3. Apply pattern to any future object-returning toolkit functions

## Example Usage

### Blueprint Flow
```
D20(1) → Handle: 456
RollGetValue(456) → Value: 15
RollGetDescription(456) → "d20[15]"
RollCleanup(456) → Memory freed
```

### C++ Subsystem Pattern
```cpp
// Store handle for later use
int32 Handle = D20FuncPtr(1);
ActiveRollHandles.Add(Handle);

// Use object through handle
int32 Value = RollGetValueFuncPtr(Handle);

// Cleanup when done
RollCleanupFuncPtr(Handle);
ActiveRollHandles.Remove(Handle);
```

## Validation Criteria

### Success Metrics
- [ ] Blueprint `D20(1)` → `RollGetValue(handle)` workflow works without crashes
- [ ] Memory registry prevents Go garbage collection of active objects
- [ ] UE subsystem cleanup properly releases all handles
- [ ] Pattern documented and reusable for future modules

### Failure Indicators
- Memory leaks from unreleased handles
- Crashes from accessing invalid handles
- Performance degradation from registry overhead
- Developer confusion about handle management

## References

- **J006**: Blueprint Testing and CGO Memory Discovery Journey
- **Swiss Army Knife Standard**: UE subsystem to toolkit module mapping
- **CGO Best Practices**: Industry patterns for Go-C interop memory management