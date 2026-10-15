---
title: "ADR-0006: Motor File Schema and Versioning Strategy"
status: "Accepted"
date: "2025-12-10"
authors: "mjordan"
tags: ["architecture", "persistence", "json", "schema", "versioning"]
supersedes: "ADR-0001"
superseded_by: ""
---

## Status

Accepted

## Context

Motor definitions are persisted as JSON files that reflect the `ServoMotor` object graph:

- Motor-level identity and base nameplate data.
- Units metadata (`UnitSettings`).
- One or more `Drive` entries.
- Per-drive `Voltage` entries.
- Per-voltage `Curve` collections with `DataPoint` arrays.

ADR-0001 documented the initial v1 JSON format and introduced a JSON Schema (`motor-schema-v1.0.0.json`) plus a schema index (`schema/index.json`). Since then:

- The runtime model evolved (e.g., explicit `ServoMotor.CurrentSchemaVersion`).
- The README and roadmap now treat `schemaVersion: "2.0"` as the canonical version.

We need a clear, long-term strategy for schema versioning so that:

- Future changes to the on-disk shape are intentional and traceable.
- The application can safely load both old and new files where appropriate.
- Tools (editors, CI, generators) can discover applicable schemas.

## Decision

We adopt a **semver-style, schema-indexed versioning strategy** for motor JSON files:

1. **Explicit `schemaVersion` field with semantic versioning**
- Every motor file includes a top-level `schemaVersion` string.
- The current canonical version is `"2.0"` (matching `ServoMotor.CurrentSchemaVersion`).
- Future incompatible changes (e.g., structural rearrangements, field renames) require bumping the major version (e.g., `3.0`).

2. **Schema index as the discovery mechanism**
- `schema/index.json` remains the central discovery document for schemas.
- For each supported major version, there is an entry containing:
  - A `file` property pointing to a concrete JSON Schema file (e.g., `motor-schema-v2.0.0.json`).
  - Metadata such as description and migration notes.
- `currentVersion` in the index points to the major version the application writes by default (currently `2`).

3. **Runtime ties schema version to model constant**
- `ServoMotor.CurrentSchemaVersion` defines the schema version string the app writes when saving files.
- Deserialization reads `schemaVersion` and can:
  - Accept known compatible versions (e.g., `"2.0"`, `"2.0.1"`).
  - Reject or migrate older versions (e.g., v1) explicitly.

4. **Compatibility and migration policy**
- Minor/patch changes to the schema (e.g., adding optional fields with defaults) may share the same major version and are generally backward compatible.
- Breaking changes that:
  - Remove fields;
  - Change meanings or types;
  - Reorganize major portions of the document structure;
  require a new major version and a new entry in `schema/index.json`.
- Migration between major versions is handled either by:
  - In-app migration code that upgrades older files on open; or
  - Standalone migration tools using the schema index for guidance.

5. **ADR-0001 as historical reference for v1**
- ADR-0001 remains as the authoritative description of the v1 JSON format but is marked Superseded by this ADR.
- ADR-0006 describes the strategy going forward and acknowledges `schemaVersion: "2.0"` as the current canonical value.

## Consequences

### Positive

- **POS-001**: Provides a clear, documented contract for how motor files evolve over time.
- **POS-002**: Aligns runtime constants, JSON Schema files, and README documentation around the same versioning story.
- **POS-003**: Makes it easier to build tools (validators, generators) that rely on `schema/index.json` for schema discovery.
- **POS-004**: Reduces risk when changing the on-disk shape by requiring explicit version bumps and ADR updates.

### Negative

- **NEG-001**: Introduces overhead when changing the data model: schemas, index, and ADRs must all be kept in sync.
- **NEG-002**: Requires careful thought about backward compatibility; ad-hoc changes to JSON field names/types are no longer acceptable.

## Alternatives Considered

### ALT-001: Implicit versioning based on model shape

- **ALT-001**: **Description**: Infer the effective format version from the presence/absence of certain fields at load time.
- **ALT-002**: **Rejection Reason**: Increases deserializer complexity and makes it difficult for tooling to know which schema applies; explicit `schemaVersion` is simpler and more transparent.

### ALT-003: Single evolving schema without versioning

- **ALT-003**: **Description**: Maintain a single schema file that evolves as the model changes, without a `schemaVersion` field in the JSON.
- **ALT-004**: **Rejection Reason**: Makes it impossible to reason about which version a given file conforms to and complicates compatibility guarantees.

## Implementation Notes

- **IMP-001**: When changing `ServoMotor` in ways that affect the JSON shape, update `ServoMotor.CurrentSchemaVersion` and add or update a JSON Schema file under `schema/`.
- **IMP-002**: Keep `schema/index.json` in sync with available schema files and update `currentVersion` when the app begins writing a new major version by default.
- **IMP-003**: When introducing breaking changes, define clear migration steps (in code or tools) and document them alongside the new schema entry.

## References

- **REF-001**: ADR-0001 – Motor JSON File Format (v1).
- **REF-002**: `src/MotorDefinition/Models/ServoMotor.cs` – `CurrentSchemaVersion` constant and JSON attributes.
- **REF-003**: `schema/index.json` – schema index.
- **REF-004**: JSON Schema files under `schema/` (e.g., `motor-schema-v2.0.0.json`).
