# Context View

**Architecture View:** Context
**Standard:** ISO/IEC/IEEE 42010
**Date:** 2025-11-11
**Version:** 1.0

---

## Overview

The Context View describes DPM-V2 within its operational environment, identifying external actors, systems, and interfaces that define the system boundary.

**Visual Reference:** See `c4-level1-context.puml` for system context diagram.

---

## System Boundary

### What is DPM-V2?

**DPM-V2 (Drone Payload Manager Version 2)** is a professional UAV camera payload management system providing real-time control and monitoring of Sony Alpha cameras from ground stations.

**System Scope:**
- Air-Side camera control service (Raspberry Pi 5)
- Ground-Side operator interface (SkyDroid H16 Android)
- Development tools (SystemTools diagnostics)
- Communication protocols (TCP/UDP)

**What DPM-V2 Does:**
- Controls Sony Alpha cameras via USB
- Broadcasts real-time telemetry
- Provides touch-based operator interface
- Monitors system health
- Enables diagnostic testing

**What DPM-V2 Does NOT Do:**
- Flight control (handled by drone autopilot)
- Video recording (handled by camera)
- Gimbal control (Phase 2 future feature)
- Video streaming (RTSP from separate source)

---

## External Actors

### 1. Drone Operator (Primary User)

**Role:** Professional UAV operator controlling camera payload from ground station

**Characteristics:**
- Technical proficiency: Medium to High
- Operating environment: Field operations, often outdoors
- Workload: High (flying drone + managing payload)
- Time pressure: Real-time decisions during flight

**Interactions with DPM-V2:**
- **Views:** Camera status, system telemetry, live video feed
- **Controls:** Shutter speed, aperture, ISO, white balance, focus mode
- **Actions:** Trigger photo capture, adjust settings in real-time
- **Interface:** Touch screen on H16 ground station tablet

**Key Concerns:**
- **Reliability:** System must not fail during flight
- **Responsiveness:** <50ms command response time required
- **Simplicity:** Interface must be usable with gloves, in sunlight
- **Visibility:** Clear status indicators for camera health

**Example Workflow:**
1. Pre-flight: Connect to Air-Side, verify camera connected
2. During flight: Monitor camera status, capture photos on demand
3. Adjust settings: Change exposure for lighting conditions
4. Post-flight: Verify image count, download if needed

---

### 2. System Maintainer (Secondary User)

**Role:** Technical personnel maintaining and troubleshooting the system

**Characteristics:**
- Technical proficiency: High
- Operating environment: Lab, hangar, or field
- Access: Physical access to both Air-Side and Ground-Side hardware
- Time frame: Pre/post flight operations

**Interactions with DPM-V2:**
- **Monitors:** System logs, diagnostic data, connection health
- **Troubleshoots:** Network issues, camera connectivity problems
- **Tests:** Protocol validation, command/response verification
- **Updates:** Software versions, configuration changes

**Interface:** SystemTools diagnostic application (Windows/Linux laptop)

**Key Concerns:**
- **Diagnosability:** Clear error messages, detailed logs
- **Observability:** Packet-level monitoring capability
- **Testability:** Ability to test without full system
- **Documentation:** Troubleshooting guides, error code references

**Example Workflow:**
1. Issue reported: Camera not connecting
2. Connect SystemTools: Monitor UDP status broadcasts
3. Analyze: Check packet rate, connection health, error codes
4. Diagnose: Identify USB issue, network problem, or SDK error
5. Fix: Apply solution, verify with diagnostic tools

---

### 3. Software Developer (Tertiary User)

**Role:** Developer extending, debugging, or certifying the system

**Characteristics:**
- Technical proficiency: Expert
- Operating environment: Development workstation + test hardware
- Access: Full system access (SSH, source code, debuggers)
- Time frame: Continuous development and maintenance

**Interactions with DPM-V2:**
- **Develops:** New features, bug fixes, optimizations
- **Debugs:** Code-level issues, protocol problems, performance
- **Tests:** Unit tests, integration tests, system tests
- **Documents:** Architecture, API, protocols, lessons learned

**Interfaces:**
- IDE (VS Code, Android Studio, CLion)
- SSH to Air-Side
- SystemTools for protocol testing
- Git for version control

**Key Concerns:**
- **Maintainability:** Clean architecture, clear separation of concerns
- **Testability:** Ability to test components in isolation
- **Documentation:** Architecture docs, API references, ADRs
- **Debuggability:** Logging, error handling, diagnostic tools

**Example Workflow:**
1. Feature request: Add new camera property control
2. Design: Update protocol, modify PropertyLoader specs
3. Implement: Air-Side C++ code, Ground-Side Kotlin UI
4. Test: SystemTools command testing, integration testing
5. Document: Update architecture docs, commit messages

---

## External Systems

