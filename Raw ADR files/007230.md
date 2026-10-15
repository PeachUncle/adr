# ADR-011: AJV for Runtime OpenAPI Validation

## Status

**Accepted** - October 24, 2025

## Context

We needed a way to validate OpenAPI documents against the official OpenAPI specification at runtime, both in our tests and potentially as a validation feature for users.

### The Problem

**Challenges:**

1. OpenAPI 3.0.x uses JSON Schema draft-04
2. OpenAPI 3.1.x uses JSON Schema 2020-12
3. Different validation approaches needed per version
4. Type-only validation (TypeScript) doesn't catch spec violations at runtime
5. Need to validate test documents to ensure they're spec-compliant

### Requirements

1. **Validate against official schemas**: Use the actual OpenAPI JSON schemas
2. **Support multiple OAS versions**: 3.0.x and future 3.1.x/3.2.x
3. **Clear error messages**: Help developers understand what's wrong
4. **Testing infrastructure**: Validate test documents automatically
5. **Type safety**: Works with `openapi3-ts` TypeScript types

## Decision

**We will use AJV (Another JSON Schema Validator) to validate OpenAPI documents against official schemas.**

### Rationale

1. **Standard**: AJV is the most popular JSON Schema validator (50M+ weekly downloads)
2. **Multi-version support**: Supports JSON Schema draft-04, 2019-09, 2020-12
3. **Fast**: Highly optimized, uses code generation
4. **Extensible**: Plugins for formats, custom keywords
5. **TypeScript support**: Good type definitions
6. **Active maintenance**: Regular updates, responsive maintainers

### Implementation

#### For OpenAPI 3.0.x (JSON Schema draft-04)

```typescript
import Ajv04 from 'ajv-draft-04';
import addFormats from 'ajv-formats';
import { readFileSync } from 'node:fs';

// Handle CJS/ESM interop
const Ajv04 = (Ajv04Module as any).default || Ajv04Module;
const addFormats = (addFormatsModule as any).default || addFormatsModule;

// Load official OpenAPI 3.0.x schema
const oas30Schema = JSON.parse(
  readFileSync('.agent/reference/openapi_schema/openapi_3_0_x_schema.json', 'utf-8'),
);

// Create validator
const ajv = new Ajv04({
  strict: false, // Allow JSON Schema extensions
  validateFormats: true, // Validate format keywords
  allErrors: true, // Report all errors, not just first
});

addFormats(ajv); // Add format validators (uri, email, etc.)

const validateOAS30 = ajv.compile(oas30Schema);

// Validate a document
const valid = validateOAS30(openApiDoc);
if (!valid) {
  console.error(validateOAS30.errors);
}
```

#### For OpenAPI 3.1.x (JSON Schema 2020-12) - Future

```typescript
import Ajv2020 from 'ajv/dist/2020.js';

const oas31Schema = JSON.parse(
  readFileSync(
    '.agent/reference/openapi_schema/openapi_3_1_x_schema_without_validation.json',
    'utf-8',
  ),
);

const ajv = new Ajv2020({
  strict: false,
  validateFormats: true,
  allErrors: true,
});

const validateOAS31 = ajv.compile(oas31Schema);
```

## Consequences

### Positive

✅ **Spec compliance**: Validates against official schemas  
✅ **Early error detection**: Catches spec violations before generation  
✅ **Clear errors**: AJV provides detailed error messages  
✅ **Test infrastructure**: Can validate all test documents  
✅ **Type safety**: Works alongside `openapi3-ts` types  
✅ **Version support**: Can handle multiple OAS versions  
✅ **Performance**: AJV is fast (code generation)

### Negative

⚠️ **CJS/ESM interop**: Required workaround for default exports  
⚠️ **Bundle size**: Adds ~50kb (not a concern for dev/test)  
⚠️ **Multiple AJV versions**: Need different versions for different JSON Schema drafts

### Mitigation

