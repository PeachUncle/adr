# ADR-004: Test Suite Optimization - Direct Assertions Over Round-Trip Validation

**Status:** Draft (Future Optimization)
**Date:** 2025-11-07
**Context:** Phase 2.3 of performance optimization roadmap

---

## Context

Following Phase 1 (AST-native parsing) and Phase 2 (removal of redundant validation), the test suite still exhibits performance overhead from extensive round-trip validation patterns. Many tests follow this pattern:

```typescript
// Current expensive pattern
test("generator produces valid CSS", () => {
  const ir = { kind: "linear-gradient", ... };
  const result = generate(ir);

  // EXPENSIVE: Re-parse the output to validate
  const parseBack = parse(result.value);
  expect(parseBack.ok).toBe(true);
});
```

**Problem:** Every generator test invokes both generator AND parser, creating thousands of redundant parse operations during test execution.

**Impact:**

- Test suite runs ~15% slower than necessary
- Redundant validation that belongs in dedicated integration tests
- Masks direct output validation with indirect round-trip checks

---

## Decision

**Proposed:** Separate unit tests (direct assertions) from integration tests (round-trip validation).

### Refactor Generator Unit Tests

Replace round-trip validation with direct string assertions:

```typescript
test("generator produces expected CSS string", () => {
  const ir = { kind: "hex", value: "#ff0000" };
  const result = generate(ir);

  // FAST: Direct string comparison
  expect(result.value).toBe("#ff0000");
});
```

### Create Dedicated Round-Trip Test Suite

Maintain round-trip validation in separate integration suite:

```typescript
describe("Integration: Round-trip validation", () => {
  test("parse → generate → parse preserves structure", () => {
    const original = "linear-gradient(red, blue)";
    const parsed = parse(original);
    const generated = generate(parsed.value);
    const reparsed = parse(generated.value);

    expect(reparsed.value).toEqual(parsed.value);
  });
});
```

---

## Rationale

### Why This Is Safe

1. **Type Safety:** Generators work with typed, validated IR structures
2. **Upstream Validation:** IR is validated during parsing phase
3. **Maintained Coverage:** Round-trip tests preserved, just separated
4. **Better Focus:** Unit tests verify exact output, integration tests verify bidirectionality

### Why Separate Test Suites

- **Performance:** Unit tests run fast for rapid feedback
- **Clarity:** Each test has single responsibility
- **Flexibility:** Can run integration tests separately (CI only, less frequently)
- **Debugging:** Direct assertions show exact vs. expected output

### Expected Benefits

- **~15% faster test suite** for local development
- Clearer test failures (exact string mismatch vs. parse failure)
- Easier to add new test cases (no setup overhead)
- Integration tests can focus on edge cases and complex scenarios

---

## Implementation Plan

### Phase 1: Audit (1-2 hours)

```bash
# Find all round-trip validation patterns
grep -r "parse.*generate\|generate.*parse" packages/*/src/**/*.test.ts
```

**Categorize:**

- Simple unit tests → refactor to direct assertions
- Complex integration tests → move to integration suite
- Critical round-trip tests → keep but document why

### Phase 2: Create Infrastructure (30 minutes)

**File:** `packages/b_*/src/__tests__/integration/round-trip.test.ts`

```typescript
/**
 * Integration tests: Verify parse ↔ generate bidirectionality
 *
 * These tests ensure that:
 * 1. All valid CSS can be parsed to IR
 * 2. All IR can be generated to valid CSS
 * 3. The round-trip preserves semantic meaning
 *
 * Note: These tests are slower. Run separately in CI if needed.
 */
describe("Round-trip validation", () => {
  // Comprehensive round-trip tests here
});
```

### Phase 3: Refactor Unit Tests (2-4 hours)

**Pattern:**

```typescript
// Before: Indirect validation via parsing
test("generates rgb() notation", () => {
  const ir = { kind: "rgb", r: 255, g: 0, b: 0 };
  const result = generate(ir);
  const parsed = parse(result.value);
  expect(parsed.ok).toBe(true);
});

// After: Direct output assertion
test("generates rgb() notation", () => {
  const ir = { kind: "rgb", r: 255, g: 0, b: 0 };
  const result = generate(ir);
  expect(result.value).toBe("rgb(255, 0, 0)");
});

// After: Move to integration suite if truly testing round-trip
describe("Integration: RGB round-trip", () => {
  test("rgb() notation preserves values", () => {
    const original = "rgb(255, 0, 0)";
    const parsed = parse(original);
    const generated = generate(parsed.value);
    expect(generated.value).toBe(original);
  });
});
```

