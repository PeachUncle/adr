# ADR 0001: Blueprint Schema Design

## Status

Accepted

## Context

Dockitect needs an internal representation (Blueprint) for Docker stacks that can:

- Be validated at runtime with strong typing
- Convert bidirectionally to/from docker-compose.yml v2.x
- Support multi-host topologies (NAS, Pi, VMs, etc.)
- Provide comprehensive type safety in TypeScript
- Enable future extensions (Kubernetes, Podman) without breaking changes
- Support conflict detection (ports, volumes, names) before deployment

The schema must balance expressiveness (supporting real-world homelab patterns) with simplicity (avoiding premature complexity).

## Decision

Use **Zod** for runtime validation with a custom **Blueprint v0** format that represents the full topology: hosts, networks, and services.

### Blueprint v0 Schema

```typescript
type Blueprint = {
    version: "v0";
    meta: {
        id: string; // UUID
        name: string; // User-visible stack name
        createdAt: string; // ISO 8601 timestamp
        updatedAt: string; // ISO 8601 timestamp
    };
    hosts: Host[]; // Physical/virtual machines (e.g., "nas", "pi-4", "vm-01")
    networks: Net[]; // Docker networks (bridge, macvlan, custom)
    services: Service[]; // Containerized services
};

type Host = {
    id: string; // UUID
    name: string; // e.g., "nas", "pi-cluster-1"
    notes?: string; // Optional description
};

type Net = {
    id: string; // UUID
    name: string; // Network name (e.g., "frontend", "backend")
    driver?: string; // Docker network driver (default: bridge)
    subnetCidr?: string; // e.g., "172.20.0.0/16" (optional for custom IPAM)
};

type Port = {
    host: number; // Host port (e.g., 8080)
    container: number; // Container port (e.g., 80)
    protocol?: "tcp" | "udp"; // Default: tcp
};

type Volume = {
    type: "bind" | "volume"; // Bind mount or named volume
    source: string; // Host path or volume name
    target: string; // Container mount path
    readOnly?: boolean; // Default: false
};

type Service = {
    id: string; // UUID
    name: string; // Service name (must be unique per stack)
    image: string; // Docker image (e.g., "jellyfin/jellyfin:latest")
    command?: string[]; // Override entrypoint command
    env?: Record<string, string>; // Environment variables
    ports?: Port[]; // Port mappings
    volumes?: Volume[]; // Volume mounts
    networks?: string[]; // Net.id references
    dependsOn?: string[]; // Service.id references (startup order)
    restart?: "no" | "always" | "unless-stopped" | "on-failure";
    labels?: Record<string, string>; // Docker labels
    hostId?: string; // Host.id (optional; single-host stacks omit this)
};
```

### Versioning Strategy

- **v0**: Current schema (MVP). Intentionally minimal; omits `deploy`, `healthcheck`, `secrets`, `configs`.
- **v1** (future): Add healthchecks, resource limits, secrets management.
- **v2** (future): Multi-stack composition, dependency graphs across stacks.

Schema migrations will be versioned and tested with round-trip import/export fixtures.

### Rationale for Custom Format vs. Direct docker-compose

**Why not use docker-compose.yml directly as the internal format?**

1. **Separation of Concerns**: Blueprint is a design artifact; Compose is a deployment artifact. Keeping them separate allows:
    - Linting/validation before export
    - Multi-target export (Compose, Kubernetes, Podman)
    - Canvas state (positions, metadata) without polluting Compose output

2. **Type Safety**: Zod provides runtime validation + TypeScript inference. docker-compose YAML lacks strong typing.

3. **Conflict Detection**: Blueprint can enforce constraints (unique service names, no port collisions) that docker-compose doesn't validate until runtime.

4. **Extensibility**: Adding `hostId` or `subnetCidr` to Blueprint doesn't require changing Compose export logic immediately.

**Alternatives Considered:**

- **Option A**: Use docker-compose.yml as the source of truth.
    - ❌ Rejected: No type safety, hard to extend, couples design to deployment format.

