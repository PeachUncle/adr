# 002: Use Groq API for LLM

## Status

Accepted

## Date

2025-12-15

## Context

The application requires a Large Language Model (LLM) to generate personalized book recommendations based on user interests. Several options were available:

Alternatives considered:
1. **OpenAI API (GPT-3.5/GPT-4)** - Industry standard, high quality
   - ❌ High cost per request
   - ❌ Rate limits on free tier
   - ❌ User initially got quota errors (429)

2. **Groq API** - Fast inference on open-source models
   - ✅ Free tier with generous limits
   - ✅ Extremely fast inference (< 1s)
   - ✅ Multiple open-source models (Llama 3.1/3.2)
   - ✅ Compatible with LangChain
   - ⚠️ Occasional model deprecation

3. **Local LLM (Ollama)** - Fully local inference
   - ❌ Requires local GPU/resources
   - ❌ Slower inference
   - ❌ Harder to deploy

4. **Anthropic Claude** - High-quality alternative
   - ❌ No free tier
   - ❌ More expensive than OpenAI

## Decision

Use Groq API as the primary LLM provider with `langchain-groq` integration.

Configuration:
- Default model: `llama-3.1-8b-instant`
- Supported models: `llama-3.1-8b-instant`, `llama-3.2-11b-text`, `llama-3.2-90b-text`
- Temperature: Configurable (default 0.8)
- API key: Environment variable `GROQ_API_KEY`

Features implemented:
- Model selection dropdown in UI
- Graceful handling of deprecated models
- Error messages for API failures
- Caching to reduce API calls

## Consequences

### Positive
- **Cost-effective**: Free tier sufficient for development and demo
- **Fast**: Sub-second inference times improve UX
- **Flexible**: Multiple models to choose from
- **Open-source models**: Llama models are well-regarded
- **Compatible**: Works seamlessly with LangChain
- **User satisfaction**: Resolved initial OpenAI quota issues

### Negative
- **Model stability**: Models occasionally deprecated (had to migrate from mixtral-8x7b-32768)
- **Quality variance**: May not match GPT-4 quality for complex tasks
- **Vendor lock-in**: Switching providers requires code changes
- **Free tier limits**: May hit limits with heavy usage

### Neutral
- Requires API key management
- Need to stay updated on model availability

### Risks
- **Model deprecation**: Monitor for deprecation notices
  - Mitigation: Support multiple models, graceful fallback
- **Rate limiting**: May hit limits during peak usage
  - Mitigation: Caching, user feedback on errors
- **Service availability**: Dependent on Groq uptime
  - Mitigation: Clear error messages

## Implementation Notes

Key files:
- `src/book_recommender/config.py`: GROQ_API_KEY, SUPPORTED_MODELS
- `src/book_recommender/recommender.py`: ChatGroq initialization
- `.env`: API key storage (gitignored)

Model migration history:
1. Initial: `mixtral-8x7b-32768` (deprecated)
2. Attempted: `llama-3.1-70b-versatile` (decommissioned)
3. Current: `llama-3.1-8b-instant` (stable, fast)

Error handling:
- Detect "decommissioned" in error messages
- Show user-friendly message to select different model
- Log errors with Sentry integration

## References

- [Groq Documentation](https://console.groq.com/docs)
- [LangChain Groq Integration](https://python.langchain.com/docs/integrations/providers/groq)
- [Llama 3.1 Announcement](https://ai.meta.com/blog/meta-llama-3-1/)
