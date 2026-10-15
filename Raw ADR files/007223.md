# ADR-004: Pure Functions and Single Responsibility Principle

## Status

**Accepted** - October 23, 2025

## Context

During Phase 1b of modernization, we addressed cognitive complexity violations in 4 files with complexity scores ranging from 104 to 31 over the threshold. The codebase had large, monolithic functions that were difficult to test, understand, and maintain.

### The Problem

**Before:**

- `openApiToTypescript.ts`: **104 complexity** (main function)
- `getZodiosEndpointDefinitionList.ts`: **47 complexity**, 175-line function
- `schema-complexity.ts`: **33 complexity**
- `getOpenApiDependencyGraph.ts`: **31 complexity**

Large functions with multiple responsibilities:

```typescript
// ❌ 175 lines, does everything
export function getZodiosEndpointDefinitionList(api: OpenAPIObject, ...) {
    // Parse paths
    // Process parameters
    // Handle request bodies
    // Process responses
    // Generate schemas
    // Build endpoint definitions
    // ... 150+ lines of nested logic
}
```

### Forces at Play

**For large functions:**

- Everything in one place
- No function call overhead
- "Simple" to understand the flow

**Against large functions:**

- Hard to test (need full OpenAPI document)
- High cognitive load
- Difficult to reuse logic
- Hard to debug
- Changes affect many concerns at once

## Decision

**We will extract logic into small, pure, single-responsibility functions wherever reasonable.**

### Principles

1. **Pure functions by default**: Same input → same output, no side effects
2. **Single Responsibility**: Each function does ONE thing well
3. **Small functions**: Target < 50 lines, ideally < 30
4. **Domain organization**: Group related helpers in dedicated files
5. **Test each function**: Unit tests for pure functions

### Complexity Thresholds

- **Target**: < 10 cyclomatic complexity (eventual goal)
- **Acceptable**: < 30 cyclomatic complexity (current)
- **Requires refactoring**: ≥ 30 cyclomatic complexity

### Extraction Strategy

When encountering complex functions:

1. **Identify responsibilities**: What distinct things does this do?
2. **Extract helpers**: Pull out each responsibility to a named function
3. **Pure functions first**: Prioritize logic with no side effects
4. **Group by domain**: Create helper files (`.helpers.ts`)
5. **Test helpers**: Write unit tests for each pure function
6. **Simplify main**: Main function orchestrates helpers

### Helper File Naming

```
module-name.ts              # Main implementation
module-name.helpers.ts      # General helpers
module-name.domain.helpers.ts  # Domain-specific helpers (e.g., operation, path)
module-name.helpers.test.ts # Helper tests
module-name.test.ts         # Integration tests
```

## Examples

### Before: Monolithic Function

```typescript
// ❌ 175 lines, complexity 47
export function getZodiosEndpointDefinitionList(api: OpenAPIObject, ...) {
    const endpoints: Endpoint[] = [];

    Object.entries(api.paths ?? {}).forEach(([path, pathItem]) => {
        Object.entries(pathItem ?? {}).forEach(([method, operation]) => {
            // 30 lines: parameter processing
            const parameters = (operation.parameters ?? []).map(param => {
                if (isReferenceObject(param)) {
                    // resolve reference
                }
                const paramSchema = param.schema ? ... : ...;
                // validate, transform, etc.
            });

            // 40 lines: request body processing
            if (operation.requestBody) {
                // extract schema
                // validate content type
                // process schema
            }

            // 50 lines: response processing
            Object.entries(operation.responses ?? {}).forEach(([status, response]) => {
                // extract response schema
                // handle multiple content types
                // process errors
            });

            // 30 lines: build endpoint definition
            endpoints.push({...});
        });
    });

    return endpoints;
}
```

### After: Extracted Functions

