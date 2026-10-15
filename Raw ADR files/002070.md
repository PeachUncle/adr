# ADR-0001: SDK Integration Approach for RAG Chatbot

## Status
Accepted

## Date
2025-12-17

## Context

We are building an integrated RAG chatbot for a Physical AI book that needs to work within a static site frontend and FastAPI backend architecture. The system needs to support two query modes (full-book context and user-selected text only) while maintaining strict grounding in the book content. We need to make key architectural decisions about which SDKs to use for agent orchestration and frontend chat experience.

Key constraints:
- Frontend must work with static sites (no SSR dependency)
- Backend uses FastAPI
- Need to integrate with OpenRouter API as LLM provider
- Must support dual query modes (full-book vs selected-text)
- Need to maintain content grounding

## Decision

We will use a combined SDK approach:

**Backend Agent Orchestration**: OpenAI Agents SDK
- Provides built-in tool calling capabilities for RAG operations
- Handles conversation memory and state management
- Works with OpenRouter API through OpenAI-compatible interface
- Supports creation of custom tools for vector search and context filtering

**Frontend Chat Experience**: OpenAI ChatKit SDK
- Provides pre-built chat UI components
- Handles message streaming and session management
- Designed for client-side integration in static sites
- Offers customization options for book-specific UI needs

**Integration Pattern**: Server-side RAG with backend handling all retrieval
- All vector search and content retrieval happens on backend
- Frontend communicates via API calls to backend
- Ensures consistent context handling and security
- Maintains separation of concerns between frontend and backend

## Alternatives Considered

1. **Custom RAG Pipeline vs OpenAI Agents SDK**
   - Custom approach: Build orchestration from scratch using OpenAI API directly
   - Trade-offs: More control over the RAG flow vs faster development with proven tool calling patterns

2. **Custom Chat UI vs ChatKit SDK**
   - Custom approach: Build React chat components from scratch
   - Trade-offs: Complete control over UI/UX vs faster development with proven components

3. **Client-assisted Retrieval vs Server-side RAG**
   - Client approach: Frontend makes direct calls to vector DB
   - Trade-offs: Reduced server load vs potential security and consistency concerns

## Consequences

**Positive:**
- Faster development time using proven SDKs
- Built-in tool calling and memory management from Agents SDK
- Pre-built chat components and streaming from ChatKit SDK
- Consistent context handling with server-side RAG
- Better security posture with backend-controlled retrieval
- Easier maintenance with established libraries

**Negative:**
- Vendor lock-in to OpenAI SDKs
- Potential limitations in customization
- Dependency on OpenRouter API compatibility with OpenAI SDKs
- Possible performance overhead from additional server round-trips
- Learning curve for team members unfamiliar with these SDKs

## References

- `specs/1-book-rag-chatbot/plan.md` - Implementation plan with architecture decisions
- `specs/1-book-rag-chatbot/research.md` - Research on SDK compatibility
- `specs/1-book-rag-chatbot/spec.md` - Feature specification