# ADR-005: Quality Gates and Fail-Loud Policy

**Date:** 2025-12-27
**Status:** Accepted

## Context

Maintaining code quality in a data analysis project requires explicit,
enforceable constraints. Without these, scripts grow unwieldy, errors get
silently swallowed, and technical debt accumulates.

This ADR establishes engineering constraints that shape the project architecture
and defines how they are enforced.

## Decision

### Script Size Limits

| Limit | Lines | Enforcement | Action |
|-------|-------|-------------|--------|
| **Soft limit** | 300 | Automated (inform) | Consider refactoring |
| **Hard limit** | 500 | Automated (test fails) | Refactor required before merge |

**Enforcement:** `test-governance-script-size.R` scans `scripts/eda/*.R` and:
- Reports scripts exceeding 300 lines via `testthat::inform()`
- Fails the test suite if any script exceeds 500 lines

**Counting rules:**
- Count all lines including comments and blank lines
- Exclude trailing blank lines
- Measured with `readLines()` in the governance test

### Line Length Policy

| Threshold | Characters | Enforcement |
|-----------|------------|-------------|
| **Target** | 80 | Policy (not enforced) |
| **Allowed** | 110 | Automated lint check |
| **Hard stop** | 120 | Policy (refactor required) |

**Enforcement:** `.lintr` is configured with `line_length_linter(110)`.
Lines exceeding 110 characters fail lint checks.

**Handling long lines:**
- Extract constants or use intermediate variables
- Break `glue()` strings across lines
- Split long pipelines
- Use `# nolint` sparingly with explanatory comment

### Path Governance

**Enforcement:** `test-governance-paths.R` scans `scripts/eda/*.R` and fails if
hardcoded `"data/"`, `"output/"`, or `"assets/"` paths appear outside of
`PATHS$...` usage. See ADR-006 for the path constants policy.

### Fail-Loud Policy

**Rule:** Orchestration scripts must not catch-and-stringify errors. Errors
should propagate with full stack traces.

**Prohibited patterns:**
```r
# DO NOT DO THIS
tryCatch(risky_operation(), error = function(e) message(e))
suppressWarnings(potentially_problematic())
suppressMessages(noisy_function())
```

**Allowed exceptions:**
- `tryCatch` with explicit re-throw after logging
- `suppressWarnings` only with user approval and documented rationale

**Enforcement:** Policy (not automated). Code review flags these patterns.

## Enforcement Summary

| Gate | Tool | Enforcement Level |
|------|------|-------------------|
| Script size (500 lines) | `test-governance-script-size.R` | Automated (test fails) |
| Script size (300 lines) | `test-governance-script-size.R` | Automated (inform only) |
| Line length (110 chars) | lintr via `.lintr` | Automated (lint fails) |
| Path constants | `test-governance-paths.R` | Automated (test fails) |
| Fail-loud | Code review | Policy (not enforced) |

### Required Quality Gate Commands

Before merging changes, run these commands in order:

```bash
# 1. Lint check (enforces line length, style)
Rscript scripts/dev/01_lint.R

# 2. Test suite (enforces script size, path governance, validates functions)
Rscript scripts/dev/02_test.R

# 3. Smoke test (runs lint + tests + pipeline)
Rscript scripts/eda/00_run_all.R --smoke
```

All three must pass with zero errors.

## Consequences

### Positive

- Consistent code quality across all scripts
- Errors surface immediately during development
- Script size and path governance enforced via test suite
- Line length enforced via lint

### Negative

- Stricter discipline required from contributors
- Some legitimate long lines need `# nolint` annotations

## References

- Project `.lintr` configuration: `line_length_linter(110)`
- [lintr package documentation](https://lintr.r-lib.org/)
- [testthat package documentation](https://testthat.r-lib.org/)
- CLAUDE.md "CRITICAL WORK RULES" section establishes fail-loud as a
  project norm
