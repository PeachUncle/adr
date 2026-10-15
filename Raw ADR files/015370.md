# SQLite as Offline POS Data Store

* Status: accepted
* Deciders: Platform Team
* Date: 2025-12-09

## Context and Problem Statement

The Offline POS application requires a local data store that can operate without network connectivity. The store must persist product catalogs (~50K SKUs), operator credentials, and pending transactions on commodity x86 mini-PCs deployed in retail locations. The data store must support synchronization with central systems when connectivity is restored.

## Decision Drivers

1. **Offline-first operation** - Must work with zero network connectivity
2. **Minimal dependencies** - Disaster recovery app needs maximum reliability
3. **Single-file deployment** - Simplify deployment to retail hardware
4. **Sufficient capacity** - Handle ~50K products (~20MB) plus transactions
5. **Sync-friendly** - Support periodic full catalog refresh and transaction upload
6. **Low resource footprint** - Run on commodity hardware alongside other POS applications

## Considered Options

1. SQLite (chosen)
2. PostgreSQL (local instance)
3. LevelDB / RocksDB (embedded key-value)
4. JSON files on disk

## Decision Outcome

Chosen option: **SQLite**

SQLite is the industry standard for embedded relational databases with zero external dependencies. Using the pure-Go driver (`modernc.org/sqlite`), SQLite compiles directly into the Go binary with no CGO or external library requirements. WAL (Write-Ahead Logging) mode provides concurrent read access during writes, which is sufficient for the single-user POS workflow.

The ~20MB product catalog fits comfortably in SQLite, and the relational model naturally supports product lookups by UPC, operator authentication by PIN, and transaction storage with JSON line items.

### Positive Consequences

- Zero external dependencies - database is embedded in the binary
- Single database file simplifies backup and deployment
- SQL queries are familiar and debuggable
- WAL mode handles concurrent UI reads during background sync writes
- Battle-tested in millions of mobile and embedded deployments
- Pure Go driver means no CGO complexity

### Negative Consequences

- Not suitable for high-concurrency scenarios (acceptable for single-user POS)
- Full catalog sync requires careful handling to avoid blocking reads
- No built-in replication (sync is application-level responsibility)

## Pros and Cons of the Options

### 1. SQLite (chosen)

**Good**
- Zero configuration, zero dependencies
- Single file database - easy to backup, deploy, reset
- Embedded in Go binary via `modernc.org/sqlite`
- Excellent read performance for product lookups
- ACID transactions for reliable transaction storage
- Well-understood failure modes

**Bad**
- Single writer at a time (mitigated by WAL mode)
- No network/remote access (not needed for this use case)
- Schema migrations require careful handling

### 2. PostgreSQL (local instance)

**Good**
- Full SQL feature set
- Excellent concurrency handling
- Familiar to backend team

**Bad**
- Requires separate process installation and management
- Significant resource overhead (~100MB+ memory)
- Adds deployment complexity to retail hardware
- Overkill for single-user embedded application
- Additional failure mode (postgres process crash)

### 3. LevelDB / RocksDB (embedded key-value)

**Good**
- Very fast writes
- Embedded, no external dependencies
- Good for append-heavy workloads

**Bad**
- Key-value model requires manual indexing for product search
- No SQL - queries become application code
- Less tooling for debugging/inspection
- CGO dependency for RocksDB

### 4. JSON files on disk

**Good**
- Simplest possible implementation
- Human-readable data files
- No database driver needed

**Bad**
- No indexing - O(n) product lookups
- Manual file locking for concurrent access
- No ACID transactions
- 50K products in JSON becomes unwieldy
- Corruption risk without careful atomic writes

## Implementation Notes and Next Steps

- Use `modernc.org/sqlite` for pure-Go SQLite (no CGO)
- Enable WAL mode for concurrent read access: `PRAGMA journal_mode=WAL`
- Schema migrations embedded in binary, run on startup
- Product sync: full table replace in transaction (TRUNCATE + INSERT)
- Transaction storage: JSON blob for line items (simple, flexible)

## References

- [Offline POS Design](../ideas/2025-12-09-offline-pos-design.md) - Full application design
- [modernc.org/sqlite](https://pkg.go.dev/modernc.org/sqlite) - Pure Go SQLite driver
- [SQLite WAL Mode](https://www.sqlite.org/wal.html) - Write-ahead logging documentation
