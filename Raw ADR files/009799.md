# ADR-003: Create Service Layer

**Status:** ✅ Accepted and Implemented  
**Date:** 2025-10-09  
**Phase:** Phase 3 - Create Service Layer

---

## Context

After extracting types, constants, and utilities in Phases 1-2, the DrawingCanvas.tsx component still contained 971 lines with domain logic mixed with UI concerns. While utilities provided pure functions, there was no layer to orchestrate business logic and maintain data contracts between the UI and utility layers.

### Problems Identified

1. **Mixed Concerns:** Domain logic (line management, snap detection) mixed with UI rendering
2. **No Data Contracts:** No clear interfaces for domain operations
3. **Direct Utility Usage:** Components called utilities directly, creating tight coupling
4. **Difficult Testing:** Domain logic couldn't be tested without rendering components
5. **Poor Abstraction:** No layer to encapsulate complex multi-step operations

---

## Decision

We decided to create a service layer that encapsulates domain logic and provides clean interfaces between hooks and utilities:

### Service Organization (`src/services/`)

**Drawing Services (`drawing/`):**
- `DrawingService.ts` - Line creation, validation, length calculation
- `LineManager.ts` - Line collection management (add, remove, update)
- `index.ts` - Barrel export

**Viewport Services (`viewport/`):**
- `ViewportService.ts` - Zoom, pan, coordinate transformation
- `index.ts` - Barrel export

**Service Layer Principles:**
- **Stateless:** Services don't maintain state (hooks do that)
- **Pure Interfaces:** Clear input/output contracts
- **Utility Orchestration:** Services compose utilities for complex operations
- **Domain Focus:** Each service handles one domain concern

---

## Consequences

### Positive

✅ **Clear Separation:** Domain logic separated from UI concerns  
✅ **Testable:** Services can be unit tested in isolation (50 tests, ~100% coverage)  
✅ **Reusable:** Services can be used by multiple hooks or components  
✅ **Maintainable:** Changes to domain logic are localized to services  
✅ **Clean Interfaces:** Well-defined contracts between layers  
✅ **Dependency Flow:** Enforced architecture (Components → Hooks → Services → Utils)

### Negative

🟡 **Additional Layer:** Adds complexity with another abstraction layer  
🟡 **More Files:** Created 9 new files (6 service files, 3 test files)  
🟡 **Learning Curve:** Developers need to understand when to use services vs. utilities

### Neutral

- **No Runtime Impact:** Service layer is just function calls, no performance overhead
- **No Behavior Change:** Functionality remains identical
- **Medium-Low Risk:** Careful testing ensures correctness

---

## Alternatives Considered

### 1. Skip Service Layer, Use Utilities Directly
**Rejected:** Would create tight coupling between hooks and utilities; no place for domain logic

### 2. Use Class-Based Services
**Rejected:** Functional approach is simpler and more testable; no need for instance state

### 3. Combine Services with Hooks
**Rejected:** Would mix stateful and stateless logic; harder to test

### 4. Create More Granular Services
**Rejected:** Current granularity (drawing, viewport) is appropriate for this application

---

## Implementation Details

### DrawingService Example

**Before (inline in component):**
```typescript
const createLine = (start: Pt, end: Pt) => {
  const length = dist(start, end);
  if (length < MIN_LINE_LENGTH) return null;
  return {
    id: uid(),
    start,
    end,
    width: currentWidth,
    color: LINE_COLOR,
  };
};
```

**After (service with tests):**
```typescript
// src/services/drawing/DrawingService.ts
/**
 * Create a new line with validation
 * @param start - Start point
 * @param end - End point
 * @param width - Line width
 * @returns New line or null if invalid
 */
export function createLine(start: Pt, end: Pt, width: number): Line | null {
  const length = calculateLineLength(start, end);
  if (length < MIN_LINE_LENGTH) return null;
  
  return {
    id: uid(),
    start,
    end,
    width,
    color: LINE_COLOR,
  };
}

// src/services/__tests__/DrawingService.test.ts
describe('createLine', () => {
  it('should create valid line', () => {
    const line = createLine({ x: 0, y: 0 }, { x: 100, y: 0 }, 8);
    expect(line).not.toBeNull();
    expect(line?.width).toBe(8);
  });
  
  it('should return null for short line', () => {
    const line = createLine({ x: 0, y: 0 }, { x: 1, y: 0 }, 8);
    expect(line).toBeNull();
  });
});
```

