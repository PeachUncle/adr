---
status: "accepted"
date: 2025-12-12
decision-makers: Geoff McCosker
---

# Use Vision-First Extraction for Response Structures

## Context and Problem Statement

We need to extract structured response requirements ("questions") from Request for Proposal (RFP) documents to automate the tender response process. These documents are provided in various formats (DOCX, XLSX, PDF) and are often highly unstructured or semi-structured.

Crucially, the "structure" of the requirements is often conveyed visually:
- Nested tables where headers define the section path.
- Visual checkboxes or form fields indicating interaction types.
- Indentation and formatting representing hierarchy.
- Instructions embedded in adjacent columns or merged cells.

Traditional text extraction methods flatten this information, losing the context required to accurately identify what constitutes a "question" versus a "heading" or "instruction."

## Decision Drivers

- Accuracy of structure extraction (correctly identifying parent-child relationships).
- Ability to handle complex layouts (tables, forms, non-standard formatting).
- Reliability across different file formats (Word, Excel, PDF).
- Minimizing the complexity of the parsing logic (avoiding bespoke parsers for every format).

## Considered Options

- **Vision-First Extraction (Chosen)**: Convert everything to PDF and use a Multimodal LLM (Gemini 2.5 Flash).
- **Standard Prompt (Text Parse)**: Extract raw text and use an LLM to structure it.
- **Smart-Parse (Markdown)**: Convert documents to Markdown to preserve some structure, then use an LLM.

## Decision Outcome

Chosen option: "Vision-First Extraction", because it provides the highest accuracy for complex layouts by preserving the visual context that defines the document structure.

### Consequences

- **Good**: Drastically simplifies the ingestion pipeline; we only need to convert inputs to PDF (using LibreOffice).
- **Good**: High accuracy on tables and forms, which are common in RFPs but difficult for text/markdown parsers.
- **Good**: Leverages Gemini's large context window to process entire documents at once, maintaining global context.
- **Bad**: Potentially higher latency and cost compared to pure text processing (due to vision tokens).
- **Bad**: Requires a dependency on LibreOffice for high-fidelity PDF conversion.

### Confirmation

The effectiveness of this decision is validated through the benchmarking script `src/cli/bench_extract.py`.
This script runs the extraction against a set of "golden" documents and calculates:
- Field Accuracy (structure matching)
- Latency and Cost
- Token usage comparisons

## Pros and Cons of the Options

### Vision-First Extraction

Strategy: Normalize all inputs (DOCX, XLSX) to PDF using LibreOffice, upload to Gemini Files API, and use a strict schema prompt.

- **Good**: "See" the document like a human does. Tables, merged cells, and checkboxes are interpreted correctly.
- **Good**: Unifies all file types into a single processing flow (PDF).
- **Good**: Highest and most consistent accuracy (0.96) in benchmarks.
- **Neutral**: Token usage is comparable to text-based methods (~1600-1800 total tokens), as efficient output generation offsets the larger vision input.
- **Bad**: Highest latency (~18s vs ~10s for text).

### Standard Prompt (Text Parse)

Strategy: Use Python libraries (e.g., `pypdf`, `python-docx`) to extract raw text and feed it to an LLM.

- **Good**: Fast (~10s) and cheap.
- **Good**: Surprisingly high accuracy (0.94-0.96) on standard layouts.
- **Bad**: Formatting is lost. Tables become jumbled text. Indentation (hierarchy) is often lost.
- **Bad**: Impossible to distinguish between a "checked" checkbox and a bullet point in many cases.

### Smart-Parse (Markdown)

Strategy: Use tools to convert the document to Markdown (e.g., `pandoc` or specialized libraries) and prompt the LLM with the markdown.

- **Bad**: Lower accuracy (0.92-0.94) observed compared to Standard and Vision approaches.
- **Good**: Lowest latency (~7-8s) in some runs.
- **Neutral**: Better than text, but often fails on complex, nested tables found in government RFPs.
- **Bad**: Conversion artifacts can confuse the model. Requires maintaining robust converters for multiple input formats.

## More Information

- **Token Usage Details**: Gemini processes PDF pages as images, costing fixed tokens per page (e.g., ~258 tokens/page for Gemini 1.5/2.5 Flash). For dense text documents, this can actually be more efficient than tokenizing the raw text.
- **LibreOffice**: We rely on LibreOffice in headless mode. While generally reliable, edge cases with complex DOCX table borders have been observed, requiring occasional visual QA.
