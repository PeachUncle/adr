# ADR-004: Plugin Sandbox & API (Import)

Status: Accepted
Date: 2025-08-21
Owners: Archon Core

## Context

Archon must ingest external data. We want a portable, safe way to run import logic without native builds or excessive attack surface.

## Decision

- **Language/Runtime (MVP):** JavaScript/TypeScript only, executed in a **sandboxed Web Worker**.
- **Default capabilities:** No filesystem, no network. Host passes file bytes explicitly. If a plugin needs network, show a **per-run consent** dialog to allow `fetch` for that operation.
- **API:**

  ```ts
  export type ArchonNode = {
    id: string; name: string; description?: string;
    properties: Record<string, string | number | boolean | null>;
    children: string[]; // child IDs in order
  };

  export type ImportResult = { root: ArchonNode };

  export interface ImportPlugin {
    meta: { id: string; name: string; version: string; formats: string[] };
    run(input: Uint8Array | string, options?: Record<string, unknown>): Promise<ImportResult>;
  }
  ```

- **Distribution (MVP):** Local directory ~/.archon/plugins. Manifest optional (manifest.json) may declare permissions (e.g., { "net": true }) for prompting.
- **Resource limits:** 60s CPU time, 256MB heap caps with termination on exceed; errors surface as structured failures.
- **Integrity:** Optional SHA-256 hash in manifest; warn if absent but allow install.

Rationale

JS workers provide portability and a narrow attack surface. Per-run consent keeps users in control. The API is minimal and stable for common imports.

Alternatives Considered

- **Go/native plugins:** Cross-compilation, ABI/plugin model complexity, security risks.
- **Full Node.js runtime:** Larger footprint; unnecessary for MVP.
- **Always-on network:** Violates least-privilege and privacy expectations.

Consequences

- **Positive:** Portable, safe, easy to distribute and upgrade.
- **Negative:** CPU/memory limits and lack of FS may constrain niche use cases.
- **Follow-ups:** Signed plugin registry, export plugins, validation helpers, richer SDK.

Implementation Notes

- **Loader:** frontend/src/plugins/loader.ts, worker pool with per-task teardown.
- **UI:** src/routes/import/ImportWizard.svelte (validate → preview → merge target → commit).
- **Errors:** { code:"E_PLUGIN_*", message, details } with stack capture.
- **Examples:** examples/plugins/csv-import/.

Review / Revisit

- Revisit when a plugin ecosystem emerges (registry/signing), or when export/transforms are introduced.
