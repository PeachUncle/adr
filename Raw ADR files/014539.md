# Architecture Decision Record: Hybrid Swift+C Implementation for Syscall Hook Module

## Status
**ACCEPTED** - 2025-06-29

## Context
Privarion projesi için STORY-2025-002 (Syscall Hook Module) implementasyonu sırasında, sistem çağrılarının interception'ı ve manipulation'ı için teknik mimari kararı alınması gerekmektedir.

### Problem Statement
- macOS'ta system call hooking için DYLD injection ve function hooking gereklidir
- Swift tek başına low-level system programming için yetersizdir
- C/C++ düşük seviye işlemler için gereklidir ancak Swift ecosystem integration'ı zordur
- Security ve stability kritik önceliklerdir

### Technical Requirements
- DYLD_INSERT_LIBRARIES mekanizması kullanılmalı
- Function hooking/replacement yapılabilmeli
- Original function'lara erişim sağlanmalı
- Type-safe configuration management gerekli
- Test edilebilir ve modüler mimari şart

## Decision
**Hybrid Swift+C Architecture** tercih edilmiştir:

### Architecture Components:
1. **Swift Layer (PrivarionCore):**
   - Configuration management
   - High-level API and orchestration
   - Type safety and error handling
   - Logging and debugging infrastructure

2. **C Bridge Layer (PrivarionHook):**
   - Low-level syscall interception
   - Function pointer manipulation
   - DYLD injection interface
   - Memory management for hook chains

3. **Swift Package Manager Integration:**
   - Mixed language targets
   - C module with modulemap
   - Swift-C FFI bridging

### Implementation Strategy:
- **Phase 1:** C bridge module with basic hooking capability
- **Phase 2:** Swift integration layer with configuration
- **Phase 3:** Advanced hooking patterns and security enhancements
- **Phase 4:** Production hardening and performance optimization

## Alternatives Considered

### 1. Pure Swift Approach
**Rejected:** Swift lacks necessary low-level capabilities for syscall hooking
- No direct function pointer manipulation
- Limited unsafe memory operations
- Missing DYLD integration APIs

### 2. Pure C/C++ Approach  
**Rejected:** Loses Swift ecosystem benefits
- No type safety for configuration
- Complex error handling
- Difficult testing and debugging
- Poor integration with existing Swift codebase

### 3. Rust FFI Approach
**Rejected:** Additional complexity without clear benefits
- Requires Rust toolchain integration
- Swift-Rust FFI less mature than Swift-C
- Team expertise primarily in Swift/C

### 4. Objective-C Bridge
**Rejected:** Adds unnecessary complexity
- Not needed for pure C functionality
- Additional runtime overhead
- No significant benefits over C bridge

## Implementation Details

### C Module Structure:
```c
// PrivarionHook module
typedef struct {
    void* original_function;
    void* replacement_function; 
    char* function_name;
} PHookEntry;

// Core hooking functions
int ph_install_hook(const char* function_name, void* replacement);
int ph_remove_hook(const char* function_name);
void* ph_get_original(const char* function_name);
```

### Swift Integration:
```swift
// Swift wrapper providing type safety
public struct SyscallHook {
    public static func installHook<T>(
        for function: SyscallFunction,
        replacement: T
    ) throws -> HookHandle<T>
}
```

### Security Considerations:
- Input validation at Swift layer
- Memory safety in C bridge
- Privilege escalation prevention
- Code signing compatibility
- SIP (System Integrity Protection) compliance

## Consequences

### Positive:
- ✅ Leverages Swift type safety and ecosystem
- ✅ Enables low-level system programming with C
- ✅ Maintains existing Swift codebase compatibility
- ✅ Allows incremental implementation
- ✅ Clear separation of concerns
- ✅ Testable at both Swift and C levels

### Negative:
- ❌ Increased complexity with multiple languages
- ❌ FFI overhead for Swift-C boundary crossings
- ❌ Additional build configuration requirements
- ❌ Potential debugging challenges across language boundaries

### Risks and Mitigations:
- **Risk:** FFI memory safety issues
  - **Mitigation:** Strict Swift wrapper boundaries, comprehensive testing
- **Risk:** Build complexity
  - **Mitigation:** Swift Package Manager native support, clear documentation
- **Risk:** Performance overhead
  - **Mitigation:** Minimize boundary crossings, profile critical paths

## Compliance and Standards
- Follows Apple's recommended practices for mixed-language Swift packages
- Maintains Codeflow System v3.0 architecture principles
- Adheres to macOS security model requirements
- Compatible with System Integrity Protection (SIP)

## Decision Rationale
This hybrid approach balances the need for low-level system access with Swift's safety and productivity benefits. The phased implementation strategy allows for incremental validation of the architecture while maintaining project momentum.

## Next Actions
1. Setup C module structure in Swift Package Manager
2. Implement basic function hooking in C layer
3. Create Swift wrapper with type-safe API
4. Establish testing framework for both layers
5. Document FFI patterns and best practices

---
**Decision Date:** 2025-06-29  
**Decision Maker:** Development Team  
**Review Date:** Upon Phase 1 completion
