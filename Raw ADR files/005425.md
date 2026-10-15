# ADR 005: State Management and Persistence Strategy

## Status
Accepted

## Context
We need a robust strategy for managing agent state, conversation history, checkpoints, and long-term memory. State management affects reliability, debuggability, user experience, and the ability to build complex multi-step workflows.

### Problem Statement
- Agents need to maintain state across multiple invocations
- Workflows should be resumable after interruptions (human-in-the-loop, errors)
- Conversation history must persist across sessions
- Need time-travel debugging capabilities
- Must support concurrent agent executions (different threads)
- Local-first architecture requires on-device persistence

### Requirements
- **Persistence**: Durable storage of agent state and checkpoints
- **Concurrency**: Multiple agents/conversations running simultaneously
- **Recovery**: Resume from failures or deliberate interruptions
- **Debugging**: Inspect state at any point in execution
- **Performance**: Minimal overhead (<10ms per state save)
- **Local-First**: No cloud dependencies, works offline
- **Simplicity**: Easy to understand and reason about

## Decision
We will use **SQLite via LangGraph's SqliteSaver** as the primary state persistence mechanism, with the following approach:
1. SQLite for all LangGraph checkpointing and state persistence
2. Thread-based isolation for concurrent conversations/workflows
3. Automatic checkpointing after each node execution
4. Optional state compression for large states
5. Built-in time-travel debugging via checkpoint history

## Rationale

### Why SQLite

**Local-First Benefits:**
- Serverless, embedded database
- Single-file storage (easy backup and portability)
- Zero configuration required
- Works completely offline
- No external processes or daemons
- Included in Python standard library
- Cross-platform compatibility

**Performance Characteristics:**
- Writes: 1,000-10,000 transactions/second
- Reads: 100,000+ queries/second
- State save overhead: 1-5ms typical
- Handles databases up to 281TB (practical limit ~100GB)
- Memory-mapped I/O for large files
- WAL mode for concurrent access

**Reliability:**
- ACID compliant
- Crash-safe (atomic commits)
- Proven track record (used in millions of applications)
- Extensive testing and hardening
- Corruption resistance
- Automatic recovery

**Developer Experience:**
```python
from langgraph.checkpoint.sqlite import SqliteSaver

# That's it!
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(checkpointer=checkpointer)
```

**LangGraph Integration:**
- First-class support (built-in)
- Automatic schema management
- Thread-based conversation isolation
- Checkpoint history tracking
- Time-travel debugging built-in

### Why Not Alternatives

**Redis:**
- ❌ Requires separate server process
- ❌ Not local-first (needs Redis daemon)
- ✅ Better for distributed systems
- **Verdict**: Overkill for single-machine use

**PostgreSQL:**
- ❌ Heavyweight (requires server)
- ❌ Complex setup and configuration
- ✅ Better concurrency and scale
- **Verdict**: Not local-first, excessive for our needs

**JSON Files:**
- ✅ Simple, human-readable
- ❌ Poor performance (full file rewrites)
- ❌ No concurrency support
- ❌ No ACID guarantees
- **Verdict**: Acceptable for demos, not production

**In-Memory Only:**
- ✅ Fastest performance
- ❌ No persistence (lost on restart)
- ❌ No debugging history
- ❌ Cannot resume workflows
- **Verdict**: Use for ephemeral testing only

## Consequences

