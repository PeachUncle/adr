---
title: "ADR-0010: Variable Point Curve Support (View-First)"
status: "Accepted"
date: "2025-12-25"
authors: "mjordan"
tags: ["architecture", "data-model", "file-format", "validation", "ux"]
supersedes: ""
superseded_by: ""
---

## Status

Accepted

## Context

The motor file format supports a variable number of curve points per voltage (0..101 points), where the X-axis (percent + rpm) is stored once per voltage and each series stores a torque array aligned to those axes.

Historically, the editor UI assumed 101 points (0..100% in 1% increments) and treated any other point count as an error. This prevented opening and viewing valid motor JSON files that used coarser sampling (for example, 21 points at 5% increments).

Relevant existing ADRs:

- ADR-0006: Motor file schema and versioning.
- ADR-0007: Status bar, validation, and user feedback conventions.
- ADR-0008: Selection and editing coordination between chart and grid.
- ADR-0009: Logging and error handling policy.

## Decision

We distinguish between:

1. **File validity (schema/shape)**
- Variable point counts (0..101) are valid.
- Axes and series must remain internally consistent:
  - `percent` length matches `rpm` length.
  - Each series torque array length matches axis length.
  - `percent` is strictly increasing and non-negative.
  - `rpm` is non-decreasing and non-negative.

2. **Editor authoring convenience (UI defaults)**
- The editor may continue to generate and edit standard 101-point curves for the primary authoring workflow.
- Point count of 101 is treated as an authoring default, not a load-time requirement.

As a result:

- Opening/viewing a motor file must not fail solely due to point count != 101.
- The directory browser “is this a motor definition?” probe must not require 101-length axes.

## Consequences

### Positive

- Users can open and inspect valid motor JSON files that contain coarser or otherwise variable sampling.
- The library remains consistent with the schema intent (0..101 points) and does not bake UI assumptions into file recognition.

### Negative

- Some editor workflows still implicitly assume aligned axes across series and may be optimized for the 101-point authoring case.
- Advanced authoring for arbitrary point counts (insert/delete points, resampling, or editing percent/rpm axes) is not guaranteed by this decision and may require additional UI work.

## Alternatives Considered

### ALT-001: Keep 101 points as a hard requirement

- **Description**: Reject files with non-101 point curves.
- **Rejection reason**: Conflicts with the file format’s documented allowance for variable point counts and blocks real-world files.

### ALT-002: Auto-resample all curves to 101 points on load

- **Description**: Load any file, but resample to 101 points for internal UI usage.
- **Rejection reason**: Mutates user data implicitly and can introduce numerical artifacts. Resampling should be explicit (user choice) if added later.

## Implementation Notes

- **IMP-001**: Editor validation must not treat point count != 101 as an error.
  - Updated in `src/MotorEditor.Avalonia/Services/ValidationService.cs`.
- **IMP-002**: File probe must accept variable axis lengths.
  - Updated in `src/MotorDefinition/MotorDefinitions/Probing/MotorFileProbe.cs`.
- **IMP-003**: Keep shape validation strict where it protects integrity (axis alignment, ordering, max point count).
  - Guarded by `src/MotorDefinition/MotorDefinitions/Validation/MotorFileShapeValidator.cs`.
- **IMP-004**: Add regression coverage with a representative real file.
  - Added `tests/CurveEditor.Tests/Services/MotorFileVariablePointsLoadTests.cs`.
- **IMP-005**: Maintain an example file that includes a non-101 curve for manual QA.
  - Updated `schema/example-motor.json` to include a 21-point series.

## References

- ADR-0006: Motor File Schema and Versioning Strategy (`docs/adr/adr-0006-motor-file-schema-and-versioning.md`).
- ADR-0007: Status Bar, Validation, and User Feedback Conventions (`docs/adr/adr-0007-status-bar-and-validation-feedback.md`).
- ADR-0008: Selection and Editing Coordination (`docs/adr/adr-0008-selection-and-editing-coordination.md`).
- ADR-0009: Logging and Error Handling Policy (`docs/adr/adr-0009-logging-and-error-handling-policy.md`).
