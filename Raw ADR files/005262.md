# 2. Using Docling to prepare context for evals

Date: 2025-08-11

## Status

Accepted

## Context

This project initially explored creating custom data formats (YAML/JSON) for cybersecurity frameworks to support LLM evaluation research. However, after establishing the research methodology in `llm-research.md`, we identified that:

1. **Research Focus Shift**: The primary research question centers on LLM performance in cybersecurity policy generation, not data format optimization
2. **Processing Overhead**: Custom format conversion introduces unnecessary complexity and potential parsing errors
3. **Standardization Benefits**: Using consistent markdown format aligns with academic reproducibility standards
4. **Context Window Research**: The research specifically examines how different input formats (including raw text vs. structured) affect LLM performance

The IBM Docling tool provides high-quality PDF-to-markdown conversion that preserves document structure while maintaining readability for LLM processing.

## Decision

We will use Docling-converted markdown files in `data/cyber-frameworks/docling/` as the primary data source for LLM evaluations, abandoning custom YAML/JSON format development.

**Specific changes:**
- Remove `data/cyber-frameworks/json/` and `data/cyber-frameworks/yaml/` directories
- Remove custom conversion scripts and schema definitions
- Focus evaluation pipeline on processing markdown-formatted cybersecurity standards
- Maintain docling conversion outputs as the canonical source for research experiments

## Consequences

**Easier:**
- Simplified data pipeline with fewer conversion steps
- Direct use of high-quality, structured markdown for LLM input
- Reduced maintenance overhead for custom parsers and validators
- Better alignment with reproducible research practices
- Clear separation between data preparation and evaluation methodology

**More Difficult:**
- Loss of structured metadata that was captured in custom formats
- Need to parse requirements from markdown during evaluation rather than using pre-structured data
- Potential inconsistencies in how different documents are converted to markdown

**Risks and Mitigations:**
- **Risk**: Docling conversion quality varies across documents
  - **Mitigation**: Manual review of critical framework conversions, documented conversion quality assessment
- **Risk**: Markdown parsing complexity during evaluation
  - **Mitigation**: Robust evaluation framework with comprehensive error handling and validation checks
