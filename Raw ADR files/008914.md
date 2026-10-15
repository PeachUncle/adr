# ADR-002: Shared Utilities Pattern

## Status
Accepted - Implemented on 2025-11-25

## Context
During analytics reorganization, we discovered duplicate helper methods across services:
- `_calculate_grade()` duplicated in 3 locations (48 lines total)
- `_generate_at_risk_recommendation()` duplicated in 2 locations (16 lines total)
- Total duplication: 64 lines of identical code

This violated DRY (Don't Repeat Yourself) principles and created maintenance issues.

## Decision
Extract common utility functions to shared module `analytics_utils.py`:

```python
# src/application/services/analytics/analytics_utils.py
def calculate_grade(percentage: float) -> str
def calculate_percentage(obtained: float, maximum: float) -> float
def calculate_sgpa(percentage: float) -> float
def get_blooms_level_name(level: str) -> str
def generate_at_risk_recommendation(percentage: float) -> str
def calculate_class_rank(student_id: int, percentages: list) -> dict
```

All analytics services import and use these shared utilities instead of implementing their own versions.

## Rationale

### DRY Principle
- **Before:** Grade calculation logic in 3 places
- **After:** Single source of truth in `analytics_utils.py`
- Updates only needed once, propagate everywhere

### Consistency
- All services use identical grading criteria
- No risk of divergent implementations
- Behavior is predictable across the system

### Testability
- Utility functions can be unit tested independently
- Services can mock utilities if needed
- Easier to verify correctness

### Maintainability
- -64 lines of duplicate code eliminated
- Smaller service files
- Clear separation between business logic and utilities

## Consequences

### Positive
- ✅ Single source of truth for calculations
- ✅ Consistent behavior across all analytics
- ✅ Easier to test utilities independently
- ✅ Reduced codebase by 64 lines
- ✅ Future grade calculation changes only need one edit

### Negative
- ⚠️ Services now depend on `analytics_utils`
- ⚠️ Breaking changes to utils affect all services
- ⚠️ Need to import utilities in each service

### Neutral
- Slight coupling between services and shared module
- Trade-off: coupling vs. duplication

## Implementation Details

### Extraction Process
1. Identified duplicate methods across services
2. Created `analytics_utils.py` with shared functions
3. Replaced `self._calculate_grade()` with `calculate_grade()`
4. Removed duplicate method definitions
5. Verified no references to old methods remain

### Verification
```bash
# Confirmed no duplicate methods remain
$ grep -r "def _calculate_grade" backend/src/application/services/analytics/
# No results ✓

$ grep -r "self\._calculate_grade" backend/src/application/services/analytics/
# No results ✓
```

## Guidelines for Future Shared Utilities

### When to Extract
Extract to shared utilities when:
1. **Used in 3+ locations** (clear duplication)
2. **Logic is identical** (not just similar)
3. **Domain-agnostic** (not service-specific business logic)

### When NOT to Extract
Keep in services when:
1. Used in only 1-2 places
2. Logic is service-specific
3. Likely to diverge in future

### Examples
**Good candidates for extraction:**
- Email validation
- Date formatting
- Percentage calculations
- Grade assignments

**Bad candidates (keep in services):**
- Business rule validation
- Domain-specific calculations
- Workflow logic

## Alternatives Considered

### Alternative 1: Keep Duplication
Leave duplicate methods in each service.

**Rejected because:**
- Violates DRY principle
- Risk of inconsistency
- Harder to maintain
- 64 lines of unnecessary code

### Alternative 2: Base Class
Create `BaseAnalyticsService` with shared methods.

**Rejected because:**
- Overengineering for simple utilities
- Tight coupling through inheritance
- Harder to test in isolation
- Python favors composition over inheritance

### Alternative 3: Global Utils Module
Create project-wide `src/shared/utils.py`.

**Deferred because:**
- Prefer domain-specific utils (analytics_utils)
- Easier to locate and understand
- Can create global utils later if needed

## References
- Implementation: `/Users/deepstacker/WorkSpace/dsaba-lms-04/backend/src/application/services/analytics/analytics_utils.py`
- Related ADRs: ADR-001 (Analytics Service Organization)
- Walkthrough: `walkthrough.md`
