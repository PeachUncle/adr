# ADR-006: Data Product Location Policy

**Date:** 2025-12-27
**Status:** Accepted

## Context

The project has two processed datasets that serve as inputs for downstream analysis:

1. **Curated CSV** (`asrs_uas_reports_clean.csv`) - 125 columns, typed, renamed
2. **Constructed RDS** (`asrs_constructed.rds`) - 136 columns (125 + 11 derived)

These are **analysis inputs** for downstream steps, not generated artifacts.
Storing them in `output/` caused confusion because `output/` semantically
implies "generated outputs that can be discarded and regenerated."

## Decision

Store curated and constructed datasets in `data/` alongside the raw source data.

| Dataset | Location |
|---------|----------|
| Raw ASRS export | `data/asrs_curated_drone_reports.csv` |
| Curated CSV | `data/asrs_uas_reports_clean.csv` |
| Constructed RDS | `data/asrs_constructed.rds` |

### Path Constants

All scripts use centralized path constants defined in `R/paths.R`:

```r
PATHS <- list(
  raw_csv = "data/asrs_curated_drone_reports.csv",
  curated_csv = "data/asrs_uas_reports_clean.csv",
  constructed_rds = "data/asrs_constructed.rds",
  output_tables = "output/tables",
  output_figures = "output/figures",
  output_notes = "output/notes",
  output_reports = "output/reports",
  apa_reference_doc = "assets/apa_reference.docx"
)
```

**Enforcement:** `test-governance-paths.R` fails if scripts contain hardcoded
path literals instead of `PATHS$...` constants.

### Directory Semantics

| Directory | Contains | Git Policy |
|-----------|----------|------------|
| `data/` | Project datasets (raw, curated, constructed) | Commit all |
| `output/` | Generated artifacts (tables, figures, reports, notes) | Commit final deliverables |

## Consequences

### Positive

- **Clear semantics**: `data/` = datasets, `output/` = artifacts
- **Stable references**: downstream scripts have reliable input paths
- **Reproducibility**: datasets are versioned with the codebase
- **Enforced**: `test-governance-paths.R` prevents path drift

### Negative

- **Git churn on RDS**: regenerating the constructed dataset changes tracked files
- **Larger repo size**: RDS files are binary and compress poorly in git

### Mitigations

- Commit RDS only when: (a) source data changes, or (b) construct logic changes
- Use `git diff --stat` to verify actual changes before committing data files

## Rules

1. `data/` contains project datasets (raw, curated, constructed)
2. `output/` contains generated analytical artifacts only
3. Scripts must not write datasets to `output/`
4. All paths must use constants from `R/paths.R`

## References

- ADR-005: Quality Gates - Documents path governance enforcement
- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/) -
  Recommends separating raw, interim, and processed data
