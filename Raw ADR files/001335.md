# ADR-017: Runtime Configuration Application Without Restart

**WHO:** CC-Air-Side
**Date:** 2025-11-18
**Time:** 22:30 UTC
**Status:** Accepted
**Deciders:** Air-Side Development Team
**Related Issues:** #115, #116, #148
**Related Views:** `view-logical.md`, `view-integration.md`
**Supersedes:** Static configuration (required container restart for changes)

---

## Context

### Problem

Air-Side configuration changes via `system.update_config` command were persisted to `local.json` but required container restart to take effect:

1. **Original Behavior:**
   - `system.update_config` → ConfigManager::set() → config_.save()
   - Changes written to file ✅
   - Running subsystems (logger, network) unaware of changes ❌
   - Container restart required to reload config

2. **User Pain Points:**
   - Testing config changes required restart (30-60 seconds downtime)
   - SystemTools passive logging changes required restart
   - Ground-Side cannot toggle Air-Side features in real-time
   - Reduced diagnostics flexibility during field operations

3. **Example Scenario:**
   ```
   User Action: Disable SystemTools logging to reduce bandwidth
   Command: system.update_config({"logging.network_systemtools_enabled": false})
   Expected: Logs stop streaming immediately
   Actual: Logs continue until container restart
   ```

### Design Question

How can we apply configuration changes to running subsystems without restart?

**Options Considered:**
1. **Option A:** Accept restart requirement (keep current behavior)
2. **Option B:** Periodic config reload (poll file every N seconds)
3. **Option C:** Explicit subsystem notification after config update
4. **Option D:** Event-driven config change propagation

---

## Decision

**We will use Option C: Explicit Subsystem Notification**

After `ConfigManager::set()` succeeds, `handleSystemUpdateConfig` will explicitly notify affected subsystems of runtime changes.

### Implementation Pattern

```cpp
json TCPServer::handleSystemUpdateConfig(const json& payload, int seq_id) {
    // 1. Apply config updates
    for (auto& [key, value] : updates.items()) {
        ConfigManager::getInstance().set(key, value);
    }

    // 2. Persist to file
    ConfigManager::getInstance().saveLocal();

    // 3. ⭐ NEW: Apply runtime updates
    for (const auto& key : updated) {
        if (key == "logging.network_systemtools_enabled") {
            bool enabled = ConfigManager::getInstance().getBool(key);
            StructuredLogger::getInstance().setSystemToolsEnabled(enabled);
            LOG_INFO("Applied runtime update: SystemTools logging " +
                     (enabled ? "ENABLED" : "DISABLED"));
        }
        // Future: Add other runtime-updatable settings here
    }

    // 4. Return response
    return success_response;
}
```

### New Subsystem Methods

**StructuredLogger:**
```cpp
void StructuredLogger::setSystemToolsEnabled(bool enabled) {
    // Find NetworkSink and update runtime state
    for (auto& sink : sinks_) {
        if (sink->name() == "NetworkSink") {
            auto network_sink = std::dynamic_pointer_cast<NetworkSink>(sink);
            network_sink->setSystemToolsEnabled(enabled);
        }
    }
}
```

**NetworkSink:**
```cpp
void NetworkSink::setSystemToolsEnabled(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    systemtools_enabled_ = enabled;
    std::cout << "SystemTools logging " << (enabled ? "ENABLED" : "DISABLED")
              << " (runtime config update)" << std::endl;
}
```

---

## Consequences

### Positive

1. **✅ Immediate Effect:**
   - Config changes apply instantly (sub-second)
   - No container restart required
   - Zero downtime for configuration adjustments

2. **✅ Better User Experience:**
   - SystemTools can toggle features in real-time
   - Ground-Side can adjust Air-Side behavior dynamically
   - Testing config changes is instant

3. **✅ Field Operations:**
   - Adjust logging levels remotely without restart
   - Toggle SystemTools monitoring on-demand
   - Reduce bandwidth usage dynamically

4. **✅ Predictable Behavior:**
   - Explicit notification (not polling-based)
   - Clear logging of runtime state changes
   - Synchronous update (change confirmed in response)

### Negative

1. **⚠️ Maintenance Overhead:**
   - Each new runtime-configurable setting requires:
     - Subsystem method (e.g., setFoo())
     - Update check in handleSystemUpdateConfig()
     - Testing of runtime state change

2. **⚠️ Complexity:**
   - Config update logic now in two places:
     - Startup initialization (from file)
     - Runtime update (from command)

3. **⚠️ Not All Settings Runtime-Updatable:**
   - Some settings still require restart:
     - Network ports (tcp_port, udp_*_port)
     - Thread pool sizes
     - Core architecture changes
   - Must clearly document which settings are runtime-updatable

### Mitigations

1. **Documentation:**
   - Mark runtime-updatable settings in config schema
   - Document restart-required settings clearly
   - Include in `system.update_config` response: `restart_required: bool`

2. **Pattern Consistency:**
   - All subsystems follow same pattern: `setFoo(value)`
   - All methods thread-safe (mutex-protected)
   - All log runtime state changes

3. **Testing:**
   - Test both startup and runtime paths for each setting
   - Verify thread safety of runtime updates
   - Confirm state consistency across restarts

---

## Related Decisions

- **ADR-006:** Multi-Threaded Air-Side Design (thread safety requirements)
- **ADR-018:** Conditional ERROR Log Streaming (uses runtime update pattern)
- **Issue #115:** system.get_config implementation
- **Issue #116:** system.update_config implementation

---

## Implementation Details

### Phase 1: Logging Configuration (✅ Complete)

**Runtime-Updatable:**
- `logging.network_systemtools_enabled` → `StructuredLogger::setSystemToolsEnabled()`

**Restart-Required:**
- `logging.level` (affects log macros, needs logger reinit)
- `logging.file_path` (affects file sink, needs reopen)

### Phase 2: Future Extensions (Planned)

**Candidates for Runtime Update:**
- `network.systemtools_ip` → `NetworkSink::setSystemToolsIP()` (already implemented)
- `network.ground_ip` → `UDPBroadcaster::setGroundIP()`
- `health.check_interval` → `HealthMonitor::setCheckInterval()`

**Always Restart-Required:**
- `network.tcp_port` (server socket bound at startup)
- `network.udp_status_port` (broadcaster socket bound at startup)
- `network.udp_heartbeat_port` (heartbeat socket bound at startup)

---

## Compliance

**ISO/IEC/IEEE 42010:2011:** Architecture concern addressed - Configuration Management
**C4 Model:** Impacts Level 3 (Components) - ConfigManager, StructuredLogger, NetworkSink
**Trade-offs:** Documented above (Positive/Negative/Mitigations)

---

## References

- Implementation: `sbc/src/protocol/tcp_server.cpp` (handleSystemUpdateConfig)
- Logging Subsystem: `sbc/src/logging/structured_logger.{h,cpp}`
- Network Sink: `sbc/src/logging/sinks/network_sink.{h,cpp}`
- Configuration Manager: `sbc/src/config/config_manager.{h,cpp}`
- Git Commit: 9a5272e (pending push)

---

**Approved by:** CC-Air-Side
**Review Date:** 2025-11-18
**Next Review:** After field deployment feedback
