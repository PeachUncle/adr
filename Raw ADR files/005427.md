# ADR 001: Why OpenRouter Instead of Direct APIs

**Date:** 2025-10-13
**Status:** Accepted

## Context

Need LLM for AI tutor with access to 50+ lessons. Requirements:
- Long context support (handle multiple lessons)
- High-quality responses
- Model flexibility
- Reliability with fallback
- Cost-effectiveness

Options considered:
- Direct APIs (OpenAI, Anthropic, Google separately)
- OpenRouter (unified API for all)
- LangChain (framework layer)

## Decision

We chose **OpenRouter** as our LLM provider.

## Rationale

### 1. Unified API for Multiple Models

Access to 100+ models through single interface:
- `anthropic/claude-3.5-sonnet` - Best for reasoning and code
- `openai/gpt-4-turbo` - Good all-rounder
- `google/gemini-pro` - Largest context window (1M tokens)
- `meta-llama/llama-3-70b` - Open source, cost-effective

### 2. Flexibility

- Change models without code changes (just update `.env`)
- Test different models easily
- Choose best model for specific questions
- Future-proof: new models auto-available

### 3. Reliability

- Automatic fallback mechanism
- If Claude unavailable → switches to GPT-4
- Load balancing across providers
- Better uptime than single provider

### 4. Cost Optimization

- Competitive pricing (sometimes cheaper than direct)
- Pay only for usage
- Can choose cheaper models for simple queries
- No minimum commitments

### 5. Developer Experience

- Single API key for everything
- Unified documentation
- Consistent error handling
- Easy integration with FastAPI

## Consequences

### Advantages

✅ **Model flexibility** - Easy to switch between Claude, GPT-4, Gemini
✅ **Automatic fallback** - Better reliability
✅ **Cost optimization** - Choose model per task
✅ **Single API key** - Simpler configuration
✅ **Future-proof** - New models automatically available
✅ **Vendor independence** - Not locked to one provider

### Disadvantages

⚠️ **Additional layer** - Extra hop in request chain
⚠️ **Vendor dependency** - Relying on OpenRouter service
⚠️ **Slight markup** - ~5-20% over direct API costs
⚠️ **Rate limits** - Subject to OpenRouter's limits

## Alternatives Considered

### Option 1: Direct APIs (OpenAI, Anthropic, Google)

**Pros:**
- No middleman
- Slightly cheaper (no markup)
- Direct relationship with provider

**Cons:**
- Need 3+ different API keys
- Different API formats for each
- Manual fallback implementation
- More complex configuration
- Harder to switch models

**Why rejected:** Loss of flexibility too significant for our use case where we want to experiment with different models.

### Option 2: LangChain

**Pros:**
- Rich feature set out of box
- Built-in chains and agents
- Good for complex workflows

**Cons:**
- Overengineered for our needs
- Steep learning curve
- More dependencies
- Harder to customize

**Why rejected:** Too complex for simple chat interface. OpenRouter + FastAPI gives us more control with less complexity.

## Implementation Notes

**Configuration** (`backend/config.py`):
```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"
FALLBACK_MODEL = "google/gemini-pro"
```

**Fallback Logic** (`backend/services/openrouter_service.py`):
```python
try:
    result = await self._send_request(model=selected_model)
except Exception:
    result = await self._send_request(model=self.fallback_model)
```

**Model Selection** (Frontend):
- User can choose model via `ModelSelector` component
- Default model used if none selected
- Model info shown in response metadata

## Future Considerations

### If OpenRouter Becomes Problematic:

1. **Create abstraction layer** - Service interface that OpenRouter implements
2. **Add direct API implementations** - Can plug in OpenAI/Anthropic services
3. **Gradual migration** - Switch one model at a time
4. **Zero downtime** - Because of layered architecture

### Monitoring Plan:

- Track response times per model
- Monitor token costs
- Log fallback frequency
- Compare quality metrics

### Cost Analysis:

Will review quarterly:
- Total OpenRouter costs
- vs Direct API costs
- Factor in development time saved
- Decide if markup worth the convenience

## Related Decisions

- ADR 002: Railway deployment choice
- ADR 003: (Future) Database selection
- ADR 004: (Future) Caching strategy

## References

- OpenRouter docs: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- Model pricing: [https://openrouter.ai/models](https://openrouter.ai/models)
- FastAPI integration: See `backend/services/openrouter_service.py`
