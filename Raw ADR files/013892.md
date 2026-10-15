# ADR-012: Backend API Architecture

## Status
Accepted

## Date
2025-12-29

## Context
The RAG system requires a backend API to handle queries, manage sessions, and coordinate with external services (vector database, AI provider). The API architecture impacts scalability, maintainability, and integration with the frontend. The system needs to support both query operations and session management.

## Decision
We will implement a FastAPI backend with two primary endpoints:
- **/query**: Handles RAG queries with support for selected text, modes (strict/augment), and returns {answer, retrieved[]}
- **/chatkit/session**: Manages conversation context and session state
- The API will be designed for serverless deployment with proper rate limiting and session management.

## Alternatives Considered
- **Node.js/Express**: Alternative JavaScript-based API
  - Pros: Familiar to frontend developers, good ecosystem
  - Cons: Performance considerations for AI integration, different async patterns
- **Go-based API**: High-performance Go backend
  - Pros: Excellent performance, good for API services
  - Cons: Different ecosystem, learning curve for team
- **Serverless Functions**: Individual functions for each endpoint
  - Pros: Cost-effective scaling, no server management
  - Cons: Cold start issues, state management complexity
- **GraphQL API**: Alternative to REST endpoints
  - Pros: Flexible queries, single endpoint
  - Cons: More complex for simple use case, learning curve

## Consequences
### Positive
- FastAPI provides excellent performance for AI integration
- Good async support for external API calls
- Built-in documentation and validation
- Python ecosystem compatibility with AI tools
- Easy testing and development workflow

### Negative
- Cold start issues with serverless deployment
- Additional dependency management
- Python-specific operational considerations
- Potential performance issues if not properly optimized

## Security and Rate Limiting
- Implement rate limiting per IP/session
- Validate input to prevent injection attacks
- Use proper authentication if needed in future
- Monitor API usage and performance

## References
- specs/002-rag-chatbot-gemini/plan.md
- specs/002-rag-chatbot-gemini/contracts/rag-api.yaml
- specs/002-rag-chatbot-gemini/data-model.md