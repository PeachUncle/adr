# ADR-004: Postgres Checkpointer with BaseCheckpointSaver Interface

Decision: Implement full LangGraph BaseCheckpointSaver interface for Postgres with JSONB storage, transactional upsert semantics, and put_writes support.

## Context

The LangGraph orchestration requires a persistent checkpointer for resumable pipeline execution. Phase 0 established the checkpointer factory pattern, but the Postgres implementation was a placeholder. Production deployment requires full LangGraph compatibility with transactional persistence.

## Decision

Implement PostgresCheckpointer extending BaseCheckpointSaver with:

- Full interface compliance (get_tuple, list, put, put_writes)
- JSONB storage for complex checkpoint data structures
- Transactional upsert semantics with ON CONFLICT
- Checkpoint versioning with parent-child relationships
- Thread-safe concurrent execution support

## Implementation Details

### Schema Design

```sql
-- Checkpoint state table
CREATE TABLE checkpointer_state (
  workflow TEXT NOT NULL,
  thread_id TEXT NOT NULL,
  checkpoint_id TEXT NOT NULL,
  parent_checkpoint_id TEXT NULL,
  checkpoint JSONB NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (workflow, thread_id, checkpoint_id)
);

-- Pending writes table for put_writes support
CREATE TABLE checkpointer_writes (
  workflow TEXT NOT NULL,
  thread_id TEXT NOT NULL,
  checkpoint_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  idx INT NOT NULL,
  channel TEXT NOT NULL,
  value JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (workflow, thread_id, checkpoint_id, task_id, idx)
);

-- Index for efficient listing
CREATE INDEX idx_checkpointer_state_workflow_thread_created
  ON checkpointer_state (workflow, thread_id, created_at DESC);
```

### Interface Methods

#### get_tuple(config)

- Extracts thread_id from LangGraph config
- Returns latest checkpoint tuple: `(checkpoint_data, metadata, parent_config)`
- Orders by `(created_at DESC, checkpoint_id DESC)` for deterministic latest retrieval

#### list(config, \*, before=None, limit=None)

- Paginates checkpoints for thread using `(created_at, checkpoint_id)` composite key
- Supports before parameter for cursor-based pagination
- Returns iterator of `(config, checkpoint, metadata, parent_config, created_at)` tuples

#### put(config, checkpoint, metadata)

- Atomic upsert using `ON CONFLICT (workflow, thread_id, checkpoint_id)`
- Preserves checkpoint versioning and parent relationships
- Transactional write with rollback on failure

#### put_writes(config, writes, task_id)

- Stores pending writes in checkpointer_writes table
- Maintains write ordering with idx field
- Transactional batch insert

## Consequences

### Positive

- ✅ Full LangGraph compatibility for production deployment
- ✅ Transactional persistence with ACID guarantees
- ✅ Efficient checkpoint retrieval and pagination
- ✅ Thread-safe concurrent pipeline execution
- ✅ Comprehensive test coverage with skip markers

### Negative

- ❌ Additional database dependency for persistence
- ❌ Schema migration management required
- ❌ psycopg import guard needed for environments without Postgres

### Risks Addressed

- **Data consistency**: Transactional writes prevent partial checkpoints
- **Performance**: Indexed queries with pagination support
- **Concurrency**: Thread-level isolation with proper locking
- **Versioning**: Checkpoint lineage tracking with parent references

## Alternatives Considered

### Option 1: Redis Checkpointer

- **Pros**: Higher performance, built-in TTL
- **Cons**: Additional infrastructure dependency, no SQL querying capabilities
- **Decision**: Rejected due to existing PostgreSQL infrastructure preference

### Option 2: File-based Checkpointer

- **Pros**: No database dependency, simple implementation
- **Cons**: Not suitable for concurrent access, no transactional semantics
- **Decision**: Rejected due to production concurrency requirements

### Option 3: Simplified Custom Interface

- **Pros**: Less complexity, tailored to our use case
- **Cons**: Not LangGraph-compatible, limits future extensibility
- **Decision**: Rejected in favor of full LangGraph integration

## Status Update (PR-004)

- Implemented full BaseCheckpointSaver interface with JSONB storage
- Added transactional upsert semantics with ON CONFLICT handling
- Created comprehensive unit and integration tests
- Updated documentation and runbooks
- Merged and tagged v0.0.1-phase0-pr004-complete</contents>
  </xai:function_call/>
  <xai:function_call name="run_terminal_cmd">
  <parameter name="command">cp docs/ADRs/ADR-004-postgres-checkpointer.md grok_share/docs/ADRs/
