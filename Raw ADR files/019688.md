# ADR 000: Architecture Goals & Constraints

**Date:** 2025-11-10  
**Status:** ✅ Accepted  
**Deciders:** Development Team  
**Context:** Vale Chronicles architecture rebuild to eliminate technical debt and establish maintainable patterns

---

## Context

The current codebase suffers from:
- 900+ line `GameProvider` god object mixing concerns
- Business logic entangled with React components
- Class-based models difficult to serialize for save/load
- No runtime data validation
- Non-deterministic behavior in battle system
- Difficult to test game logic

We need clear architectural principles to guide the rebuild.

---

## Decision

We commit to the following **non-negotiable architectural principles**:

### 1. React-Free Core (Pure Domain Logic)

**Rule:** `src/core/` contains ZERO React imports.

- ✅ Pure TypeScript functions and types only
- ✅ Deterministic, testable without React
- ✅ Can run in Node.js, tests, or workers
- ❌ No `useState`, `useEffect`, `useContext`, etc.

**Enforcement:** ESLint `import/no-restricted-paths` rule

```typescript
// ✅ ALLOWED in core/
export function calculateDamage(atk: number, def: number): number {
  return Math.max(1, atk - def);
}

// ❌ FORBIDDEN in core/
import { useState } from 'react'; // ERROR: React not allowed
```

### 2. Plain Object Models (No Classes)

**Rule:** All domain models are plain objects (POJOs), not classes.

- ✅ Easy to serialize for save/load
- ✅ Immutable updates with spread operator
- ✅ Type-safe with TypeScript interfaces
- ❌ No `class Unit`, `class Team`, `class Battle`

**Why:** Classes with methods don't serialize well and encourage mutable patterns.

```typescript
// ✅ ALLOWED
export interface Unit {
  readonly id: string;
  readonly name: string;
  readonly level: number;
  readonly stats: Stats;
  readonly equipment: EquipmentLoadout;
}

// ❌ FORBIDDEN
export class Unit {
  equipItem(item: Equipment) {
    this.equipment.weapon = item; // MUTATION!
  }
}
```

### 3. Immutable Updates

**Rule:** Never mutate objects. Always return new objects.

- ✅ Use spread operator: `{ ...unit, level: unit.level + 1 }`
- ✅ React will detect changes correctly
- ✅ Easier to reason about state changes
- ❌ No `unit.level++` or `array.push()`

```typescript
// ✅ CORRECT
export function levelUp(unit: Unit): Unit {
  return {
    ...unit,
    level: unit.level + 1,
    stats: recalculateStats(unit),
  };
}

// ❌ WRONG
export function levelUp(unit: Unit): Unit {
  unit.level++; // MUTATION!
  return unit;
}
```

### 4. Seeded RNG (Deterministic Randomness)

**Rule:** All randomness uses a seedable PRNG, not `Math.random()`.

- ✅ Same seed = same battle outcomes (replay, debug, tests)
- ✅ Can save/load RNG state
- ✅ Golden tests possible with fixed seeds
- ❌ No `Math.random()` in core logic

```typescript
// ✅ CORRECT
export interface PRNG {
  next(): number;
  nextInt(min: number, max: number): number;
  clone(): PRNG;
}

export function calculateCrit(prng: PRNG, luck: number): boolean {
  const roll = prng.next();
  return roll < luck / 100;
}

// ❌ WRONG
export function calculateCrit(luck: number): boolean {
  return Math.random() < luck / 100; // Non-deterministic!
}
```

### 5. Zod = Single Source of Truth

**Rule:** Runtime validation with Zod schemas for ALL game data.

- ✅ Zod schemas define structure
- ✅ TypeScript types derived from schemas: `z.infer<typeof Schema>`
- ✅ Validate at boundaries (startup, save/load, user input)
- ❌ No manual type definitions without validation

```typescript
// ✅ CORRECT
import { z } from 'zod';

export const AbilitySchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  manaCost: z.number().min(0),
  power: z.number().int(),
});

export type Ability = z.infer<typeof AbilitySchema>;

// ❌ WRONG
export interface Ability {
  id: string;
  name: string;
  manaCost: number; // Could be negative!
}
```

### 6. Strict Import Boundaries

**Rule:** Enforce architectural layers with ESLint.

```
ui/        ──→  state/     ──→  core/services/  ──→  core/algorithms/
(React)         (Zustand)       (orchestration)      (pure math)

✅ Allowed: ui/ → state/ → services/ → algorithms/
❌ Forbidden: core/ → ui/, ui/ → core/algorithms/ directly
```

