# Design: Platform Abstraction Architecture

## Context

The screen recorder needs to support three platforms (Windows, Linux, macOS) with fundamentally different capture APIs:

| Platform | Window Enum | Monitor Enum | Capture API |
|----------|-------------|--------------|-------------|
| Windows | Win32 EnumWindows | Win32 EnumDisplayMonitors | Windows.Graphics.Capture |
| Linux | Compositor IPC (Hyprland, etc.) | Compositor IPC | PipeWire via xdg-desktop-portal |
| macOS | CGWindowListCopyWindowInfo | NSScreen | ScreenCaptureKit |

**Stakeholders:**
- Developers implementing platform-specific capture
- Developers maintaining shared code (encoder, state, UI)
- Users expecting consistent behavior across platforms

**Constraints:**
- Windows implementation must remain fully functional during and after refactor
- No runtime performance regression
- Clear separation to enable parallel development of platform backends
- Compile-time platform selection (no runtime detection needed)

## Goals / Non-Goals

**Goals:**
- Clean separation of platform-specific and shared code
- Single interface for all capture operations
- Easy addition of new platform backends
- Maintain existing Windows functionality
- Platform-specific dependencies only compiled for target platform

**Non-Goals:**
- Implementing Linux or macOS capture (separate changes)
- Runtime platform switching
- Plugin/dynamic loading of backends
- Audio capture abstraction (separate change)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Shared Code Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ lib.rs       │  │ state.rs     │  │ encoder/               │ │
│  │ (Tauri cmds) │  │ (Recording   │  │ (FFmpeg encoding)      │ │
│  │              │  │  Manager)    │  │                        │ │
│  └──────┬───────┘  └──────┬───────┘  └────────────────────────┘ │
│         │                 │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌────────────────────────────────────────┐               │
│         │         capture/mod.rs                  │               │
│         │    Platform Dispatch + Traits           │               │
│         │  ┌────────────────────────────────┐    │               │
│         │  │ pub trait CaptureBackend       │    │               │
│         │  │ pub trait WindowEnumerator     │    │               │
│         │  │ pub trait MonitorEnumerator    │    │               │
│         │  │ pub trait HighlightProvider    │    │               │
│         │  └────────────────────────────────┘    │               │
│         └────────────────┬───────────────────────┘               │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │ #[cfg(target_os = "...")]
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ capture/windows/│ │ capture/linux/  │ │ capture/macos/  │
│                 │ │                 │ │                 │
│ mod.rs          │ │ mod.rs          │ │ mod.rs          │
│ backend.rs      │ │ backend.rs      │ │ backend.rs      │
│ window_list.rs  │ │ (stub)          │ │ (stub)          │
│ monitor_list.rs │ │                 │ │                 │
│ recorder.rs     │ │                 │ │                 │
│ region.rs       │ │                 │ │                 │
│ highlight.rs    │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Decisions

### Decision 1: Trait-Based Abstraction

**What:** Define Rust traits for all platform-dependent operations.

**Why:**
- Compile-time polymorphism (no vtable overhead in hot paths)
- Clear contract for platform implementations
- Enables mock implementations for testing
- Idiomatic Rust pattern

**Traits:**

```rust
/// Core capture operations
pub trait CaptureBackend: Send + Sync {
    /// Start capturing a window by handle/ID
    fn start_window_capture(
        &self,
        window_id: WindowId,
    ) -> Result<(FrameReceiver, StopHandle), CaptureError>;

    /// Start capturing a screen region
    fn start_region_capture(
        &self,
        region: CaptureRegion,
    ) -> Result<(FrameReceiver, StopHandle), CaptureError>;

    /// Start capturing an entire display
    fn start_display_capture(
        &self,
        display_id: DisplayId,
    ) -> Result<(FrameReceiver, StopHandle), CaptureError>;
}

/// Window enumeration
pub trait WindowEnumerator: Send + Sync {
    fn list_windows(&self) -> Result<Vec<WindowInfo>, EnumerationError>;
}

/// Monitor/display enumeration
pub trait MonitorEnumerator: Send + Sync {
    fn list_monitors(&self) -> Result<Vec<MonitorInfo>, EnumerationError>;
}

/// Visual highlight for selection feedback
pub trait HighlightProvider: Send + Sync {
    fn show_highlight(&self, x: i32, y: i32, width: i32, height: i32);
}
```

### Decision 2: Module-Per-Platform Organization

**What:** Each platform gets its own subdirectory under `capture/`.

**Why:**
- Clear physical separation of platform code
- Easy to navigate and maintain
- Prevents accidental cross-platform imports
- Aligns with Rust module conventions

**Structure:**