### LineManager Example

**Before (inline state management):**
```typescript
const addLine = (line: Line) => {
  setLines([...lines, line]);
};

const removeLine = (id: string) => {
  setLines(lines.filter(l => l.id !== id));
};
```

**After (service with immutable operations):**
```typescript
// src/services/drawing/LineManager.ts
/**
 * Add a line to the collection
 * @param lines - Current lines
 * @param line - Line to add
 * @returns New lines array
 */
export function addLine(lines: Line[], line: Line): Line[] {
  return [...lines, line];
}

/**
 * Remove a line by ID
 * @param lines - Current lines
 * @param id - Line ID to remove
 * @returns New lines array without the line
 */
export function removeLine(lines: Line[], id: string): Line[] {
  return lines.filter(l => l.id !== id);
}

// Tests ensure immutability and correctness
```

### ViewportService Example

```typescript
// src/services/viewport/ViewportService.ts
/**
 * Calculate new zoom level
 * @param currentZoom - Current zoom level
 * @param direction - Zoom direction ('in' or 'out')
 * @returns New zoom level clamped to min/max
 */
export function calculateZoom(
  currentZoom: number,
  direction: 'in' | 'out'
): number {
  const newZoom = direction === 'in'
    ? currentZoom * ZOOM_FACTOR
    : currentZoom / ZOOM_FACTOR;
  
  return Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom));
}

// Comprehensive tests for edge cases (min/max bounds, precision)
```

---

## Architecture Enforcement

### Dependency Flow Rules

```
Components
    ↓ (use)
Hooks
    ↓ (use)
Services
    ↓ (use)
Utils
    ↓ (use)
Types & Constants
```

**Enforced Rules:**
- ✅ Services can import from Utils, Types, Constants
- ❌ Services cannot import from Hooks or Components
- ✅ Services are stateless (no React hooks)
- ✅ Services have clear input/output contracts

---

## Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| DrawingCanvas.tsx Lines | 971 | 971 | 0 (services created, not yet integrated) |
| Total Files | 31 | 40 | +9 |
| Service Modules | 0 | 3 | +3 |
| Service Tests | 0 | 50 | +50 |
| Test Coverage (Services) | 0% | ~100% | +100% |
| Bundle Size | 160.01 KB | 160.01 KB | 0 KB |

---

## Testing Strategy

### Test Organization
```
src/services/__tests__/
├── DrawingService.test.ts (13 tests)
├── LineManager.test.ts (18 tests)
└── ViewportService.test.ts (19 tests)
```

### Coverage Targets
- **DrawingService:** 100% (all validation paths tested)
- **LineManager:** 100% (all CRUD operations tested)
- **ViewportService:** 100% (all transformations tested)

### Test Patterns
- **Pure Function Testing:** Easy to test with simple input/output assertions
- **Edge Case Coverage:** Min/max bounds, null values, empty arrays
- **Immutability Verification:** Ensure original data not mutated

---

## Lessons Learned

1. **Service Layer Value:** Provides clean abstraction between UI and business logic
2. **Stateless Services:** Keeping services stateless makes them easy to test and reason about
3. **Clear Contracts:** Well-defined interfaces improve maintainability
4. **Test Coverage:** 100% coverage for services provides confidence
5. **Dependency Flow:** Enforcing architecture prevents circular dependencies

---

## Related ADRs

- **ADR-001:** Extract Types & Constants (provides types for service interfaces)
- **ADR-002:** Extract Utility Functions (services compose utilities)
- **ADR-004:** Extract Custom Hooks (hooks use services for domain logic)
- **ADR-005:** Extract UI Components (components use hooks, not services directly)

---

## References

- Phase 3 Summary: `docs/phases/PHASE_3_SUMMARY.md`
- Service Layer: `src/services/`
- Service Tests: `src/services/__tests__/`
- Refactor Scorecard: `docs/REFACTOR_SCORECARD.md`

