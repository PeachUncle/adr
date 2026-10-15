# ADR-001: Use Vertex AI Gemini for LLM Operations

## Status
Accepted

## Context
The Sales Intelligence Automation System requires LLM capabilities for:
- Account scoring and prioritization
- Natural language to SQL conversion
- Email reply generation
- Semantic search and insights

We needed to choose an LLM provider that:
- Integrates well with GCP infrastructure
- Supports structured JSON output
- Has reasonable cost and latency
- Provides reliable API access

## Decision
Use **Vertex AI Gemini 2.5 Pro** as the exclusive LLM provider for all AI operations.

### Rationale
1. **GCP Integration**: Native integration with GCP services, uses Application Default Credentials (ADC)
2. **Cost Efficiency**: Competitive pricing compared to OpenAI/Anthropic
3. **Structured Output**: Supports JSON mode via `response_mime_type`
4. **Reliability**: Google's infrastructure provides high availability
5. **No API Keys**: Uses ADC, reducing secret management overhead

## Consequences

### Positive
- ✅ Seamless integration with existing GCP infrastructure
- ✅ No additional API key management required
- ✅ Lower operational overhead
- ✅ Consistent authentication model across services
- ✅ Good performance for structured outputs

### Negative
- ❌ Vendor lock-in to Google Cloud Platform
- ❌ Limited model choice compared to multi-provider approach
- ❌ Requires GCP project and Vertex AI API enabled

### Mitigations
- Abstracted model provider interface allows future migration if needed
- Mock mode available for testing without Vertex AI
- Clear documentation on Vertex AI setup and configuration

## Alternatives Considered

### OpenAI GPT-4
- **Pros**: Excellent model quality, wide adoption
- **Cons**: Requires API keys, higher cost, external dependency
- **Decision**: Rejected due to additional secret management and cost

### Anthropic Claude
- **Pros**: Strong reasoning capabilities
- **Cons**: Requires API keys, external dependency
- **Decision**: Rejected for same reasons as OpenAI

### Multi-Provider Approach
- **Pros**: Flexibility, vendor independence
- **Cons**: Increased complexity, more secrets to manage
- **Decision**: Rejected due to added complexity without clear benefit

## Implementation Notes
- Model provider abstraction in `ai/models.py`
- Default model: `gemini-2.5-pro` (configurable via `LLM_MODEL` env var)
- Uses `response_mime_type="application/json"` for structured outputs
- Error handling for model unavailability with fallback options

## References
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini Model Guide](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)