```typescript
// ✅ Main function: 26 lines, complexity < 10
export function getZodiosEndpointDefinitionList(api: OpenAPIObject, ...): Endpoint[] {
    const endpoints: Endpoint[] = [];

    Object.entries(api.paths ?? {}).forEach(([path, pathItem]) => {
        const operations = extractOperations(path, pathItem);
        operations.forEach(op => {
            endpoints.push(processOperation(op, ctx));
        });
    });

    return endpoints;
}

// ✅ Pure helper: 15 lines
function extractOperations(path: string, pathItem: PathItemObject): Operation[] {
    return HTTP_METHODS
        .filter(method => pathItem[method])
        .map(method => ({ path, method, operation: pathItem[method]! }));
}

// ✅ Single responsibility: 20 lines
function processOperation(op: Operation, ctx: Context): Endpoint {
    return {
        method: op.method,
        path: op.path,
        parameters: processParameters(op.operation.parameters, ctx),
        requestBody: processRequestBody(op.operation.requestBody, ctx),
        responses: processResponses(op.operation.responses, ctx),
    };
}

// ✅ Focused helper: 10 lines
function processParameters(params: ParameterObject[], ctx: Context): ParamDef[] {
    return params.map(param => processParameter(param, ctx));
}
```

### Helper Files Created

```
lib/src/zodiosEndpoint.helpers.ts              # General helpers (1 function)
lib/src/zodiosEndpoint.operation.helpers.ts    # Operation processing (4 functions)
lib/src/zodiosEndpoint.path.helpers.ts         # Path processing (3 functions)
lib/src/zodiosEndpoint.helpers.test.ts         # 20 unit tests
```

## Consequences

### Positive

✅ **Testability**: Pure functions are easy to unit test  
✅ **Readability**: Small functions with descriptive names  
✅ **Reusability**: Helpers can be used in multiple places  
✅ **Debugging**: Easier to isolate and fix issues  
✅ **Complexity**: Reduced from 104+47+33+31 → all < 30  
✅ **Confidence**: +47 unit tests prove behavior  
✅ **Onboarding**: New developers understand faster

### Negative

⚠️ **More files**: 6 new helper files created  
⚠️ **Navigation**: Need to jump between files  
⚠️ **Abstraction**: Need to understand the decomposition

### Mitigation

- **Clear naming**: Function names explain what they do
- **Co-location**: Helper files next to main files
- **Documentation**: Comments explain why helpers exist
- **IDE support**: Jump-to-definition works well

## Results

### Complexity Reductions

| File                               | Before | After | Reduction  |
| ---------------------------------- | ------ | ----- | ---------- |
| openApiToTypescript.ts             | 104    | < 30  | 74+ points |
| getZodiosEndpointDefinitionList.ts | 47     | < 30  | 17+ points |
| schema-complexity.ts               | 33     | < 30  | 3+ points  |
| getOpenApiDependencyGraph.ts       | 31     | < 30  | 1+ points  |

### Test Coverage

- **Before**: 207 tests
- **After**: 254 tests (+47, +23%)
- **Pure function tests**: 27 for openApiToTypescript, 20 for zodiosEndpoint

### Code Organization

- **Helper functions created**: 36
- **Helper files created**: 6
- **Lines refactored**: ~1000 lines extracted and reorganized

## Related Decisions

- [ADR-003: Type Predicates Over Boolean Filters](./ADR-003-type-predicates-over-boolean-filters.md) - Type predicates are pure functions
- [ADR-005: Enum Complexity Calculation](./ADR-005-enum-complexity-calculation.md) - Uses pure helper functions

## References

- RULES.md Section: "Core Principles" → "Prefer pure functions"
- RULES.md Section: "Single Responsibility Principle"
- `.agent/PHASE1_COMPLETE.md` - Detailed metrics
- Implementation: `lib/src/zodiosEndpoint.*.helpers.ts`
- Tests: `lib/src/zodiosEndpoint.helpers.test.ts`
- Tests: `lib/src/openApiToTypescript.helpers.test.ts`

## Commit

- Multiple commits during Phase 1b refactoring
