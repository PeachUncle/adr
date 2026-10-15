# ADR-008: Vector Database Strategy

## Status
Accepted

## Date
2025-12-29

## Context
The RAG system requires a vector database to store document embeddings for similarity search. The decision involves choosing between different vector databases and considering free tier limitations, scalability, and integration complexity. The system needs to store document chunks with their embeddings for efficient retrieval.

## Decision
We will use Qdrant Cloud Free Tier with a collection named `book_chunks` to store document embeddings. This approach provides a managed vector database solution with reasonable limits for the educational use case.

## Alternatives Considered
- **Pinecone**: Managed vector database with robust features
  - Pros: Mature product, good performance, good documentation
  - Cons: No free tier, higher cost, potential overkill for educational use
- **Weaviate Cloud**: Alternative managed vector database
  - Pros: Open-source, good performance, hybrid search capabilities
  - Cons: Free tier limitations, learning curve
- **Local Vector Store**: Use local vector storage (e.g., FAISS, HNSW)
  - Pros: Full control, no external dependencies
  - Cons: Infrastructure management, scaling challenges, persistence concerns
- **Supabase Vector**: Vector extension to PostgreSQL
  - Pros: Single database solution, good integration with existing tools
  - Cons: Limited free tier, potentially less optimized for vector operations

## Consequences
### Positive
- Managed service reduces operational overhead
- Free tier suitable for educational use case
- Good performance for similarity search
- Supports metadata storage with embeddings
- Easy integration with Python ecosystem

### Negative
- Free tier limitations on vector count and storage
- Potential rate limits affecting user experience
- Vendor lock-in to Qdrant Cloud
- Possible migration needed if scaling requirements increase

## Migration Path
If free tier limits are exceeded, we can migrate to:
- Qdrant Cloud paid tier
- Alternative vector databases with data export/import
- Self-hosted Qdrant instance

## References
- specs/002-rag-chatbot-gemini/plan.md
- specs/002-rag-chatbot-gemini/research.md