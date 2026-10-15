# ADR-0010: Use OpenAI GPT-4 as Default LLM

**Status:** Superseded

**Date:** 2025-10-15

**Deciders:** Core team

**Tags:** architecture, llm, quality

---

## Context

The mcp-web tool requires a Large Language Model for abstractive summarization. The choice of LLM significantly impacts:

1. **Summary quality:** Accuracy, coherence, relevance
2. **Cost:** Token pricing varies 10-100x between models
3. **Latency:** Response time affects user experience
4. **Capabilities:** Context window size, instruction following, language support

Key requirements:

- High-quality summaries (coherent, accurate, relevant)
- Large context window (handle long documents)
- Reliable API (high uptime, stable)
- Reasonable cost for typical usage
- Configurable (not locked to single provider)

Available LLM options as of Oct 2025:

- **OpenAI:** GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic:** Claude 3 (Opus, Sonnet, Haiku)
- **Open source:** Llama 3, Mistral, Qwen
- **Other providers:** Cohere, AI21, etc.

> **Superseded:** This decision is superseded by [ADR-0017](0017-switch-default-llm-to-llama3.md), which sets `llama3.2:3b` via Ollama as the default LLM to eliminate external quota dependencies during testing.

## Decision

We will use **OpenAI GPT-4-turbo** as the default LLM with configurable model selection:

### Default Configuration

```python
model = "gpt-4-turbo-preview"
temperature = 0.3 # Deterministic summaries
max_tokens = 1000 # Default summary length
```

### Model Selection Strategy

1. **Default:** GPT-4-turbo (best quality/cost balance)
2. **Fast mode:** GPT-3.5-turbo (cheaper, faster, lower quality)
3. **Quality mode:** GPT-4 (highest quality, highest cost)
4. **Configurable:** Users can specify any model via config

### Rationale for GPT-4-turbo

- **Quality:** Superior summarization vs GPT-3.5 or open-source models
- **Context window:** 128k tokens (handles very long documents)
- **Cost:** $10/1M input tokens, $30/1M output tokens (reasonable)
- **Speed:** Faster than base GPT-4
- **Reliability:** OpenAI has best API uptime and stability

## Alternatives Considered

### Alternative 1: GPT-3.5-turbo Default

**Description:** Use cheaper GPT-3.5-turbo as default model

**Pros:**

- **Much cheaper:** $0.50/$1.50 per 1M tokens (10x cheaper)
- **Faster:** ~2-3x faster response times
- **Good enough:** Acceptable quality for many use cases

**Cons:**

- **Lower quality:** Noticeably worse summarization
- **Smaller context:** 16k tokens (requires more map-reduce)
- **Less capable:** Weaker instruction following
- **User expectations:** Tool marketed for quality

**Reason for rejection:** Quality is primary differentiator, cost is acceptable

### Alternative 2: Claude 3 Opus Default

**Description:** Use Anthropic's Claude 3 Opus as default

**Pros:**

- **Quality:** Comparable or better than GPT-4
- **Long context:** 200k tokens (largest available)
- **Ethical AI:** Anthropic's constitutional AI approach
- **Good instruction following:** Strong capabilities

**Cons:**

- **Cost:** $15/$75 per 1M tokens (5x more expensive)
- **API stability:** Newer provider, more rate limiting
- **Lower adoption:** Less user familiarity
- **Integration complexity:** Different API patterns

**Reason for rejection:** Cost too high for default, but supported as option

### Alternative 3: Local Open-Source Models (Llama 3)

**Description:** Use local models like Llama 3 70B

**Pros:**

- **Privacy:** No data leaves user's machine
- **No API costs:** Free after initial setup
- **Customizable:** Can fine-tune for specific use cases
- **No rate limits:** Limited only by hardware

**Cons:**

- **Quality:** Significantly worse than GPT-4
- **Hardware requirements:** Needs GPU (expensive, not portable)
- **Slow:** Without good GPU, very slow
- **Setup complexity:** Installation, model management
- **Maintenance burden:** Model updates, optimization

