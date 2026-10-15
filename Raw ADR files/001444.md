# ADR-0001: Architecture Baseline

## Status
Accepted

## Context
We need to build a comprehensive documentation scraping and processing system that can:
1. Crawl entire documentation websites
2. Convert HTML to clean markdown
3. Process documents for vector database ingestion
4. Provide both CLI and GUI interfaces
5. Support LLM-powered classification

The system needs to be extensible, maintainable, and performant while respecting website policies and rate limits.

## Decision

### Overall Architecture: Pipeline-Based Processing

We will use a **pipeline architecture** with distinct stages:
1. **Scraping Stage**: Fetch and convert web content
2. **Cleaning Stage**: Remove unwanted elements
3. **Structuring Stage**: Create semantic chunks
4. **Sorting Stage**: Categorize and order documents
5. **Export Stage**: Generate vector-ready output

**Rationale**: 
- Clear separation of concerns
- Easy to test individual stages
- Can optimize each stage independently
- Allows for partial processing and resumption

### Scraping: Dual Implementation Strategy

We will provide **two scraper implementations**:
1. **Advanced Async Scraper** (`DocScraper.py`) - For production use
2. **Simple Sync Scraper** (`SimpleDocScraper.py`) - For testing/debugging

**Rationale**:
- Async provides better performance for large sites
- Sync is easier to debug and understand
- Users can choose based on their needs
- Fallback option if async causes issues

### Technology Choices

#### Web Scraping: crawl4ai + Playwright
**Chosen**: crawl4ai with Playwright backend

**Alternatives Considered**:
- BeautifulSoup + requests: Too basic, no JavaScript support
- Selenium: Slower, more resource-intensive
- Scrapy: More complex, overkill for our needs

**Rationale**:
- crawl4ai provides high-level abstractions
- Playwright handles JavaScript-rendered content
- Good balance of features and performance
- Built-in markdown conversion

#### GUI Framework: Tkinter
**Chosen**: Tkinter

**Alternatives Considered**:
- PyQt: More powerful but licensing concerns
- Kivy: Better for mobile but unnecessary
- Web-based (Flask/FastAPI): More complex deployment

**Rationale**:
- Included with Python (no extra dependencies)
- Simple and sufficient for our needs
- Cross-platform compatibility
- Easy to distribute

#### LLM Integration: OpenAI API
**Chosen**: OpenAI API with optional fallback

**Alternatives Considered**:
- Anthropic Claude API: Good but less widespread
- Local models (Ollama): Too resource-intensive
- No LLM: Limited classification quality

**Rationale**:
- Best-in-class performance
- Wide adoption and documentation
- Optional (system works without it)
- Easy to swap for alternatives

### Data Storage: File-Based with JSON Metadata

**Chosen**: Markdown files + JSON metadata

**Alternatives Considered**:
- SQLite database: Overkill for our needs
- Binary formats: Poor interoperability
- Cloud storage: Unnecessary complexity

**Rationale**:
- Simple and transparent
- Easy to version control
- Human-readable outputs
- Good for debugging

### Chunking Strategy: Semantic Boundaries with Size Limits

**Approach**:
1. Respect heading boundaries
2. Target chunk size: 1000 tokens
3. Overlap: 200 tokens
4. Never split code blocks or tables

**Rationale**:
- Maintains semantic coherence
- Works well with embedding models
- Preserves context across chunks
- Handles various content types

## Trade-offs

### Performance vs Simplicity
- **Decision**: Favor simplicity in most places, optimize hotspots
- **Trade-off**: Some operations could be faster with more complex code
- **Mitigation**: Profile and optimize only where needed

### Flexibility vs Convention
- **Decision**: Provide sensible defaults with override options
- **Trade-off**: More configuration options = more complexity
- **Mitigation**: Hide advanced options behind flags/environment variables

### Async vs Sync
- **Decision**: Support both patterns
- **Trade-off**: Duplicate code in some areas
- **Mitigation**: Share common logic where possible

### GUI vs CLI
- **Decision**: Maintain both interfaces
- **Trade-off**: More code to maintain
- **Mitigation**: Thin GUI layer over core logic

## Consequences

### Positive
- Easy to understand and modify
- Good performance for most use cases
- Flexible enough for various documentation sites
- Can be extended without major refactoring
- Works offline (except LLM features)

### Negative
- Not optimized for extremely large sites (>10,000 pages)
- Requires Python environment (no standalone executable yet)
- GUI is basic (functional but not beautiful)
- Some code duplication between sync/async versions

### Neutral
- File-based storage means no query capabilities
- Depends on external services for some features
- Rate limiting is conservative (could be faster)

## Open Questions and TODOs

### Short Term
- [ ] Add support for authentication (login-required docs)
- [ ] Implement incremental updates (only fetch changed pages)
- [ ] Add export to different vector DB formats
- [ ] Create standalone executables
- [ ] Add proxy support

### Medium Term
- [ ] Implement distributed crawling
- [ ] Add support for PDF documentation
- [ ] Create web API version
- [ ] Implement caching layer
- [ ] Add more LLM providers

### Long Term
- [ ] Machine learning for better content extraction
- [ ] Automatic documentation structure detection
- [ ] Multi-language support
- [ ] Real-time documentation monitoring
- [ ] Integration with documentation platforms

## Technical Debt

### Current Issues
1. **Test Coverage**: Need more comprehensive tests
2. **Error Handling**: Some edge cases not handled
3. **Type Hints**: Incomplete type annotations
4. **Documentation**: API docs could be more detailed
5. **Performance**: Haven't profiled all code paths

### Refactoring Opportunities
1. **Extract Common Logic**: Reduce duplication between scrapers
2. **Plugin System**: Make processors pluggable
3. **Configuration Management**: Centralize all config
4. **Logging Strategy**: Implement structured logging
5. **Async Everywhere**: Make post-processor fully async

## Validation

### How We'll Know This Works
1. **Performance Metrics**:
   - Can scrape 1000 pages in < 10 minutes
   - Post-processing 1000 docs in < 2 minutes
   - Memory usage < 1GB for typical sites

2. **Quality Metrics**:
   - Clean markdown (no navigation artifacts)
   - Proper chunk boundaries (semantic coherence)
   - Accurate categorization (>90% with LLM)

3. **Usability Metrics**:
   - New users productive in < 30 minutes
   - GUI intuitive without documentation
   - CLI follows Unix conventions

## References

- [crawl4ai Documentation](https://github.com/unclecode/crawl4ai)
- [Playwright Python Docs](https://playwright.dev/python/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Vector Database Best Practices](https://www.pinecone.io/learn/vector-database/)
- [Chunking Strategies for RAG](https://www.anyscale.com/blog/a-comprehensive-guide-for-building-rag-based-llm-applications-part-1)

## Decision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-28 | 1.0 | Initial architecture decision | Team |

## Approval

This ADR has been accepted and represents our current architecture baseline. Future changes should be documented in new ADRs that reference this one.