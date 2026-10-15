# Design: API Cleanup Strategy

## Context

BFHtheme has grown organically to 51 exported functions. This includes:
- Core theming and visualization functions (must keep)
- Convenience wrappers that duplicate functionality (candidates for removal)
- Low-level configuration helpers (candidates for internalization)
- Debug/maintenance utilities (should be internal)

The package has reached a maturity level where API stability matters. Downstream packages (BFHcharts, SPCify) and user scripts depend on the public API. This cleanup is necessary before declaring 1.0.0 stable.

### Constraints
- **Breaking changes require major version bump** (0.4.0 → 1.0.0)
- **Downstream packages must be notified** before release
- **Test coverage must remain ≥90%** after changes
- **All vignettes must continue to work** with updated examples

### Stakeholders
- **Package maintainers** - Need cleaner codebase
- **Existing users** - Need clear migration path
- **New users** - Benefit from simpler API surface
- **Downstream packages** - Need advance notice of breaking changes

## Goals / Non-Goals

### Goals
1. **Reduce exported API to ~39 core functions** (~24% reduction)
2. **Remove redundant convenience wrappers** that obscure better patterns
3. **Internalize debug/maintenance functions** not intended for end users
4. **Maintain full test coverage** for all functionality (internal + exported)
5. **Provide clear migration guide** for breaking changes

### Non-Goals
- Not removing any actual functionality (only changing visibility)
- Not refactoring internal implementation (just API boundaries)
- Not changing function signatures or behavior of retained functions
- Not introducing new features

## Decisions

### Decision 1: Which Functions to Remove vs Unexport

**Rationale:**
- **Remove** functions that are genuinely redundant and provide no unique value
- **Unexport** functions that are useful internally but shouldn't be user-facing

**Choices:**
1. **Remove `add_logo()`**: Trivial wrapper that just calls `add_bfh_logo(get_bfh_logo())`. Users can compose this in one line.
2. **Remove `apply_bfh_theme()`**: Complex API that returns a list. Better to teach users to compose `theme_bfh() + scale_color_bfh()` directly.
3. **Remove `add_bfh_color_bar()`**: Very specific styling helper used rarely. Can be done with standard ggplot2.
4. **Unexport cache/config functions**: These are implementation details that users shouldn't need to touch.

**Alternatives considered:**
- **Deprecate first, remove later**: Rejected because functions are rarely used and complexity outweighs benefit.
- **Keep all wrappers**: Rejected because it fragments the API and makes documentation harder.

### Decision 2: How to Handle Internal Functions

**Approach:** Remove `@export` roxygen tags but keep full documentation.

**Rationale:**
- Tests can still access internal functions via `:::`
- Internal functions remain documented for maintainers
- Users get cleaner namespace but can access internals if needed (with warning)

**Implementation:**
```r
#' @keywords internal
#' @noRd  # Optional: exclude from help index
clear_bfh_font_cache <- function() {
  # ... implementation
}
```

### Decision 3: Test Strategy for Internal Functions

**Approach:** Keep all existing tests, update to use `:::` operator.

**Rationale:**
- Internal functions still need test coverage
- Coverage metrics include internal functions
- Tests document expected behavior for maintainers

**Example:**
```r
# Before (exported)
test_that("clear_bfh_font_cache clears cache", {
  result <- clear_bfh_font_cache()
  expect_true(result)
})

# After (internal)
test_that("clear_bfh_font_cache clears cache", {
  result <- BFHtheme:::clear_bfh_font_cache()
  expect_true(result)
})
```

### Decision 4: Version Bumping Strategy

**Version:** 0.4.0 → 1.0.0 (major bump)

**Rationale:**
- Removing exported functions is a breaking change (semver major)
- Good opportunity to declare API stable at 1.0.0
- Signals to users that package is production-ready

## Risks / Trade-offs

### Risk 1: Breaking Existing User Code
**Impact:** High - Users with scripts calling removed functions will get errors

**Mitigation:**
1. **Clear migration guide** in NEWS.md with before/after examples
2. **Notification** to known downstream packages (BFHcharts, SPCify maintainers)
3. **Detailed error messages** if users try to access removed functions via `help()`

**Acceptance:** This is unavoidable for a cleaner API. The pain is short-term.

### Risk 2: Incomplete Migration Coverage
**Impact:** Medium - Vignettes or examples might break

**Mitigation:**
1. **Comprehensive search** for removed function references: `rg "add_logo|apply_bfh_theme|add_bfh_color_bar"`
2. **Manual vignette rebuild** to catch any issues: `devtools::build_vignettes()`
3. **Full package check** before release: `devtools::check()`

### Risk 3: Test Coverage Drops
**Impact:** Medium - Unexported functions might be harder to test

**Mitigation:**
1. **Use `:::` operator** in tests to access internal functions
2. **Monitor coverage** with `covr::package_coverage()` - maintain ≥90%
3. **Keep all existing tests** - just update access method

### Trade-off: Convenience vs Clarity
**Removed `add_logo()` and `apply_bfh_theme()` were convenient but obscured better patterns.**

- **Benefit:** Users learn composable ggplot2 patterns that work with any package
- **Cost:** Slightly more verbose code (1-2 extra lines)
- **Decision:** Clarity wins. Better for long-term maintainability and user understanding.

## Migration Plan

### Phase 1: Implementation (This Change)
1. Remove 3 functions completely
2. Unexport 9 functions (make internal)
3. Update all tests to use `:::`
4. Update all documentation and examples
5. Add NEWS.md entry with migration guide

### Phase 2: Downstream Notification
1. **Before release:** Email/message maintainers of BFHcharts and SPCify
2. **Provide migration timeline:** "Breaking changes in BFHtheme 1.0.0 releasing [date]"
3. **Offer support:** Help update their packages if needed

### Phase 3: Release
1. **CRAN submission** with clear description of breaking changes
2. **GitHub release** with migration guide prominently featured
3. **Update README.md** badge to show 1.0.0 stable

### Rollback Strategy
If critical issues discovered post-release:
1. **Option A:** Release 1.0.1 patch re-exporting removed functions (temporary)
2. **Option B:** Fast-track 1.1.0 with adjusted API if design flaw found

**Trigger for rollback:**
- More than 3 GitHub issues about broken functionality within 1 week
- Critical downstream package breakage that can't be fixed quickly

## Open Questions

1. **Should we add deprecated stubs for removed functions?**
   - **Decision:** No. Clean break is better than lingering deprecated code.
   - **Alternative:** If users complain heavily, add in 1.0.1 patch.

2. **Should font configuration functions be exported for advanced users?**
   - **Decision:** No. Advanced users can use `:::` if needed. Simplifies 90% use case.

3. **Timeline for release after proposal approval?**
   - **Proposal:** Implement immediately, test 1 week, release after downstream notification.

## Success Metrics

- ✅ NAMESPACE exports exactly 39 functions (down from 51)
- ✅ `devtools::check()` passes with 0 errors, 0 warnings, 0 notes
- ✅ `covr::package_coverage()` shows ≥90% coverage
- ✅ All vignettes build successfully
- ✅ No references to removed functions in exported code
- ✅ NEWS.md contains clear migration guide
- ✅ Version bumped to 1.0.0 in DESCRIPTION
