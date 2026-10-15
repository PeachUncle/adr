# ADR 001: Multi-Provider AI Strategy with Automatic Fallback

**Status:** Accepted
**Date:** September 8, 2025
**Deciders:** Mohit Tiwari
**Tags:** ai, reliability, cost-optimization

---

## Context

The Mohit AI platform relies heavily on large language models (LLMs) for core SDR functionality:
- Real-time conversation generation during AI calls
- BANT qualification extraction from transcripts
- Sentiment analysis and insight generation
- Follow-up message personalization

**Problem:** Dependence on a single AI provider creates several risks:
1. **Availability Risk:** API downtime = complete system outage
2. **Rate Limiting:** Sudden traffic spikes hit API limits
3. **Cost Risk:** Pricing changes could make product unviable
4. **Performance Variance:** Quality/latency degrades unpredictably

**Real-World Example (August 2025):**
During development testing, OpenAI experienced a 2-hour outage. All AI call attempts failed, demonstrating single point of failure.

---

## Decision

Implement a **multi-provider AI strategy** with automatic fallback between OpenAI GPT-4 (primary) and Google Gemini Pro (secondary).

### Architecture:

```javascript
// AI Service Factory Pattern
class AIServiceFactory {
  providers = [
    { name: 'openai', priority: 1, healthScore: 100 },
    { name: 'google', priority: 2, healthScore: 100 }
  ];

  async generateCompletion(prompt) {
    for (const provider of this.getSortedProviders()) {
      try {
        return await provider.complete(prompt);
      } catch (error) {
        this.recordFailure(provider);
        continue; // Try next provider
      }
    }
    throw new Error('All AI providers failed');
  }
}
```

### Fallback Triggers:
- **Immediate:** HTTP 429 (rate limit), 503 (service unavailable)
- **Circuit Breaker:** 3 consecutive failures → switch for 15 minutes
- **Cost-Based:** If hourly spend >$200, route to cheaper provider

---

## Considered Alternatives

### Alternative 1: Single Provider (OpenAI Only)
**Pros:**
- Simpler codebase (no abstraction layer)
- Consistent quality (GPT-4 is best-in-class)
- Easier prompt tuning (single API)

**Cons:**
- ❌ No resilience against outages
- ❌ Vendor lock-in
- ❌ No cost optimization options

**Rejection Reason:** Unacceptable availability risk for production system

### Alternative 2: Fully Redundant Multi-Cloud
**Pros:**
- Maximum redundancy
- Best performance (route to fastest)

**Cons:**
- ❌ 2x cost (pay for two providers always)
- ❌ Complex state management
- ❌ Prompt drift (models behave differently)

**Rejection Reason:** Cost outweighs benefit for current scale

### Alternative 3: On-Premise LLM (Self-Hosted)
**Pros:**
- Full control
- No API rate limits
- Potentially lower cost at scale

**Cons:**
- ❌ Requires GPU infrastructure ($$$)
- ❌ Model quality lags GPT-4/Gemini
- ❌ Operational complexity (model updates, monitoring)

**Rejection Reason:** Not viable for early-stage product

---

## Consequences

### Positive:

✅ **Availability:** 99.95% uptime (vs 99.5% single provider)
  - Math: P(both down) = 0.005 * 0.005 = 0.000025 = 99.9975% uptime

✅ **Cost Optimization:** Can route to cheaper provider during peak usage
  - Gemini is 24x cheaper for input tokens ($1.25 vs $30 per 1M)
  - Estimated savings: $500/month at 10,000 calls/month

✅ **Performance Hedging:** If OpenAI is slow, auto-route to Gemini

✅ **Negotiation Leverage:** Not locked into one vendor for pricing

### Negative:

⚠️ **Quality Variance:** GPT-4 scores 89% on BANT extraction, Gemini scores 82%
  - Mitigation: Use GPT-4 for 95% of traffic, Gemini only for fallback
  - Monitor quality metrics per provider

⚠️ **Increased Complexity:** Abstraction layer adds code paths
  - Mitigation: Comprehensive testing, clear logging

⚠️ **Prompt Compatibility:** Must maintain prompts that work across both
  - Mitigation: Shared prompt library, A/B test on both providers

### Neutral:

💭 **Monitoring Overhead:** Must track health of multiple providers
  - Required anyway for production reliability

---

## Implementation

### Phase 1: Core Factory (Completed Sep 10, 2025)
- [x] Abstract AIServiceFactory interface
- [x] OpenAI adapter (`src/services/ai/openaiService.js`)
- [x] Google AI adapter (`src/services/ai/googleAIService.js`)
- [x] Health check system

### Phase 2: Fallback Logic (Completed Sep 15, 2025)
- [x] Circuit breaker pattern
- [x] Provider health scoring
- [x] Automatic failover

### Phase 3: Monitoring (Completed Sep 22, 2025)
- [x] Provider latency tracking
- [x] Cost attribution by provider
- [x] Quality metrics dashboard

---

## Validation

### Test Results (September 2025):

**Simulated Outage Test:**
- Forced OpenAI to return 503 errors for 10 minutes
- Result: 100% of calls successfully failed over to Gemini
- Average latency impact: +200ms (acceptable)

**Quality Comparison:**
```sql
SELECT
  provider,
  AVG(bant_accuracy) as avg_accuracy,
  AVG(call_duration_sec) as avg_duration,
  AVG(cost_usd) as avg_cost
FROM ai_calls
WHERE created_at >= '2025-09-01'
GROUP BY provider;

-- Results:
-- openai | 0.89 | 320s | $0.42
-- google | 0.82 | 340s | $0.18
```

**Decision:** Keep GPT-4 as primary (quality worth the cost), use Gemini for fallback only.

---

## Future Considerations

### Potential Additions:
- **Anthropic Claude 3:** Strong reasoning, good at structured output
  - Wait for pricing to stabilize (currently $15/$75 per 1M tokens)

- **Self-Hosted Fallback:** Mistral or Llama 3 for basic qualification
  - Consider if monthly AI costs exceed $5,000

- **Cost-Based Routing:** Route simple tasks to cheaper model
  - Example: Sentiment analysis → GPT-3.5-turbo ($0.50/1M)
  - Example: BANT extraction → GPT-4 ($30/1M)

### Metrics to Monitor:
- Provider cost as % of revenue (target: <15%)
- Quality degradation during fallback (target: <5% delta)
- Fallback frequency (target: <2% of requests)

---

## References

- OpenAI API Reliability: https://status.openai.com
- Google Gemini Pricing: https://ai.google.dev/pricing
- Circuit Breaker Pattern: https://martinfowler.com/bliki/CircuitBreaker.html

---

**Author:** Mohit Tiwari
**Last Review:** October 15, 2025
