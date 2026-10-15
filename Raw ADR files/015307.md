# ADR-003: Memory Architecture

## Status
**Approved** — 2024-12-21

## Context

The Reachy Home Assistant needs to remember information about family members to provide personalized, contextual assistance. This includes:

1. **Short-term memory**: Current conversation context
2. **Long-term memory**: Learned facts, preferences, patterns
3. **Episodic memory**: Notable events and interactions
4. **Semantic memory**: General knowledge about the household

### Key Requirements
- Remember that Nico prefers to be reminded about homework after snack
- Know that Patrick has a recurring Tuesday meeting
- Recall that last week there was a discussion about the science project
- Learn patterns like "Izzy usually forgets lunch on Mondays"

## Decision

**Hybrid memory system using PostgreSQL for structured data and pgvector for semantic retrieval.**

### Memory Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Memory System                             │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  Working Memory  │  │  Episodic Memory │  │ Semantic Mem  │  │
│  │  (In-process)    │  │  (PostgreSQL)    │  │ (pgvector)    │  │
│  │                  │  │                  │  │               │  │
│  │  - Current conv  │  │  - Interactions  │  │ - Embeddings  │  │
│  │  - Active user   │  │  - Observations  │  │ - Similarity  │  │
│  │  - Session state │  │  - Events        │  │ - Retrieval   │  │
│  └──────────────────┘  └──────────────────┘  └───────────────┘  │
│           │                     │                    │           │
│           └─────────────────────┼────────────────────┘           │
│                                 ▼                                │
│                    ┌────────────────────────┐                    │
│                    │   Retrieval Manager    │                    │
│                    │   - Query expansion    │                    │
│                    │   - Relevance ranking  │                    │
│                    │   - Time decay         │                    │
│                    └────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Types

| Type | Storage | Retention | Example |
|------|---------|-----------|---------|
| Working | In-memory | Session only | "We're discussing homework" |
| Episodic | PostgreSQL + vector | Permanent (with decay) | "Helped Nico with math 3/15" |
| Semantic | pgvector | Permanent | "Nico likes dinosaurs" |
| Procedural | PostgreSQL | Permanent | "Reminder pattern for Izzy" |

### Schema Design

```sql
-- Core memory table
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    importance FLOAT DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Indexes for efficient retrieval
CREATE INDEX idx_memories_user ON memories(user_id);
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_embedding ON memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Observations (what Reachy notices)
CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    observer VARCHAR(50) DEFAULT 'reachy',
    subject_user_id UUID REFERENCES users(id),
    observation_type VARCHAR(50),
    content TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation history
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Retrieval Strategy

1. **Query embedding**: Convert query to vector using sentence-transformers
2. **Semantic search**: Find top-k similar memories via pgvector
3. **Time decay**: Apply recency weighting (recent = more relevant)
4. **User filtering**: Prioritize memories about current user
5. **Diversity**: Ensure variety in retrieved context

```python
async def retrieve_context(
    query: str,
    user_id: UUID,
    limit: int = 10
) -> list[Memory]:
    """Retrieve relevant memories for context."""
    embedding = embed(query)

    results = await db.execute("""
        SELECT *,
               1 - (embedding <=> $1) as similarity,
               POWER(0.99, EXTRACT(DAY FROM NOW() - created_at)) as recency
        FROM memories
        WHERE user_id = $2 OR user_id IS NULL
        ORDER BY (similarity * 0.7 + recency * 0.3) DESC
        LIMIT $3
    """, embedding, user_id, limit)

    return results
```

## Consequences

### Positive
- **Personalized interactions**: Remembers individual preferences
- **Contextual responses**: Uses relevant past interactions
- **Pattern learning**: Can identify and act on routines
- **Graceful degradation**: Works with partial memory

### Negative
- **Storage growth**: Memories accumulate over time
- **Retrieval latency**: Vector search adds ~10-50ms
- **Memory quality**: Garbage in, garbage out
- **Privacy sensitivity**: Stores personal observations

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Memory bloat | Implement consolidation (merge similar memories) |
| Stale memories | Apply time decay in retrieval ranking |
| Wrong memories | Confidence scores, user can correct |
| Privacy concerns | All local, user can view/delete memories |

## Implementation Notes

### Memory Formation
```python
async def remember(
    content: str,
    user_id: UUID,
    memory_type: str,
    importance: float = 0.5
):
    """Store a new memory."""
    embedding = embed(content)

    await db.execute("""
        INSERT INTO memories (user_id, memory_type, content, embedding, importance)
        VALUES ($1, $2, $3, $4, $5)
    """, user_id, memory_type, content, embedding, importance)
```

### Memory Consolidation (Background Job)
```python
async def consolidate_memories():
    """Merge similar memories to reduce bloat."""
    # Find clusters of similar memories
    # Combine into summarized memories
    # Archive originals
```

## Future Enhancements

1. **Forgetting curve**: Automatically fade unaccessed memories
2. **Memory importance learning**: ML model for importance scoring
3. **Cross-user patterns**: "The whole family tends to..."
4. **Explicit memory management**: "Reachy, remember that..."

## Related Decisions
- ADR-001: Data storage (PostgreSQL + pgvector)
- ADR-004: LLM strategy (memory informs prompts)