### Phase 4: Verify (1 hour)

```bash
# All tests must still pass
just test

# Measure improvement
time just test  # Before
# Apply changes
time just test  # After
# Expected: ~15% improvement
```

---

## Consequences

### Positive

- ✅ Faster test suite for local development
- ✅ Clearer test intent (what output is expected)
- ✅ Easier debugging (direct comparison)
- ✅ Better separation of concerns (unit vs. integration)
- ✅ Maintained coverage (tests preserved, just reorganized)

### Negative

- ⚠️ More test files (separate integration suites)
- ⚠️ Need to maintain both unit and integration tests
- ⚠️ Risk of removing valuable round-trip tests during refactor

### Neutral

- 🔄 One-time refactoring effort (2-4 hours)
- 🔄 Pattern change requires documentation update

---

## Risks and Mitigation

### Risk: Accidentally Remove Valuable Tests

**Mitigation:**

- Don't DELETE tests, MOVE and REFACTOR them
- Keep all round-trip tests in integration suite
- Code review to verify coverage maintained

### Risk: Missing Edge Cases

**Mitigation:**

- Integration suite covers complex scenarios
- Add property-based tests for round-trip validation
- Document which scenarios require round-trip testing

### Risk: Slower CI Pipeline

**Mitigation:**

- Run integration tests in parallel with unit tests
- Consider making integration tests opt-in for local dev
- Keep integration suite focused on critical paths

---

## Alternatives Considered

### Alternative 1: Keep Current Pattern

**Rejected:** Unnecessary performance overhead for common case. Unit tests should be fast.

### Alternative 2: Remove Round-Trip Tests Entirely

**Rejected:** Round-trip validation is valuable for integration testing. Don't remove, separate.

### Alternative 3: Make Round-Trip Optional

**Considered:** Could use environment variable to skip. Adds complexity without clear benefit.

---

## Examples

### Before (Mixed Concerns)

```typescript
describe("Color generator", () => {
  test("hex colors", () => {
    const result = generate({ kind: "hex", value: "#ff0000" });
    const parsed = parse(result.value); // Mixed: unit + integration
    expect(parsed.ok).toBe(true);
  });

  test("rgb colors", () => {
    const result = generate({ kind: "rgb", r: 255, g: 0, b: 0 });
    const parsed = parse(result.value); // Mixed: unit + integration
    expect(parsed.ok).toBe(true);
  });
});
```

### After (Separated Concerns)

```typescript
// Unit tests: Fast, direct assertions
describe("Color generator", () => {
  test("hex colors", () => {
    const result = generate({ kind: "hex", value: "#ff0000" });
    expect(result.value).toBe("#ff0000");
  });

  test("rgb colors", () => {
    const result = generate({ kind: "rgb", r: 255, g: 0, b: 0 });
    expect(result.value).toBe("rgb(255, 0, 0)");
  });
});

// Integration tests: Comprehensive round-trip validation
describe("Integration: Color round-trip", () => {
  test("hex → IR → hex preserves format", () => {
    const original = "#ff0000";
    const ir = parse(original).value;
    const generated = generate(ir).value;
    expect(generated).toBe(original);
  });

  test("rgb() → IR → rgb() preserves values", () => {
    const original = "rgb(255, 0, 0)";
    const ir = parse(original).value;
    const generated = generate(ir).value;
    const reparsed = parse(generated).value;
    expect(reparsed).toEqual(ir);
  });
});
```

---

## Success Metrics

- [ ] Test suite runs 10-15% faster
- [ ] All existing tests preserved (moved, not deleted)
- [ ] Clear separation: unit tests vs. integration tests
- [ ] No loss of test coverage
- [ ] Documentation updated with new patterns

---

## Notes

- This optimization is **low priority** - existing tests work fine
- Should only be pursued after Phase 1 & 2 gains are measured
- Consider combining with property-based testing exploration
- May inspire similar patterns in other test suites

---

## Related

- **Phase 1:** AST-native parsing (Session 042-043) - ✅ Complete
- **Phase 2:** Remove redundant validation (Session 044) - ✅ Complete
- **Phase 2.3:** This ADR - 🔲 Future work
- **Architectural Refactoring Plan:** `docs/sessions/041/ARCHITECTURAL_REFACTORING_PLAN.md`

---

**Status: DRAFT - Future optimization to pursue after Phase 1 & 2 gains are measured and validated.**
