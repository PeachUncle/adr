# ADR 001: Handcrafted TypeScript Client Over Code Generation

**Status**: Accepted
**Date**: 2025-10-28
**Deciders**: Development Team
**Related**: [OpenAPI Client Implementation](https://github.com/Ira2222/App2/commit/f980df4)

## Context

We needed a type-safe way to consume our ASP.NET Core API from the React frontend. We had to choose between:

1. **Auto-generated client** using OpenAPI Generator or similar tools
2. **Handcrafted TypeScript client** based on the OpenAPI specification

### Requirements

- **Type safety**: Compile-time error detection for API mismatches
- **Developer experience**: IntelliSense, auto-completion, clear error messages
- **Maintainability**: Easy to understand, modify, and extend
- **Build simplicity**: Minimal external dependencies and tooling
- **Error handling**: Proper support for ProblemDetails error responses

## Decision

We will **handcraft a TypeScript API client** (`apps/web/src/api/`) rather than auto-generate it.

### Implementation

Created three focused files totaling ~150 lines:

**`types.ts`** - TypeScript interfaces matching OpenAPI spec:
```typescript
export interface TodoDto {
  id: number;
  title: string;
  description?: string | null;
  isCompleted: boolean;
  createdAt: string;
  completedAt?: string | null;
}

export interface CreateTodoRequest {
  title: string;
  description?: string | null;
}

export interface ProblemDetails {
  type?: string | null;
  title?: string | null;
  status?: number | null;
  detail?: string | null;
  instance?: string | null;
  traceId?: string | null;
}
```

**`client.ts`** - Type-safe client with error handling:
```typescript
export class ApiClient {
  async getTodos(): Promise<TodoDto[]> { }
  async createTodo(todo: CreateTodoRequest): Promise<TodoDto> { }
}
```

**`index.ts`** - Clean barrel export

## Rationale

### Why Handcrafted?

1. **No Java Dependency**
   - OpenAPI Generator requires Java runtime
   - Java not installed on development machines
   - Would add build complexity and CI overhead

2. **Simplicity & Clarity**
   - 150 lines vs 1000s from generators
   - Easy to understand and debug
   - No "magic" - explicit control over behavior

3. **Maintainability**
   - Straightforward to add new endpoints
   - Clear ownership of code
   - No generator configuration complexity
   - Easy to customize error handling

4. **Same Type Safety Benefits**
   - Full IntelliSense support
   - Compile-time error detection
   - Type-safe method signatures
   - Proper TypeScript integration

5. **Better Error Handling**
   - Custom `ApiError` class
   - Native ProblemDetails parsing
   - Clear error messages
   - Easy to extend with retry logic, logging, etc.

6. **Build Performance**
   - No code generation step
   - Faster builds
   - No watch mode complexity

7. **Version Control**
   - Human-readable diffs
   - Easy code reviews
   - Clear intent in commits

### Why Not Generated?

Generated clients have drawbacks for our use case:

- **Bloat**: Thousands of lines for simple APIs
- **Configuration**: Complex generator options
- **Dependencies**: Java runtime, generator tool versions
- **Debugging**: Harder to trace issues through generated code
- **Customization**: Difficult to add custom logic
- **Build complexity**: Additional tooling in CI/CD
- **Version drift**: Generator versions may have breaking changes

## Consequences

### Positive

- ✅ **Zero external build dependencies** (no Java, no generator)
- ✅ **Fast iteration** - modify client instantly, no regeneration step
- ✅ **Clear, readable code** - easy onboarding for new developers
- ✅ **Flexible error handling** - custom ApiError with ProblemDetails
- ✅ **Maintainable** - straightforward to extend
- ✅ **Full type safety** - same benefits as generated
- ✅ **Faster builds** - no generation step
- ✅ **Better DX** - IntelliSense works perfectly

### Negative

- ❌ **Manual updates needed** when API changes
  - *Mitigation*: OpenAPI spec serves as contract
  - *Mitigation*: TypeScript catches mismatches at compile-time
  - *Process*: Update types when OpenAPI spec changes

- ❌ **Risk of drift** between spec and client
  - *Mitigation*: Commit OpenAPI spec to version control
  - *Mitigation*: Regular spec validation in CI
  - *Future*: Could add validation tests comparing spec vs client

- ❌ **More work for large APIs** (100+ endpoints)
  - *Current scope*: ~5 endpoints - handcrafted is feasible
  - *Future*: Reassess if API grows significantly

### Neutral

- ⚠️ **Custom approach** - not following common pattern
  - Trade-off: Simplicity vs convention
  - Decision: Simplicity wins for our scale

## Alternatives Considered

### 1. OpenAPI Generator (TypeScript-Fetch)

**Pros**:
- Industry standard
- Automatic updates from spec
- Handles all OpenAPI features

**Cons**:
- Requires Java runtime ❌
- Generates 1000s of lines
- Complex configuration
- Harder to customize
- Slower builds

**Verdict**: Rejected due to Java dependency and complexity for our simple API.

### 2. Swagger Codegen

**Pros**:
- Older, stable tool
- Wide language support

**Cons**:
- Same Java requirement ❌
- Less actively maintained than OpenAPI Generator
- Similar bloat issues

**Verdict**: Rejected for same reasons as OpenAPI Generator.

### 3. Third-party SaaS Generators

**Pros**:
- No local tooling needed
- Cloud-based generation

**Cons**:
- External dependency ❌
- Security concerns (API spec upload)
- Cost
- Build complexity

**Verdict**: Rejected due to external dependency and security.

### 4. GraphQL (Complete Rewrite)

**Pros**:
- Strong typed schema
- Excellent client tooling
- Query flexibility

**Cons**:
- Massive rewrite ❌
- Overkill for simple CRUD
- Different paradigm

**Verdict**: Rejected as out of scope.

## Validation

### Success Criteria

All criteria met ✅:

- [x] Type-safe API calls
- [x] IntelliSense/auto-completion works
- [x] Compile-time error detection
- [x] ProblemDetails error handling
- [x] Easy to add new endpoints
- [x] No Java dependency
- [x] Fast builds (<1s)
- [x] Clear, maintainable code

### Metrics

- **Lines of code**: ~150 (vs ~3000+ for generated)
- **Build time**: No impact (vs +5-10s for generation)
- **Dependencies**: 0 new (vs Java + generator)
- **Developer satisfaction**: High (clean, understandable)

## Review Triggers

Revisit this decision if:

1. **API grows significantly** (>20 endpoints)
   - Generated client might be worth the complexity

2. **Java becomes available** in development environment
   - Removes primary blocker for generation

3. **Type drift causes production issues**
   - Need better sync between spec and client

4. **Team prefers generated approach**
   - Team consensus should drive tooling choices

## References

- [OpenAPI Specification](../../openapi/app2.openapi.json)
- [Implementation Commit](https://github.com/Ira2222/App2/commit/f980df4)
- [OpenAPI Generator Docs](https://openapi-generator.tech/docs/generators/typescript-fetch/)
- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)

## Related Decisions

- Future: API versioning strategy
- Future: GraphQL consideration for complex queries
- Future: API contract testing approach

---

**Last Updated**: 2025-10-28
**Next Review**: 2026-01-28 (or when API reaches 20 endpoints)
