# ADR-0008: Use Map-Reduce Summarization Strategy

**Status:** Implemented

**Date:** 2025-10-15

**Deciders:** Core team

**Tags:** architecture, llm, performance, scalability

---

## Context

The mcp-web tool needs to summarize documents of arbitrary length, including:

- **Short documents:** <2000 tokens (single API call)
- **Medium documents:** 2000-8000 tokens (fits in one context)
- **Long documents:** 8000-100,000+ tokens (exceeds context window)

LLM context windows impose hard limits:

- GPT-3.5-turbo: 16k tokens
- GPT-4: 32k tokens
- GPT-4-turbo: 128k tokens

Even with large context windows, we face challenges:

1. **Cost scaling:** More tokens = higher costs (linear or worse)
2. **Quality degradation:** LLMs perform worse on very long contexts ("lost in the middle" problem)
3. **Latency:** Long context = slow response times

Our requirements:

1. Handle documents of any length without truncation
2. Maintain summary quality regardless of document length
3. Optimize cost and latency
4. Support query-aware summarization

## Decision

We will use a **map-reduce pattern** for document summarization:

### Strategy

1. **Short documents (<= 8k tokens):** Direct summarization in single call

- Fastest path, best quality
- No overhead from chunking/combining

1. **Long documents (> 8k tokens):** Map-reduce approach

- **Map phase:** Summarize each chunk independently (parallel)
- **Reduce phase:** Combine chunk summaries into final summary
- Recursive reduce if intermediate summaries still too long

### Implementation Details

```text
Document (15k tokens)
 ↓ chunk into 3 chunks (5k each)
 ↓
Map Phase (parallel):
 Chunk 1 → Summary 1 (500 tokens)
 Chunk 2 → Summary 2 (500 tokens)
 Chunk 3 → Summary 3 (500 tokens)
 ↓
Reduce Phase:
 Summaries 1+2+3 → Final Summary (800 tokens)
```

### Query-Aware Optimization

When a query is provided:

- Map phase includes query in prompt ("Focus on aspects related to: {query}")
- Reduce phase emphasizes query-relevant information
- Irrelevant chunks may be summarized more briefly or skipped

## Alternatives Considered

### Alternative 1: Truncate to Context Limit

**Description:** Truncate long documents to fit in context window (e.g., first 30k tokens)

**Pros:**

- Simplest implementation (single API call)
- Fast (no chunking overhead)
- Cheapest (fewest tokens)

**Cons:**

- **Information loss:** Misses content beyond truncation point
- **Biased summaries:** Over-represents beginning of document
- **Unpredictable:** Quality depends on where truncation occurs
- **Unacceptable:** Violates "no information loss" requirement

**Reason for rejection:** Unacceptable information loss

### Alternative 2: Refine Iteratively

**Description:** Summarize in stages, iteratively refining:

1. Summarize first chunk
2. Summarize second chunk + first summary
3. Continue until all content processed

**Pros:**

- Maintains context across chunks
- Single final summary (no combining step)
- Good for narrative flow

**Cons:**

- **Sequential:** Cannot parallelize (slow for long docs)
- **Error propagation:** Early mistakes compound
- **Biased:** Later content has less influence
- **More API calls:** N chunks = N calls (vs map-reduce = N+1)

**Reason for rejection:** Poor parallelization, slower than map-reduce

### Alternative 3: Stuff All Chunks

**Description:** Concatenate all chunks into single context and summarize

**Pros:**

- Single API call
- No information loss within context limit
- Simplest logic

**Cons:**

- **Fails on long documents:** Hard limit at context window
- **Expensive:** Uses maximum tokens per call
- **Slow:** Large context = slow generation
- **Quality issues:** "Lost in the middle" problem

**Reason for rejection:** Cannot handle arbitrarily long documents

## Consequences

### Positive Consequences

- **Scalable:** Handles documents of any length
- **Parallelizable:** Map phase can run concurrently (faster)
- **Cost-efficient:** Only summarizes each chunk once
- **Quality:** Avoids "lost in the middle" problem from very long contexts
- **Flexible:** Can adjust chunk size for cost/quality tradeoff

### Negative Consequences

- **Cross-chunk context loss:** Information spanning chunks may be fragmented
- **Reduction complexity:** Combining summaries requires careful prompting
- **Extra API call:** Reduce phase adds one more request
- **Recursive complexity:** Very long documents may need multiple reduce levels

### Neutral Consequences

- **Caching value:** Individual chunk summaries can be cached and reused
- **Monitoring:** Should track map vs reduce usage ratio
- **Prompt engineering:** Quality depends heavily on map/reduce prompts
- **Configurable:** Threshold for map-reduce activation should be tunable

## Implementation

**Key files:**

- `src/mcp_web/summarizer.py` - Core summarization logic
- `src/mcp_web/chunker.py` - Document chunking for map phase
- `src/mcp_web/prompts.py` - Map and reduce prompt templates

**Configuration:**

```python
SummarizerSettings(
 map_reduce_threshold: int = 8000, # Tokens to trigger map-reduce
 max_chunk_tokens: int = 4000, # Map phase chunk size
 reduce_chunk_tokens: int = 8000, # Reduce phase input size
 max_summary_tokens: int = 1000, # Target summary length
 enable_parallel: bool = True, # Parallel map phase
)
```

**Prompt patterns:**

_Map phase:_

```text
Summarize the following section of a larger document.
Focus on key points and maintain technical accuracy.
[If query provided: "Pay special attention to: {query}"]

Section:
{chunk_text}
```

_Reduce phase:_

```text
Combine the following chunk summaries into a cohesive final summary.
Eliminate redundancy while preserving unique information from each chunk.

Chunk summaries:
{combined_summaries}
```

## References

- [LangChain Summarization](https://python.langchain.com/docs/use_cases/summarization)
- [Map-Reduce Prompting Pattern](https://www.promptingguide.ai/techniques/decomposition)
- ["Lost in the Middle" Research](https://arxiv.org/abs/2307.03172)
- Related ADR: [0006-chunk-size-and-overlap.md](0006-chunk-size-and-overlap.md)
- Related ADR: [0007-tiktoken-token-counting.md](0007-tiktoken-token-counting.md)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-15 | Initial proposal and acceptance | Cascade |
| 2025-10-15 | Implemented in v0.1.0 | Cascade |