```
src-tauri/src/capture/
├── mod.rs              # Traits + platform dispatch
├── types.rs            # Shared types (WindowInfo, MonitorInfo, etc.)
├── error.rs            # Error types
├── windows/
│   ├── mod.rs          # Windows backend implementation
│   ├── window_list.rs  # EnumWindows wrapper
│   ├── monitor_list.rs # EnumDisplayMonitors wrapper
│   ├── recorder.rs     # Windows.Graphics.Capture
│   ├── region.rs       # Region capture via monitor
│   └── highlight.rs    # Layered window highlight
├── linux/
│   └── mod.rs          # Stub returning NotImplemented
└── macos/
    └── mod.rs          # Stub returning NotImplemented
```

### Decision 3: Compile-Time Platform Selection

**What:** Use `#[cfg(target_os = "...")]` for platform dispatch, not runtime detection.

**Why:**
- Zero runtime overhead
- Dead code elimination for unused platforms
- Compile errors if platform code is missing
- Simpler than dynamic dispatch

**Example:**

```rust
// capture/mod.rs
#[cfg(target_os = "windows")]
mod windows;
#[cfg(target_os = "linux")]
mod linux;
#[cfg(target_os = "macos")]
mod macos;

#[cfg(target_os = "windows")]
pub use windows::WindowsBackend as PlatformBackend;
#[cfg(target_os = "linux")]
pub use linux::LinuxBackend as PlatformBackend;
#[cfg(target_os = "macos")]
pub use macos::MacOSBackend as PlatformBackend;

/// Get the platform-specific capture backend
pub fn get_backend() -> impl CaptureBackend {
    PlatformBackend::new()
}
```

### Decision 4: Platform-Conditional Dependencies in Cargo.toml

**What:** Use target-specific dependency sections.

**Why:**
- Only compile dependencies needed for target platform
- Faster builds on non-Windows platforms
- Clearer dependency management

**Example:**

```toml
# Shared dependencies
[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

# Windows-only
[target.'cfg(windows)'.dependencies]
windows-capture = "1"
windows = { version = "0.58", features = [...] }

# Linux-only (future)
[target.'cfg(target_os = "linux")'.dependencies]
# pipewire, ashpd, zbus, etc.

# macOS-only (future)
[target.'cfg(target_os = "macos")'.dependencies]
# screencapturekit, core-graphics, etc.
```

### Decision 5: Shared Types in Common Module

**What:** Platform-agnostic types (WindowInfo, MonitorInfo, CapturedFrame) defined once.

**Why:**
- Consistent API across platforms
- Frontend doesn't need platform-specific handling
- Encoder receives same frame format from all backends

**Shared types:**

```rust
// capture/types.rs
pub struct WindowInfo {
    pub id: WindowId,      // Platform-specific opaque ID
    pub title: String,
    pub process_name: String,
}

pub struct MonitorInfo {
    pub id: DisplayId,     // Platform-specific opaque ID
    pub name: String,
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
    pub is_primary: bool,
}

pub struct CapturedFrame {
    pub width: u32,
    pub height: u32,
    pub data: Vec<u8>,     // BGRA pixel data
}

pub struct CaptureRegion {
    pub monitor_id: DisplayId,
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}
```

### Decision 6: Stub Implementations for Unimplemented Platforms

**What:** Linux and macOS modules return `CaptureError::NotImplemented`.

**Why:**
- Code compiles on all platforms immediately
- Clear error message for users
- Placeholder for future implementation
- Enables CI testing on all platforms

**Example:**

```rust
// capture/linux/mod.rs
pub struct LinuxBackend;

impl LinuxBackend {
    pub fn new() -> Self { Self }
}

impl CaptureBackend for LinuxBackend {
    fn start_window_capture(&self, _: WindowId) -> Result<...> {
        Err(CaptureError::NotImplemented(
            "Linux capture not yet implemented. See: https://..."
        ))
    }
    // ... other methods similar
}
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Refactor breaks Windows functionality | Comprehensive testing before/after; incremental moves |
| Trait design doesn't fit all platforms | Research macOS/Linux APIs before finalizing; allow trait evolution |
| ID types differ across platforms | Use opaque wrapper types with platform-specific internals |
| Performance regression from abstraction | Traits are monomorphized; benchmark critical paths |

## Migration Plan

1. **Phase 1: Create structure** - Add new directories, trait definitions, shared types
2. **Phase 2: Move Windows code** - Relocate existing files to `windows/` subdirectory
3. **Phase 3: Implement traits** - Wrap existing Windows code in trait implementations
4. **Phase 4: Update consumers** - Modify lib.rs and state.rs to use abstraction
5. **Phase 5: Add stubs** - Create Linux/macOS stub modules
6. **Phase 6: Validate** - Test Windows functionality unchanged

**Rollback:** Git revert if issues found; no database/config migrations needed.

## Open Questions

1. **Window ID representation:** Should `WindowId` be a newtype wrapper around platform-specific types, or a serializable string/integer? Current Windows code uses `isize` (HWND).

2. **Async trait methods:** Should capture methods be async? Current implementation uses sync + spawn. May need `async_trait` for cleaner async support.

3. **Error granularity:** One `CaptureError` enum or separate error types per operation? Need to balance API simplicity vs. error specificity.
