# ADR-0038 — Domain registry, orchestration domains, and MusicalSequence SSoT

- Status: Proposed
- Date: 2025-11-28
- Issue: #414

## Context

Historically the repo had multiple, partly overlapping notions of "domains" and orchestration:

- `DOMAIN_REGISTRY.json` listed only a small set of capability/process domains (e.g. `orchestration-core`, `telemetry-pipeline`, `self-healing`, `slo-dashboard`).
- `orchestration-domains.json` acted as the orchestration registry for ~59 domains (plugin + orchestration sequences) and implicitly defined the "MusicalSequence" contract.
- Context tree artifacts (e.g. `.generated/CONTEXT_TREE_INDEX.json`) treated `orchestration-domains.json` as the single source of truth for orchestration domains.
- The Architecture Governance Enforcement Symphony validated JSON shape, but there was no explicit shared JSON Schema for MusicalSequence and no explicit linkage from `DOMAIN_REGISTRY.json` or the context tree to that schema.

Issue #414 defines the target state:

- `DOMAIN_REGISTRY.json` is the single global domain universe.
- `orchestration-domains.json` is a governed projection for orchestration/MusicalSequence domains.
- Context tree artifacts must reinforce the registry (not define their own domain universe).
- There is a single canonical MusicalSequence JSON Schema, referenced consistently from registry, orchestration registries/sequences, governance symphonies, and context tree.
- Governance validation should fail when these invariants are broken.

## Decision

1. **Canonical MusicalSequence JSON Schema**
   - Introduce `docs/schemas/musical-sequence.schema.json` as the canonical JSON Schema for executable MusicalSequences (sequences with movements and beats).
   - The schema is intentionally permissive (`additionalProperties: true`) but enforces the core contract:
     - Top-level fields like `id`, `name`, `description`, `key`, `tempo`, `timeSignature`, `category`, `movements`, `metadata`.
     - `movements[]` objects with required `name` and `beats`.
     - `beats[]` objects with required `event` and basic numeric/structural constraints.

2. **Registry ↔ orchestration registry linkage (spike domains)**
   - Extend `DOMAIN_REGISTRY.json` with an `orchestration` block for orchestration-related domains, starting with a spike set:
     - `orchestration-core` — the platform orchestration backbone.
     - `renderx-web-orchestration` — the root orchestration domain for the production renderx-web codebase.
   - The `orchestration` block shape is:
     - `schema_ref`: `docs/schemas/musical-sequence.schema.json`.
     - `interface.name`: `"MusicalSequence"`.
     - `interface.source`: `packages/musical-conductor/modules/communication/sequences/SequenceTypes.ts`.
     - `registry_ref.file`: `"orchestration-domains.json"`.
     - `registry_ref.id`: `"orchestration-domains-registry"`.
     - For sequence-style domains (e.g. `renderx-web-orchestration`), `sequence_files` lists one or more JSON sequences.
   - New Vitest coverage (`tests/domain-registry-orchestration-spike.spec.ts`) asserts this linkage for the spike domains and ensures the registry projection and sequence_files are consistent with `orchestration-domains.json`.

3. **Renderx-web as meta-orchestration, not forced into beat-level schema**
   - `packages/orchestration/json-sequences/renderx-web-orchestration.json` is treated as a meta-orchestration:
     - It coordinates pipeline-level symphonies via `movements[*].orchestration` rather than defining its own `beats` arrays.
   - To avoid breaking the production root orchestration, we **do not** force this meta sequence itself through the beat-level MusicalSequence schema.
   - Instead, a new test (`tests/renderx-web-orchestration-conflation.spec.ts`) performs conflation as follows:
     - Parse `renderx-web-orchestration.json` and collect all referenced orchestration IDs from `movements[*].orchestration`.
     - For each referenced ID:
       - If a domain exists in `orchestration-domains.json` with a concrete `sequenceFile`, load that JSON and validate it against `docs/schemas/musical-sequence.schema.json` using Ajv.
       - Otherwise, require a corresponding symphony template file under `.generated/symphony-templates/{id}-template.json` and assert a minimal proto-MusicalSequence shape (id + movements[] + beats[]).
   - This design:
     - **Considers all MusicalSequence schemas and artifacts for conflation**.
     - Applies strict MusicalSequence validation only to realized sequences.
     - Keeps the renderx-web meta-orchestration JSON itself unchanged and unbroken.

4. **Context tree alignment with the domain registry and MusicalSequence schema**
   - Update `.generated/CONTEXT_TREE_INDEX.json` to explicitly acknowledge the domain registry as SSoT for domains and to propagate the MusicalSequence schema reference:
     - Add `sourceArtifacts.domainRegistrySSoT` pointing at `DOMAIN_REGISTRY.json` with the role `single-source-of-truth-for-domains` and links to:
       - The orchestration projection: `orchestration-domains.json`.
       - The shared MusicalSequence schema: `docs/schemas/musical-sequence.schema.json`.
     - Add `schemaRef: "docs/schemas/musical-sequence.schema.json"` to the existing `sourceArtifacts.sourceOfTruth` entry for `orchestration-domains.json` so that context tree descriptions of orchestration artifacts clearly reference the canonical schema.

