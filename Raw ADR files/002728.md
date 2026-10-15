title: "ADR-0001: Motor JSON File Format (v1)"
status: "Superseded"
date: "2025-12-09"
authors: "jordanrobot (Curve Editor maintainer)"
tags: ["architecture", "persistence", "json", "schema"]
supersedes: ""
superseded_by: "ADR-0006"
---

## Status

Superseded by ADR-0006 (Motor File Schema & Versioning Strategy).

## Context

The Curve Editor application persists motor configuration data to disk as JSON files. These files capture the full state required to reopen and edit a motor definition, including:

- Motor identity and base nameplate data (power, speeds, torques, mechanics).
- Unit system metadata (torque, speed, power, weight units).
- One or more drive configurations, each with one or more voltage configurations.
- For each voltage configuration, one or more torque/speed curve series consisting of ordered data points.
- File-level metadata such as creation/modification timestamps and notes.

By Phase 2, several different parts of the application depended on an implicit JSON shape derived from the `ServoMotor` object graph. We also introduced a JSON Schema file (`schema/motor-schema-v1.0.0.json`) and a schema index (`schema/index.json`) to support tooling (editor validation, CI checks, documentation), but the overall format and versioning rules were not captured in a single place.

We need an authoritative description of:

- The JSON structure used to save motor files.
- The versioning scheme for that format.
- How the JSON Schema and index relate to the runtime model (`ServoMotor`).

This ADR documents the current format and establishes it as the baseline for future evolution.

## Decision

We standardize on a **versioned JSON format** for motor definition files with the following characteristics:

1. **Top-level document structure**
   - The root JSON value is an object with these required properties:
     - `schemaVersion` (string): semantic version string for the persisted format, currently `"1.0.0"`.
     - `motorName` (string): human-readable motor name.
     - `manufacturer` (string): motor manufacturer name.
     - `partNumber` (string): manufacturer part number.
     - `power` (number ≥ 0): theoretical maximum motor power (in `units.power`).
     - `maxSpeed` (number ≥ 0): theoretical maximum speed in RPM.
     - `ratedSpeed` (number ≥ 0): rated continuous operating speed in RPM.
     - `ratedContinuousTorque` (number ≥ 0): rated continuous torque.
     - `ratedPeakTorque` (number ≥ 0): rated peak/short-term torque.
     - `weight` (number ≥ 0): motor mass.
     - `rotorInertia` (number ≥ 0): rotor inertia.
     - `feedbackPpr` (integer ≥ 0): feedback device pulses per revolution.
     - `hasBrake` (boolean): whether an integral brake is present.
     - `brakeTorque` (number ≥ 0): brake holding torque.
     - `brakeAmperage` (number ≥ 0): brake coil current.
     - `brakeVoltage` (number ≥ 0): brake voltage.
     - `units` (object): unit system for this file.
     - `drives` (array): drive configurations.
     - `metadata` (object): file metadata.

2. **Units object**
   - `units` is an object with no additional properties, containing these required string properties:
     - `torque`: unit label for torque (e.g., `"Nm"`).
     - `speed`: unit label for speed (e.g., `"rpm"`).
     - `power`: unit label for power (e.g., `"W"`).
     - `weight`: unit label for mass (e.g., `"kg"`).

3. **Drives and voltages**
   - `drives` is an array of objects, each representing a logical drive configuration connected to the motor. Each drive object has:
     - `name` (string, required): drive name.
     - `partNumber` (string, optional): drive part number.
     - `manufacturer` (string, optional): drive manufacturer name.
     - `voltages` (array, required): one or more voltage configurations.
   - Each voltage configuration object has these required properties:
     - `voltage` (number ≥ 0): nominal bus voltage.
     - `power` (number ≥ 0): maximum power at this voltage.
     - `maxSpeed` (number ≥ 0): maximum speed at this voltage.
     - `ratedSpeed` (number ≥ 0): rated continuous speed.
     - `ratedContinuousTorque` (number ≥ 0): rated continuous torque at this voltage.
     - `ratedPeakTorque` (number ≥ 0): rated peak torque at this voltage.
     - `continuousAmperage` (number ≥ 0): continuous current.
     - `peakAmperage` (number ≥ 0): peak current.
     - `series` (array, required): torque/speed curve series for this voltage.

4. **Curve series and data points**
  - `series` is an array of objects; each object maps to a `Curve` in the runtime model. Each series object has:
     - `name` (string, required): series name (e.g., `"Peak"`, `"Continuous"`).
     - `notes` (string, optional): free-form notes.
     - `locked` (boolean, required): whether the series is locked for editing in the UI.
     - `data` (array, required): ordered data points composing the torque/speed curve.
   - Each `data` entry is an object with:
     - `percent` (number, 0–100, required): percentage of base speed.
     - `rpm` (number ≥ 0, required): speed at this point.
     - `torque` (number ≥ 0, required): torque at this point.
   - Additional properties on `series` and `data` objects are disallowed in the schema to keep the format tight and predictable.

