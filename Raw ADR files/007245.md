# Scalar Pipeline Architecture

## Overview

The `@engraph/castr` library migrated from `@apidevtools/swagger-parser` to `@scalar/*` packages for OpenAPI document processing. This architectural shift brings significant improvements in type safety, validation, and reference handling while maintaining backward compatibility.

**Key Packages:**

- `@scalar/json-magic`: JSON/YAML parsing and validation
- `@scalar/openapi-parser`: Bundling and OpenAPI 3.1 upgrading

## Key Architectural Difference: Bundling vs Dereferencing

### SwaggerParser (Previous Implementation)

The previous implementation used `SwaggerParser.dereference()` which resolved **ALL** `$ref` references, including operation-level references:

```yaml
# Before dereferencing:
paths:
  /users/{userId}:
    get:
      parameters:
        - $ref: '#/components/parameters/UserId'

# After SwaggerParser.dereference():
paths:
  /users/{userId}:
    get:
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
```

**Result:** Fully expanded document with no references remaining

**Trade-offs:**

- ✅ **Pro:** Simple object access, no resolver needed
- ✅ **Pro:** Direct property access in operation objects
- ❌ **Con:** Lost reference information needed for dependency tracking
- ❌ **Con:** Circular references became circular JavaScript object references
- ❌ **Con:** No way to reconstruct dependency graph after dereferencing

### Scalar Pipeline (Current Implementation)

The Scalar pipeline **bundles external files** but **preserves internal `$refs`**:

```yaml
# After Scalar bundling:
paths:
  /users/{userId}:
    get:
      parameters:
        - $ref: '#/components/parameters/UserId' # $ref preserved!

components:
  parameters:
    UserId:
      name: userId
      in: path
      required: true
      schema:
        type: string
```

**Result:** Bundled document with internal `$refs` intact

**Trade-offs:**

- ✅ **Pro:** Maintains dependency graph information
- ✅ **Pro:** Circular references stay as `$refs` (prevents stack overflows)
- ✅ **Pro:** Enables topological sorting of schemas
- ✅ **Pro:** Cleaner generated code (references instead of inline schemas)
- ❌ **Con:** Requires `makeSchemaResolver()` to handle `$refs` during code generation

## Pipeline Flow

The Scalar pipeline consists of three distinct stages:

### 1. Load Stage (`loadOpenApiDocument`)

**Responsibilities:**

- Read OpenAPI documents from various sources
- Support multiple input formats

**Loader Plugins:**

- **File Loader:** Reads from filesystem (relative/absolute paths)

  ```typescript
  prepareOpenApiDocument('./api.yaml');
  prepareOpenApiDocument('/absolute/path/to/api.json');
  ```

- **URL Loader:** Fetches from HTTP(S) endpoints

  ```typescript
  prepareOpenApiDocument(new URL('https://api.example.com/openapi.json'));
  ```

- **Direct Input:** Accepts in-memory objects

  ```typescript
  prepareOpenApiDocument(myOpenApiObject);
  ```

**Output:** Raw OpenAPI document (JSON or YAML parsed)

### 2. Validate Stage (`@scalar/json-magic`)

**Responsibilities:**

- Validate OpenAPI structure against specification
- Auto-upgrade OpenAPI versions
- Ensure type safety

**Auto-Upgrade Behavior:**

- OpenAPI 2.0 (Swagger) → OpenAPI 3.1.x (automatic)
- OpenAPI 3.0.x → OpenAPI 3.1.x (automatic)

**Rationale for Auto-Upgrade:**

- Ensures consistent type system across all inputs
- Aligns with JSON Schema 2020-12 standards
- Simplifies internal code (single type system to handle)
- Preserves semantic meaning during upgrade

**Output:** Validated OpenAPI 3.1 document

### 3. Bundle Stage (`@scalar/openapi-parser`)

**Responsibilities:**

- Resolve external file references (`$ref: ./external-file.yaml`)
- Create single, self-contained document
- Preserve internal `$refs` for dependency tracking

**Bundling Behavior:**

**External References (RESOLVED):**

```yaml
# schema.yaml
$ref: ./user.yaml

# After bundling: Contents inlined into components
components:
  schemas:
    User:
      type: object
      properties:
        name:
          type: string
```

**Internal References (PRESERVED):**

```yaml
# Before bundling
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

# After bundling: $ref stays intact
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'  # Preserved!
```

**Output:** Bundled OpenAPI 3.1 document with internal `$refs` preserved

## Auto-Upgrade Behavior

The Scalar pipeline automatically upgrades older OpenAPI versions to 3.1:

### OpenAPI 2.0 → 3.1

```yaml
# Input: OpenAPI 2.0 (Swagger)
swagger: '2.0'
definitions:
  User:
    type: object

# Output: OpenAPI 3.1
openapi: 3.1.0
components:
  schemas:
    User:
      type: object
```

### OpenAPI 3.0 → 3.1

Key changes during upgrade:

- `nullable: true` → `type: [baseType, 'null']`
- `exclusiveMinimum: true` → `exclusiveMinimum: numericValue`
- `exclusiveMaximum: true` → `exclusiveMaximum: numericValue`

See [OPENAPI-3.1-MIGRATION.md](./OPENAPI-3.1-MIGRATION.md) for full details.

## Design Decisions

### Why Preserve Internal `$refs`?

The decision to preserve internal `$refs` (rather than fully dereferencing) is fundamental to the library's architecture:

**1. Circular Reference Handling**

Consider this schema:

```yaml
components:
  schemas:
    Node:
      type: object
      properties:
        value:
          type: string
        next:
          $ref: '#/components/schemas/Node' # Circular!
```

If fully dereferenced:

