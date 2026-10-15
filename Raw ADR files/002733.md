---
title: "ADR-0007: Status Bar, Validation, and User Feedback Conventions"
status: "Accepted"
date: "2025-12-10"
authors: "mjordan"
tags: ["architecture", "ux", "validation", "status-bar"]
supersedes: ""
superseded_by: ""
---

## Status

Accepted

## Context

The Curve Editor provides user feedback through several channels:

- A status bar at the bottom of `MainWindow` showing a `StatusMessage` and a validation summary.
- Inline validation indicators near controls.
- Occasional dialogs for exceptional conditions (e.g., delete confirmations, error dialogs).

As validation rules and operations grow (file loading, schema validation, motor/drive/voltage checks, curve data validation), we need consistent guidance for where and how to surface messages so that future contributors and agents do not introduce conflicting patterns.

## Decision

We define the following conventions for status bar usage, validation, and user feedback:

1. **Status bar is the primary non-blocking feedback channel**
- `MainWindow` hosts a status bar bound to:
  - `StatusMessage` – a short, human-readable summary of the most recent notable action (e.g., "Motor file loaded", "Validation passed", "Changes saved").
  - `HasValidationErrors` and `ValidationErrors` – aggregated validation state from the view model.
- The right-hand side of the status bar shows a warning icon and "Validation errors" label when `HasValidationErrors` is true, with a tooltip containing the aggregated error text.

2. **Validation is centralized in services and view models**
- Domain validation (e.g., RPM > 0, ascending RPM, non-negative torque) is handled by an `IValidationService` and invoked from the main view model.
- The results are summarized into:
  - A boolean `HasValidationErrors`.
  - A multi-line `ValidationErrors` string used by the status bar and, where appropriate, by inline indicators.

3. **Dialogs are reserved for blocking or destructive operations**
- Confirmation dialogs are used for operations like delete, closing with unsaved changes, or applying disruptive changes (e.g., large max-speed adjustments that reshape the chart).
- Error dialogs are used for unexpected failures (e.g., file I/O exceptions, schema mismatches) and should:
  - Present a friendly message.
  - Include enough detail for troubleshooting in logs, but not overwhelm the user.
- Transient or informational messages (e.g., "Saved", "Validation passed") should use the status bar instead of dialogs.

4. **Logging complements, but does not replace, user feedback**
- Serilog logs carry structured diagnostic information (see ADR-0009) for developers.
- User-facing feedback remains separate: status bar, inline validation, and dialogs.
- Code should not rely on logs alone to communicate issues that users need to act on.

## Consequences

### Positive

- **POS-001**: Provides a consistent mental model for users: the status bar is where they look for non-blocking feedback and validation issues.
- **POS-002**: Reduces UX fragmentation by discouraging ad-hoc dialogs for routine events.
- **POS-003**: Centralized validation state makes it easier to adjust or extend validation rules without changing multiple view components.

### Negative

- **NEG-001**: Requires discipline from contributors to respect the separation between logs, status bar messages, inline validation, and dialogs.
- **NEG-002**: The status bar has limited space; messages must be concise, and detailed explanations belong in tooltips or help content.

## Alternatives Considered

### ALT-001: Dialogs for all validation issues

- **ALT-001**: **Description**: Show a modal dialog whenever validation fails.
- **ALT-002**: **Rejection Reason**: Intrusive and fatiguing for users; not appropriate for continuous validation scenarios.

### ALT-003: Log-only validation

- **ALT-003**: **Description**: Log validation issues to Serilog but do not surface them in the UI.
- **ALT-004**: **Rejection Reason**: Users would have no immediate indication of problems and would need to inspect logs manually.

## Implementation Notes

- **IMP-001**: Keep `StatusMessage`, `HasValidationErrors`, and `ValidationErrors` on the main view model and ensure they are updated whenever validation is run or major operations occur (load/save, undo/redo, property edits).
- **IMP-002**: Use concise, action-focused messages for the status bar; use tooltips on status-bar elements or controls for more detailed explanations.
- **IMP-003**: When adding new validation rules, integrate them into the existing `IValidationService` or validation pipeline so they feed into the shared `HasValidationErrors` / `ValidationErrors` properties.

## References

- **REF-001**: `src/MotorEditor.Avalonia/Views/MainWindow.axaml` – status bar layout and bindings.
- **REF-002**: `src/MotorEditor.Avalonia/ViewModels/MainWindowViewModel.cs` – status and validation properties.
- **REF-003**: Validation service interfaces and implementations in `src/MotorEditor.Avalonia/Services`.
