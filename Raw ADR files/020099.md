# ADR 005: Enforce TypeScript Strict Mode

**Status:** Accepted

**Date:** 2025-10-18

**Context:**

WCAG Explorer is built with TypeScript, which offers a spectrum of type-checking strictness from lenient to very strict. We needed to decide on the TypeScript configuration that would:

- Catch bugs at compile time
- Improve code quality and maintainability
- Balance safety with development velocity
- Work well with React and third-party libraries
- Be sustainable for current and future team members

TypeScript's `strict` flag enables several compiler options:
- `noImplicitAny` - Error on implicit any types
- `strictNullChecks` - null and undefined are not assignable to other types
- `strictFunctionTypes` - Function parameter types are checked contravariantly
- `strictBindCallApply` - Check bind, call, and apply methods
- `strictPropertyInitialization` - Class properties must be initialized
- `noImplicitThis` - Error on this with implicit any type
- `alwaysStrict` - Parse in strict mode and emit "use strict"
- `useUnknownInCatchVariables` - Catch variables are unknown instead of any

**Decision:**

We will enable **TypeScript strict mode** for the entire WCAG Explorer codebase.

Configuration in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "useUnknownInCatchVariables": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**Consequences:**

### Positive

1. **Early Bug Detection:**
   - Null/undefined errors caught at compile time
   - Type mismatches prevented before runtime
   - Catches common mistakes like typos in property names

2. **Better IDE Support:**
   - More accurate autocomplete suggestions
   - Better refactoring capabilities
   - Inline error detection while typing

3. **Self-Documenting Code:**
   - Function signatures show exactly what types are expected
   - No guessing about whether null/undefined are valid
   - Types serve as living documentation

4. **Safer Refactoring:**
   - Changes propagate through type system
   - Breaking changes are immediately visible
   - Confidence when modifying shared code

5. **Fewer Runtime Errors:**
   - "Cannot read property 'x' of undefined" largely eliminated
   - Type-safe access to nested properties
   - Prevents passing wrong data to functions

6. **Better Error Messages:**
   - TypeScript errors are clear and actionable
   - IDE shows exactly where type mismatches occur
   - Stack traces are cleaner (fewer runtime type errors)

7. **Team Consistency:**
   - All code follows same type standards
   - No ambiguity about whether to use types
   - New team members inherit safety

8. **WCAG Data Integrity:**
   - Criterion objects have guaranteed shape
   - Filters are type-safe
   - API responses match expected types

### Negative

1. **Initial Learning Curve:**
   - Team members must understand TypeScript deeply
   - More complex type signatures in some cases
   - Need to learn handling of null/undefined properly

2. **More Verbose Code:**
   - Explicit type annotations sometimes required
   - Null checks necessary throughout code
   - Cannot rely on implicit any as escape hatch

3. **Slower Initial Development:**
   - Must fix type errors before code compiles
   - Cannot "just run it" to test ideas
   - More time thinking about types upfront

4. **Third-Party Library Issues:**
   - Some libraries have poor or missing type definitions
   - May need to write custom .d.ts files
   - Sometimes need to use type assertions as workaround

5. **Complex Generic Types:**
   - Some React patterns become more verbose
   - Higher-order components require careful typing
   - Conditional types can be hard to read

6. **Strictness Friction:**
   - Type guards needed for narrowing
   - Explicit checks for null/undefined
   - Cannot assign potentially undefined to required fields

### Examples

**Before strict mode (unsafe):**
```typescript
function getLevel(criterion) {  // implicit any
  return criterion.level;  // might be undefined
}

const results = criteria.find(c => c.id === id);
const level = results.level;  // no error even if results is undefined
```

**After strict mode (safe):**
```typescript
function getLevel(criterion: Criterion): WcagLevel {
  return criterion.level;  // typed, guaranteed to exist
}

const results = criteria.find(c => c.id === id);
const level = results?.level;  // TypeScript enforces optional chaining
// or
if (results) {
  const level = results.level;  // type narrowed to Criterion
}
```

