# Command and Query as First-Class Primitives

**Deciders**: Virgil (lead architect)  
**Date**: 2026-01-05  
**Status**: Accepted

## Problem

Traditional DDD treats commands and queries as implicit - just inputs to use cases. But in distributed systems we need:
- Idempotency (prevent duplicate operations)
- Distributed tracing (correlationId across services)
- Versioning (evolve schemas without breaking clients)
- Serialization (for message buses, event streams)
- Validation at boundary (before reaching domain)

Should Command and Query be first-class primitives or implementation details?

## Decision

**Command and Query are DDD primitives (#12 and #13).**

Both extend base classes with:
- `id` field (commandId/queryId for deduplication)
- `version` field (schema evolution)
- `correlationId` (tracing)
- Zod validation in static factory
- `toPrimitives()` / `fromPrimitives()` serialization
- Immutable (readonly fields)
- Returns `Result<T, ValidationError>`

**Paths**:
- Commands: `src/core/{context}/application/commands/`
- Queries: `src/core/{context}/application/queries/`

## Why This Matters

**Benefits**:
- Explicit CQRS separation (mutate vs read)
- Built-in idempotency via commandId
- Distributed tracing via correlationId
- Type-safe with `Command<TResult>` and `Query<TResult>`
- Separately testable validation (validation.spec.ts, serialization.spec.ts)
- Message bus ready (guaranteed serializable)

**Trade-offs**:
- 13 primitives instead of 11 (more concepts)
- Boilerplate (factory, schema, serialization per command/query)
- Extra indirection (Handler → Command → UseCase)
- Requires generators (manual creation tedious)

**Rejected Alternatives**:
- **Plain DTOs as inputs**: No idempotency, versioning, or serialization guarantees
- **Bus without primitives**: No standardized validation/serialization
- **Commands as Events**: Conflates intent (command) with fact (event)

## Enforcement

**Check Compliance**:
```bash
# Verify all commands/queries extend base classes
npm run lint -- --rule require-command-base --rule require-query-base

# Check for validation schemas
grep -r "z.object" src/core/*/application/commands/
grep -r "z.object" src/core/*/application/queries/

# Verify test files exist
find src/core/*/application/commands -name "*.validation.spec.ts"
find src/core/*/application/queries -name "*.serialization.spec.ts"
```

**Automation**:
- ESLint: `require-command-base` - Enforces `extends Command<TResult>`
- ESLint: `require-query-base` - Enforces `extends Query<TResult>`
- ESLint: `require-command-id` - Enforces `id` field for idempotency
- ESLint: `require-query-id` - Enforces `id` field for deduplication
- ESLint: `require-command-validation` - Enforces Zod schema in factory
- ESLint: `require-command-serialization` - Enforces toPrimitives/fromPrimitives
- Generator: `nx generate command --context=... --name=...` scaffolds class + schema + 2 test files
- Generator: `nx generate query --context=... --name=...` scaffolds class + schema + 2 test files
- CI: `test-coverage-check` validates validation.spec.ts and serialization.spec.ts exist
- TypeScript: `--strict` enforces readonly fields, Result return types

**Manual Review**:
- [ ] Command/query doesn't contain business logic (only validation)
- [ ] Version field considered if schema may evolve
- [ ] correlationId flows through to use case tracing
- [ ] Serialization round-trip tested (toPrimitives → fromPrimitives)
- [ ] Idempotency strategy documented (if applicable)

## References

- [Command specification](../../ddd-implementation/primitives/command/specification.md)
- [Command enforcement](../../ddd-implementation/primitives/command/enforcement.md)
- [Query specification](../../ddd-implementation/primitives/query/specification.md)
- [Query enforcement](../../ddd-implementation/primitives/query/enforcement.md)
- [CQRS Pattern - Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
