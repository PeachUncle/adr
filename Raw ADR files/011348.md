# ADR 003: Tier 0 API Gateway / Middleware - LiteLLM Proxy

*   **Status:** Proposed
*   **Date:** 2025-04-27
*   **Deciders:** Architect Mode
*   **Consulted:** `docs/project-specifications.md` v2.3 (Sections 3, 4, 5.2, 7.1), `docs/reports/litellm_vs_langchain_philograph.md`, `docs/reports/embedding_middleware_for_philograph.md`
*   **Affected:** Tier 0 Implementation, Backend Service, Search Service, Ingestion Service, Configuration Management, Migration Path (All Tiers).

## Context and Problem Statement

PhiloGraph Tier 0 needs to interact with an external cloud API (Vertex AI) for embedding generation. Future tiers will likely interact with multiple external LLM and embedding APIs. We need a consistent, manageable, and flexible way to handle these external API calls from within the local Tier 0 environment and ensure a smooth transition to cloud deployments. Key requirements include managing API keys securely, controlling costs, handling rate limits/retries, and abstracting away provider-specific SDKs/APIs.

## Decision Drivers

*   **Provider Abstraction:** Avoid hardcoding dependencies on specific provider SDKs (e.g., Google Vertex AI SDK) in the core application logic.
*   **Flexibility:** Easily switch or add new embedding/LLM providers in the future without major code changes.
*   **Centralized Management:** Manage API keys, costs, rate limits, and retries in one place.
*   **Standard Interface:** Provide a consistent interface (ideally OpenAI-compatible) for internal services to consume.
*   **Cost Control:** Enable features like cost tracking and budget limits.
*   **Operational Robustness:** Implement automatic retries and potentially fallbacks.
*   **Hybrid Strategy:** Align with the project's decision to use LiteLLM as the unified API gateway across all tiers.
*   **Specification v2.3:** Explicitly selects LiteLLM Proxy for Tier 0.

## Considered Options

1.  **LiteLLM Proxy:** An open-source proxy server specifically designed to manage calls to various LLM/embedding APIs, providing an OpenAI-compatible interface. Runs in Docker.
2.  **Direct SDK Integration:** Use the official provider SDK (e.g., `google-cloud-aiplatform`) directly within the backend/ingestion services.
3.  **Custom-Built Proxy:** Develop a bespoke proxy service to handle API calls.
4.  **LangChain (as Proxy):** Use LangChain's provider integrations and potentially LCEL to manage API calls (though LangChain is explicitly excluded from Tier 0 core logic per spec).

## Decision Outcome

**Chosen Option:** 1. LiteLLM Proxy.

**Rationale:**

*   **Purpose-Built:** LiteLLM is specifically designed for this exact problem: managing and standardizing calls to diverse LLM/embedding APIs.
*   **Provider Abstraction & Flexibility:** Supports a wide range of providers (including Vertex AI, OpenAI, Anthropic, Cohere, etc.). Switching models or providers becomes a configuration change in LiteLLM, not application code.
*   **Centralized Management:** Offers built-in features for API key management (including Virtual Keys), cost tracking, rate limiting, retries, and fallbacks.
*   **Standard Interface:** Provides an OpenAI-compatible API endpoint, which is a widely adopted standard, simplifying integration for internal services.
*   **Alignment with Strategy:** Directly implements the project's strategic decision to use LiteLLM as the unified gateway across all tiers, establishing the pattern early.
*   **Open Source & Local Deployment:** Free, open-source, and runs easily in Docker for Tier 0.
*   **Reduces Boilerplate:** Handles complexities like retry logic, specific API authentication headers, etc., reducing boilerplate code in the backend services.

**Rejection Rationale:**

*   *Direct SDK Integration:* Tightly couples the application to specific providers, making future changes difficult. Requires implementing key management, cost tracking, retries, etc., manually in the application. Violates the provider abstraction goal.
*   *Custom-Built Proxy:* Significant development effort to replicate features already available in LiteLLM. High risk and maintenance burden.
*   *LangChain (as Proxy):* While LangChain has provider integrations, using it *solely* as a proxy in Tier 0 contradicts the spec's exclusion of LangChain for core logic and doesn't align with the strategic decision to use LiteLLM as the dedicated gateway. LangChain is better suited for application-level orchestration (Tier 1+), calling *through* the LiteLLM proxy.

## Consequences

*   **Positive:**
    *   Decouples backend services from specific embedding/LLM providers.
    *   Simplifies switching or adding new providers in the future.
    *   Centralizes control over API keys, costs, and operational policies (retries, rate limits).
    *   Provides a standard OpenAI-compatible interface for internal development.
    *   Reduces boilerplate code in backend services.
    *   Establishes the core API gateway pattern required for Tier 1+ from the beginning.
*   **Negative:**
    *   Adds another service (the LiteLLM Proxy container) to manage in the Docker environment.
    *   Requires learning LiteLLM's configuration (`config.yaml`, environment variables).
    *   Introduces an additional network hop for embedding requests (internal service -> LiteLLM -> external API), though likely negligible latency impact locally.
    *   Potential single point of failure if the proxy container goes down (mitigated by Docker restart policies).

## Validation

*   Successful deployment of the LiteLLM Proxy container via Docker Compose.
*   Successful configuration of LiteLLM to route requests for an internal model name (e.g., `philo-embed`) to the Vertex AI API using appropriate credentials.
*   Backend services (Ingestion, Search) can successfully make requests to the LiteLLM Proxy's `/embeddings` endpoint and receive valid embeddings.
*   Features like Virtual Keys and basic cost logging function as expected.

## Links

*   `docs/project-specifications.md` v2.3 (Sections 3, 4, 5.2, 7.1)
*   `docs/architecture/tier0_mvp_architecture.md`
*   `docs/reports/litellm_vs_langchain_philograph.md`
*   `docs/reports/embedding_middleware_for_philograph.md`
*   [LiteLLM Documentation](https://docs.litellm.ai/)