5. **Metadata**
   - `metadata` is an object with no additional properties and the following optional fields:
     - `created` (string, ISO 8601 `date-time`): creation timestamp.
     - `modified` (string, ISO 8601 `date-time`): last modification timestamp.
     - `notes` (string): free-form notes for the file.

6. **Versioning rules**
  - The application exposes a constant `ServoMotor.CurrentSchemaVersion`, currently set to `"1.0.0"`, and persists this value as the `schemaVersion` field in every saved motor file.
   - The JSON Schema for this version (`schema/motor-schema-v1.0.0.json`) enforces that `schemaVersion` matches the regex `^1\.0\.0$`.
   - The schema index (`schema/index.json`):
     - Contains `currentVersion` (integer) indicating the active format generation (currently `1`).
     - Has a `schemas` object with a property `"1"` describing the v1 schema, including a `file` property that points to a schema file name matching `^motor-schema-v[0-9]+\.[0-9]+\.[0-9]+\.json$`.
   - Future changes to the on-disk shape that are not backward-compatible will:
     - Bump `ServoMotor.CurrentSchemaVersion` (e.g., to `"2.0.0"`).
     - Introduce a new JSON Schema file and corresponding entry in `schema/index.json`.

7. **Source of truth**
  - The runtime object graph for a motor is represented by `ServoMotor` and its related model types (`Drive`, `Voltage`, `Curve`, `DataPoint`, `UnitSettings`, `MotorMetadata`).
   - JSON serialization uses `System.Text.Json` with:
     - `JsonPropertyName` attributes to bind JSON fields to CLR properties.
     - A case-insensitive option for property names, allowing minor JSON variations while still preferring the canonical names defined in this ADR.
  - The combination of this ADR, `ServoMotor` and related models, and `schema/motor-schema-v1.0.0.json` is the normative definition of the motor file format.

## Consequences

### Positive

- **POS-001**: Establishes a single, authoritative description of the motor JSON file format, reducing ambiguity for contributors and tooling.
- **POS-002**: The strict JSON Schema (`motor-schema-v1.0.0.json`) and schema index (`index.json`) enable editor integration, CI validation, and automated documentation.
- **POS-003**: Explicit `schemaVersion` and semver-style versioning create a clear path for evolving the format while maintaining backward compatibility strategies.
- **POS-004**: Aligning the JSON format with the `ServoMotor` object graph keeps serialization/deserialization straightforward and minimizes mapping logic.

### Negative

- **NEG-001**: The format is relatively strict (no additional properties in many objects), which can make ad-hoc extensions harder without a formal schema update.
- **NEG-002**: Changing the on-disk shape now requires coordinated updates to the model classes, JSON Schema, schema index, and this ADR.
- **NEG-003**: Rigid validation (e.g., enforcing `schemaVersion` via regex) can make migrations noisy if files are manually edited without understanding the versioning rules.

## Alternatives Considered

### Alternative A: Unversioned, schema-less JSON

- **ALT-001**: **Description**: Persist the `ServoMotor` graph as JSON without a `schemaVersion` field and without a maintained JSON Schema.
- **ALT-002**: **Rejection Reason**: Makes it difficult to evolve the format safely, hampers tooling support (validation, editor hints), and forces all compatibility logic into application code.

### Alternative B: Implicit versioning via model shape only

- **ALT-003**: **Description**: Infer the format version from the presence/absence of fields instead of an explicit `schemaVersion` string.
- **ALT-004**: **Rejection Reason**: Increases deserializer complexity and ambiguity; explicit versioning is simpler for humans and tools and easier to document.

### Alternative C: Non-JSON persistence (e.g., binary or XML)

- **ALT-005**: **Description**: Use a binary or XML format instead of JSON for on-disk storage.
- **ALT-006**: **Rejection Reason**: JSON offers better interoperability with existing tooling (editors, validators, diff tools) and is already used throughout the project; switching formats would add unnecessary complexity.

## Implementation Notes

- **IMP-001**: The canonical JSON Schema for the current format is stored at `schema/motor-schema-v1.0.0.json` and should be kept in sync with `ServoMotor` and this ADR when fields are added or removed.
- **IMP-002**: The schema index at `schema/index.json` is the entry point for tools that need to discover schema versions and associated files; when introducing a new format version, add a new entry and consider updating `currentVersion`.
- **IMP-003**: When loading files, future versions of the application should examine `schemaVersion` and, if necessary, apply migration steps or report incompatibilities explicitly.

## References

- **REF-001**: Runtime model: `src/MotorDefinition/Models/ServoMotor.cs` and related model types.
- **REF-002**: JSON Schema: `schema/motor-schema-v1.0.0.json`.
- **REF-003**: Schema index: `schema/index.json`.
- **REF-004**: Example motor file: `schema/example-motor.json`.
