# ADR-023: Intermediate Representation (IR) Architecture for Schema Generation

## Status

Accepted

## Date

December 2025 (Updated January 2026)

## Context

The project needed to transition from direct format-to-format conversion (OpenAPI→Zod) to a universal schema conversion architecture where **any input format can be converted to any output format**.

The key insight: without a canonical Intermediate Representation, converting N formats requires O(N²) converters. With an IR, it requires only O(N) parsers + O(N) transformers = O(2N) = O(N).

**Strategic Vision:** See `.agent/VISION.md` for the full N×M conversion goal and roadmap.

### Problems with Direct Conversion

1. **Complexity explosion**: Each format pair needs dedicated conversion logic
2. **Edge case multiplication**: Circular references, polymorphism, and composition handled differently in each converter
3. **Format quirks leaking**: OpenAPI nullable semantics bleeding into Zod generation logic
4. **Type safety gaps**: "Prop drilling" context through deep call stacks

## Decision

**The IR architecture uses a canonical AST representation as the center of gravity for the entire system.**

After input parsing, the original document is conceptually discarded. All operations—validation, transformation, dependency analysis, code generation—work exclusively on the canonical AST.

### Architecture

```text
Input Formats              Canonical AST (Single Source of Truth)   Output Formats
─────────────              ───────────────────────────────────────   ──────────────
OpenAPI 3.1.x ──┐                                              ┌──▶ Zod 4 schemas
Zod 4 schemas ──┼──▶ Parser ──▶ [ CastrSchema, CastrSchemaNode,   ──┼──▶ TypeScript types
JSON Schema ────┘              IROperation, IRDependencyGraph ]   └──▶ JSON Schema
                                        │
                                        ▼
                            All transformers read from AST
                            Nothing reads from input directly
```

### Multi-Stage Pipeline

1. **IR Generation**: Parse input documents into a lossless internal representation
   - Graph structure representing schemas, endpoints, relationships
   - All `$ref`s resolved; circular dependencies explicitly tracked
   - Strictly typed; format-agnostic

2. **Context Building**: Transform IR into `TemplateContext` for specific output
   - Optimized for the target format (Zod + TypeScript, JSON Schema, etc.)
   - Includes metadata for dependency ordering, import management

3. **Code Generation**: Use `ts-morph` to generate code from context
   - Writers are pure functions: context → AST nodes
   - No string concatenation for code generation

### Key Types

| Type                 | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `CastrSchema`        | Type definition with constraints and metadata             |
| `CastrSchemaNode`    | Individual schema with context (required, nullable, etc.) |
| `IROperation`        | API endpoint definition (from OpenAPI)                    |
| `IRDependencyGraph`  | Reference tracking, topological sort, circular detection  |
| `CastrSchemaContext` | Discriminated union for schema usage contexts             |

### Key Invariants

1. **Input discarded after parsing** - Only the canonical AST is consulted for all operations
2. **No format-specific code in core** - Format knowledge lives only in parsers/transformers
3. **All transforms are AST → Output** - Never Input → Output directly
4. **Strict typing throughout** - No `any`, no unchecked assertions

## Consequences

### Positive

- **O(N) complexity**: Adding a new format requires one parser + one transformer
- **Single point of truth**: Edge cases handled once in IR model
- **Testability**: Each stage (parsing, IR, transformation) tested independently
- **Format evolution**: New format versions (OpenAPI 3.2, Zod 5) need only parser updates
- **Debugging**: IR can be inspected and validated separately from output

### Negative

- **Initial learning curve**: Contributors must understand IR structure
- **Abstraction overhead**: Simple conversions go through multiple stages
- **IR design critical**: Mistakes in IR design propagate everywhere

### Mitigation

- Comprehensive TSDoc on all IR types
- Test helpers for creating IR fixtures (`createMockCastrSchema`, `createMockCastrSchemaNode`)
- IR design based on well-understood patterns (compiler IR, search engine indexes)

## Format Implementation Order

The order of format support is **deliberate**. By implementing both input (parser) and output (writer) for a format before adding new formats, we discover shared patterns and prevent premature generalisation.

| Phase | Transform                 | Rationale                                     |
| ----- | ------------------------- | --------------------------------------------- |
| 1     | **OpenAPI → Zod**         | Established baseline                          |
| 2     | **Zod → OpenAPI**         | Complete round-trip; discover shared patterns |
| 3     | **JSONSchema ↔ OpenAPI** | Cross-format bridges                          |
| 4     | **JSONSchema ↔ Zod**     | Complete triangulation                        |
| 5     | **tRPC ↔ IR**            | Additional formats as needed                  |

See `VISION.md` for full rationale.

## Compliance

This decision aligns with:

- **VISION.md**: Implements the N×M conversion architecture
- **RULES.md**: Follows type safety, engineering excellence principles
- **Cardinal Rule**: The canonical AST is the single source of truth

## References

- `.agent/VISION.md` - Strategic vision and roadmap
- `.agent/RULES.md` - Engineering standards (Cardinal Rule section)
- `lib/src/context/ir-schema.ts` - IR type definitions
- `lib/src/context/ir-context.ts` - Schema context types
- [ADR-018](./ADR-018-openapi-3.1-first-architecture.md) - OpenAPI 3.1-first decision
