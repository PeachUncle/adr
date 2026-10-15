# ADR-003: Vector Storage Strategy (pgvector + Pinecone Hybrid)

## Status

**Accepted** - January 2026

## Context

Sentinel RFP requires vector similarity search for:

- Semantic search in knowledge library
- Document chunk retrieval
- Similar question matching
- Response caching

We need to choose between:

1. **pgvector**: PostgreSQL extension for vectors
2. **Pinecone**: Managed vector database
3. **Weaviate**: Self-hosted vector DB
4. **Hybrid**: Combination approach

### Scale Requirements (Phase 1-2)

- ~100K vectors per tenant (avg)
- ~1M total vectors (10 tenants)
- Query latency <100ms P95
- 1536-dimensional embeddings (OpenAI)

### Scale Requirements (Phase 3+)

- ~1M vectors per tenant
- ~50M total vectors (50 tenants)
- Query latency <50ms P95
- Multi-region requirements

## Decision

**Implement pgvector as primary vector store for Phase 1-2, with architecture ready for Pinecone migration at scale.**

### Rationale

| Factor                     | pgvector          | Pinecone             |
| -------------------------- | ----------------- | -------------------- |
| Setup complexity           | Low (extension)   | Medium (new service) |
| Cost (Phase 1)             | $0 (included)     | ~$70/month           |
| Railway native             | Yes               | External service     |
| Performance (1M vectors)   | Good              | Excellent            |
| Performance (10M+ vectors) | Degrades          | Excellent            |
| Metadata joins             | Native SQL        | Separate query       |
| Backup/recovery            | PostgreSQL native | Pinecone managed     |

### Implementation

#### Phase 1-2: pgvector

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Vector columns in relevant tables
ALTER TABLE library_entries
ADD COLUMN content_embedding vector(1536);

ALTER TABLE chunks
ADD COLUMN content_embedding vector(1536);

-- IVFFlat index for approximate nearest neighbor
CREATE INDEX idx_library_embedding ON library_entries
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

-- Performance tuning
SET ivfflat.probes = 10;  -- Higher = more accurate, slower
```

#### Vector Service Abstraction

```typescript
// Abstraction layer for future migration
interface VectorStore {
  upsert(vectors: VectorRecord[]): Promise<void>;
  search(query: number[], topK: number, filter?: Filter): Promise<SearchResult[]>;
  delete(ids: string[]): Promise<void>;
}

class PgVectorStore implements VectorStore {
  async search(query: number[], topK: number, filter?: Filter) {
    return this.prisma.$queryRaw`
      SELECT id, content,
             1 - (content_embedding <=> ${query}::vector) as similarity
      FROM library_entries
      WHERE organization_id = ${filter.organizationId}
        AND status = 'active'
      ORDER BY content_embedding <=> ${query}::vector
      LIMIT ${topK}
    `;
  }
}

// Future: Swap implementation
class PineconeStore implements VectorStore {
  async search(query: number[], topK: number, filter?: Filter) {
    const results = await this.pinecone.query({
      vector: query,
      topK,
      filter: { organizationId: filter.organizationId },
      includeMetadata: true,
    });
    return results.matches;
  }
}
```

### Performance Benchmarks

| Operation         | pgvector (100K) | pgvector (1M) | Target |
| ----------------- | --------------- | ------------- | ------ |
| Single query      | 15ms            | 45ms          | <100ms |
| Batch query (10)  | 50ms            | 180ms         | <500ms |
| Insert (1K batch) | 200ms           | 300ms         | <1s    |

### Migration Trigger to Pinecone

Migrate when ANY of these occur:

- Query latency P95 >100ms
- Vector count per tenant >1M
- Total vectors >10M
- Multi-region requirement

### Migration Strategy

```
Phase 1: Dual-Write
├── Write to both pgvector and Pinecone
├── Read from pgvector (primary)
└── Validate Pinecone results match

Phase 2: Shadow Read
├── Write to both
├── Read from both, compare
└── Log discrepancies

Phase 3: Pinecone Primary
├── Write to both (pgvector as backup)
├── Read from Pinecone
└── Keep pgvector for joins/fallback

Phase 4: Cleanup
├── Stop writing to pgvector vectors
├── Keep metadata in PostgreSQL
└── Full Pinecone for similarity search
```

## Consequences

### Positive

- **Simplicity**: Single database for Phase 1-2
- **Cost**: No additional service costs initially
- **Transactions**: Vectors and metadata in same transaction
- **Joins**: Can join vectors with relational data
- **Railway native**: No external dependencies

### Negative

- **Scale limit**: Performance degrades >1M vectors
- **Features**: Missing Pinecone features (hybrid search, sparse vectors)
- **Migration work**: Will need to migrate eventually

### Mitigations

- Build abstraction layer from day one
- Monitor vector counts and latency
- Document migration procedure
- Test migration in staging before needed

## Index Configuration

```sql
-- For 100K vectors: lists = 100
-- For 1M vectors: lists = 1000
-- Rule: sqrt(num_vectors)

CREATE INDEX idx_library_embedding ON library_entries
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

-- Tune probes based on recall/latency tradeoff
-- probes = 1: Fast, ~60% recall
-- probes = 10: Balanced, ~95% recall
-- probes = lists: Slow, 100% recall (exact)
SET ivfflat.probes = 10;
```

## Related ADRs

- ADR-002: Multi-Agent RAG Architecture
- ADR-006: LLM Provider Abstraction

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [ANN Benchmarks](http://ann-benchmarks.com/)
