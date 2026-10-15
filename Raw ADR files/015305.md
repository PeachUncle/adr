# ADR-001: Data Storage Architecture

## Status
**Approved** — 2024-12-21

## Context

The Reachy Home Assistant requires persistent storage for:

1. **Structured data**: User profiles, chores, tasks, schedules, configuration
2. **Semantic memory**: Observations, conversation context, learned patterns about household members
3. **Sync state**: Coordination between web app and robot

Key constraints identified:
- Privacy preference (family data stays local)
- Must work without internet (reliability)
- 4-person household (small scale, <100K vectors over years)
- Web app and robot need coordinated access
- Optional cloud backup/sync desired, not required

## Decision

**Local PostgreSQL with pgvector extension**, running on the same machine as the assistant service.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Machine                         │
│                                                         │
│  ┌─────────────┐    ┌─────────────────────────────────┐ │
│  │  Web App    │───▶│  PostgreSQL + pgvector          │ │
│  │  (React)    │    │  ┌─────────────────────────────┐│ │
│  └─────────────┘    │  │ Structured tables           ││ │
│                     │  │ (users, chores, tasks)      ││ │
│  ┌─────────────┐    │  ├─────────────────────────────┤│ │
│  │  Assistant  │───▶│  │ Vector tables               ││ │
│  │  Service    │    │  │ (memories, embeddings)      ││ │
│  └─────────────┘    │  └─────────────────────────────┘│ │
│        │            └─────────────────────────────────┘ │
│        ▼                                                │
│  ┌─────────────┐                                        │
│  │ Reachy Mini │                                        │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
         │
         ▼ (optional, future)
┌─────────────────────┐
│  Cloud Backup       │
│  (encrypted export) │
└─────────────────────┘
```

### Components

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Database | PostgreSQL 16+ | Mature, reliable, excellent Python support |
| Vector extension | pgvector | Integrated with PostgreSQL, no separate service |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` | Fast, local, good quality for semantic search |
| Connection | Unix socket (local) | Lowest latency, no network config |
| Backup | pg_dump + encrypted archive | Simple, standard, scriptable |

### Why Not Alternatives

| Alternative | Reason Rejected |
|-------------|-----------------|
| Supabase | Cloud-first conflicts with privacy preference; adds internet dependency |
| SQLite + ChromaDB | Two systems to manage; ChromaDB adds complexity for marginal benefit at this scale |
| ChromaDB alone | No relational data support; would need second database anyway |
| Local Supabase (self-hosted) | Overkill for single-machine deployment; adds Docker complexity |

## Consequences

### Positive
- **Privacy**: All data stays on local machine
- **Reliability**: Works without internet
- **Simplicity**: One database for everything
- **Performance**: Local access, sub-millisecond queries at this scale
- **Cost**: $0 ongoing
- **Portability**: Standard PostgreSQL; can migrate anywhere

### Negative
- **No built-in real-time sync**: Must implement web ↔ robot coordination (WebSocket or polling)
- **Backup responsibility**: Must set up and maintain backup scripts
- **Single point of failure**: If the machine dies, data is lost without backups
- **No mobile access outside home**: Web app only works on local network (acceptable for now)

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data loss (hardware failure) | Medium | High | Automated daily backups to external drive or cloud storage (encrypted) |
| Database corruption | Low | High | WAL archiving, regular pg_dump verification |
| Performance degradation at scale | Very Low | Low | Won't hit scale limits with 4 users; pgvector handles 100K+ vectors fine |

## Implementation Notes

### Setup Requirements
```bash
# PostgreSQL with pgvector (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-16-pgvector

# Or via Docker
docker run -d \
  --name reachy-db \
  -e POSTGRES_PASSWORD=<secure-password> \
  -v reachy-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### Schema Preview (Detailed in ADR-003)
```sql
-- Enable vector extension
CREATE EXTENSION vector;

-- Example memory table
CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  content TEXT NOT NULL,
  embedding vector(384),  -- MiniLM-L6-v2 dimension
  memory_type VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  relevance_decay FLOAT DEFAULT 1.0
);

-- Similarity search index
CREATE INDEX ON memories
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

### Optional Cloud Sync (Future)

When/if desired, cloud backup can be added via:
1. Encrypted pg_dump to cloud storage (S3, Backblaze, etc.)
2. Or: Supabase as read replica (one-way sync from local)
3. Or: Custom sync service to personal cloud

This is explicitly deferred — build local-only first, add sync when there's a real need.

## Related Decisions
- ADR-002: Cozi integration (imports data into this database)
- ADR-003: Memory architecture (defines vector schema and retrieval logic)