### 1. Sony Alpha Camera

**Type:** Hardware Device (External)
**Connection:** USB 3.0 bulk transfer
**Models Supported:** α1, α7R V, α7 IV, α7S III (Sony E-mount cameras)

**Role:** Professional mirrorless camera providing high-quality still photography

**Interface with DPM-V2:**
- **Connection:** USB-C cable from camera to Raspberry Pi 5
- **Protocol:** Sony proprietary camera protocol (via SDK)
- **Communication:** Request/response for commands, streaming for LiveView
- **Power:** Camera battery (independent of DPM-V2)

**Data Exchanged:**
- **From Camera:** Status, property values, image count, battery level
- **To Camera:** Control commands (shutter, property set, mode changes)

**Dependencies:**
- Camera must be powered on
- USB cable connected
- Camera in PC Remote mode
- Compatible firmware version

**Failure Modes:**
- Camera powered off → DPM-V2 reports "disconnected"
- USB cable disconnected → Auto-reconnect on reconnection
- Camera firmware incompatible → SDK initialization fails
- Battery depleted → Connection lost

---

### 2. Sony Camera Remote SDK v2.00.00

**Type:** Software Library (External)
**Vendor:** Sony Corporation
**License:** Proprietary

**Role:** Provides C++ API for camera control and monitoring

