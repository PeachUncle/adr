# ADR-001: Three-Domain Microservices Architecture

**Status:** Accepted
**Date:** 2024-10 (Initial design)
**Updated:** 2025-11-11
**Deciders:** System Architect, Development Team
**Related Issues:** #63
**Related Views:** `view-logical.md`, `view-deployment.md`

---

## Context

DPM-V2 requires controlling a Sony professional camera from a UAV ground station over a wireless data link. The system must support:

1. **Performance-critical** camera control with minimal latency
2. **User-facing** mobile UI for field operations
3. **Diagnostic** tools for development and troubleshooting
4. **Hardware integration** with disparate platforms (Pi 5, H16 tablet, workstations)
5. **Independent deployment** of subsystems
6. **Technology heterogeneity** (C++ SDK, Android framework, Python tools)

**Key Constraints:**
- Sony Camera Remote SDK only available in C++ (no Java/Kotlin bindings)
- Ground station is Android-based H16 tablet (limited to Android APIs)
- Wireless network link with 20-50ms latency and limited bandwidth
- Need rapid prototyping for diagnostic tools

---

## Decision

**We will adopt a Three-Domain Microservices Architecture** separating the system into three independent domains communicating via network protocols:

1. **Air-Side (Performance Domain)**
   - Technology: C++17
   - Platform: Raspberry Pi 5 (Ubuntu 24.04 ARM64, Docker)
   - Responsibility: Camera control, Sony SDK integration, system telemetry
   - Rationale: Performance-critical, requires C++ SDK, hardware-integrated

2. **Ground-Side (User Domain)**
   - Technology: Kotlin, Jetpack Compose
   - Platform: SkyDroid H16 Android tablet
   - Responsibility: User interface, touch control, real-time monitoring
   - Rationale: UI-rich, user-facing, benefits from modern Android frameworks

3. **Dev-Tools (Diagnostic Domain)**
   - Technology: Python 3.8+
   - Platform: Developer workstations (Windows/Linux/macOS)
   - Responsibility: Protocol testing, diagnostics, log analysis
   - Rationale: Rapid prototyping, cross-platform, easy to iterate

**Communication:** JSON over TCP/UDP network protocols (ports 5000-5002)

**Decoupling:** Each domain is independently deployable, testable, and versioned

---

## Alternatives Considered

### Alternative 1: Monolithic Android Application

**Approach:** Single Android app with JNI bindings to Sony SDK

**Pros:**
- Single codebase, simpler deployment
- No network protocol overhead
- Tighter integration

**Cons:**
- ❌ Sony SDK C++ ↔ Android JNI bridge complex and fragile
- ❌ Camera must be physically connected to H16 tablet (impractical for UAV)
- ❌ All processing runs on resource-constrained H16
- ❌ Testing requires full Android build for every change
- ❌ No separation of concerns (UI + camera control mixed)

**Rejection Reason:** Physical topology requires camera on UAV, UI on ground station → necessitates network link

---

### Alternative 2: Two-Domain Architecture (Air + Ground only)

**Approach:** Only Air-Side and Ground-Side, no separate Dev-Tools

**Pros:**
- Simpler than three domains
- Fewer communication paths

**Cons:**
- ❌ Diagnostic tools must be built into Ground-Side UI (clutters production UI)
- ❌ Protocol testing requires full Air-Side rebuild
- ❌ Harder to develop/debug protocol without standalone tools

