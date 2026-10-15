## ADR 0003: Motor Property Undo Design

### Status

- Accepted

### Date

- 2025-12-07

---
title: "ADR-0003: Generalized Undo/Redo Command Pattern"
status: "Accepted"
date: "2025-12-10"
authors: "mjordan"
tags: ["architecture", "undo", "commands", "mvvm"]
supersedes: "ADR-000X, ADR-000Y"
superseded_by: ""
---

## Status

Accepted

## Context

The Curve Editor uses a command-based undo/redo infrastructure (`IUndoableCommand`, `UndoStack`) that now covers:

- Motor text and scalar properties via `EditMotorPropertyCommand` and view-model edit methods.
- Drive and voltage properties via `EditDrivePropertyCommand` and `EditVoltagePropertyCommand`.
- Curve data table edits and chart-driven point edits via `EditPointCommand`.
- Series metadata (name, visibility, lock state, color) via `EditSeriesCommand`.

These capabilities were originally specified across multiple ADRs:

- ADR-0003 (motor property undo design).
- ADR-000X (voltage property undo design).
- ADR-000Y (generalized undo/redo pattern).

Additionally, the roadmap (`.github/planning/04-mvp-roadmap.md`) and Phase 2 plan (`.github/planning/phase-2-plan.md`) describe requirements such as:

- A single per-document undo stack (`UndoStack`) with `CanUndo`/`CanRedo` and dirty-state integration.
- Global Ctrl+Z / Ctrl+Y behavior at the window level, not per-control.
- Whole-field, command-based undo steps for text fields (not per-character), consistent with chart/grid edits.

As more undoable scenarios are added (EQ-style editing, additional configuration panels, etc.), we need one **authoritative, generalized pattern** so future work follows the same rules without re-discovering subtle details scattered across several documents.

## Decision

We adopt a **single generalized undo/redo pattern** for all user-visible, undoable operations in the Curve Editor. Any new undoable operation must follow these rules:

1. **All domain mutations go through commands**
- The only code that mutates domain objects (`ServoMotor`, `Drive`, `Voltage`, `Curve`, `DataPoint`, etc.) is inside `IUndoableCommand.Execute()` and `Undo()` implementations.
- Views and view models never set these properties directly in response to UI events; instead they construct and push commands via the shared `UndoStack`.

2. **Exactly one edit method per logical user operation**
- Each logical user action that changes state has a single, named method on the relevant view model, e.g.:
  - `EditMotorName`, `EditMotorMaxSpeed`, `EditMotorBrakeTorque`.
  - `EditDriveName`, `EditSelectedVoltagePower`, `EditSelectedVoltageMaxSpeed`.
  - `TryEditTorqueCell`, `ApplyTorqueDeltaToSelection`, `ToggleSeriesLock`.
- That method is the **only** place that:
  - Reads the current value from the model into `oldValue`.
  - Parses/normalizes the user input into `newValue`.
  - Applies business rules and guards (e.g., series is not locked, selection is valid).
  - Constructs an `IUndoableCommand` with `oldValue` and `newValue` and calls `_undoStack.PushAndExecute(command)`.

3. **Editor buffers for text-based input**
- UI `TextBox` controls bind to simple editor properties (e.g., `MotorNameEditor`, `VoltagePowerEditor`, `VoltagePeakTorqueEditor`) instead of binding directly to domain-model properties.
- These editor properties live on the view model and are updated via data binding.
- On commit (typically `LostFocus`, Enter, or an explicit Apply button), view or code-behind calls the corresponding edit method, which:
  - Parses the editor buffer text into the target type.
  - Constructs and pushes an undoable command.
  - Refreshes editor properties from the canonical model state.

4. **Commands always capture old and new values explicitly**
- Command constructors receive `oldValue` and `newValue` (or equivalent) at creation time.
- `Execute()` sets the model property/collection to `newValue`.
- `Undo()` restores `oldValue` exactly, without needing to infer anything from current model state.
- Commands do **not** compute `oldValue` by inspecting the model during `Execute()` or `Undo()`.

5. **Per-document shared undo stack**
- `MainWindowViewModel` owns a single `UndoStack` per open motor/document.
- Sub-view-models (`ChartViewModel`, `CurveDataTableViewModel`, etc.) receive a reference to the same stack.
- All undoable operations that affect the current document push into this stack so undo/redo is linear and global for that document.

6. **Global undo/redo wiring at the window level**
- `MainWindow` defines the keyboard bindings for `Ctrl+Z` / `Ctrl+Y` and menu items bound to `UndoCommand` / `RedoCommand` on `MainWindowViewModel`.
- Per-control undo is disabled (`IsUndoEnabled="False"`) for text boxes that participate in the global command pattern so Ctrl+Z / Ctrl+Y always route to the document-level undo history.
- Grid cells and other complex input controls forward undo/redo keystrokes to the global commands rather than using private stacks.

