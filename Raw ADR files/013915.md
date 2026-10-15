# ADR 004: Qdrant Cloud for Vector Database

**Status:** Accepted  
**Date:** 2025-11-27  
**Decision Makers:** Hassan RJ, Development Team

---

## Context

The RAG (Retrieval-Augmented Generation) chatbot requires a vector database to:
- Store embeddings of book content chunks
- Perform semantic similarity search for relevant context retrieval
- Scale to handle thousands of document embeddings
- Provide fast query performance (< 100ms for retrieval)
- Integrate easily with Python backend
- Support filtering by metadata
- Require minimal setup and maintenance

**Alternatives Considered:**
1. **Qdrant Cloud** - Purpose-built vector database with cloud hosting
2. **Pinecone** - Managed vector database service
3. **Weaviate** - Open-source vector search engine
4. **ChromaDB** - Lightweight vector database
5. **PostgreSQL + pgvector** - PostgreSQL extension for vector similarity

---

## Decision

We will use **Qdrant Cloud** (free tier) as the vector database for RAG embeddings.

---

## Consequences

### Positive

1. **Free Tier**: 1GB storage free tier sufficient for educational project
2. **Managed Service**: No infrastructure setup or maintenance required
3. **Performance**: Optimized for fast similarity search with HNSW algorithm
4. **Python Client**: Official `qdrant-client` Python library with great DX
5. **REST API**: HTTP API for flexibility if needed
6. **Metadata Filtering**: Support for filtering vectors by metadata fields
7. **Collections**: Organize embeddings into separate collections
8. **Open Source**: Self-host option available if needed in future
9. **Scalability**: Easy to upgrade to paid tier if project grows
10. **Documentation**: Excellent documentation and examples

### Negative

1. **Vendor Lock-in**: Cloud-hosted service dependency
2. **Cold Starts**: Free tier may experience latency after inactivity
3. **Storage Limits**: 1GB limit (sufficient for ~50,000 chunks at 768 dimensions)
4. **Feature Limits**: Some advanced features only in paid tiers
5. **Geographic Latency**: Server location may add latency for some users

### Mitigation

- **Vendor Lock-in**: Qdrant is open-source, can self-host if needed
- **Cold Starts**: Acceptable for educational project, implement warming if needed
- **Storage Limits**: Monitor usage, optimize chunk sizes, upgrade if necessary
- **Feature Limits**: Free tier features sufficient for current requirements
- **Latency**: Use content chunking strategy to minimize retrieval time

---

## Implementation Notes

### Setup
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# Create collection
client.create_collection(
    collection_name="book_content",
    vectors_config=VectorParams(
        size=768,  # Gemini embedding dimension
        distance=Distance.COSINE
    )
)
```

### Data Ingestion
```python
# Chunk text and create embeddings
chunks = chunk_text(book_content, chunk_size=500, overlap=50)
embeddings = embed_texts(chunks)  # Using Gemini embeddings

# Upload to Qdrant
points = [
    {
        "id": idx,
        "vector": embedding,
        "payload": {
            "text": chunk,
            "chapter": chapter_name,
            "section": section_name
        }
    }
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
]

client.upload_points(collection_name="book_content", points=points)
```

### RAG Retrieval
```python
async def retrieve_context(query: str, top_k: int = 3):
    query_embedding = await embed_text(query)
    
    results = client.search(
        collection_name="book_content",
        query_vector=query_embedding,
        limit=top_k
    )
    
    return [hit.payload["text"] for hit in results]
```

### Environment Variables
```env
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

### Collection Strategy
- **Collection Name**: `book_content`
- **Vector Size**: 768 (Gemini embedding dimension)
- **Distance Metric**: Cosine similarity
- **Metadata**: chapter, section, page number

### Chunking Strategy
- **Chunk Size**: 500 tokens (~2000 characters)
- **Overlap**: 50 tokens (~200 characters)
- **Rationale**: Balance between context preservation and retrieval precision

---

## Performance Benchmarks

- **Ingestion**: ~1000 chunks in ~30 seconds
- **Query Latency**: ~50-100ms for top-3 retrieval
- **Storage**: ~50KB per chunk (text + embedding + metadata)
- **Capacity**: Can store ~20,000 chunks in 1GB free tier

---

## References

- [Qdrant Official Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Project Constitution](./constitution.md) - Principle 5: Performance Requirements
- [Implementation Plan](../../plans/002-rag-chatbot-backend.md)
