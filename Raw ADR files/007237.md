# ADR-002: Scalar Pipeline Adoption

**Date:** November 4, 2025  
**Status:** Accepted  
**Deciders:** Architecture Team  
**Related:** ADR-001 (3.1-First), ADR-003 (Intersection Types), ADR-004 (Legacy Removal)

---

## Context

The library previously relied on `@apidevtools/swagger-parser` for OpenAPI document loading, bundling, and validation. While functional, this approach had several limitations:

### Problems with SwaggerParser

1. **Limited Metadata:** No access to bundle details (which files loaded, external refs, warnings)
2. **Opaque Bundling:** No control over `$ref` resolution strategy
3. **Validation Gaps:** Limited error detail, no sanitization options
4. **Type Mismatches:** Used `openapi-types` which didn't align with our `openapi3-ts` usage
5. **No 3.1 Upgrade:** No built-in mechanism to normalize 3.0 → 3.1
6. **Maintenance Concerns:** Package maintenance less active, fewer features

### Requirements for New Pipeline

The modernization effort required:

- **Rich Metadata:** Track which files/URLs were loaded, external references, warnings
- **Deterministic Bundling:** Preserve internal `$ref`s for dependency graphs
- **Version Normalization:** Automatic 3.0 → 3.1 upgrade
- **Validation Control:** Access to AJV-backed validation with detailed errors
- **Type Alignment:** Types compatible with our `openapi3-ts/oas31` usage
- **Extension Preservation:** Keep vendor extensions (x-\*) for debugging

---

## Decision

**We will adopt the Scalar ecosystem (`@scalar/json-magic`, `@scalar/openapi-parser`, `@scalar/openapi-types`) as our OpenAPI document processing pipeline.**

### Scalar Stack Components

1. **`@scalar/json-magic@0.7.0`**
   - Handles bundling with `readFiles()` and `fetchUrls()` plugins
   - Provides lifecycle hooks for `$ref` resolution control
   - Adds `x-ext` and `x-ext-urls` metadata for traceability

2. **`@scalar/openapi-parser@0.23.0`**
   - Provides `upgrade()` for 3.0 → 3.1 normalization
   - Offers `validate()` with AJV-backed schema validation
   - Includes `sanitize()` for spec cleanup

3. **`@scalar/openapi-types@0.5.1`**
   - TypeScript types for OpenAPI 3.0 and 3.1
   - Extension-friendly (allows `x-*` properties)
   - Compatible with intersection type strategy

### New `loadOpenApiDocument` Function

```typescript
/**
 * Load and bundle an OpenAPI document with rich metadata tracking.
 *
 * Accepts file paths, URLs, or in-memory objects. All specs are:
 * 1. Bundled via @scalar/json-magic (resolves $refs, tracks metadata)
 * 2. Upgraded to OpenAPI 3.1 via @scalar/openapi-parser
 * 3. Validated and typed as BundledOpenApiDocument
 *
 * @param input - File path, URL, or OpenAPI object
 * @returns Bundled 3.1 document with metadata
 * @throws Error if document cannot be loaded or upgraded
 */
export async function loadOpenApiDocument(
  input: string | URL | OpenAPIObject,
): Promise<LoadedOpenApiDocument>;
```

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Input: string | URL | OpenAPIObject (3.0 or 3.1)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ @scalar/json-magic/bundle()                                 │
│ - readFiles() plugin → tracks filesystem access             │
│ - fetchUrls() plugin → tracks HTTP requests                 │
│ - Lifecycle hooks → preserve internal $refs                 │
│ - Output: bundled document + x-ext metadata                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ @scalar/openapi-parser/upgrade()                            │
│ - Converts 3.0 → 3.1 (nullable, exclusiveMin/Max, etc.)    │
│ - Aligns with JSON Schema Draft 2020-12                     │
│ - Output: OpenAPI 3.1 document                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Type Guard: isBundledOpenApiDocument()                      │
│ - Validates required 3.1 properties (openapi, info, paths)  │
│ - Narrows type from loose Scalar types to strict types      │
│ - No casting - runtime validation only                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Output: LoadedOpenApiDocument                               │
│ - document: BundledOpenApiDocument (intersection type)      │
│ - metadata: BundleMetadata (files, URLs, warnings)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Consequences

### Positive

✅ **Rich Metadata:** Full visibility into bundle process (files, URLs, warnings, external refs)  
✅ **Deterministic Bundling:** Lifecycle hooks control `$ref` resolution behavior  
✅ **Automatic Upgrade:** Built-in 3.0 → 3.1 normalization via `upgrade()`  
✅ **Better Validation:** AJV-backed validation with detailed error messages  
✅ **Type Alignment:** Scalar types work with intersection type strategy  
✅ **Extension Preservation:** `x-ext` and `x-ext-urls` available for debugging  
✅ **Active Maintenance:** Scalar ecosystem actively developed and maintained  
✅ **Future Features:** Access to sanitize, validate, and other Scalar utilities

