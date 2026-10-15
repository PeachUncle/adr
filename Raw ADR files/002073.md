# ADR-0005: Chatkit RAG Integration Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** chatkit-rag
- **Context:** Need to integrate OpenAI Chatkit widgets with existing RAG backend for the Physical AI Book website, supporting both authenticated and guest users while maintaining static site compatibility.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement a three-tier architecture with:
- **Frontend**: Docusaurus React components using @openai/chatkit-react widgets
- **Backend**: Python services using openai-chatkit SDK to connect to RAG system
- **Data Layer**: Qdrant vector store for RAG content, Neon Postgres for user sessions
- **Integration**: Adapter pattern to bridge Chatkit requests with Qdrant vector search
- **Session Management**: Differentiated handling for authenticated (persistent) vs guest (temporary) users
- **Error Handling**: Circuit breaker pattern with graceful degradation

## Consequences

### Positive

- Clear separation of concerns between frontend, backend, and data layers
- Supports both authenticated and guest users with appropriate session management
- Maintains static site compatibility for GitHub Pages deployment
- Leverages official Chatkit widgets for reliable chat functionality
- Provides fallback mechanisms when RAG backend is unavailable
- Scalable architecture that can handle multiple concurrent users

### Negative

- Additional complexity from three-tier architecture vs simpler approaches
- Dependency on external Chatkit service which may introduce vendor lock-in
- Increased operational complexity with multiple data stores (Qdrant + Neon Postgres)
- Potential latency from multiple service hops in the request chain
- Additional infrastructure costs for external services

## Alternatives Considered

Alternative Architecture A: Custom chat UI with direct RAG integration
- Pros: More control over UI, fewer service dependencies
- Cons: More development effort, less reliable chat functionality, violates requirement to use Chatkit widgets

Alternative Architecture B: Serverless functions with edge deployment
- Pros: Potentially lower latency, better scaling
- Cons: More complex session management, potential compatibility issues with static hosting

Alternative Architecture C: Monolithic architecture combining frontend and backend
- Pros: Simpler deployment, fewer service boundaries
- Cons: Tightly coupled components, harder to maintain, doesn't follow separation of concerns principle

## References

- Feature Spec: ../../specs/5-chatkit-rag/spec.md
- Implementation Plan: ../../specs/5-chatkit-rag/plan.md
- Related ADRs: ADR-0004 (frontend-backend integration strategy)
- Evaluator Evidence: ../../history/prompts/chatkit-rag/002-create-implementation-plan.plan.prompt.md