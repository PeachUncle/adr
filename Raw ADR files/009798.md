# ADR-002: Extract Utility Functions

**Status:** ✅ Accepted and Implemented  
**Date:** 2025-10-09  
**Phase:** Phase 2 - Extract Utility Functions

---

## Context

After extracting types and constants in Phase 1, the DrawingCanvas.tsx component still contained 1,155 lines with numerous pure functions performing calculations for geometry, coordinate transformations, snap detection, and scale conversions. These functions were:

- Mixed with stateful component logic
- Difficult to test in isolation
- Not reusable across modules
- Lacking comprehensive test coverage

### Problems Identified

1. **Testability:** Pure functions embedded in component couldn't be unit tested without rendering the component
2. **Reusability:** Utility logic couldn't be shared with other components or services
3. **Complexity:** Component file was too large and handled too many concerns
4. **Maintainability:** Changes to utility logic required navigating a 1,155-line file
5. **No Test Coverage:** 0% unit test coverage for utility functions

---

## Decision

We decided to extract all pure functions into domain-organized utility modules with comprehensive unit tests:

### Utility Organization (`src/utils/`)

**Geometry Utilities (`geometry/`):**
- `points.ts` - Point distance calculations
- `lines.ts` - Line segment operations (distance to point, closest point)
- `index.ts` - Barrel export

**Canvas Utilities (`canvas/`):**
- `coordinates.ts` - Coordinate transformations (screen ↔ canvas)
- `rendering.ts` - Canvas rendering setup (HiDPI, viewport transform)
- `index.ts` - Barrel export

**Snap Utilities (`snap/`):**
- `snapDetection.ts` - Snap target detection logic
- `index.ts` - Barrel export

**Scale Utilities (`scale/`):**
- `scaleConversion.ts` - Pixel to unit conversions
- `index.ts` - Barrel export

**General Utilities:**
- `id.ts` - Unique ID generation

### Testing Strategy

- **Unit Tests:** Comprehensive tests for all utility functions
- **Coverage Target:** ≥80% for all utilities
- **Test Organization:** Mirror source structure in `__tests__/` directory
- **Test Framework:** Vitest for fast, modern testing

---

## Consequences

### Positive

✅ **High Testability:** All utilities can be unit tested in isolation  
✅ **95% Test Coverage:** Achieved ~95% coverage for utilities (51 tests)  
✅ **Improved Reusability:** Utilities can be imported by services, hooks, and components  
✅ **Better Organization:** Domain-based structure makes utilities easy to find  
✅ **Reduced Complexity:** Removed 184 lines from DrawingCanvas.tsx  
✅ **Documentation:** JSDoc comments explain function purpose and usage  
✅ **Fast Tests:** Unit tests run in ~2ms per test suite

### Negative

🟡 **More Files:** Created 17 new files (12 utility files, 5 test files)  
🟡 **Import Overhead:** Component now imports utilities instead of using inline functions  
🟡 **Test Maintenance:** 51 tests need to be maintained

### Neutral

- **No Runtime Impact:** Pure function extraction doesn't affect performance
- **No Behavior Change:** All functionality remains identical
- **Low Risk:** Pure functions are safe to extract and test

---

## Alternatives Considered

### 1. Keep Functions Inline
**Rejected:** Would prevent unit testing and maintain high complexity

### 2. Single utils.ts File
**Rejected:** Would create a large, unorganized file; domain organization is clearer

### 3. Co-locate with Components
**Rejected:** Utilities should be independent of UI concerns

### 4. Use Class-Based Utilities
**Rejected:** Functional approach is simpler and more testable

---

## Implementation Details

### Geometry Utility Example

**Before (inline):**
```typescript
function dist(a: Pt, b: Pt): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  return Math.sqrt(dx * dx + dy * dy);
}
```

**After (extracted with tests):**
```typescript
// src/utils/geometry/points.ts
/**
 * Calculate Euclidean distance between two points
 * @param a - First point
 * @param b - Second point
 * @returns Distance between points
 */
export function dist(a: Pt, b: Pt): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  return Math.sqrt(dx * dx + dy * dy);
}

// src/utils/__tests__/geometry.test.ts
describe('dist', () => {
  it('should calculate distance between two points', () => {
    expect(dist({ x: 0, y: 0 }, { x: 3, y: 4 })).toBe(5);
  });
});
```

### Coordinate Transformation Example

**Before (inline):**
```typescript
function screenToCanvas(screenPt: Pt, transform: ViewportTransform): Pt {
  return {
    x: (screenPt.x - transform.offset.x) / transform.scale,
    y: (screenPt.y - transform.offset.y) / transform.scale,
  };
}
```

**After (extracted with comprehensive tests):**
```typescript
// src/utils/canvas/coordinates.ts
/**
 * Transform screen coordinates to canvas coordinates
 * @param screenPt - Point in screen space
 * @param transform - Viewport transformation
 * @returns Point in canvas space
 */
export function screenToCanvas(screenPt: Pt, transform: ViewportTransform): Pt {
  return {
    x: (screenPt.x - transform.offset.x) / transform.scale,
    y: (screenPt.y - transform.offset.y) / transform.scale,
  };
}

// Tests cover: identity transform, scaled transform, offset transform, combined transform
```

---

## Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| DrawingCanvas.tsx Lines | 1,155 | 971 | -184 (-16%) |
| Total Files | 14 | 31 | +17 |
| Utility Functions | Inline | 12 modules | Organized |
| Unit Tests | 0 | 51 | +51 |
| Test Coverage (Utils) | 0% | ~95% | +95% |
| Bundle Size | 159.91 KB | 160.01 KB | +0.1 KB |

---

## Testing Strategy Details

### Test Organization
```
src/utils/__tests__/
├── geometry.test.ts (13 tests)
├── canvas.test.ts (10 tests)
├── snap.test.ts (9 tests)
├── scale.test.ts (14 tests)
└── id.test.ts (5 tests)
```

### Coverage Targets
- **Geometry:** 100% (all edge cases covered)
- **Canvas:** 95% (HiDPI setup has browser-specific code)
- **Snap:** 100% (all snap types tested)
- **Scale:** 100% (all scale types tested)
- **ID:** 100% (simple function, fully covered)

---

## Lessons Learned

1. **Test First Mindset:** Writing tests revealed edge cases not considered in original implementation
2. **Domain Organization:** Grouping by domain (geometry, canvas, snap, scale) is intuitive
3. **Pure Functions Win:** Pure functions are easy to test and reason about
4. **Comprehensive Tests:** High coverage (95%) provides confidence for future refactoring
5. **Fast Feedback:** Vitest provides instant feedback during development

---

## Related ADRs

- **ADR-001:** Extract Types & Constants (provides types for utilities)
- **ADR-003:** Create Service Layer (uses utilities for domain logic)
- **ADR-004:** Extract Custom Hooks (uses utilities indirectly via services)

---

## References

- Phase 2 Summary: `docs/phases/PHASE_2_SUMMARY.md`
- Utility Functions: `src/utils/`
- Unit Tests: `src/utils/__tests__/`
- Refactor Scorecard: `docs/REFACTOR_SCORECARD.md`

