# Design: Adapter Base Class Implementation

## Context

This is the core foundation of the `nest-hex` library. The Adapter base class must provide a reusable pattern for creating NestJS dynamic modules that implement the Ports & Adapters (Hexagonal Architecture) pattern.

**Key stakeholders:**
- Library consumers who will extend this class to create adapters
- Feature module authors who will receive `AdapterModule<TToken>` instances

**Constraints:**
- Must be compatible with NestJS dynamic module system
- Must enforce TypeScript strict mode and isolated declarations
- Must support both sync and async configuration patterns
- Zero runtime dependencies (NestJS is peer dependency)

## Goals / Non-Goals

**Goals:**
- Eliminate boilerplate for creating adapter modules
- Provide type-safe token binding at compile time
- Support both `register()` and `registerAsync()` patterns
- Auto-handle provider registration, aliasing, and exports
- Enable declarative token binding via `forToken()` helper

**Non-Goals:**
- Feature module implementation (separate change)
- Example adapters (documentation concern)
- Testing utilities (future enhancement)
- Runtime validation of tokens (TypeScript provides compile-time safety)

## Decisions

### Decision 1: Abstract Base Class Pattern

**What:** Use an abstract base class with protected abstract properties and static methods.

**Why:**
- Enables inheritance-based API (natural for class-based NestJS modules)
- Static methods (`register()`, `registerAsync()`, `forToken()`) provide clean API
- Abstract properties enforce required configuration (token, implementation)
- Allows optional hooks (`imports()`, `extraPoviders()`) for customization

**Alternatives considered:**
- Function factories: Rejected - less natural for NestJS, harder to extend
- Decorators: Rejected - doesn't fit dynamic module pattern, adds complexity
- Mixins: Rejected - TypeScript support is complex, harder to document

### Decision 2: `AdapterModule<TToken>` Type with `__provides` Field

**What:** Define `AdapterModule<TToken>` as `DynamicModule & { __provides: TToken }`

**Why:**
- Provides compile-time proof that an adapter provides a specific token
- Enables type-safe feature module registration (compile error if wrong adapter)
- The `__provides` field is for structural typing only (not used at runtime)
- Leverages TypeScript's structural type system without runtime overhead

**Alternatives considered:**
- Branded types with unique symbols: Rejected - adds complexity, same result
- Generic constraints only: Rejected - doesn't provide compile-time token proof
- Runtime token registry: Rejected - violates zero runtime dependency goal

### Decision 3: `forToken()` Declarative Helper

**What:** Provide static `Adapter.forToken(TOKEN)` that returns a base class with token pre-bound.

**Why:**
- Declare token once in class definition, not in constructor or methods
- Reads naturally: `class S3Adapter extends Adapter.forToken(STORAGE_TOKEN)<Options> {}`
- Eliminates repetition of token binding in every adapter
- TypeScript infers the token type automatically

**Alternatives considered:**
- Constructor injection: Rejected - tokens should be constant, not injected
- Decorator: Rejected - doesn't fit NestJS dynamic module pattern
- Manual token property: Works but verbose, easy to forget

### Decision 4: Optional `imports()` and `extraPoviders()` Hooks

**What:** Protected methods that adapters can override to customize module configuration.

**Why:**
- `imports()`: Allows adapters to import other NestJS modules (e.g., HttpModule, ConfigModule)
- `extraPoviders()`: Enables initialization logic, helper services, options providers
- Optional: Most adapters won't need them, but power users can extend behavior
- Receives options as parameter for dynamic configuration

**Alternatives considered:**
- Abstract methods: Rejected - most adapters don't need them, would require boilerplate
- Configuration objects: Rejected - less flexible than code-based hooks
- Separate lifecycle methods: Rejected - over-engineering for initial version

### Decision 5: `register()` vs `registerAsync()` Implementation

**What:**
- `register(options)`: Sync registration, receives plain options object
- `registerAsync({ imports, inject, useFactory })`: Async registration with DI

**Why:**
- Follows established NestJS pattern (ConfigModule, TypeOrmModule, etc.)
- `register()` is simpler for most use cases (app provides resolved config)
- `registerAsync()` enables DI-based configuration when needed
- Both return `AdapterModule<TToken>` for type safety

**Implementation note:**
- `registerAsync()` passes empty options `{}` to `extraPoviders()` in base implementation
- Adapters needing DI-resolved options should create their own options token in `extraPoviders()`

## Risks / Trade-offs

### Risk: `registerAsync()` with `extraPoviders()` complexity

**Risk:** Adapters using both `registerAsync()` and `extraPoviders()` may need custom options tokens.

**Mitigation:**
- Document pattern in JSDoc comments
- Recommend keeping adapter options sync when possible
- Provide example in spec.md (S3 adapter uses `init()` pattern)

**Trade-off:** Simplicity for common case vs flexibility for advanced cases. We choose simplicity.

### Risk: `__provides` field is runtime overhead

**Risk:** Every adapter module carries an extra field in the returned object.

**Mitigation:**
- Field is used for structural typing only, not runtime logic
- TypeScript erases types at runtime, but the field itself is minimal
- Alternative (branded types) has same or worse runtime characteristics

**Trade-off:** Tiny runtime overhead vs compile-time type safety. We choose type safety.

### Risk: Abstract class limits composition

**Risk:** Single inheritance means adapters can't extend other base classes.

**Mitigation:**
- Use composition for shared behavior (inject services instead of inheriting)
- Document this limitation in public API docs
- Most adapters won't need multiple inheritance

**Trade-off:** Inheritance simplicity vs composition flexibility. We choose simplicity for v1.

## Migration Plan

**N/A** - This is the initial implementation, no migration needed.

**Future considerations:**
- If we add runtime validation, it should be opt-in
- If we add more lifecycle hooks, they should be optional (backward compatible)
- Breaking changes should follow semver (major version bump)

## Open Questions

None - the spec.md provides complete implementation guidance.
