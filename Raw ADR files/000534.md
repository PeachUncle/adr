# ADR-002: LLM Provider Choice

## Status

Accepted

## Date

16-12-2025

## Context

Alembic requires an LLM for:
- Generating tarot interpretations (primary use case)
- Handling follow-up conversations about readings
- Future: Personalization based on user history

Requirements:
- High quality interpretations with distinctive voice
- Cost-effective for a bootstrapped project
- Reasonable latency (< 10s for generation)
- API stability and availability
- Large context window for conversation history

## Decision

**Production**: xAI Grok 4.1 Fast via LiteLLM
**Development**: Ollama (local) for free testing

### Pricing Comparison (as of December 2025)

| Provider | Model | Input $/1M | Output $/1M | Context |
|----------|-------|------------|-------------|---------|
| xAI | Grok 4.1 Fast | $0.20 | $0.50 | 2M tokens |
| Anthropic | Claude 4 Sonnet | $3.00 | $15.00 | 200K tokens |
| OpenAI | GPT-4o | $2.50 | $10.00 | 128K tokens |
| xAI | Grok 4 | $3.00 | $15.00 | 256K tokens |

### Cost Analysis

Estimated per-reading cost (assuming ~2K tokens):
- Grok 4.1 Fast: ~$0.001-0.002
- Claude Sonnet: ~$0.03-0.04
- GPT-4o: ~$0.02-0.03

**Grok is 15-30x cheaper** for our use case.

## Alternatives Considered

### Claude 4 Sonnet

- Pros: Excellent reasoning, nuanced responses, great safety
- Cons: 15x more expensive, smaller context window
- Decision: Rejected primarily on cost

### GPT-4o

- Pros: Well-tested, large ecosystem, good performance
- Cons: 12x more expensive, smaller context
- Decision: Rejected on cost

### Grok 4 (Full)

- Pros: Most capable Grok model
- Cons: Same price as Claude, overkill for our needs
- Decision: Rejected - Fast model sufficient

### Self-hosted (Ollama production)

- Pros: Zero marginal cost, full control
- Cons: Requires GPU server, maintenance burden, quality concerns
- Decision: Rejected for production, used for development

## Implementation

```python
from litellm import acompletion

# Production
response = await acompletion(
    model="xai/grok-4.1-fast",
    messages=[...],
    api_key=settings.XAI_API_KEY,
)

# Development (when XAI_API_KEY not set)
response = await acompletion(
    model="ollama/llama3.2",
    messages=[...],
    api_base="http://localhost:11434",
)
```

## Consequences

### Positive

1. **Cost Savings**: 15-30x cheaper than alternatives
2. **Large Context**: 2M tokens allows extensive conversation history
3. **Distinctive Voice**: Grok's personality suits the tarot domain
4. **Fast Development**: Ollama provides free local testing
5. **Flexibility**: LiteLLM allows easy provider switching

### Negative

1. **Younger API**: Less battle-tested than OpenAI/Anthropic
2. **Smaller Community**: Fewer examples and resources
3. **Potential Instability**: xAI is a newer company
4. **Quality Variance**: May need more prompt engineering

### Neutral

1. **Voice Consistency**: Grok's edgy tone needs calibration for tarot
2. **Fallback Strategy**: Should implement fallback to local model
3. **Rate Limits**: Need to monitor and handle appropriately

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| xAI API instability | Implement retry logic and fallback to Ollama |
| Cost unexpectedly high | Monitor usage, implement response caching |
| Quality issues | Extensive prompt testing, user feedback loop |
| Rate limiting | Implement queue and backoff strategy |

