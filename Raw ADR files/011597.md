# ADR-002: Database Strategy - PostgreSQL + Pinecone Hybrid

**Status:** Accepted
**Date:** 2025-01-15
**Deciders:** System Architect
**Context:** Database selection for content metadata and semantic search

## Context and Problem Statement

Meta-Media-Search requires:

1. **Relational data** for content metadata, users, and relationships
2. **Vector similarity search** for semantic content matching
3. **High read throughput** for concurrent users
4. **Transaction support** for user data consistency
5. **Cost-effective scaling** as dataset grows

The system must support both traditional querying (filter by genre, year, platform) and AI-native semantic search (find content similar to user's taste profile).

## Decision Drivers

1. **Vector Search Performance:** <100ms for similarity queries across 100K+ content items
2. **ACID Guarantees:** For user accounts, ratings, and payment data
3. **Query Flexibility:** Complex joins, aggregations, and filters
4. **Operational Simplicity:** Minimize number of data stores
5. **Cost:** Optimize for startup budget (<$500/mo at 10K users)
6. **Developer Experience:** Strong ORM support, good tooling
7. **Scalability:** Handle 1M+ content items, 100K+ users

## Considered Options

### Option 1: PostgreSQL Only (with pgvector)

**Pros:**

- Single database (operational simplicity)
- ACID transactions for all data
- Excellent relational query support
- pgvector extension for vector similarity
- Cost-effective (single RDS instance)
- Strong ecosystem (ORMs, tools)

**Cons:**

- pgvector performance degrades at scale (>100K vectors)
- No specialized vector indexing (HNSW only recently added)
- Requires manual tuning for vector queries
- Read replicas needed for scale

**Cost:** ~$150/mo (db.r5.large)
**Vector Search Latency:** ~200ms @ 100K vectors, ~1s @ 1M vectors

### Option 2: PostgreSQL + Pinecone

**Pros:**

- Best-in-class vector search (<50ms @ millions of vectors)
- Automatic scaling and indexing
- PostgreSQL for relational data (proven, reliable)
- Clear separation of concerns
- Pinecone handles embedding updates efficiently

**Cons:**

- Two databases to manage (operational complexity)
- Data synchronization required
- Additional cost for Pinecone
- Potential consistency issues

**Cost:** ~$150/mo (PostgreSQL) + $70/mo (Pinecone starter) = $220/mo
**Vector Search Latency:** ~30ms @ 1M vectors

### Option 3: MongoDB + Atlas Vector Search

**Pros:**

- Single database for all data
- Native vector search support
- Flexible schema (JSON documents)
- Managed service (Atlas)

**Cons:**

- Weaker relational query support
- No ACID across collections
- Less mature vector search vs. Pinecone
- Vendor lock-in to Atlas
- Team less familiar with MongoDB

**Cost:** ~$200/mo (M30 cluster with vector search)
**Vector Search Latency:** ~100ms @ 1M vectors

### Option 4: PostgreSQL + Elasticsearch

**Pros:**

- Strong full-text search
- Good for keyword + semantic hybrid
- Scalable read throughput

**Cons:**

- Elasticsearch not optimized for vector search
- Higher operational complexity
- More expensive than Pinecone
- Overkill for our use case

**Cost:** ~$150/mo (PostgreSQL) + $150/mo (Elasticsearch) = $300/mo
**Vector Search Latency:** ~150ms @ 1M vectors

### Option 5: Neo4j (Graph Database)

**Pros:**

- Natural fit for content relationships
- Powerful graph traversal queries
- Good for recommendation algorithms

**Cons:**

- Steep learning curve
- Expensive at scale
- No native vector search
- Still need relational DB for user data
- Overkill for current requirements

**Cost:** ~$500/mo (Enterprise)
**Not suitable for vector search**

## Decision Outcome

**Chosen Option:** **PostgreSQL + Pinecone Hybrid**

### Rationale

The hybrid approach leverages each database's strengths:

- **PostgreSQL** for relational data (users, metadata, transactions)
- **Pinecone** for vector similarity search (content embeddings, user taste profiles)

This provides:

1. **Best Performance:** <50ms vector search at any scale
2. **Data Integrity:** ACID for critical user data
3. **Future-Proof:** Scales to millions of content items
4. **Cost-Effective:** Only $70/mo additional vs. pgvector performance issues
5. **Operational:** Pinecone is fully managed (no DevOps burden)

### Architecture

```
┌─────────────────────────────────────────┐
│         Application Layer                │
└────────────┬─────────────────┬──────────┘
             │                 │
             ↓                 ↓
┌────────────────────┐  ┌──────────────────┐
│    PostgreSQL      │  │     Pinecone     │
│                    │  │                  │
│  • Users           │  │  • Content       │
│  • Content         │  │    Embeddings    │
│    Metadata        │  │  • User Taste    │
│  • Platforms       │  │    Embeddings    │
│  • Viewing History │  │  • Query         │
│  • Ratings         │  │    Embeddings    │
│  • Preferences     │  │                  │
└────────────────────┘  └──────────────────┘
```

### Data Synchronization Strategy

1. **Content Creation:**

   ```typescript
   async function createContent(content: MediaContent) {
     // 1. Save metadata to PostgreSQL
     const dbContent = await db.content.create({ data: content });

     // 2. Generate embedding
     const embedding = await generateContentEmbedding(content);

     // 3. Upsert to Pinecone
     await pinecone.upsert({
       id: dbContent.id,
       values: embedding,
       metadata: {
         title: content.title,
         genres: content.genres,
         year: content.year,
         rating: content.rating,
       },
     });

     return dbContent;
   }
   ```

2. **Semantic Search:**

   ```typescript
   async function searchContent(query: string, filters: FilterSet) {
     // 1. Generate query embedding
     const queryEmbedding = await generateQueryEmbedding(query);

     // 2. Vector search in Pinecone
     const pineconeResults = await pinecone.query({
       vector: queryEmbedding,
       topK: 100,
       filter: {
         year: { $gte: filters.yearRange?.[0] },
         rating: { $gte: filters.ratingRange?.[0] },
       },
     });

     // 3. Fetch full metadata from PostgreSQL
     const contentIds = pineconeResults.matches.map(m => m.id);
     const fullContent = await db.content.findMany({
       where: { id: { in: contentIds } },
       include: { cast: true, platforms: true },
     });

     return fullContent;
   }
   ```

3. **Consistency:**
   - **Write:** Synchronous - transaction fails if either DB fails
   - **Read:** Eventually consistent - Pinecone may lag PostgreSQL by <1s
   - **Updates:** Use message queue (Bull) for bulk re-indexing

### PostgreSQL Schema Optimization

```sql
-- Indexes for common queries
CREATE INDEX idx_content_year_rating ON content(year DESC, rating DESC);
CREATE INDEX idx_content_genres ON content USING GIN(genre_ids);
CREATE INDEX idx_platform_availability ON platform_availability(platform_id, available);

-- Partial indexes for performance
CREATE INDEX idx_recent_content ON content(created_at DESC)
  WHERE created_at > NOW() - INTERVAL '30 days';

-- Materialized views for expensive aggregations
CREATE MATERIALIZED VIEW content_popularity AS
SELECT
  content_id,
  COUNT(*) as view_count,
  AVG(rating) as avg_rating
FROM viewing_history
WHERE watched_at > NOW() - INTERVAL '7 days'
GROUP BY content_id;

CREATE UNIQUE INDEX ON content_popularity(content_id);
REFRESH MATERIALIZED VIEW CONCURRENTLY content_popularity;
```

### Pinecone Index Configuration

```typescript
// Create namespace-based indexes for multi-tenancy
await pinecone.createIndex({
  name: 'media-content',
  dimension: 1536,
  metric: 'cosine',
  pods: 1,
  podType: 'p1.x1', // Starter tier
});

// Upsert with metadata filtering
await index.upsert({
  vectors: contents.map(c => ({
    id: c.id,
    values: c.embedding,
    metadata: {
      title: c.title,
      year: c.year,
      rating: c.rating,
      genres: c.genres, // Filterable
      platforms: c.platforms, // Filterable
    },
  })),
  namespace: 'production',
});

// Query with metadata filters
const results = await index.query({
  vector: queryEmbedding,
  topK: 100,
  filter: {
    year: { $gte: 2020 },
    rating: { $gte: 7.0 },
    genres: { $in: ['Action', 'Thriller'] },
  },
  includeMetadata: true,
  namespace: 'production',
});
```

### Caching Layer (Redis)

Add Redis between application and databases:

```typescript
async function getCachedContent(id: string): Promise<MediaContent> {
  // 1. Check Redis cache
  const cached = await redis.get(`content:${id}`);
  if (cached) return JSON.parse(cached);

  // 2. Cache miss - fetch from PostgreSQL
  const content = await db.content.findUnique({ where: { id } });

  // 3. Cache for 1 hour
  await redis.setex(`content:${id}`, 3600, JSON.stringify(content));

  return content;
}
```

## Consequences

### Positive

- ✅ Best vector search performance (<50ms at scale)
- ✅ ACID guarantees for critical data
- ✅ Familiar PostgreSQL for relational queries
- ✅ Pinecone handles vector scaling automatically
- ✅ Clear separation of concerns
- ✅ Can evolve independently (e.g., add pgvector for simple queries)

### Negative

- ❌ Two databases increase operational complexity
- ❌ Synchronization logic required (error handling, retries)
- ❌ Additional $70/mo cost
- ❌ Potential consistency issues (eventual consistency)
- ❌ More complex testing (mock both databases)

### Mitigation Strategies

1. **Synchronization Reliability:**
   - Use idempotent operations (upsert, not insert)
   - Implement retry logic with exponential backoff
   - Dead letter queue for failed syncs
   - Daily reconciliation job to detect drift

2. **Cost Optimization:**
   - Start with Pinecone starter ($70/mo)
   - Cache aggressively to reduce queries
   - Batch upserts to Pinecone (1000 vectors at once)
   - Monitor usage and optimize as needed

3. **Consistency:**
   - Write-through cache invalidation
   - Version numbers to detect stale data
   - Accept eventual consistency for non-critical paths

## Validation

**Success Criteria:**

- [ ] Vector search <50ms p95 latency @ 100K vectors
- [ ] PostgreSQL queries <20ms p95 for common patterns
- [ ] Sync success rate >99.9%
- [ ] Monthly cost <$250 for 100K content items
- [ ] Zero data loss in PostgreSQL
- [ ] Acceptable data lag in Pinecone (<5s p99)

**Testing Plan:**

1. Load test: 100K content items, 1K concurrent users
2. Failure simulation: Pinecone downtime, PostgreSQL replica lag
3. Consistency audit: Compare PostgreSQL and Pinecone daily
4. Cost monitoring: Track database costs weekly

## Future Considerations

### When to Add pgvector

If Pinecone costs become prohibitive (>$500/mo), consider:

- Use pgvector for simple similarity queries (<10K vectors)
- Keep Pinecone for complex queries and user embeddings
- Hybrid approach reduces Pinecone usage

### When to Add Neo4j

If relationship traversal becomes critical (e.g., "find shortest path between two movies via shared actors"):

- Add Neo4j for graph analytics
- Sync relationship data from PostgreSQL
- Use for advanced recommendation algorithms

## References

- [Pinecone Documentation](https://docs.pinecone.io/)
- [pgvector Performance Analysis](https://github.com/pgvector/pgvector#performance)
- [PostgreSQL Indexing Best Practices](https://www.postgresql.org/docs/current/indexes.html)
- [Vector Database Comparison](https://benchmark.vectorview.ai/)
