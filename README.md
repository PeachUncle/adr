# Architectural Decision Records (ADRs): Dataset and Replication Package

This repository provides the dataset, coding materials, analysis scripts, and supplementary results for an empirical study of Architectural Decision Records (ADRs) in open-source software projects.

The study investigates what architectural decisions are recorded, which factors are considered in those decisions, and how ADR recording practices evolve across different project contexts.

## Dataset at a glance

The curated dataset contains **18,983 ADRs from 4,107 GitHub repositories** after the study's filtering and deduplication procedures. 

## Repository structure

```text
.
├── ADRs dataset/
├── Analysis scripts and supplementary results/
│   ├── Analysis data.xlsx
│   ├── Scripts/
│   │   ├── RQ1/
│   │   ├── RQ2/
│   │   └── RQ3/
│   └── Supplementary materials/
│       ├── RQ1/
│       ├── RQ2/
│       └── RQ3/
├── Codebook and results/
├── Raw ADR files/
└── Repos and ADRs metadata/
```

### `ADRs dataset/`
The curated collection of ADRs retained for the empirical study.

### `Analysis scripts and supplementary results/`
This directory organizes the research-question-specific analysis materials:

- **`Analysis data.xlsx`** — The analysis workbook located alongside the scripts and supplementary materials. Examine its worksheets and column names to determine which variables each script uses.
- **`Scripts/RQ1/`, `Scripts/RQ2/`, `Scripts/RQ3/`** — Analysis scripts organized by research question.
- **`Supplementary materials/RQ1/`, `Supplementary materials/RQ2/`, `Supplementary materials/RQ3/`** — Corresponding supplementary materials organized by research question, such as supporting outputs where present.

The parallel `RQ1`–`RQ3` subdirectories make it possible to navigate from a research question to its scripts and associated supplementary materials. 

### `Codebook and results/`
Coding documentation and associated results. Refer to the codebook for definitions and decision rules concerning decision topics, quality attributes, non-quality factors, and trade-off types.

### `Raw ADR files/`
The collected source ADR text files, which can be consulted to inspect the original decision documentation underlying the analysis.

### `Repos and ADRs metadata/`
Repository-level and ADR-level metadata, used to connect decisions to repository contexts and support analyses involving classifications and temporal information.