# ADR-002: Streaming Translation Architecture

## Status

**Accepted** - 2026-01-07

## Context

Luminote needs to provide progressive, block-level translation rendering to
users. Long documents may take 30+ seconds to translate fully, and waiting for
complete translation before showing results creates a poor user experience.

Key requirements:

- Users should see translated blocks as they become available
- Frontend should update UI progressively without full page reload
- Backend should stream translation results efficiently
- Connection should be resilient to temporary network issues
- Cost should be predictable (one API call per block)

We need to choose a streaming technology that:

- Works well with FastAPI backend
- Integrates easily with SvelteKit frontend
- Is supported by GitHub Copilot patterns
- Handles errors gracefully

## Decision

We will use **Server-Sent Events (SSE)** for streaming translation results from
backend to frontend.

### Architecture

```
┌──────────┐                    ┌──────────┐                    ┌──────────┐
│ Frontend │                    │ Backend  │                    │ Provider │
│          │                    │          │                    │   API    │
└────┬─────┘                    └────┬─────┘                    └────┬─────┘
     │                               │                               │
     │ POST /api/v1/translate/stream │                               │
     │───────────────────────────────>                               │
     │                               │                               │
     │ Accept: text/event-stream     │                               │
     │                               │                               │
     │                               │ For each content block:       │
     │                               │                               │
     │                               │ POST /translate               │
     │                               │──────────────────────────────>│
     │                               │                               │
     │                               │ <─────────────────────────────│
     │                               │ Translation response          │
     │                               │                               │
     │ SSE: data: {"block_id": 1,    │                               │
     │            "translated_text"} │                               │
     │<───────────────────────────────│                               │
     │                               │                               │
     │ (Repeat for each block)       │                               │
     │                               │                               │
     │ SSE: event: done              │                               │
     │<───────────────────────────────│                               │
     │                               │                               │
```

### Backend Implementation

```python
# backend/app/api/v1/endpoints/translate.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.translation_service import TranslationService
import json

router = APIRouter()

@router.post("/stream")
async def stream_translation(request: TranslationRequest):
    """
    Stream translation results block-by-block.

    Returns SSE stream with events:
    - data: Block translation completed
    - error: Translation error for specific block
    - done: All blocks processed
    """

    async def event_generator():
        translation_service = TranslationService()

        try:
            async for result in translation_service.translate_blocks(
                content_blocks=request.content_blocks,
                target_language=request.target_language,
                provider=request.provider,
                model=request.model,
                api_key=request.api_key
            ):
                # Send block result
                yield f"data: {json.dumps(result.dict())}\n\n"

            # Send completion event
            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            # Send error event
            error_data = {"error": str(e), "code": "TRANSLATION_ERROR"}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

### Frontend Implementation

```typescript
// frontend/src/lib/utils/translation-stream.ts

export interface BlockTranslation {
  block_id: string;
  translated_text: string;
  metadata?: Record<string, any>;
}