**Null handling:**
```typescript
// Before: runtime error waiting to happen
function toggleFavorite(id) {
  favorites.delete(id);
}

// After: explicit null checking
function toggleFavorite(id: string | undefined): void {
  if (!id) return;  // type guard required
  favorites.delete(id);
}
```

**API types:**
```typescript
// Strong typing for API responses
export interface PaginatedResult<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export async function getCriteria(
  filters: QueryFilters
): Promise<PaginatedResult<Criterion>> {
  // TypeScript ensures return type matches
}
```

**Alternatives Considered:**

### Loose TypeScript (strict: false)
- **Pros:**
  - Faster initial development
  - Easier migration from JavaScript
  - Less friction with third-party libraries
- **Cons:**
  - Loses primary benefits of TypeScript
  - Type errors slip through to runtime
  - Code is less maintainable
- **Reason for rejection:** Using TypeScript without strict mode misses most of its value. Would be better to use JavaScript if not going strict.

### Gradual Strictness (per-file)
- **Pros:**
  - Can enable strict mode incrementally
  - Less disruptive for existing codebases
  - Each file opts in with `// @ts-strict`
- **Cons:**
  - Inconsistent codebase
  - Easy to forget enabling strict mode
  - Type issues at boundaries between strict/non-strict
- **Reason for rejection:** WCAG Explorer is a new project, so no migration burden. Better to start strict from the beginning.

### ESLint Type Rules Instead
- **Pros:**
  - More flexible than compiler
  - Can have warnings instead of errors
  - Easier to disable specific rules
- **Cons:**
  - Doesn't provide compile-time safety
  - Can be ignored or disabled
  - Not as comprehensive as TypeScript's checking
- **Reason for rejection:** Complementary to TypeScript, not a replacement. We use both.

### TypeScript + Zod for Runtime Validation
- **Pros:**
  - Compile-time and runtime type safety
  - Validates external data (API responses)
  - Single source of truth for types
- **Cons:**
  - Additional dependency
  - More boilerplate for schemas
  - Performance overhead for validation
- **Reason for rejection:** Not needed yet. API is trusted (same team maintains it). Could add later if integrating with external APIs.

**Migration Strategy:**

Since this is a new project, strict mode was enabled from the start. For future developers:

1. **Never disable strict mode** - If struggling with types, improve the types rather than disabling checks
2. **Avoid `any` escapes** - Use `unknown` and type guards instead
3. **Handle null/undefined explicitly** - Use optional chaining `?.` and nullish coalescing `??`
4. **Use type guards** - Write small functions to narrow types safely
5. **Trust the compiler** - If TypeScript says there's an error, there's likely a real issue

**Handling Common Patterns:**

### Optional Props
```typescript
interface Props {
  criterion: Criterion;
  className?: string;  // optional
  onToggleFavorite?: () => void;  // optional callback
}

// Use optional chaining and defaults
<div className={className ?? 'default-class'} />
<button onClick={onToggleFavorite ?? (() => {})}>
```

### Array Methods
```typescript
// find() returns T | undefined
const criterion = criteria.find(c => c.id === id);
if (criterion) {
  // TypeScript knows criterion is defined here
  doSomething(criterion);
}
```

### Event Handlers
```typescript
// Type the event parameter
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};
```

### Catch Blocks
```typescript
try {
  await fetchData();
} catch (err) {
  // err is unknown in strict mode
  const errorMsg = err instanceof Error ? err.message : 'Unknown error';
  setError(errorMsg);
}
```

**Notes:**

- Strict mode is non-negotiable for WCAG Explorer
- Type safety is especially important for accessibility-focused applications (wrong types could break AT)
- The upfront investment in types pays off quickly
- Most runtime bugs in JavaScript come from type issues that TypeScript prevents