**Rejection Reason:** Experience showed need for independent diagnostic tools (Issue #11 camera disconnection debugging)

---

### Alternative 3: Shared Library Architecture

**Approach:** Common C++ core library with thin clients for Air/Ground/Tools

**Pros:**
- Code reuse across domains
- Consistent behavior

**Cons:**
- ❌ Requires C++ on Android (JNI complexity)
- ❌ Requires C++ on workstations (build complexity)
- ❌ Tight coupling prevents independent evolution
- ❌ Doesn't leverage platform-native frameworks (Jetpack Compose, Python ecosystem)

**Rejection Reason:** Platform-specific frameworks provide better UX than lowest-common-denominator approach

---

## Consequences

### Positive

✅ **Technology Flexibility:** Each domain uses best-fit technology
- Air-Side: C++ for performance and SDK compatibility
- Ground-Side: Kotlin/Compose for modern reactive UI
- Dev-Tools: Python for rapid diagnostic tool development

✅ **Independent Deployment:** Update one domain without rebuilding others
- Docker container for Air-Side (fast rebuild, isolated)
- APK for Ground-Side (Android app store distribution)
- Python scripts for Dev-Tools (no build step)

✅ **Fault Isolation:** Failure in one domain doesn't crash others
- Ground-Side UI crash doesn't affect camera operation
- Air-Side crash auto-restarts via Docker (< 10 seconds)
- Dev-Tools diagnostics don't interfere with production

✅ **Parallel Development:** Teams can work independently
- Air-Side developer works in C++ on Pi 5
- Ground-Side developer works in Kotlin on H16
- Protocol changes affect only network interfaces (versioned)

✅ **Testing Simplification:**
- Unit test each domain in isolation with mocked interfaces
- Integration test via network protocol (black-box)
- Dev-Tools enable real-time protocol validation

✅ **Platform Optimization:** Leverage platform-native capabilities
- Air-Side: Direct USB access, system-level resource monitoring
- Ground-Side: Material Design 3, Jetpack Compose reactive UI
- Dev-Tools: Python ecosystem (paramiko SSH, tkinter GUI)

---

### Negative

⚠️ **Network Overhead:** All domain communication via network (latency + bandwidth)
- Mitigation: TCP for reliability (commands), UDP for performance (status)
- Measured impact: <50ms command round-trip (acceptable for camera control)

⚠️ **Protocol Synchronization Required:** Air/Ground/Tools must agree on message formats
- Mitigation: Specification-First Architecture (ADR-002) with shared JSON specs
- Maintenance: Protocol version field in all messages

⚠️ **Increased System Complexity:** Three repos/build systems/deployment processes
- Mitigation: Monorepo structure (`sbc/`, `android/`, `tools/` subdirectories)
- Documentation: Comprehensive `docs/` with cross-references

⚠️ **Network Dependency:** System non-functional if network fails
- Mitigation: Auto-reconnect with exponential backoff (ADR-014)
- Mitigation: Heartbeat protocol detects failures within 10 seconds

⚠️ **Debugging Complexity:** End-to-end issues span multiple domains
- Mitigation: Dev-Tools provide packet analysis and log correlation
- Mitigation: Comprehensive logging with WHO tags (Issue #24)

---

## Implementation Notes

**Directory Structure:**
```
DPM-V2/
├── sbc/              # Air-Side (C++, Docker)
├── android/          # Ground-Side (Kotlin, Gradle)
├── tools/            # Dev-Tools (Python)
└── docs/             # Shared documentation
```

**Communication Ports:**
- TCP 5000: Commands (bidirectional, reliable)
- UDP 5001: Status broadcast (Air→Ground/Tools, 5Hz)
- UDP 5002: Heartbeat (bidirectional, 1Hz)

**Deployment Units:**
- Air-Side: Docker container `payload-manager:latest`
- Ground-Side: Android APK `uk.unmannedsystems.dpm_android`
- Dev-Tools: Python scripts (no packaging required)

**Verified Platforms:**
- Air-Side: Raspberry Pi 5 (Ubuntu 24.04 ARM64)
- Ground-Side: SkyDroid H16 (Android API 24-36)
- Dev-Tools: Ubuntu 22.04, Windows 10+, macOS 12+

---

## Related Decisions

- **ADR-002:** Specification-First Property Management (protocol sync solution)
- **ADR-003:** TCP/UDP Protocol Split (network communication design)
- **ADR-004:** Docker Containerization (Air-Side deployment)
- **ADR-012:** C++ for Air-Side Performance (technology choice rationale)
- **ADR-013:** Jetpack Compose for Ground UI (technology choice rationale)

---

## References

- Architecture Views: `docs/architecture/view-logical.md` (Component architecture)
- C4 Diagrams: `docs/architecture/c4-level2-container.puml` (Visual representation)
- Deployment: `docs/architecture/view-deployment.md` (Physical topology)
- LESSONS_LEARNED.md: Cross-Domain Coordination section
