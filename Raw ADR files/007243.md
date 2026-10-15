# ADR-029: Canonical Source Structure

**Date:** 2026-01-12  
**Status:** Accepted  
**Context:** Discovered 3 duplicate IR→OpenAPI implementations in different directories, revealing lack of coherent organizational principle

---

## Decision

The following directory structure is THE canonical organization for all format transforms in Castr:

```
lib/src/
├── ir/                        # Intermediate Representation (the core)
│   ├── schema.ts              # CastrDocument, CastrSchema types
│   ├── schema.types.ts        # Supporting IR types
│   └── serialization.ts       # serializeIR, deserializeIR
│
├── parsers/                   # Format → IR (Input Layer)
│   ├── openapi/               # OpenAPI → IR
│   │   ├── index.ts           # buildIR (main entry)
│   │   ├── builder.*.ts       # Component-specific builders
│   │   └── types.ts           # Parser-specific types
│   └── zod/                   # Zod source → IR
│       ├── index.ts           # parseZodSource (main entry)
│       └── *.ts               # Parser modules
│
├── writers/                   # IR → Format (Output Layer)
│   ├── openapi/               # IR → OpenAPI
│   │   ├── index.ts           # writeOpenApi (main entry)
│   │   └── *.ts               # Writer modules
│   ├── zod/                   # IR → Zod code
│   │   ├── index.ts           # writeZod (main entry)
│   │   └── *.ts               # Writer modules
│   └── typescript/            # IR → TypeScript types
│       ├── index.ts           # writeTypeScript
│       └── *.ts               # Writer modules
│
└── [other directories]        # See Rationale
```

---

## Naming Conventions

| Layer      | Directory           | Function Prefix    | Example                     |
| ---------- | ------------------- | ------------------ | --------------------------- |
| **Input**  | `parsers/{format}/` | `parse*`, `build*` | `parseZodSource`, `buildIR` |
| **Output** | `writers/{format}/` | `write*`           | `writeOpenApi`, `writeZod`  |

**Rejected alternatives:**

- `transformers/` — VISION.md term, but `writers/` is established ts-morph convention
- `generators/` — Conflated with code generation (deleted per ADR-028)
- `converters/` — Ambiguous direction (deleted per ADR-028)

---

## Current State → Target State

| Current Location          | Target Location                | Status             |
| ------------------------- | ------------------------------ | ------------------ |
| `context/ir-schema.ts`    | `ir/schema.ts`                 | ✅ Complete        |
| `context/ir-builder.ts`   | `parsers/openapi/index.ts`     | ✅ Complete        |
| `context/ir-builder.*.ts` | `parsers/openapi/builder.*.ts` | ✅ Complete        |
| `parsers/zod/*`           | `parsers/zod/*`                | ✅ Already correct |
| `writers/openapi/*`       | `writers/openapi/*`            | ✅ Already correct |
| `writers/zod-writer.ts`   | `writers/zod/index.ts`         | ✅ Complete        |
| `writers/typescript.ts`   | `writers/typescript/index.ts`  | ✅ Complete        |

---

## Other Directories (Unchanged)

| Directory     | Purpose                                  | Notes                  |
| ------------- | ---------------------------------------- | ---------------------- |
| `shared/`     | Utilities, dependency graph, type guards | Keep                   |
| `validation/` | MCP validation, type guards              | Keep                   |
| `rendering/`  | CLI orchestration, Handlebars templating | Keep (legacy pipeline) |
| `cli/`        | CLI entry point                          | Keep                   |
| `endpoints/`  | Endpoint metadata extraction             | Keep                   |
| `context/`    | TemplateContext (reduced after moves)    | Keep                   |
| `conversion/` | Convenience facades                      | Consider deprecating   |

---

## Consequences

1. **Any new format** gets two directories: `parsers/{format}/` and `writers/{format}/`
2. **No more ad-hoc directories** for transforms (`generators/`, `converter/`, `conversion/`)
3. **IR is centralized** in `ir/` directory
4. **Update VISION.md** to reflect `parsers/` + `writers/` (not `transformers/`)

---

## References

- [ADR-028: IR→OpenAPI Consolidation](./ADR-028-ir-openapi-consolidation.md)
- [VISION.md](../../.agent/VISION.md)
