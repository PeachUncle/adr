# ADR-005: Global Hotkey Implementation

## Status

Accepted

## Date

2026-01-04

## Context

The soundboard needs global hotkeys that work when other applications (games, Discord) have focus. We needed to choose an implementation approach for capturing keyboard input system-wide.

## Decision

We use the Win32 `RegisterHotKey` API with a message-only window (`HWND_MESSAGE`) to receive `WM_HOTKEY` messages.

### Implementation

```
Physical Key Press
    ↓
Windows OS (RegisterHotKey API)
    ↓
WM_HOTKEY message → WindowMessageSink (HWND_MESSAGE window)
    ↓
HotkeyService.OnHotkeyPressed()
    ↓
100ms debounce check → Fire event to MainViewModel
```

We also use:
- `MOD_NOREPEAT` flag to prevent OS-level auto-repeat
- 100ms software debounce as additional protection
- Suspend/Resume pattern for hotkey learning mode

## Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **RegisterHotKey (chosen)** | Simple, no admin needed, low CPU, anti-cheat safe | Fails in exclusive fullscreen games |
| **Low-level hooks (SetWindowsHookEx)** | Works in exclusive fullscreen | Blocked by anti-cheat (EAC, BattlEye, Vanguard), higher CPU, called for every keypress |
| **Raw Input API** | Direct hardware access, works in exclusive fullscreen | Complex implementation, flagged by some anti-cheat, must decode scancodes manually |
| **DirectInput** | Legacy game input API | Deprecated since Windows 8, poor modern OS integration |

## Rationale

### Why RegisterHotKey?

1. **Simplicity**: ~50 lines of code total for the entire hotkey system
2. **Safety**: Cannot crash Windows, break other apps, or trigger anti-cheat detection
3. **No elevation**: Works without admin privileges
4. **Low overhead**: OS delivers messages only when registered hotkeys are pressed
5. **Error detection**: Error 1409 immediately tells you if a hotkey is already in use

### Why not low-level hooks?

While low-level hooks work in exclusive fullscreen, they have critical drawbacks:

- **Anti-cheat incompatibility**: Easy Anti-Cheat, BattlEye, Riot Vanguard, and Ricochet all block or flag low-level keyboard hooks as potential aim-assist/cheat vectors
- **CPU overhead**: Hook is called for every keypress system-wide, even if filtered
- **Complexity**: Requires careful callback management and can cause system-wide input lag if poorly implemented

For a soundboard used alongside competitive games, triggering anti-cheat is a worse outcome than hotkeys not working in fullscreen.

### The exclusive fullscreen trade-off

RegisterHotKey **does not work** when a game runs in exclusive fullscreen mode because:
- The game has exclusive control of GPU and input
- Windows message pump doesn't run in exclusive mode
- No way to deliver WM_HOTKEY to our message window

**Affected scenarios**: ~10% of gaming situations (exclusive fullscreen DirectX/Vulkan games)

**Unaffected scenarios**: Windowed mode, borderless windowed, streaming setups, Discord, most modern games defaulting to borderless

## Consequences

### Positive
- Works reliably in ~90% of target scenarios
- Zero risk of anti-cheat bans
- Simple, maintainable codebase
- Excellent hotkey conflict detection
- Clean learning mode (suspend/resume all hotkeys)

### Negative
- **Silent failure in exclusive fullscreen**: Hotkeys simply don't fire, with no user feedback
- Users must use Alt+Tab or borderless windowed mode for these games
- Cannot work around games that aggressively block input

### Mitigations
- Document the exclusive fullscreen limitation in user-facing help
- Recommend borderless windowed mode for gaming
- The app's target use case (streaming/Discord with VoiceMeeter) typically uses windowed mode anyway

### Technical Debt
- Consider adding detection for exclusive fullscreen (via `GetForegroundWindow` + window style check) and warning the user
- Could add optional Raw Input fallback as an advanced setting, with clear anti-cheat risk warning

## Implementation Notes

Key files:
- `Services/HotkeyService.cs` - Core registration, learning mode suspend/resume
- `Interop/NativeMethods.cs` - P/Invoke declarations
- `Interop/WindowMessageSink.cs` - HWND_MESSAGE window for WM_HOTKEY

### Hotkey ID scheme
- Tiles: 1000-1015 (TileHotkeyIdBase + tileIndex)
- Stop Current: 100
- Stop All: 101

### Learning mode
When user clicks "Set" to assign a hotkey:
1. `SuspendAll()` unregisters all hotkeys temporarily
2. Window captures keypress via `PreviewKeyDown`
3. If key conflicts with another tile, that tile is unbound automatically
4. `ResumeAll()` re-registers all hotkeys with new assignment

This allows seamlessly reassigning keys that are already in use.
