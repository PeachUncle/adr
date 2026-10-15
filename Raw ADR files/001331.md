# ADR-012: C++ for Air-Side Performance

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** #1, #2, #33
**Related Views:** `view-logical.md`, `view-deployment.md`

---

## Context

Air-Side must:
1. Integrate with Sony Camera Remote SDK (C++ library only)
2. Control camera with low latency (<50ms command response)
3. Run on resource-constrained Pi 5 (8GB RAM)
4. Handle USB communication
5. Multi-threaded architecture

**Technology Choice:** What language for Air-Side implementation?

---

## Decision

**Air-Side Language: C++17**

**Rationale:**
1. **SDK Requirement:** Sony SDK only available in C++ (no Java/Kotlin/Python bindings)
2. **Performance:** Native code, no GC pauses, direct memory control
3. **USB Access:** Linux USB APIs (libusb) designed for C/C++
4. **Pi 5 ARM64:** Excellent C++ compiler support (GCC, Clang)
5. **Team Expertise:** Team has C++ experience

---

## Alternatives Considered

### Alternative 1: Python with C++ Bindings (ctypes/CFFI)

**Approach:** Python calling Sony SDK via ctypes

**Pros:**
- Rapid development
- Easy to debug

**Cons:**
- ❌ **GIL (Global Interpreter Lock):** Blocks multi-threading (Sony SDK callbacks deadlock)
- ❌ **Performance:** 10-100× slower than C++
- ❌ **Memory Overhead:** Python runtime ~50MB
- ❌ **Binding Complexity:** Must wrap entire Sony SDK API

**Rejection:** GIL incompatible with Sony SDK threading model

---

### Alternative 2: Rust

**Approach:** Rust with C++ FFI to Sony SDK

**Pros:**
- Memory safety
- Modern language features
- Good performance

**Cons:**
- ❌ **C++ Interop:** Rust ↔ C++ FFI painful (name mangling, RAII mismatch)
- ❌ **Learning Curve:** Team not familiar with Rust
- ❌ **Sony SDK Wrappers:** Must write Rust wrappers for entire C++ SDK
- ❌ **Compilation Time:** Rust slower to compile than C++

**Rejection:** C++ interop overhead not worth memory safety benefits (Pi 5 not safety-critical)

---

### Alternative 3: Java/Kotlin with JNI

**Approach:** JVM calling Sony SDK via JNI

**Pros:**
- Garbage collection
- Modern language (Kotlin)

**Cons:**
- ❌ **JVM Overhead:** ~100MB RAM minimum
- ❌ **GC Pauses:** Can cause latency spikes
- ❌ **JNI Complexity:** C++ ↔ Java bridge fragile
- ❌ **Deployment:** Must bundle JRE on Pi

**Rejection:** JVM too heavyweight for Pi 5 embedded service

---

## Consequences

### Positive

✅ **Native SDK Integration:** Direct C++ SDK calls (no FFI overhead)
✅ **Performance:** Measured <30ms command latency, <5% CPU usage
✅ **Memory Efficient:** ~50MB RAM (vs ~200MB for JVM)
✅ **Deterministic:** No GC pauses
✅ **USB Direct Access:** Standard Linux APIs (libusb-1.0)

### Negative

⚠️ **Manual Memory Management:** Must track pointers, avoid leaks
- Mitigation: Use RAII (smart pointers, containers)

⚠️ **Longer Development:** C++ slower to write than Python
- Acceptable: Performance critical, one-time development

⚠️ **Debugging Complexity:** Segfaults, memory corruption
- Mitigation: Valgrind, AddressSanitizer, extensive testing

---

## C++17 Features Used

- **std::thread:** Multi-threading (ADR-006)
- **std::mutex, std::lock_guard:** Thread safety
- **std::unique_ptr, std::shared_ptr:** Automatic memory management
- **std::optional:** Null safety
- **std::filesystem:** File operations
- **std::string_view:** Efficient string handling

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (explains why not shared language)
- **ADR-004:** Docker Containerization (C++ builds in Docker)
- **ADR-006:** Multi-Threaded Design (C++ threading model)

---

## References

- Logical View: `view-logical.md` (Air-Side component architecture)
- Deployment View: `view-deployment.md` (C++ build in Dockerfile)
- Sony SDK Documentation: Proprietary (under NDA)