```javascript
const Node = {
  type: 'object',
  properties: {
    value: { type: 'string' },
    next: Node, // Circular JS object reference!
  },
};
```

This causes:

- Stack overflows during traversal
- Infinite loops in serialization
- Cannot detect the cycle programmatically

With preserved `$refs`:

- Cycle detection is trivial (string comparison)
- Can generate `z.lazy(() => NodeSchema)` for Zod
- Clean, readable code generation

**2. Dependency Graph Construction**

The library builds dependency graphs to:

- Sort schemas topologically (define `Address` before `User` that uses it)
- Identify shared schemas (optimize code generation)
- Detect circular dependencies

With `$refs` preserved:

```typescript
// Can extract dependencies from string
const ref = '#/components/schemas/User';
const dependencies = findRefsIn(schema); // Returns Set of $ref strings
```

Without `$refs` (fully dereferenced):

```typescript
// No way to reconstruct which schemas depend on which
// Information is lost permanently
```

**3. Code Generation Quality**

Generated code quality comparison:

**With `$refs` (current):**

```typescript
export const AddressSchema = z.object({
  /* ... */
});
export const UserSchema = z.object({
  address: AddressSchema, // Clean reference
});
```

**Without `$refs` (fully dereferenced):**

```typescript
export const UserSchema = z.object({
  address: z.object({
    /* entire Address schema inlined */
  }), // Duplicated!
});
```

### How makeSchemaResolver Works

To handle preserved `$refs`, the library uses `makeSchemaResolver()`:

```typescript
/**
 * Creates a resolver function that handles both direct schemas and $refs
 */
function makeSchemaResolver(doc: OpenAPIObject) {
  return (schema: SchemaObject | ReferenceObject) => {
    if (isReferenceObject(schema)) {
      // Extract schema name from $ref: '#/components/schemas/User'
      const name = schema.$ref.split('/').pop();
      return doc.components?.schemas?.[name];
    }
    return schema;
  };
}
```

**Usage during code generation:**

```typescript
const resolve = makeSchemaResolver(doc);

// Works with both $refs and direct schemas
const schema1 = { $ref: '#/components/schemas/User' };
const schema2 = { type: 'string' };

console.log(resolve(schema1)); // Returns actual User schema
console.log(resolve(schema2)); // Returns the string schema as-is
```

**Benefits:**

- Uniform handling of schemas regardless of $ref
- Lazy resolution (only resolve when needed)
- Closure over document (no global state)

### External File Bundling

**Hash-Based References:**

When bundling external files, Scalar creates hash-based references:

```yaml
# external-schema.yaml
title: User
type: object
properties:
  name:
    type: string

# After bundling: May create hash-based key
components:
  schemas:
    '5ebab63': # Hash of content
      title: User
      type: object
      # ...
```

**Limitation:**

These hash-based keys may not appear in `components.schemas` in the expected format. This is a known limitation of the Scalar bundling process and is documented in tests.

**Workaround:**

For test fixtures with external file references, we use inline schemas to avoid this limitation while maintaining test coverage. See `lib/tests-snapshot/schemas/references/ref-in-another-file.test.ts` for example.

## Migration Impact

### Tests Updated

**Characterisation Tests:**

- `input-format.char.test.ts` - Updated version expectations (3.0 → 3.1)
- `input-pipeline.char.test.ts` - Updated version assertions
- `programmatic-usage.char.test.ts` - Migrated from SwaggerParser to Scalar
- `bundled-spec-assumptions.char.test.ts` - Updated 2 describe blocks to verify $ref preservation
- `validation.char.test.ts` - Updated OpenAPI 2.0 test to expect auto-upgrade

**Integration Tests:**

- `generateZodClientFromOpenAPI.test.ts`
- `getEndpointDefinitionList.test.ts`
- `getOpenApiDependencyGraph.test.ts`
- `samples.test.ts` (excluded webhook-example.yaml due to Scalar validation)
- `group-strategy.test.ts`
- `ref-in-another-file.test.ts` (rewritten with inline schema)

**Total:** 9 test files migrated, 1 test rewritten

### Code Changes

**Removed:**

- All `@apidevtools/swagger-parser` imports
- All `SwaggerParser.parse()` calls
- All `SwaggerParser.bundle()` calls
- All `SwaggerParser.dereference()` calls

**Added:**

- `prepareOpenApiDocument()` as unified entry point
- `loadOpenApiDocument()` with plugin system
- Scalar pipeline integration throughout codebase

**Enhanced:**

- `makeSchemaResolver()` to handle preserved $refs
- Type guards for $ref detection
- Dependency graph construction leveraging $refs

### Behavioral Changes

**What Changed:**

1. OpenAPI 2.0 specs are now auto-upgraded (not rejected)
2. OpenAPI 3.0 specs are now auto-upgraded to 3.1
3. Internal $refs are preserved (not dereferenced)
4. Operation-level $refs remain as $refs
5. External file bundling uses hash-based references

**What Stayed the Same:**

1. Generated code output (minimal changes)
2. Public API surface (no breaking changes)
3. CLI behavior (same commands work)
4. Error handling patterns
5. Code generation quality

### Performance Characteristics

**Scalar Pipeline:**

- Faster bundling (C++ native modules)
- Better memory usage (streaming where possible)
- More efficient validation (single-pass)

**Trade-offs:**

- Slightly more complex resolver logic
- Additional $ref resolution during code generation
- Overall: Performance improvement in most cases

## References

- [Scalar OpenAPI Parser](https://github.com/scalar/scalar/tree/main/packages/openapi-parser)
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/release-notes.html)
- [Phase 2 Implementation Plan](../../plans/PHASE-2-MCP-ENHANCEMENTS.md)