- **Option B**: Use a generic infrastructure-as-code format (HCL, CUE).
    - ❌ Rejected: Overengineered for MVP; adds learning curve for contributors.

- **Option C**: Custom JSON Schema without Zod.
    - ❌ Rejected: Loses TypeScript type inference; more boilerplate.

## Consequences

### Positive

- ✅ **Runtime validation** with TypeScript type inference (DX win)
- ✅ **Clear separation** between design (Blueprint) and deployment (Compose)
- ✅ **Multi-host support** from day one (future-proof for homelab sprawl)
- ✅ **Versioned schema** enables backward-compatible migrations
- ✅ **Lint-friendly**: Can validate port/volume/name conflicts before export

### Negative

- ❌ **Custom format** requires import/export logic (added complexity)
- ❌ **Not 1:1 with Compose**: Users familiar with docker-compose must learn Blueprint
- ❌ **Maintenance burden**: Must keep import/export mappings in sync with Compose spec changes

### Neutral

- 🔄 **Future additions**: `networks.ipam`, `services.healthcheck`, `services.deploy` will be additive (non-breaking)
- 🔄 **Migration path**: Version field enables schema evolution (v0 → v1 → v2)

## Implementation Notes

1. **Zod schema location**: `/packages/schema/src/blueprint.ts`
2. **JSON Schema export**: Use `zod-to-json-schema` for API documentation
3. **Test fixtures**: Include 5+ Blueprint examples in `/packages/schema/__fixtures__/`
4. **Round-trip tests**: Compose → Blueprint → Compose (semantic equivalence)

Designer-first workflow: The new Library feature stores serialized Blueprint snapshots (both service templates and full stacks), keeping the schema the single source of truth. User-saved templates and stacks simply serialize the existing Blueprint and introduce no new entities or structural changes. Unsupported Compose fields surfaced via the YAML editor will be preserved as labels/annotations where possible or emitted as warnings, aligned with the Designer-First proposal.

## Implementation Status

✅ **Completed** (P1.1 - 2025-01-04)

The Blueprint v0 schema has been implemented in `/packages/schema` with the following:

### Package Structure

```
packages/schema/
├── src/
│   ├── blueprint.ts       # Core Zod schemas
│   ├── json-schema.ts     # JSON Schema export helper
│   └── index.ts           # Public API exports
├── __tests__/
│   └── blueprint.test.ts  # Comprehensive test suite (34 tests)
├── package.json
├── tsconfig.json
├── vitest.config.ts
└── eslint.config.js
```

### Validation Features

- **Port validation**: Integer range 1-65535, protocol defaults to "tcp"
- **Volume validation**: Type enforcement (bind/volume), read-only defaults to false
- **UUID validation**: All entity IDs validated as UUIDs
- **Datetime validation**: ISO 8601 timestamps for createdAt/updatedAt
- **Enum validation**: Restart policies (no/always/unless-stopped/on-failure)
- **Non-empty strings**: Names and paths must have length ≥ 1

### Test Coverage

- 34 test cases covering all schema types
- Validation of valid inputs
- Rejection of invalid inputs with clear error messages
- Edge cases (empty strings, invalid UUIDs, out-of-range ports)
- Default value behavior (protocol, readOnly)
- Complex nested structures (multi-service with dependencies)

### Exports

```typescript
// Core schemas
export {
  BlueprintSchema,
  PortSchema,
  VolumeSchema,
  HostSchema,
  NetSchema,
  ServiceSchema,
  BlueprintMetaSchema,
};

// TypeScript types (inferred from Zod)
export type {
  Blueprint,
  Port,
  Volume,
  Host,
  Net,
  Service,
  BlueprintMeta,
};

// JSON Schema helper
export { getBlueprintJsonSchema };
```

### Dependencies

- `zod@^3.22.4` - Runtime validation
- `zod-to-json-schema@^3.24.6` - JSON Schema export

All tests pass ✅ | TypeScript validation passes ✅

## References

- [Docker Compose Specification v2.x](https://docs.docker.com/compose/compose-file/)
- [Zod Documentation](https://zod.dev/)
- Dockitect vision: `/Dockitect.md` (section 10: data model)
