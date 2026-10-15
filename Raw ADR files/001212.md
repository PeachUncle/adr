# ADR-008: Priority Enum Comparison Operators Implementation

**Date**: 2025-12-30
**Status**: Accepted
**Deciders**: @executor, @critic
**Documented By**: @recorder
**Part of**: P0-006 Target 3 - Branch Coverage Quick Wins Initiative

## Context

The `Priority` enum in `cf_core/models/priority.py` lacked complete comparison operators (`__gt__`, `__ge__`), and the existing `__lt__` and `__le__` operators had incorrect logic. Additionally, the test suite had conflicting comparison semantics between different test functions.

### Issues Identified by @critic
1. Missing `__gt__` and `__ge__` comparison operators
2. Incorrect inverted logic in `__lt__` and `__le__` implementations
3. 8 test functions with incorrect expectations and conflicting semantics
4. Inconsistency between `test_comparison` and `test_comparison_operators`

## Decision

Implement **complete comparison operator suite** with **priority-level semantics** and **unified test expectations**.

### Comparison Operator Logic
- **Priority-level semantics**: `CRITICAL > HIGH` (higher importance wins)
- **Inverted sort_order**: Lower numbers = higher priority (min-heap pattern)
- **Type safety**: Return `NotImplemented` for non-Priority types

## Rationale

### Options Considered

1. **Sort-order semantics** (0 < 1 < 2...)
   - Pros: Matches internal sort_order directly
   - Cons: Counter-intuitive (`Priority.CRITICAL < Priority.HIGH`)
   - Rejected: Users expect higher priority > lower priority

2. **Priority-level semantics** ✅ SELECTED
   - Pros: Intuitive (`Priority.CRITICAL > Priority.HIGH`)
   - Cons: Requires inverted sort_order logic in implementation
   - Selected: User-friendly, matches business expectations

3. **No comparison operators**
   - Pros: Avoids complexity
   - Cons: No sorting, filtering, or priority-based logic
   - Rejected: Business logic requires priority comparison

### Implementation Details

```python
def __gt__(self, other: Priority) -> bool:
    """Higher priority > lower priority."""
    if not isinstance(other, Priority):
        return NotImplemented
    return self.sort_order < other.sort_order  # Inverted!

def __lt__(self, other: Priority) -> bool:
    """Lower priority < higher priority."""
    if not isinstance(other, Priority):
        return NotImplemented
    return self.sort_order > other.sort_order  # Inverted!
```

### Test Unification Strategy

- **Unified semantics**: All tests use "lower priority < higher priority" pattern
- **Fixed 8 functions**: Corrected expectations to match implementation
- **Type safety**: Added TypeError assertions for non-Priority comparisons

## Consequences

### Positive
✅ **Complete operator suite**: All comparison operations now supported
✅ **Intuitive semantics**: `CRITICAL > HIGH` reads naturally
✅ **Type safety**: `NotImplemented` pattern prevents runtime errors
✅ **Unified tests**: No more conflicting semantics in test suite
✅ **100% coverage**: All 133 tests passing with consistent behavior

### Negative
⚠️ **Mypy warnings**: Liskov substitution warnings for str-based enum
⚠️ **Implementation complexity**: Inverted logic requires careful documentation

### Neutral
📝 **Learning curve**: Developers must understand sort_order vs priority inversion
📝 **Documentation need**: Clear examples of comparison behavior required

## Implementation

### Files Modified
- **cf_core/models/priority.py**: Added `__gt__`, `__ge__`; fixed `__lt__`, `__le__`
- **tests/cf_core/unit/models/test_priority.py**: Fixed 8 test function expectations

### Test Results
- **Before**: 123/133 tests passing (10 expectation failures)
- **After**: 133/133 tests passing (100% success rate)
- **Coverage**: 100% branch coverage maintained

### Quality Gates
- ✅ Ruff linting: "All checks passed"
- ✅ Bandit security: No issues
- ✅ Type safety: NotImplemented pattern verified

## Validation

### Interactive Verification
```python
from cf_core.models.priority import Priority

assert Priority.CRITICAL > Priority.HIGH     # True - intuitive
assert Priority.HIGH < Priority.CRITICAL     # True - intuitive
assert Priority.MEDIUM <= Priority.MEDIUM    # True - equality
assert Priority.LOW >= Priority.NONE         # True - ordering
```

### Test Coverage
All comparison combinations tested across 133 comprehensive test cases.

## Future Considerations

1. **Mypy warnings**: Consider adding code comment documenting str-enum tradeoff
2. **Documentation**: Add comparison examples to docstrings
3. **Performance**: Current O(1) implementation optimal for business needs

## References

- [P0-006 Initiative](../projects/P0-CFWORK-DOCUMENTATION/P0-006-TARGETS.md)
- [Python Comparison Protocol](https://docs.python.org/3/reference/datamodel.html#object.__lt__)
- [Priority Module Implementation](../../cf_core/models/priority.py)
- [Implementation Artifact](../artifacts/impl-2025-12-30-priority-comparison-operators.yaml)

---

**Impact**: Critical - Enables priority-based sorting, filtering, and business logic throughout cf_core and MCP systems.

**Validation**: @critic approved - All acceptance criteria met, quality gates passed.
