# ADR-008: Schema Validation Strategy

## Status

Accepted

## Date

2025-01-27

## Context

NEURECTOMY needs consistent validation across:

- API request/response payloads
- Configuration files (agents, workflows, tasks)
- User input in UI forms
- Cross-service communication
- Database entities

Current challenges:

1. Validation logic duplicated across TypeScript and Rust
2. No standardized error message format
3. API contracts not machine-readable
4. Difficult to generate documentation from schemas

## Decision

We will adopt a **Zod-first schema strategy** with JSON Schema as the interchange format:

### Schema Definition Flow

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────┐
│ Zod Schema  │──────▶│ JSON Schema  │──────▶│ Language-specific│
│ (Source)    │       │ (Interchange)│       │ Validators       │
└─────────────┘       └──────────────┘       └─────────────────┘
       │                     │                       │
       ▼                     ▼                       ▼
  TypeScript            OpenAPI/             Rust (serde_json)
  Type Inference        AsyncAPI             Python (pydantic)
```

### Key Components

1. **@neurectomy/core** - Contains Zod schema definitions
2. **@neurectomy/schema-codegen** - Generates JSON schemas and type guards
3. **Generated artifacts** - JSON Schema files for cross-language validation

### Validation Rules

| Context      | Validation Level  | Error Behavior                  |
| ------------ | ----------------- | ------------------------------- |
| API Input    | Strict            | Return 400 with detailed errors |
| Config Files | Strict + Defaults | Fail fast on missing required   |
| UI Forms     | Progressive       | Show inline errors              |
| Database     | Coerce            | Auto-convert compatible types   |

### Error Format

All validation errors follow this structure:

```typescript
interface ValidationError {
  code: "VALIDATION_ERROR";
  message: string;
  issues: ValidationIssue[];
}

interface ValidationIssue {
  path: string[]; // ["config", "timeout"]
  code: string; // "too_small"
  message: string; // "Must be at least 1000"
  expected?: unknown; // 1000
  received?: unknown; // 500
}
```

### Schema Locations

```
packages/
  core/src/schemas/
    agent.schema.ts       # Zod definitions
    workflow.schema.ts
    task.schema.ts
  schema-codegen/
    generated/            # JSON Schema output
      agent.schema.json
      workflow.schema.json
```

## Consequences

### Positive

- **Single source of truth**: Zod schemas define all validations
- **Type safety**: TypeScript types inferred from schemas
- **Cross-language**: JSON Schema works in Rust, Python, etc.
- **Documentation**: Schemas generate API docs automatically
- **Runtime validation**: Zod provides runtime checks
- **Composable**: Schemas can extend and combine

### Negative

- **Learning curve**: Team must learn Zod API
- **Build step**: JSON Schema generation adds to build
- **Schema drift**: Must keep generated files in sync
- **Bundle size**: Zod adds ~12KB to client bundle

### Mitigations

- Pre-commit hook validates schema generation
- CI fails if generated schemas are stale
- Bundle splitting for client-side schemas

## Alternatives Considered

### 1. JSON Schema First

**Rejected**: Writing JSON Schema by hand is verbose and error-prone. Zod provides better DX with TypeScript integration.

### 2. TypeScript Types Only

**Rejected**: No runtime validation. Types erased at compile time.

### 3. io-ts

**Rejected**: More complex API, smaller ecosystem, less intuitive error messages.

### 4. Ajv (JSON Schema validator)

**Partially adopted**: Used for validating JSON Schema files, but Zod remains primary.

## Implementation

### Phase 1: Core Schemas (Complete)

- [x] Define schemas in @neurectomy/core
- [x] Create schema-codegen package
- [x] Generate JSON Schema files

### Phase 2: Integration

- [ ] Add Zod to all API routes
- [ ] Create form validation hooks
- [ ] Generate OpenAPI from schemas

### Phase 3: Cross-Language

- [ ] Rust schema validation with serde
- [ ] Python validation with pydantic
- [ ] Schema version management

## References

- [Zod Documentation](https://zod.dev)
- [JSON Schema Specification](https://json-schema.org/)
- [zod-to-json-schema](https://github.com/StefanTerdell/zod-to-json-schema)
