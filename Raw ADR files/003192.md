# ADR: AI Integration — LangChain.js + Azure/OpenAI models

- Status: Accepted
- Date: 2025-11-11
- Owners: AI Team <ai-team@example.com>
- Links: PDR: `#PDRs/2025-10-30_MVP_Chat_PDR.md`, LangChain docs, OpenAI/Azure docs

## Context

The product roadmap includes an AI-powered Chat that can generate Projects, TaskLists and Tasks. This requires integrating LLMs with conversation history, tools (ProjectService), and safe prompt engineering.

Evidence:
- LangChain.js provides composable agents, chains, memory, streaming, and provider integrations (docs reviewed).
- OpenAI/Azure docs provide model APIs with streaming, embeddings, and function calling.

## Decision

We will implement the AI orchestration layer using LangChain.js (LangChain JS) on the backend. For LLM provider we will integrate with Azure OpenAI (or OpenAI via API) depending on enterprise requirements — Azure is preferred if we require managed corporate compliance and tenancy.

Key points:
- Use LangChain.js for prompt templates, memory (conversation history), chaining and tool orchestration.
- Use Azure OpenAI / OpenAI Responses API for model calls, streaming responses and embeddings.
- Persist chat history in `ChatMessages` table; only send minimal required context to the model and redact PII.

## Alternatives Considered

- Call provider APIs directly without LangChain: Pros: less dependency; Cons: lose orchestration, memory and reuse of tooling.
- Use a hosted RAG product (Pinecone + managed RAG): Pros: quicker for retrieval; Cons: higher cost and less control.

## Consequences

- Positive: Reusable orchestration, robust tool integrations, easier to implement RAG and agents.
- Negative: Additional dependency (LangChain) and operational monitoring for token/cost usage. Requires careful prompt-cost monitoring and token limits.

## Implementation Plan

- [ ] Add `langchain` packages and provider adapters
- [ ] Create `ChatService` with the following responsibilities:
  - [ ] Persona prompt and system messages
  - [ ] Conversation history storage and memory management (truncate or summarise history)
  - [ ] Call Azure/OpenAI with streaming (or poll fallback)
  - [ ] Orchestrate call to `ProjectService` when model indicates project generation
- [ ] Store minimal transcript in `ChatMessages` and mark generated artifacts
- [ ] Instrument metrics: token_count_total, ai_calls_total, ai_errors_total, avg_response_latency

## Test Cases

- [ ] Unit tests for prompt templates and parsers
- [ ] Integration test: send sample prompt, verify Azure/OpenAI called and response saved
- [ ] Privacy test: ensure no PII is included in model calls for test prompts containing PII markers

## Traceability

| RF ID | RF Description | RNF | Component(s) Impacted |
|-------|----------------|-----|-----------------------|
| RF-AI-001 | Generate Project from Chat | Accuracy/Cost | ChatService, AI provider |

## Effort Estimate

Dev:
- LangChain integration and basic agent: 8h
- Streaming + ProjectService orchestration: 6h
- Tests and monitoring: 4h

Ops:
- Configure Azure/OpenAI credentials in CI/CD: 1h
- Set up cost alerts and dashboards: 2h
