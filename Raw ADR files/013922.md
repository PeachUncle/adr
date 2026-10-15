# ADR-001: RAG Chatbot Architecture for AI-Native Textbook

**Status:** Accepted
**Date:** 2025-12-10

## Context

The AI-Native Textbook for Physical AI & Humanoid Robotics requires an intelligent chatbot that can answer student questions using textbook content. The system needs to support two distinct modes:
- Global mode: Answer questions using the entire textbook corpus
- Selected-text mode: Answer questions using only highlighted/selected text

The solution must maintain academic rigor, provide fast responses (under 5 seconds), achieve 90% accuracy, and handle 1,000 concurrent users. We need to decide on the architecture that balances performance, accuracy, and maintainability.

## Decision

We will implement a Retrieval-Augmented Generation (RAG) architecture using:

**Backend Stack:**
- OpenAI API for language model capabilities (gpt-3.5-turbo or gpt-4)
- Qdrant vector database for efficient similarity search
- FastAPI backend with PostgreSQL for session management
- Embedding model: OpenAI's text-embedding-3-small for cost/performance balance

**Frontend Integration:**
- React-based chat interface integrated into Docusaurus textbook
- Dual-mode context selector (global vs selected-text)
- Real-time response with source citations
- Client-side validation and fallback mechanisms

**Architecture Components:**
- Content indexing pipeline that converts textbook chapters to vector embeddings
- RAG service orchestrating retrieval and generation
- Session management for conversation context
- Accuracy validation and response quality monitoring
- Circuit breaker and retry mechanisms for resilience

## Alternatives Considered

1. **Local LLM + Vector Database:**
   - Pros: Full control, privacy, no API costs
   - Cons: Requires significant computational resources, complex deployment, slower inference

2. **Simple Chat Interface without RAG:**
   - Pros: Simpler implementation, lower cost
   - Cons: No access to textbook content, cannot meet accuracy requirements

3. **Hybrid Approach (Local + Cloud):**
   - Pros: Fallback capability, cost optimization
   - Cons: Complex architecture, additional maintenance overhead

4. **Third-party Chatbot Services (e.g., Langchain + various providers):**
   - Pros: Faster development, managed infrastructure
   - Cons: Less control over customization, potential vendor lock-in

## Consequences

**Positive:**
- High accuracy through direct textbook content access
- Fast response times using vector similarity search
- Scalable architecture supporting concurrent users
- Academic rigor maintained through proper citations
- Flexible dual-mode operation

**Negative:**
- Dependency on external APIs (OpenAI)
- Additional infrastructure complexity (vector database)
- Ongoing API costs
- Complexity of maintaining textbook content embeddings

## References

- specs/001-ai-textbook-physical-ai/plan.md
- specs/001-ai-textbook-physical-ai/research-rag.md
- specs/001-ai-textbook-physical-ai/data-model-rag.md
- specs/001-ai-textbook-physical-ai/contracts/chatbot-api.yaml