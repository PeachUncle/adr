# ADR-006: TypeScript Strict Mode

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-001 (Inversify DI)](./ADR-001-inversify-dependency-injection.md), [ADR-009 (Zod Validation)](./ADR-009-zod-validation.md)

## Context

The Sovren codebase had inconsistent type safety leading to runtime errors:

- **Runtime Type Errors**: `Cannot read property 'x' of undefined` in production
- **Implicit Any**: 1000+ implicit `any` types hiding bugs
- **Null/Undefined Bugs**: Missing null checks causing crashes
- **Type Assertions**: Unsafe type assertions (`as Type`) masking errors
- **Low Type Coverage**: Only 48% type coverage initially

**Impact**: 15% of production bugs were preventable with proper type checking.

## Decision

We will enforce **TypeScript strict mode** with comprehensive type safety across the entire codebase.

**tsconfig.json**:
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
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

**Key Principles**:
1. Eliminate all `any` types - use `unknown` when type unclear
2. Explicit null handling with optional chaining and nullish coalescing
3. Type guards for runtime type checking
4. Branded types for domain primitives
5. Utility types for type transformations

**Examples**:
```typescript
// Before: Unsafe
function getUser(id: any) {
  return users.find(u => u.id === id);
}
const user = getUser('123');
user.email.toLowerCase(); // Runtime error if user undefined!

// After: Type-safe
function getUser(id: string): User | undefined {
  return users.find(u => u.id === id);
}
const user = getUser('123');
if (user) {
  user.email.toLowerCase(); // Safe!
}

// Or with optional chaining
const email = getUser('123')?.email?.toLowerCase();

// Branded types for domain primitives
type UserId = string & { readonly brand: unique symbol };
type Email = string & { readonly brand: unique symbol };

function createUser(id: UserId, email: Email): User {
  // Can't accidentally pass raw strings
}
```

## Consequences

### Positive

1. **94% Type Coverage Achieved**: Up from 48%
2. **Catch Errors at Compile Time**: 40% reduction in runtime errors
3. **Better IntelliSense**: Accurate autocomplete and refactoring
4. **Self-Documenting Code**: Types serve as documentation
5. **Refactoring Confidence**: TypeScript catches breaking changes

### Negative

1. **Initial Migration Effort**: 200+ hours to fix existing code
2. **Slower Development**: More upfront type definitions required
3. **Learning Curve**: Team needed training on advanced TypeScript

**Why Worth It**: Long-term code quality and maintainability far outweigh initial costs.

## Alternatives Considered

- **Gradual Typing**: Keep `strict: false` - Rejected: Doesn't prevent bugs
- **Flow**: Facebook's type system - Rejected: Less ecosystem support
- **JSDoc**: Comments for types - Rejected: Not enforced at compile time

## Related Documentation

- [TypeScript Migration Report](/docs/type-coverage-report.md)
- [Type Coverage Quick Start](/docs/type-coverage-quick-start.md)
- [Developer Guide - Type Safety](/docs/development/backend-developer-guide.md#type-safety)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
