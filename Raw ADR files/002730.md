---
title: "ADR-0004: Layout and Panel Persistence Strategy"
status: "Accepted"
date: "2025-12-10"
authors: "mjordan"
tags: ["architecture", "ui", "persistence"]
supersedes: ""
superseded_by: ""
---

## Status

Accepted

## Context

The main window of the Curve Editor hosts several resizable, collapsible panels:

- Directory browser panel on the left.
- Chart and curve data panel in the center.
- Motor/drive/voltage properties panel on the right.

Users expect the application to remember:

- Window bounds and position.
- Panel widths/heights when expanded.
- Whether each panel was expanded or collapsed.

Phase 2 introduced `WindowBoundsPersistence` and `PanelLayoutPersistence` helpers that store this information in JSON under `%APPDATA%/CurveEditor`. However, without a documented strategy, future changes could easily diverge (e.g., duplicating persistence logic in view models, persisting zero-width/zero-height values, or using inconsistent keys).

## Decision

We standardize layout persistence around a **view-driven, JSON-backed strategy** with the following rules:

1. **Persistence is managed at the view (window) level**
- `MainWindow` is responsible for attaching persistence helpers to grids and panels.
- View models remain platform-agnostic and do not know about window bounds or panel sizes.
- This keeps layout logic close to XAML and avoids polluting view models with UI-specific concerns.

2. **Named keys per window and panel**
- Each persisted dimension or boolean uses a stable string key of the form:
  - `"<WindowName>.<PanelName>"`, e.g. `"MainWindow.BrowserPanel"`, `"MainWindow.PropertiesPanel"`, `"MainWindow.CurveDataPanel"`.
- Column and row sizes and the corresponding expanded/collapsed booleans share the same logical key prefix.
- New windows or panels must follow this convention when attaching persistence.

3. **Attach helpers to concrete grid rows/columns**
- `PanelLayoutPersistence.AttachColumn(window, grid, columnIndex, key)` is used for left/right panels.
- `PanelLayoutPersistence.AttachRow(window, grid, rowIndex, key, isExpandedFunc)` is used for the curve data panel row.
- These helpers read/write JSON files in the app data folder, restoring sizes the next time the window opens.

4. **Do not persist zero-size as the last expanded size**
- When a panel is collapsed, the code:
  - Captures the current `ActualWidth`/`ActualHeight` **only if positive**.
  - Writes that value back to persistence as the "expanded" size.
  - Then sets the grid column/row to `0` (for side panels) or `Auto` (for the curve data header row).
- On expand, if the remembered size is zero or missing, a sensible default is used (e.g., 200px for the browser, 280px for properties, 200px for curve data height).

5. **Curve data panel uses an "Auto when collapsed" pattern**
- The curve data panel lives in a dedicated row beneath the chart in `CenterGrid`.
- When collapsed:
  - The row height is set to `Auto`, so only the header toggle remains visible.
  - The last positive height is remembered for future expansion.
- When expanded:
  - The row height is set to the remembered height in pixels.

6. **Boolean expanded/collapsed state is persisted separately**
- For each panel, `PanelLayoutPersistence.AttachBoolean` is used to persist `IsBrowserPanelExpanded`, `IsPropertiesPanelExpanded`, and `IsCurveDataExpanded`.
- On window open, these values determine whether the corresponding columns/rows should be restored to their expanded sizes or collapsed.

## Consequences

### Positive

- **POS-001**: Provides a clear, reusable pattern for panel persistence that future panels and windows can follow.
- **POS-002**: Keeps layout and persistence concerns in the view layer, preserving MVVM boundaries.
- **POS-003**: Avoids the common UX pitfall of "stuck" panels that restore to zero size after being collapsed.
- **POS-004**: Makes it trivial to add new persisted panels by attaching helpers and choosing a key.

### Negative

- **NEG-001**: The persistence layer is string-keyed; renaming windows or panels without updating keys can orphan old data and lose layout state.
- **NEG-002**: Column/row indices are hard-coded in `MainWindow.axaml.cs`; structural grid changes must be kept in sync with the persistence attachment code.

## Alternatives Considered

### ALT-001: View-model driven persistence

- **ALT-001**: **Description**: Store panel sizes and states directly on the main view model and persist them as part of user settings.
- **ALT-002**: **Rejection Reason**: Couples view models to Avalonia-specific layout details and adds complexity for tests and non-UI consumers.

### ALT-003: Do not persist panel sizes

- **ALT-003**: **Description**: Always start panels at fixed widths/heights on launch and only remember expanded/collapsed booleans.
- **ALT-004**: **Rejection Reason**: Degrades user experience for power users who carefully size panels for their workflow.

## Implementation Notes

- **IMP-001**: When adding a new resizable/collapsible panel, choose a unique key (e.g., `"MainWindow.NewPanel"`), then call the appropriate `AttachColumn`/`AttachRow` and `AttachBoolean` helpers from the window's `OnOpened` handler.
- **IMP-002**: Always capture current `ActualWidth`/`ActualHeight` **before** setting a panel's grid size to 0 or `Auto`, and only persist positive values.
- **IMP-003**: In property-changed handlers for `Is*PanelExpanded`, call helper methods like `ApplyBrowserPanelLayout`/`ApplyPropertiesPanelLayout`/`ApplyCurveDataPanelLayout` that encapsulate the expand/collapse behavior and persistence updates.
- **IMP-004**: Keep defaults (e.g., 200–280px) in a single place to make future tuning easier.

## References

- **REF-001**: `src/MotorEditor.Avalonia/Views/MainWindow.axaml` – layout grid definitions for browser, chart, curve data, and properties panels.
- **REF-002**: `src/MotorEditor.Avalonia/Views/MainWindow.axaml.cs` – `OnOpened` and `Apply*PanelLayout` methods.
- **REF-003**: Panel persistence helpers in `CurveEditor.Behaviors` (`WindowBoundsPersistence`, `PanelLayoutPersistence`).