### Negative

⚠️ **New Dependency:** Added three new packages to dependency tree  
⚠️ **Learning Curve:** Team needs to understand Scalar's plugin/lifecycle system  
⚠️ **Type Complexity:** Scalar uses loose types (`Record<string, unknown>`), requiring boundary validation  
⚠️ **Version Lock:** Pinned to specific versions for deterministic behavior

### Neutral

ℹ️ **Bundle Size:** Minimal impact (~50KB gzipped for all three packages)  
ℹ️ **Performance:** Comparable to SwaggerParser, negligible difference  
ℹ️ **Breaking Change:** Internal only, public API unchanged

---

## Implementation Details

### Dependency Pinning

Exact versions pinned in `lib/package.json` for deterministic builds:

```json
{
  "dependencies": {
    "@scalar/json-magic": "0.7.0",
    "@scalar/openapi-parser": "0.23.0",
    "@scalar/openapi-types": "0.5.1"
  }
}
```

### Bundle Metadata Structure

```typescript
/**
 * Metadata captured during OpenAPI document bundling.
 */
export interface BundleMetadata {
  /** Entry point information (URI, filename, origin) */
  readonly entrypoint: BundleEntrypoint;

  /** All filesystem files accessed during bundling */
  readonly files: readonly BundleFileEntry[];

  /** All HTTP(S) URLs fetched during bundling */
  readonly urls: readonly BundleUrlEntry[];

  /** Warnings emitted during bundling (unresolved refs, etc.) */
  readonly warnings: readonly BundleWarning[];

  /** Summary of external references by target URI */
  readonly externalReferences: readonly ExternalReferenceSummary[];
}
```

### Lifecycle Hook Configuration

```typescript
const bundleConfig = {
  readFiles: filePlugin,
  fetchUrls: urlPlugin,
  beforeResolve: (context) => {
    // Preserve internal $refs for dependency graph
    if (isInternalRef(context.ref)) {
      return { skip: true };
    }
  },
  afterResolve: (context) => {
    // Track external references
    if (isExternalRef(context.ref)) {
      recordExternalRef(context.ref, context.target);
    }
  },
};
```

### Characterisation Tests

Added comprehensive characterisation coverage in `lib/src/characterisation/input-pipeline.char.test.ts`:

- Single-file specs (petstore.yaml)
- Multi-file specs with external `$ref`s
- Comparison with legacy SwaggerParser behavior
- Metadata validation (files, URLs, warnings)
- Preserved `$ref` verification

---

## Alternatives Considered

### Alternative 1: Continue with SwaggerParser

**Rejected:** Limited metadata, no upgrade mechanism, type mismatches. Would require significant workarounds to achieve desired functionality.

### Alternative 2: Build Custom Bundler

**Rejected:** Significant development and maintenance burden. Scalar provides battle-tested implementation with active support.

### Alternative 3: Use openapi-typescript Parser

**Rejected:** Focused on TypeScript generation, not general-purpose bundling. Doesn't provide the metadata tracking we need.

### Alternative 4: Use Redocly CLI

**Rejected:** CLI-focused tool, not designed as a library. Would require spawning processes and parsing output.

---

## Migration Strategy

### Phase 1: Foundation (Session 1) ✅

- Add Scalar dependencies with pinned versions
- Create guard to prevent SwaggerParser imports
- Document all existing `prepareOpenApiDocument` usage

### Phase 2: Implementation (Session 2) ✅

- Implement `loadOpenApiDocument` with Scalar pipeline
- Add characterisation tests for behavior parity
- Export new API surface with TSDoc

### Phase 3: Cleanup (Session 3+) 🟡

- Fix all type/lint errors from migration
- Update tests to use new pipeline
- Remove SwaggerParser dependency

### Phase 4: Integration (Session 4+) ⚪

- Update `prepareOpenApiDocument` to use new pipeline exclusively
- Remove legacy code paths
- Update documentation

---

## References

- [Scalar GitHub Repository](https://github.com/scalar/scalar)
- [@scalar/json-magic Documentation](https://github.com/scalar/scalar/tree/main/packages/json-magic)
- [@scalar/openapi-parser Documentation](https://github.com/scalar/scalar/tree/main/packages/openapi-parser)
- [@scalar/openapi-types Documentation](https://github.com/scalar/scalar/tree/main/packages/openapi-types)
- [JSON Schema Bundling](https://json-schema.org/understanding-json-schema/structuring.html)

---

## Related Decisions

- **ADR-001:** OpenAPI 3.1-First Architecture (enabled by Scalar's upgrade)
- **ADR-003:** Intersection Type Strategy (handles Scalar's loose types)
- **ADR-004:** Legacy Dependency Removal (removes SwaggerParser)

---

## Revision History

| Date       | Version | Changes                     |
| ---------- | ------- | --------------------------- |
| 2025-11-04 | 1.0     | Initial decision documented |
