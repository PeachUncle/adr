---
title: "ADR-0005: Keyboard Shortcuts and Input Routing Policy"
status: "Accepted"
date: "2025-12-10"
authors: "mjordan"
tags: ["architecture", "input", "keyboard", "ux"]
supersedes: ""
superseded_by: ""
---

## Status

Accepted

## Context

The Curve Editor exposes a growing set of keyboard shortcuts, including:

- File operations: `Ctrl+N`, `Ctrl+O`, `Ctrl+S`, `Ctrl+Shift+S`.
- Undo/redo: `Ctrl+Z`, `Ctrl+Y`.
- Panel visibility toggles: `Ctrl+B` (browser), `Ctrl+R` (properties), `Ctrl+G` (curve data).

Early iterations mixed window-level key bindings with control-local undo and ad-hoc handlers. This produced surprising behavior:

- In some contexts, `Ctrl+Z` would only undo the last change in a single `TextBox` instead of the last document-level edit.
- Shortcuts were not consistently discoverable in the UI.

We need a clear policy so new shortcuts are added consistently, and undo/redo routing remains predictable as the app grows.

## Decision

We adopt a **window-level shortcut and input routing policy** with the following rules:

1. **All global shortcuts are defined on `MainWindow`**
- `MainWindow.axaml` owns the authoritative list of keyboard shortcuts in `<Window.KeyBindings>`.
- Shortcuts map to commands on `MainWindowViewModel` (or its sub-view-models via properties), not to code-behind handlers.
- Examples:
  - `Ctrl+N` → `NewMotorCommand`.
  - `Ctrl+O` → `OpenFileCommand`.
  - `Ctrl+S` → `SaveCommand`.
  - `Ctrl+Shift+S` → `SaveAsCommand`.
  - `Ctrl+Z` → `UndoCommand`.
  - `Ctrl+Y` → `RedoCommand`.
  - `Ctrl+B` / `Ctrl+R` / `Ctrl+G` → panel toggle commands.

2. **Shortcuts are mirrored in menus via `InputGesture`**
- For discoverability, each key binding that is relevant to end users is reflected in the menu bar:
  - File menu items (`New`, `Open`, `Save`, `Save As`) specify `InputGesture` attributes.
  - Edit menu items (`Undo`, `Redo`) show `Ctrl+Z` / `Ctrl+Y`.
  - View menu panel toggles show `Ctrl+B`, `Ctrl+R`, `Ctrl+G`.
- This ensures users can learn shortcuts without reading documentation.

3. **Undo/redo keyboard behavior is always global**
- `Ctrl+Z` / `Ctrl+Y` are reserved for document-level undo/redo via `UndoCommand` / `RedoCommand`.
- For text fields that participate in the command-based undo pattern, `TextBox.IsUndoEnabled="False"` is set so they do not maintain private undo stacks.
- Where necessary (e.g., inside grid editors), key handlers forward `Ctrl+Z` / `Ctrl+Y` to the global commands instead of triggering control-local behavior.

4. **Feature-specific shortcuts must go through view-model commands**
- New shortcuts (e.g., for EQ-style editing, selection tools, or overlays) must be:
  - Bound to commands on view models (using CommunityToolkit.Mvvm `[RelayCommand]` where appropriate).
  - Declared in `MainWindow.KeyBindings`.
  - Reflected in `MenuItem.InputGesture` where applicable.
- Code-behind should not introduce its own global key processing logic that bypasses this mechanism.

5. **Platform considerations**
- The current target platform is Windows, so `Ctrl+` combinations are used by default.
- If a macOS port is introduced, equivalent `Cmd+` bindings will be added in a platform-conditional way, but the policy of window-level definition and menu mirroring remains the same.

## Consequences

### Positive

- **POS-001**: Users get consistent, predictable keyboard behavior across the app.
- **POS-002**: Discoverability is improved because shortcuts appear directly in menus.
- **POS-003**: Centralized key binding makes it easier to review and avoid conflicts when adding new shortcuts.
- **POS-004**: Ensures undo/redo is always routed through the shared `UndoStack` and `UndoCommand`/`RedoCommand`, aligning with ADR-0003.

### Negative

- **NEG-001**: Slightly more boilerplate when adding shortcuts (command + key binding + menu `InputGesture`).
- **NEG-002**: Requires discipline to avoid adding ad-hoc key handlers that bypass `MainWindow.KeyBindings`.

## Alternatives Considered

### ALT-001: Per-control shortcut handlers

- **ALT-001**: **Description**: Define keyboard shortcuts directly on controls (e.g., individual views or text boxes) using local key bindings.
- **ALT-002**: **Rejection Reason**: Leads to inconsistent behavior and makes it difficult to track the full shortcut set or to ensure they integrate with undo/redo correctly.

### ALT-003: Implicit shortcuts only (no menu reflection)

- **ALT-003**: **Description**: Keep key bindings but do not show them in menus.
- **ALT-004**: **Rejection Reason**: Hurts usability and discoverability; users must rely on documentation or trial and error.

## Implementation Notes

- **IMP-001**: When adding a new shortcut, first define a view-model command, then add a `<KeyBinding>` in `MainWindow.axaml`, and finally add or update a corresponding `MenuItem` with `InputGesture`.
- **IMP-002**: For text boxes and grid editors that participate in undo/redo, set `IsUndoEnabled="False"` and ensure their key handlers forward `Ctrl+Z` / `Ctrl+Y` to the global commands.
- **IMP-003**: Periodically review `MainWindow.KeyBindings` to ensure no conflicts and that all user-facing shortcuts are mirrored in menus.

## References

- **REF-001**: `src/MotorEditor.Avalonia/Views/MainWindow.axaml` – key bindings and menu definitions.
- **REF-002**: `src/MotorEditor.Avalonia/ViewModels/MainWindowViewModel.cs` – undo/redo and other commands.
- **REF-003**: ADR-0003 – generalized undo/redo command pattern.
