# ADR: V2 Gamification Architecture

* Status: Proposed
* Date: 2025-04-19

## Context

The V2 specification introduces a complex gamification element (Req 3.5) involving a multi-stage puzzle, an interactive AI agent leveraging philosophical texts, personalization based on user data and behavior, UI transformations, and potentially collective elements. This requires a robust architecture beyond the core Next.js/Supabase stack.

## Decision

We will implement the gamification features using a modular architecture centered around a dedicated **MCP (Model Context Protocol) Server** and leveraging Supabase for state persistence.
1.  **AI Agent Logic & State:** A new MCP server (likely Node.js or Python) will be created to:
    *   Manage the AI agent's persona and conversation state.
    *   Interact with an external LLM API (e.g., OpenAI, Anthropic) via libraries like LangChain/LlamaIndex.
    *   Query a Vector Database containing embeddings of philosophical texts.
    *   Access user registration/profile data from Supabase for personalization.
    *   Determine AI responses, puzzle progression, and potential UI effects.
2.  **Vector Database:** Use Supabase's `pgvector` extension initially for storing philosophical text embeddings due to its integration. Evaluate dedicated vector databases (e.g., Pinecone, Weaviate) if performance or scalability become issues. A separate process will be needed for text ingestion and embedding.
3.  **User Progress & State:** Store user-specific puzzle progress (current stage, completed steps, flags, interaction history) in a dedicated Supabase table (e.g., `user_puzzle_progress`) linked to the user's profile. The MCP server will read/write to this table.
4.  **Frontend Interaction:** The Next.js frontend will communicate with the MCP server (via WebSocket or HTTP) to send user inputs and receive AI responses and state updates. Client-side logic will handle UI transformations based on the received state.
5.  **Notifications & Triggers:** Supabase Edge Functions will be used for scheduled or event-triggered actions like sending delayed cryptic emails (Req 3.5.12) or processing specific puzzle events based on database changes.
6.  **User Activity Tracking:** Basic tracking via Supabase Analytics. Custom tracking (page views, puzzle interactions) logged to a Supabase table via client-side events or middleware, accessible by the MCP server for personalization.

## Consequences

*   **Pros:**
    *   Isolates the complex, potentially resource-intensive gamification logic from the core web application.
    *   Allows the AI agent service to be scaled, updated, or even replaced independently.
    *   Enables the use of specialized tools and libraries best suited for AI/LLM interaction (Python/Node.js ecosystems, LangChain, vector DB clients).
    *   Provides a clear interface (MCP) between the frontend and the gamification backend.
    *   Leverages Supabase for persistent state management, which is already part of the stack.
*   **Cons:**
    *   Introduces an additional service (the MCP server) to build, deploy, and maintain.
    *   Requires defining and managing the MCP interface.
    *   Increases overall system complexity compared to keeping all logic within the Next.js app (which is likely infeasible for this feature set).
    *   Potential latency in communication between the frontend, MCP server, LLM, and databases.
    *   Requires infrastructure for hosting the MCP server and potentially the vector database (if not using `pgvector`).