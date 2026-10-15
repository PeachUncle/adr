---
title: "ADR-0008: Selection and Editing Coordination Between Chart and Grid"
status: "Accepted"
date: "2025-12-10"
authors: "mjordan"
tags: ["architecture", "selection", "chart", "grid"]
supersedes: ""
superseded_by: ""
---

## Status

Accepted

## Context

The Curve Editor presents curve data in two main views:

- A chart (via LiveCharts2) that supports hovering and, in future phases, point selection and dragging.
- A curve data table that shows the same data points in a tabular form.

Phase 4 introduces more advanced interactions (EQ-style editing, rubber-band selection, multi-point edits) that will involve both the chart and the table. Without a clear coordination strategy, we risk:

- Selection feedback loops between chart and table.
- Inconsistent selection semantics (replace vs. extend vs. toggle).
- Divergent implementations of edit operations originating from different views.

An `EditingCoordinator` concept already exists to help manage this, but its intended responsibilities and invariants need to be documented.

## Decision

We define `EditingCoordinator` as the **single source of truth for selection and coordinated edits** between the chart and curve data table:

1. **Centralized selection state**
- `EditingCoordinator` (or an equivalent service) owns the authoritative representation of:
  - The currently selected series.
  - The set of selected points (e.g., indices or keys into the data set).
- Both chart and table query and update selection through this coordinator rather than managing their own independent selection models.

2. **Selection origin tagging**
- Methods that change selection accept an origin parameter (e.g., `SelectionOrigin.Chart`, `SelectionOrigin.Table`).
- When the coordinator updates selection, it can:
  - Notify subscribers with both the new selection and the origin.
  - Allow views to avoid echoing changes back to the originator (preventing cycles).

3. **Consistent selection semantics**
- The coordinator defines and enforces how selection behaves for:
  - Replace (single-click): replace current selection with a single point or region.
  - Extend (Shift-click): extend the selection range.
  - Toggle (Ctrl-click): add or remove individual points.
- Both chart and table use the same semantics by delegating to the coordinator instead of reimplementing them.

4. **Editing operations treat selection as input, not state**
- Commands that modify curve data (e.g., EQ-style adjustments, bulk torque shifts) accept a snapshot of selection from the coordinator at the time of invocation.
- The commands themselves do not manage selection; they only operate on the selected points and rely on ADR-0003 for undo/redo.

## Consequences

### Positive

- **POS-001**: Reduces risk of selection feedback loops and inconsistent selection UX.
- **POS-002**: Provides a clear extension point for future selection-related features (e.g., selection presets, copy/paste of selections).
- **POS-003**: Keeps edit commands focused on data changes, not on selection management.

### Negative

- **NEG-001**: Introduces another coordination component that must be understood and tested.
- **NEG-002**: Requires careful design of the selection model (e.g., data structures, performance for large selections).

## Alternatives Considered

### ALT-001: Independent selection in chart and table

- **ALT-001**: **Description**: Let the chart and table each manage their own selection and sync loosely via events.
- **ALT-002**: **Rejection Reason**: Difficult to avoid cycles and keep semantics consistent; harder to reason about.

## Implementation Notes

- **IMP-001**: Implement `EditingCoordinator` as a view-model-level service (not as a view) so it can be tested without UI.
- **IMP-002**: Use clear method names such as `SetSelection`, `ToggleSelection`, and `ExtendSelection` that accept an origin and a set of points.
- **IMP-003**: Views subscribing to selection changes should check the origin to avoid re-triggering the same change.
- **IMP-004**: Editing commands should obtain a snapshot of selected points from the coordinator at the time they are created and then operate purely on that snapshot.

## References

- **REF-001**: `src/MotorEditor.Avalonia/ViewModels/EditingCoordinator.cs` (or equivalent) – selection coordination implementation.
- **REF-002**: ADR-0003 – generalized undo/redo command pattern.
- **REF-003**: Roadmap Phase 4 – advanced editing and selection coordination.