export async function streamTranslation(
  request: TranslationRequest,
  onBlock: (translation: BlockTranslation) => void,
  onError: (error: Error) => void,
  onComplete: () => void
): Promise<void> {
  const response = await fetch('/api/v1/translate/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const translation = JSON.parse(data);
            onBlock(translation);
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        } else if (line.startsWith('event: done')) {
          onComplete();
          return;
        } else if (line.startsWith('event: error')) {
          const nextLine = lines[lines.indexOf(line) + 1];
          if (nextLine?.startsWith('data: ')) {
            const errorData = JSON.parse(nextLine.slice(6));
            onError(new Error(errorData.error));
          }
          return;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
```

### Event Types

**Data Event (Block Translation):**

```
data: {"block_id": "1", "translated_text": "Translated content", "metadata": {...}}

```

**Error Event:**

```
event: error
data: {"error": "Translation failed", "code": "RATE_LIMIT_EXCEEDED", "block_id": "3"}

```

**Done Event:**

```
event: done
data: {}

```

## Consequences

### Positive

- **Progressive Rendering**: Users see results immediately as blocks complete
- **Simple Protocol**: SSE is simpler than WebSockets
- **HTTP-Based**: Works with standard HTTP infrastructure (proxies, load
  balancers)
- **Browser Support**: Native EventSource API in browsers
- **Unidirectional**: Matches our use case (server → client only)
- **Reconnection**: Built-in automatic reconnection in EventSource
- **Copilot-Friendly**: Well-documented patterns for SSE in FastAPI and fetch
  API

### Negative

- **Unidirectional**: Cannot send updates from client mid-stream (acceptable for
  our use case)
- **Text-Only**: Must JSON-encode all data (acceptable overhead)
- **Connection Limits**: Browsers limit concurrent SSE connections (6 per
  domain)
- **No Binary**: Cannot stream binary data (not needed for our use case)

### Trade-offs

- Chose SSE over WebSockets for simplicity (we only need server → client
  streaming)
- Chose streaming over polling for better performance and user experience
- Chose block-level over character-level streaming for better structure and
  error handling

## Alternatives Considered

### 1. WebSockets

**Pros:**

- Bidirectional communication
- Binary data support
- Lower latency

**Cons:**

- More complex to implement
- Harder to work with HTTP infrastructure
- Bidirectional capability not needed
- More difficult for Copilot to generate correct code

**Verdict:** Rejected - SSE is simpler for our unidirectional use case

### 2. Long Polling

**Pros:**

- Works with any HTTP client
- Simple to implement

**Cons:**

- Inefficient (repeated requests)
- Higher latency
- More server load
- Poor user experience for long translations

**Verdict:** Rejected - Not suitable for real-time streaming

### 3. Regular HTTP with Polling

**Pros:**

- Very simple
- Works everywhere
- Easy to cache

**Cons:**

- Not real-time
- Wasteful polling
- Bad user experience
- Difficult to determine when translation is complete

**Verdict:** Rejected - Doesn't meet progressive rendering requirement

### 4. Character-Level Streaming

**Pros:**

- More fine-grained progress
- Smoother UI updates

**Cons:**

- Much higher overhead
- Harder to track block boundaries
- More complex error handling
- Difficult to version/rollback

**Verdict:** Rejected - Block-level is sufficient and more structured

## Implementation Notes

### For GitHub Copilot

When implementing streaming endpoints:

1. **Always use async generators:**

```python
async def event_generator():
    async for item in process_items():
        yield f"data: {json.dumps(item)}\n\n"
```

1. **Set correct headers:**

```python
StreamingResponse(
    generator(),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache"}
)
```

1. **Handle errors gracefully:**

```python
try:
    async for result in process():
        yield result
except Exception as e:
    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

### Error Handling

- Individual block failures should emit error events but continue streaming
- Critical failures (invalid API key) should close stream with error event
- Frontend should display partial results even on stream failure
- Implement retry logic for transient errors

### Testing

**Backend Test:**

```python
def test_stream_translation(client):
    response = client.post(
        "/api/v1/translate/stream",
        json={"content_blocks": [...], ...}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

    events = []
    for line in response.iter_lines():
        if line.startswith(b"data: "):
            events.append(json.loads(line[6:]))

    assert len(events) > 0
```

**Frontend Test:**

```typescript
test('streamTranslation handles events', async () => {
  const blocks: BlockTranslation[] = [];

  await streamTranslation(
    request,
    (block) => blocks.push(block),
    (error) => console.error(error),
    () => console.log('done')
  );

  expect(blocks.length).toBeGreaterThan(0);
});
```

## Performance Considerations

- **Backpressure**: Service should wait if client is slow to consume
- **Buffering**: Disable proxy buffering for real-time delivery
- **Timeouts**: Set appropriate timeout for long translations
- **Concurrency**: Limit concurrent streams per user
- **Cleanup**: Ensure generators are properly closed on disconnect

## References

- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Feature Specifications - Progressive Rendering](../feature-specifications.md#12-progressive-block-level-rendering)

## Changelog

- 2026-01-07: Initial version accepted