5. **Governance symphony reference to the canonical schema**
   - Update `packages/orchestration/json-sequences/architecture-governance-enforcement-symphony.json` movement 1, beat 1 (`validateJSONSchemaStructure`) to:
     - Describe validation in terms of the **canonical MusicalSequence schema** where applicable.
     - Reference `docs/schemas/musical-sequence.schema.json` alongside `orchestration-domains.json` and `packages/orchestration/json-sequences/*.json`.
   - This ties the governance orchestration spec itself to the canonical schema while leaving detailed Ajv enforcement to dedicated tests and/or future handler enhancements.

6. **TDD and invariants via tests (initial slice)**
   - Introduce and gate the behavior via Vitest tests instead of immediately tightening all governance scripts:
     - `tests/musical-sequence-schema.spec.ts` — guards the structure and intent of `docs/schemas/musical-sequence.schema.json` against regressions and ensures it remains aligned with real sequence JSON.
     - `tests/domain-registry-orchestration-spike.spec.ts` — enforces the presence and shape of `orchestration` blocks for spike domains in `DOMAIN_REGISTRY.json` and their linkage into `orchestration-domains.json`.
     - `tests/renderx-web-orchestration-conflation.spec.ts` — enforces conflation behavior between renderx-web meta-orchestration, the orchestration registry, and concrete/template MusicalSequences without breaking the production orchestration.
   - These tests serve as the first enforcement layer for the invariants described in issue #414, with room to expand coverage to all orchestration domains in future work.

## Consequences

- **Single MusicalSequence SSoT**
  - The MusicalSequence contract is now explicitly captured in a JSON Schema file, referenced from:
    - Orchestration-related entries in `DOMAIN_REGISTRY.json`.
    - Context tree source artifacts.
    - The Architecture Governance Enforcement Symphony.
    - Dedicated Vitest suites which use Ajv for validation.

- **Registry, orchestration registry, and context tree are connected**
  - `DOMAIN_REGISTRY.json` now carries an `orchestration` block for key orchestration domains, giving consumers a discoverable path from a domain to:
    - Its orchestration registry projection (`orchestration-domains.json`).
    - Its MusicalSequence definition(s).
    - The canonical MusicalSequence schema.
  - Context tree artifacts no longer treat `orchestration-domains.json` as an isolated SSoT; they acknowledge the domain registry and the shared schema.

- **Renderx-web production orchestration is preserved**
  - `renderx-web-orchestration.json` remains a meta-orchestration that orchestrates other symphonies.
  - New conflation tests validate the things it orchestrates (where realized) without forcing the meta-layer itself into a beat-level schema that would currently fail and risk breaking the production root orchestration.

- **Incremental tightening path**
  - The invariants in #414 are enforced for a spike subset of domains and sequences first, via tests, without requiring immediate population of `DOMAIN_REGISTRY.json` with all ~60 orchestration domains.
  - As more orchestration domains are registered in `DOMAIN_REGISTRY.json` and realized as JSON sequences, the same patterns and tests can be extended to cover them.

- **Fractal orchestration domains as systems of systems**
  - When a registry entry gains an `orchestration` block and a corresponding MusicalSequence definition, the domain is promoted from a static concept to a governed system with movements, beats, and handlers.
  - That system in turn is projected back into `DOMAIN_REGISTRY.json` and `orchestration-domains.json` as a domain that can participate inside higher-order orchestrations, enabling the recursive "domain → system → domain" pattern across scales.
  - The example sequence `packages/orchestration/json-sequences/fractal-orchestration-domain-symphony.json` captures this pattern explicitly as a didactic MusicalSequence for architecture discussions and governance experiments.

## Implementation Notes

- Canonical MusicalSequence schema: `docs/schemas/musical-sequence.schema.json`.
- Spike orchestration domains in `DOMAIN_REGISTRY.json`:
  - `orchestration-core` (platform orchestration backbone).
  - `renderx-web-orchestration` (production meta-orchestration root).
- Orchestration registry projection: `orchestration-domains.json`.
- Context tree SSoT linkage: `.generated/CONTEXT_TREE_INDEX.json` (`sourceArtifacts.domainRegistrySSoT` and `sourceArtifacts.sourceOfTruth.schemaRef`).
- Governance symphony reference: movement 1, beat 1 of `architecture-governance-enforcement-symphony.json`.

## Testing

- New and updated Vitest suites:
  - `tests/musical-sequence-schema.spec.ts`
  - `tests/domain-registry-orchestration-spike.spec.ts`
  - `tests/renderx-web-orchestration-conflation.spec.ts`
- All three suites are run as part of the local TDD workflow and must pass before changes related to #414 are considered complete.

## Links

- Issue: https://github.com/BPMSoftwareSolutions/renderx-plugins-demo/issues/414
- Related domain registry docs: `DOMAIN_REGISTRY_REPRESENTATION.md`, `DOMAIN_REGISTRY_QUERY_TOOLS.md`
- Context tree index: `.generated/CONTEXT_TREE_INDEX.json`
- Governance symphony: `packages/orchestration/json-sequences/architecture-governance-enforcement-symphony.json`