**Layers:**

| Layer | Purpose | Can Import |
|-------|---------|------------|
| `core/models/` | Type definitions | Nothing |
| `core/algorithms/` | Pure calculations | `models/` |
| `core/services/` | Business logic | `models/`, `algorithms/` |
| `core/validation/` | Zod schemas | `models/` |
| `state/` | State management | `core/services/`, `core/models/` |
| `ui/` | React components | `state/`, `core/models/` (types only) |

### 7. Result Type (No Throwing Across Boundaries)

**Rule:** Services return `Result<T, E>` instead of throwing errors.

- ✅ Explicit error handling
- ✅ Type-safe error cases
- ✅ No try/catch noise at boundaries
- ❌ No `throw new Error()` in services

```typescript
// ✅ CORRECT
export function equipItem(
  unit: Unit,
  item: Equipment
): Result<Unit, { code: string; message: string }> {
  if (unit.level < item.requiredLevel) {
    return Err('level_too_low', `Requires level ${item.requiredLevel}`);
  }
  return Ok({ ...unit, equipment: { ...unit.equipment, weapon: item } });
}

// ❌ WRONG
export function equipItem(unit: Unit, item: Equipment): Unit {
  if (unit.level < item.requiredLevel) {
    throw new Error('Level too low'); // Forces try/catch everywhere!
  }
  return { ...unit, equipment: { ...unit.equipment, weapon: item } };
}
```

### 8. No console.* in Production

**Rule:** No `console.log`, `console.error` in production code.

- ✅ Use structured logging/events in dev only
- ✅ CI rejects console.* (ESLint rule)
- ❌ No debug logs in shipped code

```typescript
// ✅ CORRECT (dev only)
if (import.meta.env.DEV) {
  console.log('[EquipmentService] Item equipped:', item.name);
}

// ❌ WRONG
console.log('Equipped:', item); // Leaks to prod!
```

### 9. No `any` in core/**

**Rule:** Strict TypeScript, zero `any` types in core logic.

- ✅ Use `unknown` and type guards instead
- ✅ Leverage Zod for runtime validation
- ❌ No type safety escape hatches

```typescript
// ✅ CORRECT
function processInput(input: unknown): Result<Ability> {
  const result = AbilitySchema.safeParse(input);
  if (!result.success) return Err('invalid_input', result.error.message);
  return Ok(result.data);
}

// ❌ WRONG
function processInput(input: any): Ability {
  return input as Ability; // No validation!
}
```

---

## Consequences

### Positive

- ✅ **Testability:** Core logic testable in isolation without React
- ✅ **Maintainability:** Clear boundaries prevent spaghetti code
- ✅ **Reliability:** Validation catches bugs early
- ✅ **Determinism:** Battles are reproducible with seeds
- ✅ **Type Safety:** Zod + strict TypeScript prevent runtime errors

### Negative

- ⚠️ **Learning Curve:** Team must learn Result types, Zod, PRNG patterns
- ⚠️ **Boilerplate:** More explicit error handling vs try/catch
- ⚠️ **Migration Cost:** Existing code needs significant refactoring

### Risks

- 🔴 **Save Breaking:** May need one-time migration for users
- 🟡 **Performance:** Immutability overhead (mitigated by structural sharing)
- 🟡 **Testing Gaps:** Determinism only works if RNG is injected everywhere

---

## Enforcement Checklist (CI/CD)

Every PR must pass:

- [ ] `npm run typecheck` (TypeScript strict mode)
- [ ] `npm run lint` (ESLint boundaries + no-console + no-any)
- [ ] `npm run test` (Vitest with ≥80% core coverage)
- [ ] `npm run validate:data` (Zod validates all registries)
- [ ] `npm run dep:cycles` (No circular dependencies)
- [ ] `npm run dep:rules` (Import boundaries enforced)

---

## References

- **Result Type Pattern:** [Rust's Result<T, E>](https://doc.rust-lang.org/std/result/)
- **Immutability:** [Immer.js patterns](https://immerjs.github.io/immer/)
- **PRNG:** [xorshift128+](https://en.wikipedia.org/wiki/Xorshift)
- **Zod:** [Official Docs](https://zod.dev/)
- **Boundaries:** [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

## Next ADRs

- **ADR 001:** State Management Strategy (Zustand vs Redux Toolkit)
- **ADR 002:** Save Format & Migration Strategy
- **ADR 003:** Testing Strategy (Unit, Property, Golden, E2E)