- **Interop handled**: Implemented `.default` fallback pattern
- **Bundle size**: Only used in tests and CLI (not runtime library)
- **Version management**: Clear separation in imports

## Test Infrastructure

### Compliance Test Pattern

```typescript
describe('openapi-spec-compliance', () => {
  let ajv: InstanceType<typeof Ajv04>;
  let validateOAS30: ValidateFunction;

  beforeAll(() => {
    ajv = new Ajv04({
      strict: false,
      validateFormats: true,
      allErrors: true,
    });
    addFormats(ajv);
    validateOAS30 = ajv.compile(oas30Schema);
  });

  test('validates compliant document', async () => {
    const doc: OpenAPIObject = {
      openapi: '3.0.3',
      info: { title: 'Test API', version: '1.0.0' },
      paths: {},
    };

    // Step 1: Validate against official schema
    const valid = validateOAS30(doc);
    expect(valid).toBe(true);

    // Step 2: Verify our code handles it correctly
    await expect(
      generateZodClientFromOpenAPI({
        disableWriteToFile: true,
        openApiDoc: doc,
      }),
    ).resolves.toBeDefined();
  });

  test('rejects invalid document', async () => {
    const doc: OpenAPIObject = {
      openapi: '3.0.3',
      // Missing required 'info' and 'paths'
    } as OpenAPIObject;

    // Step 1: AJV catches the error
    const valid = validateOAS30(doc);
    expect(valid).toBe(false);
    expect(validateOAS30.errors?.[0]?.message).toContain("must have required property 'info'");

    // Step 2: Our code also throws
    await expect(
      generateZodClientFromOpenAPI({
        disableWriteToFile: true,
        openApiDoc: doc,
      }),
    ).rejects.toThrow();
  });
});
```

### Benefits

1. **Double validation**: Both AJV and our code validate
2. **Spec adherence**: Tests prove we follow the spec
3. **Regression prevention**: Catch spec violations in tests
4. **Documentation**: Tests serve as spec examples

## CJS/ESM Interop Pattern

TypeScript issue: `ajv-draft-04` and `ajv-formats` default exports don't work correctly with ESM.

**Solution:**

```typescript
import * as Ajv04Module from "ajv-draft-04";
import * as addFormatsModule from "ajv-formats";

// Handle both CJS and ESM
const Ajv04 = (Ajv04Module as any).default || Ajv04Module;
const addFormats = (addFormatsModule as any).default || addFormatsModule;

// Now works correctly
const ajv: InstanceType<typeof Ajv04> = new Ajv04({ ... });
addFormats(ajv);
```

## Official Schema Files

Stored in `.agent/reference/openapi_schema/`:

- `openapi_3_0_x_schema.json` - OpenAPI 3.0.x (JSON Schema draft-04)
- `openapi_3_1_x_schema_*.json` - OpenAPI 3.1.x (JSON Schema 2020-12)
- `openapi_3_2_x_schema_*.json` - OpenAPI 3.2.x (JSON Schema 2020-12)

**Source**: <https://github.com/OAI/OpenAPI-Specification/tree/main/schemas>

## Future: Validation Mode

Could expose validation as a CLI feature:

```bash
# Future enhancement
$ @engraph/castr validate ./swagger.json
✓ Valid OpenAPI 3.0.3 document
✓ All references resolve
✓ No spec violations

$ @engraph/castr validate ./broken.json
✗ Invalid OpenAPI document
  - Line 42: Parameter missing 'schema' or 'content'
  - Line 89: Invalid $ref: #/components/schemas/Missing
```

## Related Decisions

- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Validates in our code too
- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Types complement validation

## References

- AJV documentation: <https://ajv.js.org>
- Implementation: `lib/tests/openapi-spec-compliance.test.ts`
- Official schemas: `.agent/reference/openapi_schema/`
- JSON Schema specs: <https://json-schema.org/specification>

## Commits

- `eb9faa2` feat(tests): add comprehensive OpenAPI spec compliance tests
- `647a08e` fix: resolve AJV type issues with CJS/ESM interop
