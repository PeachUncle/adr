### **ADR-025: Choice of OpenAI Agent Toolkit Implementation Pattern**

**Date:** 2025-10-11

**Status:** Decided

**Supersedes:** [ADR-002: Choice of AI Provider](./002-choice-of-ai-provider.md)

### **Context**

The PlumbingPOC application requires intelligent handling of customer quote requests and business triage analysis. Initial implementations used basic form submissions and manual review processes, but to improve user experience and operational efficiency, we need AI-powered assistance.

Key requirements:
- Streamlined quote collection with minimal user friction
- Automated triage and prioritization of service requests
- Cost-effective AI usage to maintain profitability
- Deterministic workflows where possible to reduce reliance on expensive models

The OpenAI Agent Toolkit provides a framework for building structured AI agents with tools, handoffs, and guardrails. This ADR establishes the implementation pattern to ensure cost efficiency and reliability.

### **Decision**

We will adopt the OpenAI Agent Toolkit for quote and triage agents, following these key principles:

1. **Static Questions First**: Use predefined, deterministic question flows from `serviceDefinitions.ts` before invoking AI
2. **AI Fallback Only**: Call AI models only when static questions are insufficient for completion
3. **Cheap Model Selection**: Use `gpt-4o-mini` for follow-up questions and `gpt-4o` for complex analysis requiring higher reasoning
4. **Tool-Based Determinism**: Implement domain-specific tools for leak assessment, emergency detection, complexity calculation, etc.
5. **Structured Outputs**: Define explicit output schemas for reliable, machine-readable results
6. **Guardrails**: Implement content filters to keep conversations focused on legitimate plumbing services

Implementation includes:
- QuoteAgent: Handles customer quote collection with static questions → decision node → AI clarification → submission
- TriageAgent: Analyzes requests for priority scoring and profitability assessment

### **Consequences**

*   **Pros:**
    *   **Cost Optimization:** Static logic and cheap models significantly reduce AI API costs
    *   **Reliability:** Deterministic tools provide consistent results for common scenarios
    *   **User Experience:** Smooth quote flows with AI assistance only when needed
    *   **Maintainability:** Modular agent design with clear separation of concerns
    *   **Scalability:** Agent Toolkit framework supports future expansion and specialization

*   **Cons:**
    *   **Implementation Complexity:** Requires careful design of static flows and tool integrations
    *   **Testing Overhead:** Need to validate both static and AI paths thoroughly
    *   **Model Limitations:** Cheap models may have lower accuracy for edge cases
    *   **Dependency on OpenAI:** Tied to OpenAI's Agent Toolkit ecosystem

### **Alternatives Considered**

1. **Pure AI Implementation**: Use GPT models for entire quote/triage process. Rejected due to high costs and potential inconsistency.
2. **No AI Enhancement**: Maintain manual processes. Rejected as it doesn't meet user experience and efficiency goals.
3. **Alternative AI Frameworks**: Consider other agent platforms. Rejected due to existing OpenAI integration (ADR-002) and ecosystem maturity.
4. **Expensive Models Only**: Use GPT-4 or GPT-5 for all interactions. Rejected due to cost concerns for a small business application.

This pattern balances cost efficiency with intelligent automation, ensuring the application remains profitable while providing modern AI capabilities.
