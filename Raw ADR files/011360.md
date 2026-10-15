# ADR-0012: Use Monolithic Tool Design for MCP Interface

**Status:** Implemented

**Date:** 2025-10-15

**Deciders:** Core team

**Tags:** architecture, api-design, mcp

---

## Context

The Model Context Protocol (MCP) allows servers to expose tools (functions) that AI assistants can invoke. We need to decide how to structure our API:

**Options:**

1. **Monolithic:** Single `summarize_urls` tool with rich parameters
2. **Modular:** Multiple tools (`fetch_url`, `extract_content`, `summarize_text`, etc.)
3. **Hybrid:** Core tool + utility tools

Considerations:

- **User experience:** How many tools must users learn?
- **Composability:** Can tools be combined in workflows?
- **Complexity:** Internal orchestration vs external orchestration
- **MCP limitations:** Tool calling patterns, parameter passing

Typical usage patterns:

- **90% case:** Fetch URL → Extract → Summarize (full pipeline)
- **10% case:** Specialized operations (extract only, custom summarization)

## Decision

We will implement a **monolithic tool design** with a single primary tool:

### Primary Tool

```python
@mcp.tool()
async def summarize_urls(
 urls: List[str],
 query: Optional[str] = None,
 follow_links: int = 0,
 max_depth: int = 1,
 include_metadata: bool = False,
) -> AsyncIterator[str]:
 """
 Fetch, extract, and summarize content from URLs.

 Performs complete pipeline:
 1. Fetch HTML (httpx with Playwright fallback)
 2. Extract main content (trafilatura)
 3. Chunk intelligently (hierarchical/semantic)
 4. Summarize (LLM with query awareness)
 5. Follow links if requested
 """
 ...
```

### Rationale

1. **Simple user interface:** One tool to learn, one invocation
2. **Optimized pipeline:** Internal orchestration can optimize better than external
3. **Better error handling:** Failures handled within single tool context
4. **Streaming efficiency:** Single stream for entire pipeline
5. **Caching coordination:** Internal caching more effective
6. **Common case optimization:** 90% use case is full pipeline

### Additional Tools (Utility)

For advanced use cases, expose utility tools:

```python
@mcp.tool()
async def get_cache_stats() -> str:
 """Get cache statistics and usage."""
 ...

@mcp.tool()
async def clear_cache(level: Optional[str] = None) -> str:
 """Clear cache (all or specific level)."""
 ...
```

## Alternatives Considered

### Alternative 1: Modular Tools (Microservices Style)

**Description:** Separate tools for each pipeline stage

```python
@mcp.tool()
async def fetch_url(url: str) -> str:
 """Fetch HTML from URL."""
 ...

@mcp.tool()
async def extract_content(html: str) -> str:
 """Extract main content from HTML."""
 ...

@mcp.tool()
async def summarize_text(text: str, query: str) -> str:
 """Summarize text content."""
 ...
```

**Pros:**

- **Composable:** Can mix and match tools
- **Reusable:** Each tool independently useful
- **Clear separation:** Single responsibility per tool
- **Testable:** Easier to unit test individual tools

**Cons:**

- **Complex orchestration:** User/AI must coordinate 3+ tool calls
- **Inter-tool communication:** Passing large text between tools (inefficient)
- **Error propagation:** Failures cascade across tool calls
- **No pipeline optimization:** Can't optimize across boundaries
- **Poor streaming:** Multiple separate streams, not cohesive
- **Cache coordination:** Difficult to cache intermediate results

**Reason for rejection:** Complexity outweighs benefits for primary use case

### Alternative 2: Hybrid (Core + Utilities)

**Description:** Main tool + specialized tools for power users

```python
@mcp.tool()
async def summarize_urls(...) -> AsyncIterator[str]:
 """Main tool (full pipeline)."""
 ...

@mcp.tool()
async def fetch_url(...) -> str:
 """Advanced: Fetch only."""
 ...

@mcp.tool()
async def extract_content(...) -> str:
 """Advanced: Extract only."""
 ...
```

**Pros:**