7. **Guards and locking enforced before commands are created**
- Guards such as "no current motor", "no selected voltage", or "series is locked" are applied in the view-model edit methods **before** creating commands.
- If a guard fails, the edit method exits without constructing or pushing a command.
- This keeps command implementations simple and ensures invalid operations never appear in the undo history.

8. **Centralized dirty-state tracking and refresh**
- Any method that successfully pushes and executes a command must:
  - Mark the document dirty (e.g., `MarkDirty()`), so dirty state and title asterisk are correct.
  - Call shared refresh helpers, such as:
    - `RefreshMotorEditorsFromCurrentMotor()`;
    - `ChartViewModel.RefreshChart()`;
    - `CurveDataTableViewModel.RefreshData()`.
- Global `UndoCommand` / `RedoCommand` always:
  - Call `_undoStack.Undo()` / `_undoStack.Redo()`;
  - Then call the same refresh helpers.

## Consequences

### Positive

- **POS-001**: Provides a single, consistent pattern for all undoable operations, reducing the chance of ad-hoc mutations that bypass the undo stack.
- **POS-002**: Makes the codebase easier for future engineers and agents to extend: each new undoable feature follows the same small set of rules.
- **POS-003**: Simplifies reasoning and testing, since all domain changes originate from clearly named edit methods and well-scoped command objects.
- **POS-004**: Ensures global keyboard shortcuts behave uniformly across charts, tables, and property panels, improving UX predictability.
- **POS-005**: Integrates neatly with dirty-state tracking and layout of Phase 1.8/Phase 2 features as documented in the roadmap and phase plan.

### Negative

- **NEG-001**: Introduces more ceremony than direct bindings: new fields typically require an editor property, an edit method, and possibly a command type.
- **NEG-002**: Requires discipline; casual direct property sets in view models or code-behind can easily violate the pattern if not reviewed.
- **NEG-003**: Reflection-based command implementations (for generic scalar editing) rely on property-name strings, which are not refactor-safe without tests.

## Alternatives Considered

### ALT-001: Direct two-way bindings with ad-hoc undo

- **ALT-001**: **Description**: Bind `TextBox.Text` and other inputs directly to domain properties and rely on control-local undo stacks or manual snapshots.
- **ALT-002**: **Rejection Reason**: Early prototypes showed race conditions between bindings and commands, inconsistent Ctrl+Z behavior (sometimes per-control, sometimes global), and difficulty grouping logically related changes.

### ALT-003: Observing `INotifyPropertyChanged` as an audit log

- **ALT-003**: **Description**: Listen to model `PropertyChanged` events and retroactively create commands from observed changes.
- **ALT-004**: **Rejection Reason**: Inverts control and breaks the link between user-intent and command creation; makes it hard to apply guards, coalesce operations, or avoid double mutations.

### ALT-005: Immutable snapshots for entire `ServoMotor`

- **ALT-005**: **Description**: Treat each edit as replacing an entire `ServoMotor` snapshot and push whole-document diffs onto the undo stack.
- **ALT-006**: **Rejection Reason**: Overly heavy for the current app, complicates partial updates and selection coordination, and diverges from the existing mutable-model architecture.

## Implementation Notes

- **IMP-001**: When adding a new undoable operation, always start by identifying the owning domain type and property/collection, then design or reuse an appropriate command type that stores old/new values explicitly.
- **IMP-002**: Add a single edit method on the appropriate view model that performs validation, computes `oldValue`/`newValue`, constructs the command, pushes it via `_undoStack.PushAndExecute`, marks dirty, and triggers shared refresh helpers.
- **IMP-003**: For any text-based field, introduce an editor property (e.g., `NewPropertyEditor`) bound to the `TextBox`, and commit via `LostFocus` or an explicit user action that calls the edit method; set `IsUndoEnabled="False"` on such text boxes.
- **IMP-004**: Ensure `UndoCommand` and `RedoCommand` in `MainWindowViewModel` always call both the undo stack and shared refresh helpers so all views (chart, grid, property panels) stay in sync with the current undo state.
- **IMP-005**: When refactoring existing code, search for direct mutations of domain models in views or code-behind and route them through edit methods and commands instead.

## References

- **REF-001**: Undo/redo infrastructure and commands in `src/MotorEditor.Avalonia/Services/UndoStack.cs` and related command classes.
- **REF-002**: Motor, drive, voltage, and curve models in `src/MotorEditor.Avalonia/Models`.
- **REF-003**: View-model integration and editor buffers in `src/MotorEditor.Avalonia/ViewModels/MainWindowViewModel.cs` and related view models.
- **REF-004**: Roadmap and phase plan: `.github/planning/04-mvp-roadmap.md` (section 1.8) and `.github/planning/phase-2-plan.md`.
- **REF-005**: Superseded ADRs `adr-000X-voltage-property-undo-design.md` and `adr-000Y-undo-redo-general-pattern.md` (now consolidated into this document).