**Reason for rejection:** Quality and UX requirements not met for default

### Alternative 4: Multi-Model Ensemble

**Description:** Use multiple models and combine/vote on results

**Pros:**

- **Robustness:** Reduces single-model failure risk
- **Quality:** Ensemble may outperform single model
- **Redundancy:** Fallback if one provider down

**Cons:**

- **Cost:** 2-3x API costs
- **Latency:** 2-3x slower (unless parallel, but still increased)
- **Complexity:** Combining strategies, conflict resolution
- **Overkill:** Single quality model sufficient

**Reason for rejection:** Cost and complexity not justified

## Consequences

### Positive Consequences

- **Best-in-class quality:** GPT-4-turbo provides excellent summaries
- **Large context:** 128k tokens minimizes map-reduce overhead
- **Good cost-quality tradeoff:** Acceptable cost for quality delivered
- **Stable API:** OpenAI has mature, reliable infrastructure
- **Wide adoption:** Users familiar with GPT-4 capabilities
- **Configurable:** Easy to swap models via configuration

### Negative Consequences

- **Cost:** ~$0.01-0.05 per summary (mitigated by caching)
- **API dependency:** Requires OpenAI API key and internet
- **Rate limits:** Subject to OpenAI rate limiting
- **Privacy:** Content sent to OpenAI (GDPR considerations)
- **Lock-in risk:** Heavy reliance on one provider

### Neutral Consequences

- **Model evolution:** GPT-4-turbo will be superseded eventually
- **Monitoring:** Should track API costs and usage
- **Fallback strategy:** Should support degraded mode if API unavailable
- **Multi-provider:** Should maintain abstraction for easy model swapping

## Implementation

**Key files:**

- `src/mcp_web/summarizer.py` - LLM client and summarization logic
- `src/mcp_web/config.py` - Model configuration settings
- `src/mcp_web/prompts.py` - Model-specific prompt templates

**Dependencies:**

- `openai >= 1.40.0` - OpenAI Python client
- `anthropic >= 0.34.0` - Anthropic client (optional, for Claude support)

**Configuration:**

```python
SummarizerSettings(
 model: str = "gpt-4-turbo-preview",
 provider: str = "openai", # openai, anthropic, local
 api_key: str = os.getenv("OPENAI_API_KEY"),
 temperature: float = 0.3, # Low for consistent summaries
 max_tokens: int = 1000, # Target summary length
 top_p: float = 1.0,
 presence_penalty: float = 0.0,
 frequency_penalty: float = 0.0,
)
```

**Model registry:**

```python
SUPPORTED_MODELS = {
 "openai": [
 "gpt-4-turbo-preview",
 "gpt-4",
 "gpt-3.5-turbo",
 "gpt-4o",
 ],
 "anthropic": [
 "claude-3-opus",
 "claude-3-sonnet",
 "claude-3-haiku",
 ],
 "local": [
 "llama-3-70b",
 "mistral-large",
 ]
}
```

**Cost tracking:**

```python
# Track token usage and costs
metrics.log_llm_call(
 model="gpt-4-turbo-preview",
 input_tokens=3500,
 output_tokens=850,
 cost=0.045, # Calculated from pricing
 latency_ms=4200,
)
```

## References

- [OpenAI Model Pricing](https://openai.com/pricing)
- [GPT-4 Technical Report](https://openai.com/research/gpt-4)
- [Claude 3 Model Card](https://www.anthropic.com/claude)
- [Llama 3 Model Card](https://ai.meta.com/llama/)
- [LLM Benchmarks (LMSYS Chatbot Arena)](https://chat.lmsys.org/?leaderboard)
- Related ADR: [0008-map-reduce-summarization.md](0008-map-reduce-summarization.md)
- Related ADR: [0011-enable-streaming-output.md](0011-enable-streaming-output.md)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-15 | Initial proposal and acceptance | Cascade |
| 2025-10-15 | Implemented in v0.1.0 | Cascade |
