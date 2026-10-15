# ADR-001: RAG Chatbot Technology Stack

**Status**: Accepted
**Date**: 2025-12-13

## Context

We need to build a Retrieval-Augmented Generation (RAG) chatbot system that allows users to interact with book content. The system must process Markdown files from a `/docs` folder using the context7-Mcp utility, store content in a vector database, and provide a chat interface. The system has specific constraints requiring the use of context7-Mcp for preprocessing and qdrant-mcp-server for indexing.

## Decision

We will use the following technology stack:

**Frontend**: Next.js 14 with App Router
- Reason: React-based framework with excellent SSR capabilities, strong ecosystem, and good TypeScript support

**Backend**: FastAPI with Python 3.10+
- Reason: Modern Python framework with automatic API documentation, type validation, async support, and excellent integration with ML/AI libraries

**Vector Database**: Qdrant Cloud (Free Tier)
- Reason: Dedicated vector database optimized for similarity search with good Python/JS SDKs and supports the required qdrant-mcp-server interface

**AI Service**: OpenAI API with Agent SDK
- Reason: Proven RAG capabilities, good documentation, and strong ecosystem for building AI applications

**Chat Interface**: Pusher ChatKit SDK
- Reason: Real-time chat interface SDK with React components and session management capabilities

**Embedding Model**: sentence-transformers all-MiniLM-L6-v2
- Reason: Efficient model providing 384-dimensional embeddings with good balance of speed and accuracy

## Consequences

### Positive
- Clear separation of concerns between frontend and backend services
- Strong ecosystem support for all chosen technologies
- Good performance characteristics for RAG operations
- Scalable architecture that can handle the requirements
- Compliance with project constraints (context7-Mcp, qdrant-mcp-server)

### Negative
- Additional infrastructure management for Qdrant Cloud
- Potential vendor lock-in with ChatKit and OpenAI
- Learning curve for team members unfamiliar with chosen technologies
- Qdrant Cloud Free Tier limitations may require migration later

## Alternatives

### Alternative Stack Options:
- **React + Express + Pinecone**: JavaScript ecosystem familiarity but vendor lock-in concerns
- **SvelteKit + Hono + Weaviate**: Lightweight frameworks but less ecosystem maturity
- **Remix + Node.js + MongoDB Atlas Vector Search**: Familiar JS stack but less efficient vector search

## References

- specs/rag-chatbot/spec.md
- specs/rag-chatbot/research.md
- specs/rag-chatbot/data-model.md