**Interface with DPM-V2:**
- **Integration:** Native C++ library linking
- **Location:** Air-Side only (Raspberry Pi 5)
- **Libraries:** libCr_Core.so + CrAdapter/*.so (dynamic adapters)
- **Initialization:** SDK initialization on Air-Side startup

**APIs Used:**
- Camera enumeration and connection
- Property get/set operations
- Shutter release commands
- Status monitoring
- LiveView streaming (future)

**Dependencies:**
- libxml2, libusb-1.0 system libraries
- USB device access permissions
- Compatible camera firmware

**Constraints:**
- Proprietary (no source code access)
- Limited error documentation
- Model-specific adapters required
- Some properties undocumented

---

### 3. Android OS (SkyDroid H16)

**Type:** Platform (External)
**Version:** Android 7.0+ (API 24-36)
**Vendor:** Google (customized by SkyDroid)

**Role:** Operating system hosting Ground-Side application

**Interface with DPM-V2:**
- **Runs:** Ground-Side APK (DPM Android)
- **Provides:** Touch UI, network stack, storage, video playback
- **Lifecycle:** Manages app lifecycle, permissions, resources

**APIs Used:**
- Kotlin/Java Android SDK
- Jetpack Compose for UI
- AndroidX lifecycle, ViewModel, DataStore
- ExoPlayer for RTSP video
- Network sockets (TCP/UDP)

**Dependencies:**
- Network access permission
- Storage permission (for settings)
- Wake lock (for continuous operation)

**Constraints:**
- Touch-optimized UI required
- Battery life considerations
- Background process restrictions
- Android security model

---

### 4. Docker Engine

**Type:** Container Runtime (External)
**Version:** Docker 20.10+
**Platform:** Raspberry Pi 5 (Ubuntu 24.04 ARM64)

**Role:** Containerizes Air-Side service for isolation and repeatability

**Interface with DPM-V2:**
- **Runs:** Air-Side service in container
- **Provides:** Process isolation, dependency management, restart policy
- **Mounts:** Sony SDK libraries, USB devices

**Container Configuration:**
- **Image:** Built from `sbc/Dockerfile`
- **Name:** payload-manager
- **Network:** Host mode (for UDP broadcast)
- **Volumes:**
  - `/usr/local/lib` → Sony SDK
  - `/dev/bus/usb` → USB devices
- **Restart:** Always (auto-restart on failure)

**Benefits:**
- Consistent runtime environment
- Easy deployment and updates
- Resource isolation
- Automatic restart on crash

---

### 5. Network Infrastructure

**Type:** Physical Infrastructure (External)
**Components:** WiFi AP, Ethernet switches, R16 data link

**Role:** Provides communication between Air-Side, Ground-Side, and Dev-Tools

#### Production Network (R16 Ethernet Link)
- **Technology:** SkyDroid H16 ↔ R16 Air Unit digital data link
- **Topology:** VXLAN bridge (Layer 2 tunnel)
- **Addressing:** 192.168.144.x subnet
  - Air-Side: 192.168.144.53
  - Ground-Side: 192.168.144.92
- **Bandwidth:** 20-50 Mbps typical
- **Latency:** <50ms typical
- **Range:** Up to several kilometers

#### Development Network (WiFi)
- **Technology:** WiFi 802.11ac/ax
- **Addressing:** 10.0.1.x subnet
  - Air-Side: 10.0.1.53
  - Ground-Side: 10.0.1.92
  - Dev-Tools: 10.0.1.x (various)
- **Purpose:** Development, testing, SSH access
- **Not used in production flight**

**DPM-V2 Network Requirements:**
- **Static IP addresses** (DHCP not supported for VXLAN)
- **UDP broadcast support** (for status telemetry)
- **TCP connection stability** (long-lived command channel)
- **Low latency** (<100ms for responsive control)

---

## External Interfaces

### 1. USB Camera Interface

**Direction:** Air-Side ↔ Sony Camera (bidirectional)
**Protocol:** USB bulk transfer + Sony proprietary protocol
**Physical:** USB 3.0 Type-C

**Data Exchange:**
- **Commands:** Shutter, property set, mode changes
- **Responses:** Status, property values, acknowledgments
- **Telemetry:** Battery, image count, error codes

**Performance:**
- **Latency:** <20ms typical for commands
- **Throughput:** Low (commands/status only, no image transfer)
- **Reliability:** USB retry mechanism built-in

---

### 2. Network Interfaces (TCP/UDP)

**Direction:** Air-Side ↔ Ground-Side / Dev-Tools (bidirectional)

#### TCP Command Channel (Port 5000)
- **Purpose:** Bidirectional command/response
- **Protocol:** JSON over TCP
- **Connection:** Long-lived, Ground→Air client connection
- **Use:** Camera commands, property queries, responses

#### UDP Status Broadcast (Port 5001)
- **Purpose:** Real-time telemetry
- **Protocol:** JSON over UDP
- **Direction:** Air→Ground/Dev unidirectional broadcast
- **Rate:** 5 Hz (200ms interval)
- **Use:** Camera status, system metrics

#### UDP Heartbeat (Port 5002)
- **Purpose:** Connection health monitoring
- **Protocol:** JSON over UDP
- **Direction:** Bidirectional
- **Rate:** 1 Hz
- **Timeout:** 10 seconds → trigger reconnect

#### UDP Log Streaming (Port 5005)
- **Purpose:** Real-time diagnostic log streaming
- **Protocol:** JSON over UDP
- **Direction:** Air→Ground/Dev (unidirectional, on-demand)
- **Activation:** Via `logging.enable_streaming` command
- **Duration:** Configurable (default 300 seconds)
- **Features:** Dynamic client registration, auto-disable, multi-client support

**See INTEGRATION_POINTS.md for detailed protocol specifications**

---

### 3. SSH Interface (Development)

**Direction:** Dev-Tools → Air-Side (inbound to Pi 5)
**Protocol:** SSH (port 22)
**Purpose:** Remote access for diagnostics and maintenance

**Use Cases:**
- Log retrieval and analysis
- System diagnostics
- Manual testing
- Software updates
- Configuration changes

**Security:** SSH key-based authentication recommended

---

## System Context Concerns

### Stakeholder Concerns Addressed

**Operators:**
- ✅ Clear system boundary (what DPM-V2 controls vs drone autopilot)
- ✅ External dependencies identified (camera, network)
- ✅ Failure modes documented (what happens when camera disconnects)

**Maintainers:**
- ✅ External systems clearly identified for troubleshooting
- ✅ Interface points documented (where problems can occur)
- ✅ Diagnostic access paths defined (SSH, SystemTools)

**Developers:**
- ✅ External APIs documented (Sony SDK, Android, Docker)
- ✅ System boundary clear (what's in-scope for development)
- ✅ Integration points explicit (where to focus testing)

---

## Context Evolution

### Current State (v2.7)
- Three-domain architecture (Air/Ground/Tools)
- USB camera control (Sony SDK)
- Network communication (TCP/UDP)
- Development tools operational

### Planned Evolution
- **Phase 2 (Future):** Gimbal integration, RTSP video streaming
- **Phase 3 (Future):** Log download, remote file access
- **Certification:** External system for flight approval

### External System Changes
- **Sony SDK:** Updates may require compatibility testing
- **Android OS:** API level increases require adaptation
- **R16 Link:** Firmware updates may affect network performance

---

## Dependencies and Constraints

### Critical Dependencies
1. **Sony SDK:** Must be compatible with camera firmware
2. **Network Infrastructure:** Static IPs required for VXLAN
3. **USB Connection:** Camera must be in PC Remote mode
4. **Android Platform:** Minimum API 24 (Android 7.0)

### External Constraints
1. **Proprietary SDK:** Limited control over Sony SDK behavior
2. **Network Latency:** R16 link latency impacts responsiveness
3. **USB Power:** Camera battery independent of system
4. **Android Lifecycle:** App may be killed by OS

---

## Related Documents

- **Visual:** `c4-level1-context.puml` - System context diagram
- **Integration:** `INTEGRATION_POINTS.md` - Network protocol details
- **Deployment:** `view-deployment.md` - Physical deployment architecture
- **Security:** `view-security-reliability.md` - Security concerns with external systems

