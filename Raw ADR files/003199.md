# ADR-002: Choice of Primary AI Provider

**Date:** 2025-09-02

**Status:** Decided & Implemented

## Context

The PlumbingPOC platform's core value proposition includes intelligent features that automate lead qualification and analysis. This requires a powerful Large Language Model (LLM) for two key tasks:
1.  Dynamically generating context-aware follow-up questions to fully qualify a user's request (`requestController.js`).
2.  Analyzing a completed request to provide a triage summary and profitability score for the business owner (`triageController.js`).

## Decision

We will use the **OpenAI API**, specifically leveraging GPT-4 class models (`gpt-4`, `gpt-4-1106-preview`), as our primary provider for all generative AI tasks.

## Consequences

*   **Pros:**
    *   **State-of-the-Art Performance:** At the time of development, GPT-4 models provided best-in-class reasoning and instruction-following, critical for the accuracy of both the triage and follow-up features.
    *   **Robust JSON Mode:** The ability to force JSON output (`response_format: { type: 'json_object' }` in `triageController.js`) is essential for creating reliable, deterministic AI components that adhere to a strict data contract. This eliminates fragile string parsing.
    *   **Mature Ecosystem:** OpenAI's API is well-documented with mature client libraries (`openai` package), making integration straightforward.

*   **Cons:**
    *   **Cost:** GPT-4 models are premium services. Every AI Triage and ambiguous follow-up call incurs a direct, variable cost. This must be monitored closely to ensure feature profitability.
    *   **Latency:** Calls to powerful models can have higher latency, which could impact user experience in real-time conversational flows.
    *   **Vendor Lock-in:** Our prompts and logic are tailored to the behavior of OpenAI's models. Switching providers (e.g., to Anthropic's Claude) would require re-prompting and re-testing.
    *   **Data Privacy:** Sending customer request data to a third-party API requires careful handling. The application mitigates this by not sending explicit PII (as per `PlumbingAgentRequirements.md`), but the policy must be strictly maintained.

*   **Alternatives Considered:**
    *   **Anthropic Claude:** A very strong competitor, particularly for its large context windows and strong reasoning. At the time of implementation, OpenAI's ecosystem and JSON mode were deemed slightly more mature for this specific use case.
    *   **Self-hosted Open Source Models (e.g., Llama 3):** This would provide maximum data privacy and potentially lower long-term cost. However, it was rejected due to the immense initial infrastructure and MLOps overhead (GPU provisioning, model deployment, monitoring), which was out of scope for a rapid POC.
