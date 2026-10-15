# ADR-1: Backend Integration Architecture

## Context

We need to integrate an existing RAG agent built with OpenAI Agents SDK with a ChatKit UI. The constraint is that we cannot modify the existing agent or UI code. We need to create a minimal FastAPI backend that serves as an integration layer between the UI and the agent.

The system already has:
- A fully built RAG agent using OpenAI Agents SDK (Python)
- Embeddings, chunking, and Qdrant vector store
- Neon database provisioned
- Chatbot UI built using ChatKit and embedded in the book
- A project-level .env file at the root

The backend must be compatible with Vercel Python Serverless Functions and remain stateless.

## Decision

We will implement a FastAPI-based backend service with the following architecture:

1. **FastAPI Application**: Main application entry point with proper CORS configuration for ChatKit UI
2. **API Routers**: Separate router for chat endpoints under `/chat` and `/chat-stream`
3. **Agent Client**: Thin wrapper around existing agent functions (black box integration)
4. **Pydantic Schemas**: Request/response validation using Pydantic models
5. **Error Handling**: Centralized exception handlers for consistent error responses
6. **Neon Logging**: Interaction metadata logging to Neon Serverless Postgres
7. **Qdrant Integration**: Read-only access to Qdrant Cloud (agent handles all vector operations)
8. **Serverless Compatibility**: Stateless design suitable for Vercel Python Functions

## Status

Accepted

## Date

2025-12-13

## Consequences

### Positive
- Maintains existing agent and UI code (satisfies constraints)
- Provides clean separation of concerns between UI, backend, and agent
- Supports both synchronous and streaming responses
- Follows modern Python web development practices
- Enables proper error handling and logging to Neon
- Allows for configuration via existing .env file
- Supports proper CORS for ChatKit UI integration
- Compatible with Vercel Python Serverless deployment
- Read-only access to Qdrant Cloud maintains agent integrity

### Negative
- Adds additional network hop between UI and agent (potential latency)
- Requires maintaining additional service layer
- Additional dependencies (FastAPI, uvicorn, psycopg2-binary, etc.)
- Statelessness constraint may limit some optimization possibilities
- Additional complexity with Neon database logging

## Alternatives

### Alternative 1: Direct UI to Agent Integration
**Approach**: Modify the UI to directly call the agent functions
**Rejected because**: Would require modifying existing UI code, which violates the constraint of not changing existing components

### Alternative 2: Node.js/Express Backend
**Approach**: Use Node.js/Express instead of Python/FastAPI
**Rejected because**: The agent is already in Python, so using Python for the backend maintains consistency and allows for easier integration with the existing agent code

### Alternative 3: Traditional Server Deployment
**Approach**: Deploy as a traditional persistent server instead of serverless
**Rejected because**: Would not meet the deployment requirements for Vercel Python Serverless Functions

### Alternative 4: Direct Qdrant Integration
**Approach**: Have the backend interact directly with Qdrant instead of through the agent
**Rejected because**: Would violate the black box agent requirement and require modifying existing RAG logic

## References

- specs/1-backend-agent-integration/spec.md
- specs/1-backend-agent-integration/plan.md
- specs/1-backend-agent-integration/research.md