# ADR-017: Unified Bundle-Only OpenAPI Input Pipeline

## Status

**Accepted** - 2025-01-XX

## Context

During the unified OpenAPI input pipeline implementation (Phase 1, Part 5), we discovered a critical bug in our handling of OpenAPI documents:

1. **Circular Reference Failures**: Tests for circular schema references were failing with stack overflow errors (`RangeError: Maximum call stack size exceeded`) when processing in-memory OpenAPI objects.

2. **SwaggerParser.validate() Mutation Bug**: Investigation revealed that `SwaggerParser.validate()` mutates in-memory OpenAPI objects by resolving `$ref` strings into actual circular JavaScript object references. This mutation then causes `SwaggerParser.bundle()` to fail because it cannot traverse the circular structure.

3. **Architectural Goal**: We wanted a single, unified pipeline that works consistently for all input types (file paths, URLs, in-memory objects) without requiring different processing modes.

4. **Previous Approach**: The codebase had support for both `bundle` and `dereference` modes via CLI flags (`--input-mode`), creating complexity and potential inconsistencies.

## Decision

We decided to:

1. **Use Bundle Mode Exclusively**: Remove support for `dereference` mode and use `bundle()` mode for all OpenAPI document processing.

2. **Remove Separate validate() Call**: Call `SwaggerParser.bundle()` directly without a prior `validate()` call. Bundle mode performs validation internally, and the separate `validate()` call was causing the mutation bug.

3. **Single Processing Point**: All OpenAPI input (CLI and programmatic) flows through `prepareOpenApiDocument()`, ensuring deterministic behavior.

4. **Remove `--input-mode` CLI Flag**: Deprecate and remove the CLI flag that allowed users to choose between bundle and dereference modes.

## Rationale

### Why Bundle Mode?

1. **Circular References**: Bundle mode preserves `$ref` strings, allowing us to detect cycles and use Zod's `z.lazy()` appropriately. Dereferencing creates circular JavaScript objects that cause stack overflows.

2. **Dependency Tracking**: Our dependency graph relies on `$ref` strings to determine schema ordering. After dereferencing, these `$ref`s are gone, making it impossible to determine which schemas depend on which.

3. **Code Generation**: The Zod conversion code expects `$ref`s, not inlined schemas. It handles `$ref`s by generating references to other schema constants, maintaining clean, readable generated code.

### Why Not validate() + bundle()?

Calling `SwaggerParser.validate()` on in-memory objects mutates them by resolving `$ref` strings into circular JavaScript references. This mutation then causes `bundle()` to fail with stack overflow errors. Since `bundle()` performs validation internally, the separate `validate()` call is redundant and harmful.

### Why Remove Mode Selection?

1. **Simplicity**: A single processing mode reduces complexity and potential for bugs.
2. **Consistency**: All inputs are processed identically, regardless of source (file, URL, or in-memory object).
3. **Correctness**: Bundle mode is the correct choice for our use case (circular refs, dependency tracking, code generation).

## Consequences

### Positive

- ✅ **Fixed Circular Reference Bug**: Circular schemas now work correctly with `z.lazy()`.
- ✅ **Simplified Architecture**: Single processing mode reduces complexity.
- ✅ **Deterministic Behavior**: All inputs processed identically.
- ✅ **Better Error Messages**: Single code path means consistent error handling.
- ✅ **OpenAPI 3.1.x Support**: Discovered that the codebase inherently supports 3.1.x features (type arrays, numeric exclusive bounds, etc.) without special handling.

### Negative

- ❌ **Removed CLI Option**: Users can no longer choose `dereference` mode. However, this was rarely needed and caused bugs.
- ❌ **Breaking Change**: CLI flag `--input-mode` removed (but this was a relatively new feature).

### Neutral

- Bundle mode is the default and recommended mode in SwaggerParser documentation.
- Most users were already using bundle mode (or the default).

## Implementation Details

The fix involved:

1. Removing `SwaggerParser.validate()` call from `prepareOpenApiDocument()`.
2. Using only `SwaggerParser.bundle()` which performs validation internally.
3. Removing `--input-mode` CLI flag and related validation logic.
4. Removing `parserOptions` parameter from `generateZodClientFromOpenAPI()`.
5. Updating all tests to reflect bundle-only behavior.
6. Removing brittle tests that checked for specific error message strings.

## Related ADRs

- None (this is a bug fix and architectural simplification, not a new feature)

## References

- SwaggerParser documentation: https://apitools.dev/swagger-parser/docs/swagger-parser.html
- Bundle vs Dereference: https://apitools.dev/swagger-parser/docs/swagger-parser.html#bundleapi-options-callback
- Issue discovered during Phase 1, Part 5 implementation (unified OpenAPI input pipeline)
