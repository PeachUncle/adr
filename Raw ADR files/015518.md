# ADR-0014 — JSON-defined default sequences per plugin

- Status: Accepted
- Date: 2025-08-23
- Issue: #13

## Context
Default symphony sequences were defined as TypeScript objects inside plugin registrars and mounted during register(). This tightly coupled orchestration data with code, making it harder to override/extend and harder to validate outside TS.

## Decision
- Move all default sequences into JSON files, organized per plugin, alongside an index.json catalog for each plugin.
- Add a startup loader (src/conductor.ts → loadJsonSequenceCatalogs) that loads catalogs and mounts sequences using the existing TypeScript handlers referenced by name.
- Preserve beat kinds (pure/io/api/stage-crew) in JSON. Handlers remain implemented in TS and exported as a `handlers` map.
- Implement duplicate-mount protection: if a sequence id is already mounted, skip and log a warning via conductor.logger.
- Update plugin register() functions to no-op for sequence mounts; loader is the single source of truth.

## Consequences
- Sequences become data-driven and can be validated statically.
- Browsers load from public/json-sequences; tests/Node load from json-sequences.
- Handlers remain tree-shakeable and testable in TS modules.

## Implementation Notes
- Catalog schema: { version: string, sequences: [{ file, handlersPath }] }
- Sequence schema (partial): { pluginId, id, name, movements: [{ id, beats: [{ beat, event, handler, timing?, kind? }] }] }
- Loader resolves handlersPath with dynamic import; mounts via conductor.mount(seq, handlers, seq.pluginId).

## Alternatives Considered
- Keep mounting in register() (Option B): increases risk of duplicate mounts during migration; rejected for simplicity. Guarding remains in loader.

## Testing
- Unit tests target the loader to assert correct mounts per plugin.
- Smoke tests cover library load; drag→drop→create; select; drag; resize flows.

## Links
- Issue: https://github.com/BPMSoftwareSolutions/renderx-plugins-demo/issues/13

