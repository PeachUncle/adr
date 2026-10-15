# ADR-0011: Enable Streaming Output for LLM Responses

**Status:** Implemented

**Date:** 2025-10-15

**Deciders:** Core team

**Tags:** architecture, ux, performance

---

## Context

LLM summarization can take significant time, especially for long documents:

- **Short documents:** 2-5 seconds
- **Medium documents:** 5-15 seconds
- **Long documents (map-reduce):** 15-60 seconds

User experience challenges:

1. **Long wait times:** No feedback during processing creates poor UX
2. **Perceived slowness:** Batch response feels slower than streaming
3. **Cancellation:** Cannot interrupt long-running operations
4. **Progress tracking:** No visibility into processing status

The Model Context Protocol (MCP) supports streaming tool outputs, allowing partial results to be displayed progressively.

Our requirements:

- Show progress to user during summarization
- Allow cancellation of long operations
- Minimize perceived latency
- Handle errors gracefully during streaming

## Decision

We will implement **streaming output** for all LLM-based operations using async generators:

### Streaming Architecture

```python
async def summarize_urls(urls: List[str], query: str) -> AsyncIterator[str]:
 """Stream summary results progressively."""
 for url in urls:
 yield f"## Fetching: {url}\n"
 content = await fetch(url)

 yield f"## Summarizing: {url}\n"
 async for chunk in llm_summarize_stream(content, query):
 yield chunk # Stream LLM tokens as they arrive

 yield "\n\n---\n\n"
```

### Streaming Levels

1. **Status updates:** Major processing steps (fetching, extracting, summarizing)
2. **LLM tokens:** Stream OpenAI/Anthropic responses token-by-token
3. **Progress indicators:** Show current document N of M
4. **Error messages:** Stream errors immediately when encountered

### Error Handling

- Errors during streaming yield error message then raise
- Partial results preserved (user sees progress before failure)
- Cancellation supported via async task cancellation

## Alternatives Considered

### Alternative 1: Batch Response Only

**Description:** Wait for complete summary, return all at once

**Pros:**

- **Simplest implementation:** No streaming logic needed
- **Easier error handling:** Atomic success/failure
- **Cleaner output:** No partial results
- **Easier testing:** Deterministic output

**Cons:**

- **Poor UX:** Long waits with no feedback (30-60s silence)
- **Perceived slowness:** Feels much slower than reality
- **No cancellation:** Must wait for completion
- **No progress:** User doesn't know if it's working or hung

**Reason for rejection:** UX requirements not met

### Alternative 2: Progress Callbacks

**Description:** Use callback functions to report progress

```python
def on_progress(stage: str, percent: float):
 print(f"{stage}: {percent}%")

summarize_urls(urls, on_progress=on_progress)
```

**Pros:**

- **Structured progress:** Percentage-based tracking
- **Flexible:** Client controls how to display progress
- **Less coupling:** Doesn't force streaming

**Cons:**

- **Not MCP-native:** Callbacks don't map to MCP streaming
- **Less elegant:** Callback hell in async code
- **No content streaming:** Progress only, not partial results
- **Complexity:** Managing callback state across async operations

**Reason for rejection:** Not aligned with MCP streaming model

### Alternative 3: Server-Sent Events (SSE)

**Description:** Use SSE protocol for streaming

**Pros:**

- **Standard protocol:** Well-defined, widely supported
- **HTTP-based:** Works through proxies/firewalls
- **Automatic reconnection:** Client can resume

**Cons:**

- **Not MCP:** MCP has own streaming protocol
- **Overkill:** More complex than needed
- **HTTP-specific:** Doesn't work for other transports

**Reason for rejection:** MCP already provides streaming mechanism

### Alternative 4: Polling-Based Status

**Description:** Client polls server for status updates

```python
status = get_status(job_id)
# {'stage': 'summarizing', 'progress': 0.6, 'done': False}
```

**Pros:**

- **Simple server:** No streaming infrastructure
- **Resilient:** Works with disconnections
- **Scalable:** Stateless requests

**Cons:**

- **High latency:** Polling interval creates delay
- **Inefficient:** Many wasteful requests
- **Complex client:** Polling logic, state management
- **Poor UX:** Delayed updates

**Reason for rejection:** Inefficient, poor UX

## Consequences

### Positive Consequences

- **Responsive UX:** Users see immediate feedback
- **Perceived speed:** Streaming feels faster (time to first byte)
- **Cancellable:** Can interrupt long operations via async cancellation
- **Progressive disclosure:** Show partial results for multiple URLs
- **Real-time monitoring:** See exactly what's happening
- **Error visibility:** Failures appear immediately, not after timeout

### Negative Consequences

- **Complex error handling:** Must handle failures mid-stream
- **Partial results:** Client may see incomplete output on errors
- **State management:** Streaming generators require careful cleanup
- **Testing complexity:** Must test streaming behavior, not just final output
- **Buffering issues:** Client must handle potentially large stream buffers

### Neutral Consequences

- **Backpressure:** AsyncIterator handles backpressure automatically
- **Resource cleanup:** Must ensure generators properly closed
- **Progress formatting:** Need consistent status message format
- **Cancellation:** Client responsible for cancelling tasks

## Implementation

**Key files:**

- `src/mcp_web/mcp_server.py` - MCP tool with streaming output
- `src/mcp_web/summarizer.py` - Streaming LLM client
- `src/mcp_web/fetcher.py` - Status updates during fetch

**Streaming pattern:**

```python
@mcp.tool()
async def summarize_urls(
 urls: List[str],
 query: Optional[str] = None
) -> AsyncIterator[str]:
 """MCP tool with streaming output."""
 for i, url in enumerate(urls, 1):
 # Status update
 yield f"\n## [{i}/{len(urls)}] Processing: {url}\n"

 try:
 # Fetch with status
 yield "Fetching content...\n"
 content = await fetch_url(url)

 # Extract with status
 yield "Extracting main content...\n"
 extracted = extract_content(content)

 # Summarize with streaming
 yield "Summarizing...\n"
 async for token in stream_summary(extracted, query):
 yield token

 yield "\n\n"

 except Exception as e:
 yield f"\n❌ Error: {str(e)}\n\n"
 # Continue with next URL
```

**OpenAI streaming:**

```python
async def stream_summary(text: str, query: str) -> AsyncIterator[str]:
 """Stream LLM summary token by token."""
 response = await openai_client.chat.completions.create(
 model="gpt-4-turbo-preview",
 messages=[...],
 stream=True # Enable streaming
 )

 async for chunk in response:
 if chunk.choices[0].delta.content:
 yield chunk.choices[0].delta.content
```

**Metrics collection:**

```python
# Track streaming performance
metrics.log_stream_event(
 event="stream_start",
 url=url,
 timestamp=time.time()
)

# ... streaming ...

metrics.log_stream_event(
 event="stream_complete",
 url=url,
 total_bytes=len(output),
 duration_ms=elapsed
)
```

## References

- [MCP Streaming Documentation](https://modelcontextprotocol.io/docs/concepts/streaming)
- [OpenAI Streaming API](https://platform.openai.com/docs/api-reference/streaming)
- [Anthropic Streaming](https://docs.anthropic.com/claude/reference/streaming)
- [Python AsyncIterator](https://docs.python.org/3/library/typing.html#typing.AsyncIterator)
- Related ADR: [0010-openai-gpt4-default-llm.md](0010-openai-gpt4-default-llm.md)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-15 | Initial proposal and acceptance | Cascade |
| 2025-10-15 | Implemented in v0.1.0 | Cascade |
