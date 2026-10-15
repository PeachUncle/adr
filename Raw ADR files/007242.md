# ADR-026: No Regex for Schema Parsing

**Status:** Accepted  
**Date:** 2026-01-10  
**Deciders:** Engineering Team

## Context

During Phase 2, Session 2.3 implementation of the Zod parser, an initial approach using regular expressions was attempted for parsing Zod schema expressions. This approach quickly revealed fundamental limitations:

1. **Fragility:** Regex patterns failed on nested structures (e.g., `z.object({ a: z.string() })` broke patterns using `[^)]+`)
2. **Complexity:** Patterns became unreadable and required multiple eslint-disable comments
3. **Maintainability:** Each new Zod feature required new regex patterns and edge case handling
4. **Inappropriate tool:** The project already has ts-morph for AST manipulation

## Decision

**No regular expressions shall be used for parsing schema source code.**

The Zod parser (and any future source code parsers) must use proper tooling:

| Tool                        | Use Case                                                |
| --------------------------- | ------------------------------------------------------- |
| **ts-morph**                | TypeScript/JavaScript AST traversal and manipulation    |
| **TypeScript Compiler API** | Type resolution, symbol tables, semantic analysis       |
| **Zod runtime**             | Schema validation and type extraction (when applicable) |

Regex remains acceptable only for:

- Simple string matching (e.g., checking if a string starts with a prefix)
- User input validation (emails, UUIDs, etc.)
- Non-parsing utilities

## Consequences

### Positive

- **Robustness:** AST-based parsing handles all valid TypeScript syntax
- **Maintainability:** Code is easier to understand and extend
- **Correctness:** Proper handling of nested structures, comments, whitespace
- **Tooling alignment:** Leverages existing ts-morph investment from ADR-014

### Negative

- **Refactoring required:** Existing regex-based Session 2.2 and 2.3 code must be rewritten
- **Learning curve:** ts-morph API requires familiarity

## Implementation Notes

The following files contain regex-based parsing that must be refactored:

- `zod-parser.primitives.ts` — Uses `parseZodChain()` with regex
- `zod-parser.chain.ts` — Entire module is regex-based
- `zod-parser.object.ts` — Uses regex for property extraction
- `zod-parser.union.ts` — Uses regex patterns
- `zod-parser.intersection.ts` — Uses regex patterns
- `zod-parser.transforms.ts` — Uses regex patterns

## References

- [ADR-014: Migrate tanu to ts-morph](./ADR-014-migrate-tanu-to-ts-morph.md)
- [ts-morph documentation](https://ts-morph.com/)