- **Best of both:** Simple default, advanced options
- **Flexibility:** Power users get fine-grained control
- **Backward compatible:** Can add specialized tools later

**Cons:**

- **API surface growth:** More tools to document/maintain
- **Confusion:** When to use which tool?
- **Duplication:** Logic duplicated across tools
- **Limited benefit:** Specialized use cases rare

**Reason for rejection:** Added complexity not justified by usage patterns

### Alternative 3: Configuration-Based Modes

**Description:** Single tool with mode parameter

```python
@mcp.tool()
async def process_url(
 url: str,
 mode: str = "full", # full, fetch-only, extract-only, summarize-only
 ...
) -> AsyncIterator[str]:
 """Process URL with specified mode."""
 ...
```

**Pros:**

- **Single tool:** Simple API surface
- **Flexible:** Can skip stages via modes
- **Unified:** One tool, many behaviors

**Cons:**

- **Confusing modes:** What does each mode do?
- **Complex parameters:** Mode interactions with other params
- **Unclear naming:** "process_url" too generic
- **Poor discoverability:** Modes hidden in parameters

**Reason for rejection:** Less clear than monolithic design

## Consequences

### Positive Consequences

- **Simple API:** One primary tool for 90% of use cases
- **Optimized pipeline:** Internal coordination enables optimizations
- **Better UX:** Single invocation, cohesive streaming output
- **Efficient caching:** Can cache intermediate results internally
- **Clear purpose:** "summarize_urls" is self-explanatory
- **Easy to learn:** Minimal API surface for users

### Negative Consequences

- **Less composable:** Cannot reuse fetch/extract independently via MCP
- **Opaque pipeline:** Harder to customize individual stages
- **Testing complexity:** Unit testing requires mocking more stages
- **Inflexible:** Changes require modifying core tool

### Neutral Consequences

- **Programmatic access:** Python modules still reusable (only MCP is monolithic)
- **Future expansion:** Can add specialized tools if demand emerges
- **Mitigation:** Expose configuration for pipeline customization

## Implementation

**Key files:**

- `src/mcp_web/mcp_server.py` - MCP server with tool definitions
- `src/mcp_web/__init__.py` - Programmatic API (still modular)

**MCP tool definition:**

```python
@mcp.tool()
async def summarize_urls(
 urls: List[str],
 query: Optional[str] = None,
 follow_links: int = 0,
 max_depth: int = 1,
 include_metadata: bool = False,
 model: Optional[str] = None,
) -> AsyncIterator[str]:
 """
 Fetch and summarize content from one or more URLs.

 Args:
 urls: List of URLs to process
 query: Optional query to focus summarization
 follow_links: Number of relevant links to follow
 max_depth: Maximum depth for link following
 include_metadata: Include page metadata in output
 model: Override default LLM model

 Yields:
 Streaming summary output with status updates
 """
 async for result in _summarize_urls_impl(
 urls, query, follow_links, max_depth, include_metadata, model
 ):
 yield result
```

**Internal pipeline (still modular):**

```python
# Programmatic API remains modular for library users
from mcp_web import fetch_url, extract_content, summarize_text

# Can still use individual functions
html = await fetch_url("https://example.com")
content = extract_content(html)
summary = await summarize_text(content)
```

**Utility tools:**

```python
@mcp.tool()
async def get_cache_stats() -> str:
 """Get statistics about cache usage."""
 ...

@mcp.tool()
async def clear_cache(level: Optional[str] = None) -> str:
 """Clear cache entries."""
 ...

@mcp.tool()
async def prune_cache() -> str:
 """Remove expired cache entries."""
 ...
```

## References

- [Model Context Protocol Tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [API Design Principles](https://www.gov.uk/guidance/gds-api-technical-and-data-standards)
- [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy) (contrast: we chose monolithic over composition)
- Related ADR: [0001-use-httpx-playwright-fallback.md](0001-use-httpx-playwright-fallback.md)
- Related ADR: [0011-enable-streaming-output.md](0011-enable-streaming-output.md)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-15 | Initial proposal and acceptance | Cascade |
| 2025-10-15 | Implemented in v0.1.0 | Cascade |
