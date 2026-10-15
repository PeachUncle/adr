# ADR-017: SystemTools JSON-Based Filters and Configuration Management Architecture

**Status:** Accepted

**Date:** 2025-11-18

**WHO:** CC-Dev-Tools

**Deciders:** SystemTools Development Team

**Related Issues:** #74, #105, #115, #116, #136, #147, #149

---

## Context

SystemTools (Dev-Tools) has evolved significantly from a basic diagnostic tool to a comprehensive professional monitoring and management suite. Several architectural challenges emerged:

1. **GUI Freeze Bug (Issue #146):** Real-time filter evaluation on large log streams caused UI freezing
2. **Hardcoded Filter Logic:** Filter definitions embedded in code, requiring redeployment for changes
3. **Missing Config Management:** No remote configuration capability for Air-Side system
4. **Limited Testing Tools:** Manual testing of error responses required external tools
5. **Scattered File Access:** Multiple file transfer mechanisms without unified architecture

### Problem Statement

How can we provide a flexible, performant, and maintainable architecture for:
- Dynamic log filtering without UI freezes?
- Remote Air-Side configuration management?
- Protocol validation and testing?
- Unified file access across multiple sources?

---

## Decision

We adopt a **multi-layered architectural enhancement** for SystemTools:

### 1. JSON-Based Dynamic Filter System (Issue #147)

**Architecture:**
```
┌─────────────────────────────────────────┐
│ UI Layer (Tkinter Checkboxes)          │
│ - Multi-select contexts                 │
│ - Multi-select levels                   │
│ - Preset buttons                        │
│ - Apply button (explicit filter)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ LogFilterManager                        │
│ - load() from JSON                      │
│ - get_log_contexts()                    │
│ - get_log_levels()                      │
│ - get_filter_presets()                  │
│ - apply_preset(name)                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ config/log_filter_labels.json          │
│ {                                       │
│   "log_contexts": [...],                │
│   "log_levels": [...],                  │
│   "filter_presets": [...],              │
│   "ui_settings": {...}                  │
│ }                                       │
└─────────────────────────────────────────┘
```

**Key Principles:**
- **Deferred Evaluation:** Filter applied only on button click, not real-time
- **JSON-Driven:** UI generated from configuration file
- **User-Customizable:** Edit JSON to add/modify filters without code changes
- **Multi-Criteria:** AND/OR logic for combining context and level filters

### 2. Manager-Based Client Architecture

**Pattern:**
```
┌─────────────────┐
│ UI Tab          │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Domain Manager                  │
│ (AirSideManager / GroundSide)  │
│ - Connection state management   │
│ - Protocol serialization        │
│ - Retry logic                   │
│ - Response validation           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Network Client  │
│ (TCP/UDP/SSH)   │
└─────────────────┘
```

**Responsibilities:**
- **UI Tab:** User interaction, display
- **Manager:** Business logic, state, protocol
- **Network Client:** Low-level I/O

### 3. Air-Side Configuration Management (Issues #115, #116)

**Implementation:**
```python
# Protocol Command: system.get_config
{
  "command": "system.get_config",
  "parameters": {}
}

# Protocol Command: system.update_config
{
  "command": "system.update_config",
  "parameters": {
    "updates": {
      "logging.level": "DEBUG",               # Flat dotted-key format
      "network.tcp_port": 5000,               # Not nested objects
      "logging.network_systemtools_enabled": true
    }
  }
}
```

**Integration:**
- Advanced Settings tab provides UI
- AirSideManager sends commands
- Real-time validation and feedback
- Restart detection and warnings

### 4. SQLite Performance Analytics

**Schema:**
```sql
CREATE TABLE system_metrics (
    timestamp INTEGER PRIMARY KEY,
    cpu_percent REAL,
    memory_used_mb INTEGER,
    disk_used_mb INTEGER,
    network_rx_mbps REAL,
    network_tx_mbps REAL
);

CREATE TABLE command_latency (
    timestamp INTEGER PRIMARY KEY,
    command TEXT,
    latency_ms REAL,
    success BOOLEAN
);

CREATE TABLE connection_health (
    timestamp INTEGER PRIMARY KEY,
    domain TEXT,
    connected BOOLEAN,
    latency_ms REAL
);
```

**Benefits:**
- Persistent metrics across restarts
- Historical trend analysis
- Lightweight (SQLite embedded)
- Easy export (CSV, JSON)

---

## Consequences

### Positive

1. **No More GUI Freeze:**
   - Explicit Apply button prevents real-time filter evaluation
   - Users can construct complex filters without lag
   - Eliminates Issue #146 permanently

2. **Easy Customization:**
   - Edit `log_filter_labels.json` to add filters
   - No code changes or redeployment
   - User-specific filter configurations possible

3. **Remote Config Management:**
   - Change Air-Side settings from SystemTools
   - No SSH needed for configuration changes
   - Supports both runtime and persistent updates

4. **Better Testing:**
   - Invalid command test validates protocol compliance
   - Error response verification built-in
   - Log context verification ([COMMAND] not [NETWORK])

5. **Historical Analytics:**
   - SQLite provides persistent storage
   - Trend analysis over time
   - Performance regression detection

6. **Cleaner Architecture:**
   - Manager pattern separates concerns
   - UI decoupled from network details
   - Easy to add new domains/tabs

### Negative

1. **Increased Complexity:**
   - More layers (UI → Manager → Client)
   - JSON configuration adds abstraction
   - SQLite adds database management

2. **Learning Curve:**
   - Developers must understand manager pattern
   - JSON schema for filters must be documented
   - SQL queries for analytics

3. **Migration Effort:**
   - Existing code needs refactoring to use managers
   - Old filter logic must be replaced
   - Testing all new components

4. **Storage Requirements:**
   - SQLite database grows over time
   - Need cleanup/archival strategy
   - Disk space monitoring required

### Mitigations

1. **Documentation:**
   - Created comprehensive architecture documentation (this ADR)
   - Updated SOFTWARE_ARCHITECTURE_DOCUMENT.md with deprecation notes
   - Inline code comments for manager pattern

2. **Cleanup Strategy:**
   - SQLite retention policy (default: 7 days)
   - Auto-cleanup on startup
   - Manual export/archive capability

3. **Backward Compatibility:**
   - Old sections deprecated (not deleted) in architecture docs
   - Evolution history preserved
   - Migration path documented

---

## Alternatives Considered

### Alternative 1: Keep Real-Time Filtering

**Approach:** Optimize filter evaluation instead of deferring

**Pros:**
- Immediate feedback
- No Apply button needed
- Familiar pattern

**Cons:**
- Cannot eliminate freeze on complex filters
- Optimization has limits with large log streams
- Still causes UI lag

**Rejected Because:** Cannot guarantee freeze-free operation

### Alternative 2: Use External Database (PostgreSQL)

**Approach:** Use PostgreSQL instead of SQLite for analytics

**Pros:**
- More powerful queries
- Better concurrency
- Network access

**Cons:**
- Requires installation and configuration
- Overkill for single-user diagnostic tool
- Connection management complexity
- Not portable (can't run without DB server)

**Rejected Because:** SQLite sufficient for this use case

### Alternative 3: Hardcoded Presets

**Approach:** Keep filter definitions in Python code

**Pros:**
- Simpler implementation
- No JSON parsing
- Type safety from Python

**Cons:**
- Requires code changes for new filters
- No user customization
- Redeployment needed

**Rejected Because:** Flexibility more important than simplicity

---

## Implementation

### Components Created/Modified

**New Components:**
- `utils/log_filter_manager.py` - JSON filter manager
- `config/log_filter_labels.json` - Filter definitions
- `data/performance.db` - SQLite analytics database
- `managers/air_side_manager.py` - Enhanced with config commands
- `gui/tab_advanced_settings.py` - Config management UI

**Modified Components:**
- `DPM_Management_System.py` - Renamed from main.py, integrated all features
- `gui/tab_logs.py` - Integrated JSON filter system
- `gui/tab_remote_control.py` - Added invalid command test
- `gui/tab_file_browser.py` - Enhanced with Docker Logs sub-tabs (Issue #136)

**Documentation:**
- `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md` - Updated (v1.3)
- `docs/architecture/c4-level3-dev-tools-components.puml` - Updated diagram
- `/tmp/systemtools_architecture_update.md` - Change summary

### Git Commits

**Expected Commits:**
- `[SYSTEMTOOLS][FEATURE] JSON-Based Dynamic Filter System - Issue #147`
- `[SYSTEMTOOLS][FIX] Protocol Compliance Fixes for system.update_config - Issues #115, #116`
- `[SYSTEMTOOLS][ENHANCEMENT] Air-Side Remote Tab Improvements - Issue #149`
- `[ARCHITECTURE][SYSTEMTOOLS] Architecture Documentation Update - Issues #74-#149`

---

## Compliance

### Protocol Compliance

**Validated:**
- ✅ Flat dotted-key format for config updates (`logging.level` not nested)
- ✅ [COMMAND] log context for config commands (not [NETWORK])
- ✅ Error codes match protocol spec (5000-5003)
- ✅ Message format follows protocol/commands.json

### ARCHITECTURE_UPDATE_RULES.md Compliance

**Followed:**
- ✅ Deprecated sections commented out (not deleted)
- ✅ WHO/Date/Time stamps added to new sections
- ✅ Superseded by references included
- ✅ Architecture update issue will be created (#150 expected)

### Organization Architecture Standard Compliance

**Per `docs/standards/ARCHITECTURE_DOCUMENTATION_STANDARD.md`:**
- ✅ ADR follows template structure
- ✅ Context clearly stated
- ✅ Decision explicit
- ✅ Alternatives documented (3 alternatives)
- ✅ Consequences identified (positive and negative)
- ✅ Implementation details included

---

## References

**Issues:**
- #74 - Tri-Domain Log Aggregation Foundation
- #105 - GUI Integration
- #115 - system.get_config implementation
- #116 - system.update_config implementation
- #136 - File Browser Docker Logs
- #146 - GUI Freeze Bug (eliminated by #147)
- #147 - JSON-Based Dynamic Filter System
- #149 - Air-Side Remote Testing Enhancements

**Documents:**
- `protocol/commands.json` - Protocol specification
- `.claude/ARCHITECTURE_UPDATE_RULES.md` - Architecture update rules
- `docs/standards/ARCHITECTURE_DOCUMENTATION_STANDARD.md` - Org standard
- `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md` (v1.3) - System architecture

**Code:**
- `SystemTools/utils/log_filter_manager.py` - Filter manager implementation
- `SystemTools/config/log_filter_labels.json` - Filter configuration
- `SystemTools/DPM_Management_System.py` - Main application

---

## Status History

| Date | Status | Notes |
|------|--------|-------|
| 2025-11-18 | Proposed | Initial draft |
| 2025-11-18 | Accepted | Implementation complete, awaiting PM review |

---

## Notes

This ADR consolidates multiple related architectural decisions made during SystemTools evolution from Phase 1 (Issue #74) through Phase 5 (Issue #149). Each phase built upon previous work:

- **Phase 1:** Foundation (tri-domain log aggregation)
- **Phase 2:** GUI integration
- **Phase 3:** Config management
- **Phase 4:** JSON filter system
- **Phase 5:** Testing enhancements

The architecture has evolved from a simple diagnostic tool to a comprehensive professional monitoring and management suite while maintaining backward compatibility and preserving architectural evolution history.

---

**ADR-017 - Approved by CC-Dev-Tools - 2025-11-18**
