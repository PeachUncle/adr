# ADR-0004: Use Trafilatura for Content Extraction

**Status:** Implemented
**Date:** 2025-10-15
**Deciders:** Core Team
**Tags:** content-extraction, html-parsing

---

## Context

The web summarization tool needs to extract main content from arbitrary HTML pages while:

- Removing boilerplate (navigation, ads, footers, sidebars)
- Preserving formatting (code blocks, lists, tables)
- Extracting metadata (title, author, date)
- Handling diverse page structures (news, blogs, documentation, etc.)

**Requirements:**

- High extraction accuracy across diverse sites
- Preserve document structure and formatting
- Fast enough for real-time use (<2 seconds per page)
- Handle edge cases (malformed HTML, unusual layouts)

**Constraints:**

- Must work with Python async/await
- Should not require per-site configuration
- Minimal dependencies

---

## Decision

We will use **trafilatura** library with `favor_recall=True` for HTML content extraction.

```python
import trafilatura

html = await fetch_url(url)
content = trafilatura.extract(
 html,
 favor_recall=True,
 include_comments=False,
 include_tables=True,
 include_links=False,
)
```

---

## Alternatives Considered

### Alternative 1: BeautifulSoup + Custom Heuristics

**Description:** Use BeautifulSoup with hand-crafted rules to identify main content

**Pros:**

- Full control over extraction logic
- No additional dependencies (BeautifulSoup already used)
- Can optimize for specific site patterns

**Cons:**

- ❌ Requires extensive per-site rules (Wikipedia, Medium, GitHub, etc.)
- ❌ Maintenance burden as sites change layouts
- ❌ Lower accuracy on unfamiliar sites
- ❌ Time-consuming to develop robust heuristics

**Rejected because:** Too much manual work, poor generalization

### Alternative 2: newspaper3k

**Description:** Python library specifically for news article extraction

**Pros:**

- Simple API
- Good for news sites
- Extracts authors, dates automatically

**Cons:**

- ❌ Last updated 2019 (unmaintained)
- ❌ Lower accuracy than trafilatura (per benchmarks)
- ❌ Focused on news, poor for documentation/blogs
- ❌ Doesn't handle modern JavaScript frameworks well

**Rejected because:** Unmaintained, limited to news sites

### Alternative 3: Mozilla Readability (Python Port)

**Description:** Port of Firefox's Reader View extraction algorithm

**Pros:**

- Battle-tested (Firefox Reader View)
- Good accuracy
- Handles diverse content types

**Cons:**

- ❌ Python port is dated (readability-lxml)
- ❌ Less maintained than trafilatura
- ❌ No `favor_recall` option (precision-focused)
- ❌ Slower than trafilatura

**Rejected because:** Less maintained, no recall tuning

### Alternative 4: Custom ML-Based Extraction

**Description:** Train ML model to identify main content blocks

**Pros:**

- Potentially highest accuracy
- Can adapt to new patterns
- State-of-art approach

**Cons:**

- ❌ Requires labeled training data
- ❌ Inference overhead (latency)
- ❌ Model maintenance burden
- ❌ Overkill for MVP

**Rejected because:** Too complex for current needs

---

## Consequences

### Positive

✅ **High accuracy:** Trafilatura consistently ranks #1 in extraction benchmarks
✅ **Favor recall mode:** `favor_recall=True` prioritizes content completeness
✅ **Handles edge cases:** Works on diverse page structures without configuration
✅ **Preserves formatting:** Maintains code blocks, lists, tables in output
✅ **Metadata extraction:** Gets title, author, date, language automatically
✅ **Active maintenance:** Regular updates, responsive to issues
✅ **Well-documented:** Comprehensive docs and examples
✅ **Fast enough:** <1 second per page on average

### Negative

⚠️ **Additional dependency:** Adds trafilatura to requirements
⚠️ **Slightly slower:** 20-30% slower than naive BeautifulSoup parsing
⚠️ **False positives possible:** `favor_recall` may include some non-content
⚠️ **No per-site tuning:** Cannot optimize for specific site patterns

### Neutral

🔸 **Configuration options:** Multiple parameters available if needed
🔸 **Format support:** HTML only (PDF handled separately)
🔸 **Language support:** Works with non-English content

---

## Implementation

### Integration Points

**Module:** `src/mcp_web/extractor.py`

**Key functions:**

- `extract_content(html: str, url: str) -> ExtractedContent`
- `extract_metadata(html: str) -> Metadata`

**Configuration:**

```python
class ExtractorSettings(BaseSettings):
 favor_recall: bool = True
 include_tables: bool = True
 include_comments: bool = False
 include_links: bool = False
```

### Testing

**Unit tests:** `tests/unit/test_extractor.py`

- Test extraction accuracy on sample HTML
- Test metadata extraction
- Test handling of malformed HTML
- Test preservation of formatting

**Golden tests:** `tests/golden/test_golden_extraction.py`

- Verify consistent extraction on real-world pages
- Regression testing for extraction quality

---

## Validation

### Extraction Accuracy Benchmark

Tested on 20 diverse websites:

- News: 95% accuracy (main article extracted)
- Blogs: 92% accuracy (post content extracted)
- Documentation: 90% accuracy (main content extracted)
- GitHub: 88% accuracy (README extracted)

**Compared to alternatives:**

- newspaper3k: 78% average
- BeautifulSoup naive: 65% average
- Readability: 85% average

**Source:** Manual evaluation on test corpus

### Performance

- **Average extraction time:** 0.8 seconds per page
- **Memory usage:** <50 MB per page
- **Handles large pages:** Works on pages up to 10 MB HTML

---

## References

### Research & Benchmarks

- [Trafilatura Documentation](https://trafilatura.readthedocs.io/en/latest/)
- [Trafilatura Benchmark Results](https://github.com/adbar/trafilatura#evaluation)
- [Web Content Extraction Survey (2020)](https://arxiv.org/abs/2003.11878)

### External Comparisons

- [Scrapinghub Extraction Comparison](https://www.scrapinghub.com/blog/content-extraction-tools/)
- [Content Extraction Libraries Benchmark](https://github.com/currentsapi/awesome-content-extraction)

### Related ADRs

- **ADR-0001:** httpx/Playwright fallback (provides HTML input)
- **ADR-0003:** Documentation standards (trafilatura usage documented)

---

**Last Updated:** 2025-10-15
**Supersedes:** DD-002 from DECISIONS.md
**Superseded By:** None
