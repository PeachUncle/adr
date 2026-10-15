# ADR-0013: AI Chatbot Architecture and OpenAI Agents SDK Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-01
- **Feature:** 001-physical-ai-robotics-book
- **Context:** The need to enhance the RAG chatbot with intelligent, dynamic responses and context awareness, leveraging the OpenAI Agents SDK within the existing FastAPI/React ecosystem. The goal is to provide sophisticated conversational capabilities and improved user experience through explicit referencing of RAG results.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement a hybrid RAG-Agent architecture using:
- **Agent Framework**: OpenAI Agents SDK for intelligent response generation, multi-turn reasoning, and tool use.
- **Backend**: FastAPI for core RAG services, agent orchestration, and API endpoints.
- **Vector Database**: Qdrant for efficient retrieval of relevant documents.
- **Embedding Model**: Gemini API for generating vector representations of text.
- **Frontend**: ChatKit/React for the user interface, integrating with the new agent capabilities and displaying "selected text functionality."
- **Key Functionality**: The system will support "selected text functionality" to highlight or directly reference retrieved RAG content in agent responses, providing transparent sourcing and improved context.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- More intelligent and context-aware chatbot responses.
- Improved user experience through explicit referencing of RAG results.
- Leverages a powerful agent SDK for advanced conversational patterns.
- Reusability of existing RAG components (Qdrant, Gemini, FastAPI).
- Alignment with the existing technology stack (Python, FastAPI, React).

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

- Increased complexity of backend architecture due to agent orchestration and state management.
- Potential for higher LLM token usage and associated costs, requiring careful monitoring and optimization.
- Increased integration effort between OpenAI Agents SDK, FastAPI, and frontend components.
- Debugging and tracing agent behavior can be more challenging.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

- **Rely solely on RAG without an explicit agent framework**:
    - **Why rejected**: Simpler architecture, but would lack sophisticated conversational capabilities, multi-turn reasoning, and advanced tool use offered by an agent SDK. Would struggle with complex queries requiring multiple steps or external interactions.
- **Use a different agent framework (e.g., LangChain, LlamaIndex agents)**:
    - **Why rejected**: Could offer different features/ecosystems, but would require evaluating integration complexity, learning curve, and community support against OpenAI Agents SDK. OpenAI Agents SDK was chosen for its direct integration with OpenAI models and its focus on robust agent primitives.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/001-physical-ai-robotics-book/spec.md
- Implementation Plan: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/001-physical-ai-robotics-book/plan.md
- Related ADRs:
    - ADR-0006: User Data Management and Storage
    - ADR-0007: Frontend Framework and Structure
    - ADR-0008: API Design and Security
    - ADR-0009: Text Selection Strategy
    - ADR-0010: RAG System Model Choice and Hybrid Search Strategy
    - ADR-0012: FastAPI RAG Backend Framework
- Evaluator Evidence: /home/abdullahiqbal/Abdullah/hackathon-book-project/history/prompts/001-physical-ai-robotics-book/0029-integrate-openai-agents-sdk-with-rag-chatbot-plan.plan.prompt.md