### Positive
- Simple, reliable persistence with minimal code
- Time-travel debugging enables powerful development workflows
- Thread-based isolation prevents state contamination
- Checkpoint history useful for analytics and learning
- Portable (single file contains all state)
- Battle-tested reliability (SQLite's reputation)
- Excellent performance for single-machine workloads
- Zero operational overhead

### Negative
- Single-writer limitation (not ideal for highly concurrent writes)
- Database file can grow large (requires cleanup strategy)
- No built-in distribution (single-machine only)
- Less human-readable than JSON
- Schema changes require migration logic
- Write performance degrades with very large states (>1MB)

### Mitigation Strategies
1. **Concurrency**: Use WAL mode, separate DB per high-traffic agent
2. **Size Growth**: Implement checkpoint pruning (keep last N)
3. **Large States**: Compress large values, store references to separate storage
4. **Schema Changes**: Version state schemas, migration tools
5. **Debugging**: SQLite browser tools for inspection

## Implementation

### Standard Pattern
```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

# 1. Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    iteration: int
    metadata: dict

# 2. Create checkpointer
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# 3. Build graph
workflow = StateGraph(AgentState)
# ... add nodes and edges ...

# 4. Compile with checkpointing
app = workflow.compile(checkpointer=checkpointer)

# 5. Execute with thread ID
config = {"configurable": {"thread_id": "conversation-123"}}
result = app.invoke(initial_state, config)

# 6. Resume from checkpoint
# Same thread_id automatically loads last checkpoint
result = app.invoke(None, config)
```

### Thread Management
```python
# utils/thread_manager.py
import uuid
from datetime import datetime

class ThreadManager:
    """Manage conversation threads and checkpoints"""

    def create_thread(self, user_id: str = None) -> str:
        """Create new conversation thread"""
        thread_id = f"{user_id or 'anonymous'}-{uuid.uuid4()}"
        return thread_id

    def get_config(self, thread_id: str) -> dict:
        """Get LangGraph config for thread"""
        return {"configurable": {"thread_id": thread_id}}

    def list_checkpoints(self, checkpointer: SqliteSaver, thread_id: str):
        """List all checkpoints for a thread"""
        config = self.get_config(thread_id)
        checkpoints = list(checkpointer.list(config))
        return checkpoints

    def get_state_at_checkpoint(
        self,
        app,
        thread_id: str,
        checkpoint_id: str
    ):
        """Time-travel to specific checkpoint"""
        config = self.get_config(thread_id)
        config["configurable"]["checkpoint_id"] = checkpoint_id
        return app.get_state(config)

# Usage
tm = ThreadManager()
thread_id = tm.create_thread("user_42")
config = tm.get_config(thread_id)

result = app.invoke(initial_state, config)
```

### Checkpoint Pruning
```python
# utils/checkpoint_pruning.py
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class CheckpointPruner:
    """Manage checkpoint lifecycle"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def prune_old_checkpoints(
        self,
        thread_id: str,
        keep_last_n: int = 10
    ):
        """Keep only last N checkpoints per thread"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SQLite-specific query
        cursor.execute("""
            DELETE FROM checkpoints
            WHERE thread_id = ?
            AND checkpoint_id NOT IN (
                SELECT checkpoint_id
                FROM checkpoints
                WHERE thread_id = ?
                ORDER BY checkpoint_ns DESC
                LIMIT ?
            )
        """, (thread_id, thread_id, keep_last_n))

        conn.commit()
        conn.close()

    def prune_by_age(self, days: int = 30):
        """Delete checkpoints older than N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM checkpoints
            WHERE checkpoint_ns < strftime('%s', 'now', ? || ' days') * 1000000000
        """, (f"-{days}",))

        conn.commit()
        conn.close()

    def vacuum_database(self):
        """Reclaim disk space after deletions"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()

# Usage
pruner = CheckpointPruner("checkpoints.db")
pruner.prune_old_checkpoints("conversation-123", keep_last_n=10)
pruner.prune_by_age(days=30)
pruner.vacuum_database()
```

### State Compression
```python
# utils/state_compression.py
import gzip
import json
from typing import Any

def compress_state_value(value: Any) -> bytes:
    """Compress large state values"""
    json_str = json.dumps(value)
    if len(json_str) > 10_000:  # Compress if >10KB
        return gzip.compress(json_str.encode())
    return json_str.encode()

def decompress_state_value(data: bytes) -> Any:
    """Decompress state value if compressed"""
    try:
        # Try gzip first
        decompressed = gzip.decompress(data)
        return json.loads(decompressed.decode())
    except gzip.BadGzipFile:
        # Not compressed
        return json.loads(data.decode())

# Custom state class with compression
class CompressedAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    large_context: str  # Will be compressed

    @classmethod
    def compress(cls, state: dict) -> dict:
        """Compress before saving"""
        if "large_context" in state:
            state["large_context"] = compress_state_value(state["large_context"])
        return state

    @classmethod
    def decompress(cls, state: dict) -> dict:
        """Decompress after loading"""
        if "large_context" in state:
            state["large_context"] = decompress_state_value(state["large_context"])
        return state
```

### Debugging Tools
```python
# utils/checkpoint_debugger.py
from langgraph.checkpoint.sqlite import SqliteSaver
from rich.console import Console
from rich.table import Table

class CheckpointDebugger:
    """Debug and inspect checkpoints"""

    def __init__(self, checkpointer: SqliteSaver):
        self.checkpointer = checkpointer
        self.console = Console()

    def show_checkpoint_history(self, thread_id: str):
        """Display checkpoint history for thread"""
        config = {"configurable": {"thread_id": thread_id}}
        checkpoints = list(self.checkpointer.list(config))

        table = Table(title=f"Checkpoints for {thread_id}")
        table.add_column("Checkpoint ID", style="cyan")
        table.add_column("Step", style="green")
        table.add_column("Timestamp", style="yellow")
        table.add_column("State Size", style="magenta")

        for checkpoint in checkpoints:
            table.add_row(
                str(checkpoint["checkpoint_id"])[:8],
                checkpoint.get("metadata", {}).get("step", "N/A"),
                str(checkpoint["checkpoint_ns"]),
                f"{len(str(checkpoint['channel_values']))} bytes"
            )

        self.console.print(table)

    def diff_checkpoints(self, checkpoint1, checkpoint2):
        """Show difference between two checkpoints"""
        # Implementation: compare state values
        pass

    def replay_from_checkpoint(
        self,
        app,
        thread_id: str,
        checkpoint_id: str
    ):
        """Replay execution from specific checkpoint"""
        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id
            }
        }
        return app.invoke(None, config)

# Usage
debugger = CheckpointDebugger(checkpointer)
debugger.show_checkpoint_history("conversation-123")
```

### Performance Optimization
```python
# config/sqlite_config.py
import sqlite3

def optimize_sqlite_connection(conn: sqlite3.Connection):
    """Apply performance optimizations"""
    cursor = conn.cursor()

    # WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")

    # Memory-mapped I/O
    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB

    # Larger cache
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB

    # Synchronous mode (balance safety/performance)
    cursor.execute("PRAGMA synchronous=NORMAL")

    # Temp store in memory
    cursor.execute("PRAGMA temp_store=MEMORY")

    conn.commit()

# Usage with SqliteSaver
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("checkpoints.db")
optimize_sqlite_connection(conn)
checkpointer = SqliteSaver(conn)
```

## Verification

### Success Criteria
- [ ] State persists across application restarts
- [ ] Checkpointing overhead <10ms per save
- [ ] Time-travel debugging works reliably
- [ ] Concurrent threads don't interfere
- [ ] Checkpoint pruning prevents unbounded growth
- [ ] Examples demonstrate common patterns

### Testing Strategy
```python
# tests/test_state_management.py
def test_checkpoint_persistence():
    """Verify state persists across restarts"""

def test_thread_isolation():
    """Verify threads don't interfere"""

def test_checkpoint_history():
    """Verify checkpoint history tracking"""

def test_time_travel():
    """Verify replay from checkpoint works"""

def test_checkpoint_pruning():
    """Verify old checkpoints deleted correctly"""

def test_large_state_compression():
    """Verify compression for large states"""

# tests/benchmarks/state_benchmark.py
def benchmark_checkpoint_overhead():
    """Measure checkpointing performance impact"""

def benchmark_database_size_growth():
    """Track database growth over time"""
```

### Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Checkpoint save | <10ms | Small state (<100KB) |
| Checkpoint load | <5ms | Memory-mapped DB |
| Thread switch | <1ms | Config change only |
| Pruning (1000 checkpoints) | <100ms | Batch deletion |
| Vacuum | <1s | Per 100MB database |

## Migration Path

### Phase 1: Foundation (Current)
- SqliteSaver integration
- Basic thread management
- Checkpoint examples

### Phase 2: Advanced Features
- Checkpoint pruning utilities
- State compression
- Debugging tools
- Time-travel UI

### Phase 3: Optimization
- Performance tuning
- Large state handling
- Monitoring and analytics
- Backup/restore tools

### From In-Memory to Persistent
```python
# Before: In-memory (no persistence)
app = workflow.compile()
result = app.invoke(initial_state)

# After: Persistent with SQLite
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "conversation-1"}}
result = app.invoke(initial_state, config)

# Resume later
result = app.invoke(None, config)  # Automatically loads last checkpoint
```

## References
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [SqliteSaver Documentation](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite Performance Tuning](https://www.sqlite.org/performance.html)
- [LangGraph Persistence Tutorial](https://langchain-ai.github.io/langgraph/tutorials/persistence/)

## Related ADRs
- ADR-001: Local-First Architecture (storage requirements)
- ADR-002: LangGraph Choice (checkpoint integration)
- Future: ADR on long-term memory and semantic caching

## Changelog
- 2025-10-26: Initial version - SQLite-based state persistence via LangGraph
