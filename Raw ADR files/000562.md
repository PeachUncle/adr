## Context

The Graphviz Gallery scraper is the first data collection pipeline for the AnecDOT project. It must extract structured training pairs from graphviz.org/gallery/ while ensuring syntactic validity and proper licensing metadata.

**Key Constraints:**
- Must respect EPL-2.0 licensing from Graphviz documentation
- All DOT code must be compiler-validated before inclusion
- Output must conform to strict JSONL schema for training pipeline
- Scraper must be respectful of the source website (rate limiting, robots.txt)
- Implementation must be reproducible and resumable

**Stakeholders:**
- Data pipeline (depends on JSONL output format)
- Training pipeline (depends on schema consistency)
- Separate dataset repository (receives EPL-2.0 licensed outputs)

## Goals / Non-Goals

**Goals:**
- Extract all available examples from Graphviz Gallery with high fidelity
- Generate instruction-response pairs suitable for causal language modeling
- Validate 100% of scraped DOT code using Graphviz compiler
- Provide clear metadata for licensing compliance and data provenance
- Enable incremental updates when gallery content changes

**Non-Goals:**
- Scraping non-gallery Graphviz documentation (future work: guides, attribute references)
- Parsing DOT syntax into AST (validation only, not parsing)
- Data augmentation or transformation (synthetic stream handles this)
- Generating variations of examples (teacher LLM's role)
- Hosting or distributing the dataset (belongs in separate Repo B)

## Decisions

### Decision 1: Use Beautiful Soup for HTML Parsing
**Rationale:** Beautiful Soup provides robust HTML parsing with lxml backend, handles malformed HTML gracefully, and is widely used in the Python ecosystem. Alternative (Scrapy) would be overkill for a single-site scraper with simple structure.

**Trade-offs:**
- Pro: Simple API, good documentation, handles edge cases
- Pro: No need for XPath complexity (CSS selectors sufficient)
- Con: Slower than raw lxml for large-scale scraping (not a concern here)

### Decision 2: Subprocess-Based DOT Validation as Reusable Component
**Rationale:** Create a dedicated `validation/dot_validator.py` module that uses `subprocess.run(['dot', '-Tpng', '-o', '/dev/null'], input=dot_code)` to validate syntax. This component will be reused across all three data streams (documentation, logic, synthetic) and in Phase II training validation.

**Reusability Benefits:**
- Single source of truth for DOT validation logic across the entire project
- Consistent validation behavior in dataset generation and model evaluation
- Easier to add features like caching, batch validation, and performance metrics
- Phase I.2 (FSM parser) and Phase I.3 (synthetic generator) can import and use immediately
- Phase II.3 (Pass@1 validation) uses identical validation as training data

**Trade-offs:**
- Pro: 100% accurate (uses official compiler)
- Pro: Simple implementation, no need to understand DOT grammar
- Pro: Matches the validation used in training evaluation metrics
- Pro: Reusable across all pipelines (avoids code duplication)
- Con: Slower than regex-based validation (acceptable for dataset generation)
- Con: Requires Graphviz installed (documented dependency)

**Alternatives Considered:**
- Regex-based syntax checking: Too fragile, won't catch semantic errors
- Python DOT parser library (pydot/pygraphviz): Still wraps Graphviz, adds complexity
- Separate validator per stream: Code duplication, inconsistent validation behavior

### Decision 3: JSONL Over CSV/Parquet for Dataset Format
**Rationale:** JSONL (JSON Lines) is the standard format for LLM training data, supports nested metadata, is streamable, and enables easy deduplication.

**Schema:**
```json
{
  "id": "graphviz-gallery-{hash}",
  "source": "graphviz_gallery",
  "source_url": "https://graphviz.org/gallery/{example}",
  "license": "EPL-2.0",
  "task_type": "NL_TO_DOT",
  "input_text": "{title}. {description}. {additional_context}",
  "context_snippet": null,
  "output_dot": "{literal DOT code}",
  "verification_status": "passed_compiler|failed_compiler",
  "scraped_at": "2025-11-18T16:12:18Z"
}
```

**Trade-offs:**
- Pro: Standard for HuggingFace datasets, easy to load
- Pro: Human-readable, easy to debug
- Pro: Append-only writes (safe for interrupted runs)
- Con: Larger file size than binary formats (acceptable for ~100-500 examples)

### Decision 4: Single-Pass Architecture (No Database)
**Rationale:** For the gallery (estimated <500 examples), a single-pass scraper that writes directly to JSONL is sufficient. No need for intermediate database storage.

**Flow:**
1. Fetch gallery index page
2. Extract all example links
3. For each link:
   - Fetch example page
   - Parse title, description, DOT code
   - Validate DOT with compiler
   - If valid, append to JSONL file
4. Write summary statistics

**Trade-offs:**
- Pro: Simple, no database setup required
- Pro: Output is immediately usable
- Pro: Easy to resume (check existing IDs in JSONL)
- Con: Re-scraping requires full run (mitigated by incremental logic)

**Complexity Trigger:** If gallery grows to >10,000 examples or requires complex query patterns, consider SQLite intermediate storage.

### Decision 5: ID Generation Using Content Hash
**Rationale:** Use `sha256(output_dot)[:16]` as the ID suffix to enable natural deduplication. If the same DOT code appears multiple times (edge case), it's the same training example.

**Trade-offs:**
- Pro: Deduplication happens automatically (same hash = same example)
- Pro: Deterministic, reproducible across runs
- Con: Collision risk (mitigated by using sufficient hash length)

### Decision 6: Shared Infrastructure for All Data Streams
**Rationale:** Extract common functionality into reusable modules to avoid code duplication across the three data streams (documentation, logic, synthetic).

**Shared Components:**
```
validation/
├── dot_validator.py       # DOT compilation validation (already reusable)
├── schema.py              # JSONL schema definition and validation
└── writer.py              # Atomic JSONL writer with deduplication

common/
├── id_generator.py        # Content-hash ID generation
├── metrics.py             # Summary statistics tracking
└── logging_config.py      # Structured logging setup
```

**Per-Stream Code (source-specific):**
```
scrapers/
├── graphviz_gallery.py    # Documentation stream (this change)
├── fsm_parser.py          # Logic stream (Phase I.2)
└── synthetic_generator.py # Synthetic stream (Phase I.3)
```

**Benefits:**
- Schema consistency across all three streams (same JSONL format)
- Validation logic identical (same compiler, same thresholds)
- ID generation prevents cross-stream duplicates (global dedup)
- Statistics comparable across streams (same metrics)
- New streams can be added by importing shared components

**Trade-offs:**
- Pro: Zero code duplication for validation, schema, writing
- Pro: Easy to add Phase I.2 and I.3 without reimplementing infrastructure
- Pro: Consistent behavior across all data sources
- Pro: Bugs fixed in one place benefit all streams
- Con: Slightly more upfront abstraction (mitigated by clear interfaces)

**Interface Design:**
```python
# Each scraper implements same pattern:
from validation.dot_validator import validate_dot
from validation.schema import DataRecord
from validation.writer import JSONLWriter

# Scraper-specific extraction logic
records = extract_records(source)  # Source-specific

# Shared validation and writing
for record in records:
    result = validate_dot(record.output_dot)
    if result.is_valid:
        writer.append(DataRecord.from_dict(record))
```

## Risks / Trade-offs

### Risk: Gallery Structure Changes
**Impact:** HTML parsing breaks if Graphviz redesigns their gallery pages.

**Mitigation:**
- Use flexible CSS selectors (e.g., fallback to class patterns)
- Add comprehensive logging to detect parsing failures
- Version the scraper and document the gallery structure it targets
- Monitor pass rate; significant drop indicates structural changes

### Risk: Rate Limiting or Blocking
**Impact:** IP blocked by Graphviz.org during scraping.

**Mitigation:**
- Add 1-2 second delay between requests
- Set respectful User-Agent header
- Check and respect robots.txt (if exists)
- Implement exponential backoff on HTTP errors
- Document acceptable scraping practices in code

### Risk: Invalid DOT Despite Passing Compiler
**Impact:** Some DOT examples may compile but have semantic issues (e.g., disconnected subgraphs for pedagogical reasons).

**Trade-off:** Accept this risk. The compiler check ensures syntactic validity, which is the primary training objective. Semantic quality will be addressed in Phase II evaluation (LLM-as-a-Judge).

### Risk: Incomplete Metadata Extraction
**Impact:** Some examples may lack descriptions or have minimal context.

**Mitigation:**
- Make description field optional in schema
- Use title-only as fallback instruction
- Log examples with missing metadata for manual review
- Accept minimal examples (still valid training data)

## Migration Plan

**N/A** - This is a net-new capability with no existing code to migrate.

**Deployment Steps:**
1. Implement scraper in `scrapers/` directory
2. Run scraper locally to generate initial dataset
3. Validate output schema and DOT compilation pass rate
4. Transfer generated JSONL to separate Repo B (EPL-2.0)
5. Archive this change and update specs/

**Rollback:**
N/A - Scraper is a data generation tool, not production code. Failed runs can simply be re-executed.

### Decision 7: Multi-Example Page Handling
**Rationale:** Gallery pages may contain multiple DOT code blocks demonstrating variations of a concept. Each block represents a distinct training example.

**Implementation:**
- Extract each DOT block as a separate JSONL record
- Share the same title and description across all blocks from the page
- Append sequential index to ID: `graphviz-gallery-{hash}-1`, `graphviz-gallery-{hash}-2`
- Preserves maximum training diversity while maintaining context

**Trade-offs:**
- Pro: More training examples from same source
- Pro: Each example is self-contained and compilable
- Con: Slight ID complexity (mitigated by clear suffix pattern)

### Decision 8: Gallery Scope (Documentation Only)
**Rationale:** Focus Phase I.1 exclusively on the Graphviz Gallery. Attribute references and user guides are deferred to future work to maintain clear scope boundaries.

**Scope:**
- **In scope:** graphviz.org/gallery/ examples only
- **Out of scope:** Attribute documentation, user guides, language spec
- **Future:** Phase I.4 or separate change can add attribute reference scraping

**Trade-offs:**
- Pro: Clear, achievable milestone for Phase I.1
- Pro: Simpler HTML parsing (gallery has consistent structure)
- Con: Misses some documentation (acceptable, can add later)

### Decision 9: Compilation Failure Rate Threshold
**Rationale:** Target >98% pass rate for scraped DOT examples. Lower rates indicate scraping errors rather than invalid gallery content.

**Implementation:**
- Track pass/fail rate in summary statistics
- If <98% pass rate, investigate failures manually:
  - Parsing error: Fix scraper
  - Invalid DOT in gallery: Log and skip, note in documentation
  - Graphviz version issue: Document required version
- Report failure details for each run

**Trade-offs:**
- Pro: High quality bar ensures dataset reliability
- Pro: Forces investigation of issues rather than silent failures
- Con: May require multiple scraper iterations (acceptable for quality)

### Decision 10: Preserve Exact DOT Formatting
**Rationale:** Keep exact source formatting (whitespace, indentation, comments) without normalization to preserve authorship style as training signal.

**Implementation:**
- Extract DOT code exactly as appears in HTML
- No prettification or reformatting
- Preserve comments, blank lines, indentation style
- Whitespace-only differences result in different hashes (not duplicates)

**Trade-offs:**
- Pro: Preserves diverse coding styles for model to learn
- Pro: Maintains original author intent
- Pro: No risk of introducing formatting bugs
- Con: Slight increase in dataset size (negligible)

### Decision 11: External Dependencies Handling
**Rationale:** Include examples that reference external files or plugins if the DOT code compiles successfully. Document dependency presence in metadata for future filtering.

**Implementation:**
- Compiler validation is the only gating criterion
- If DOT compiles → include in dataset
- If references detected (regex scan for file paths, image attributes):
  - Add optional `has_external_refs: true` to metadata
  - Log for potential future filtering
- Don't attempt to fetch or validate external resources

**Trade-offs:**
- Pro: Maximizes training data (more examples)
- Pro: Teaches model about realistic DOT usage patterns
- Con: Examples may not render without dependencies (acceptable, syntax is valid)

## Open Questions

None remaining - all design decisions finalized.
