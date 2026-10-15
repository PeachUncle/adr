# ADR-005: TypeScript Strict Mode Configuration

## Status

Accepted (Sprint 1)

## Context

TypeScript offers various strictness levels from loose (default) to strict mode. Must decide configuration for game codebase balancing safety vs developer experience.

**Options:**

1. **Default (loose):** `strict: false`, allows `any`, implicit returns, null unsafety
2. **Strict mode:** `strict: true`, enforces all safety checks
3. **Custom:** Pick specific checks to enable

## Decision

Enable full strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true, // Enable all strict checks
    "noImplicitAny": true, // Error on implicit 'any'
    "strictNullChecks": true, // Null safety (no implicit null/undefined)
    "strictFunctionTypes": true, // Function parameter contravariance
    "strictBindCallApply": true, // Type-check bind/call/apply
    "strictPropertyInitialization": true, // Class properties must be initialized
    "noImplicitThis": true, // Error on implicit 'this'
    "alwaysStrict": true, // Emit 'use strict' in JS output

    // Additional strict checks (not part of "strict" flag)
    "noUnusedLocals": true, // Error on unused variables
    "noUnusedParameters": true, // Error on unused function parameters
    "noImplicitReturns": true, // All code paths must return value
    "noFallthroughCasesInSwitch": true // Switch cases must have break/return
  }
}
```

## Rationale

**Why strict mode?**

1. **Catch bugs at compile time** - Null checks, implicit any, unused code
2. **Self-documenting code** - Types serve as documentation
3. **Refactoring confidence** - Compiler catches breaking changes
4. **No runtime `any` types** - Current codebase has 0 `any` types (goal: maintain this)

**Specific checks explained:**

**`strictNullChecks: true`** (most impactful)

```typescript
// Without strictNullChecks (BAD):
function getPlayer() {
  return players[0]; // Could be undefined!
}
const player = getPlayer();
player.x = 100; // Runtime error if undefined!

// With strictNullChecks (GOOD):
function getPlayer(): Player | undefined {
  return players[0];
}
const player = getPlayer();
if (player) {
  // Compiler forces null check
  player.x = 100; // Safe!
}
```

**`noImplicitReturns: true`**

```typescript
// Without check (BAD):
function getScore(level: number) {
  if (level > 10) {
    return level * 100;
  }
  // Missing return! Implicitly returns undefined
}

// With check (GOOD):
function getScore(level: number): number {
  if (level > 10) {
    return level * 100;
  }
  return level * 50; // Compiler forces explicit return
}
```

**`noUnusedLocals: true`**

```typescript
// Without check (messy):
function fireBullet() {
  const player = getPlayer(); // Unused!
  const bulletPool = getBulletPool();
  // ... uses bulletPool only
}

// With check (clean):
function fireBullet() {
  const bulletPool = getBulletPool(); // Compiler catches unused `player`
  // ...
}
```

## Consequences

**Positive:**

- **Fewer runtime errors:** Null checks, type mismatches caught at compile time
- **Self-documenting:** Function signatures show exactly what types are used
- **Refactoring safety:** Compiler catches breaking changes across codebase
- **Code quality:** Forces explicit types, no lazy `any` usage
- **Team alignment:** All contributors follow same strictness level

**Negative:**

- **Steeper learning curve:** New contributors must understand TypeScript strictness
  - _Mitigation:_ CONTRIBUTING.md explains common patterns
- **More verbose:** Null checks add boilerplate (`if (x)` before every access)
  - _Mitigation:_ Use optional chaining (`x?.property`) and nullish coalescing (`x ?? default`)
- **Slower initial development:** Must satisfy compiler before running
  - _Mitigation:_ Type safety prevents runtime bugs, net time savings

## Alternatives Considered

### 1. Loose Mode (Rejected)

```json
{ "strict": false }
// Pros: Faster to write, fewer type errors
// Cons: Runtime errors, implicit any, null unsafety
```

### 2. Custom Strict (Rejected)

Enable only some strict checks (e.g., `strictNullChecks` but not `noUnusedLocals`)
**Pros:** Balance between safety and convenience
**Cons:** Inconsistent strictness, team confusion on what's allowed

### 3. JSDoc with JavaScript (Rejected)

Use JSDoc comments for types without TypeScript compiler
**Pros:** No build step, gradual adoption
**Cons:** No compile-time checks, types not enforced

## Related

- Configuration: `tsconfig.json`
- Type definitions: `src/types/index.ts`
- Contributing guide: `CONTRIBUTING.md` (explains TypeScript usage)
