# ADR-0002: Use SQLite for Data Storage

**Date:** 2023-01-01 (Retroactive)  
**Status:** Accepted  
**Deciders:** Project Team  
**Consulted:** N/A  
**Informed:** All Developers

## Context

The Graph Browser application needs to store and query graph data representing relationships between nodes (in this case, train routes). The application requires:

- Storage for nodes (entities) and edges (relationships)
- Ability to query nodes by ID
- Ability to find connected nodes (children/neighbors)
- Simple deployment without external database servers
- Reasonable performance for moderate-sized datasets

### Problem Statement
Select a database technology that provides reliable graph data storage with simple deployment and good query performance for the application's use case.

### Constraints
- Must support relational queries (nodes and edges)
- Should be easy to deploy (embedded/file-based preferred)
- Must work well with Node.js
- Should have SQL-like query capabilities
- Zero-configuration setup desired
- Low operational overhead

### Assumptions
- Dataset size will remain moderate (thousands of nodes, not millions)
- Complex graph traversal queries are not needed
- Application is primarily read-heavy with occasional writes
- Single-user access patterns (no high concurrency requirements)

## Decision

We will use **SQLite3** as the database for storing graph data, with a simple schema consisting of `nodes` and `edges` tables.

### Proposed Solution
Implement data storage using:
- **SQLite3** database engine
- **sqlite3** npm package for Node.js integration
- File-based database (`trains.db`) stored in the application directory
- Simple schema:
  - `nodes` table: stores node information (id, name, data as JSON)
  - `edges` table: stores relationships (source, target)
- SQL initialization script (`trains.sql`) for database setup

### Rationale
1. **Zero Configuration**: SQLite requires no separate database server or configuration
2. **Embedded**: Database file can be included in the repository or easily distributed
3. **Simple Deployment**: Just copy the .db file - no database installation needed
4. **Good Performance**: SQLite is fast for read-heavy workloads with moderate data sizes
5. **SQL Support**: Standard SQL queries make it easy to work with
6. **Reliable**: SQLite is extensively tested and widely used
7. **Cross-Platform**: Works identically on all operating systems
8. **ACID Compliant**: Ensures data integrity
9. **Small Footprint**: Minimal resource requirements

## Alternatives Considered

### Alternative 1: PostgreSQL
**Description:** Use PostgreSQL database with proper graph extensions or standard relational tables

**Pros:**
- More powerful query capabilities
- Better support for concurrent access
- Rich ecosystem of tools and extensions
- Native JSON support
- Better scalability for large datasets
- ACID compliance with advanced features

**Cons:**
- Requires separate database server installation
- More complex deployment and configuration
- Higher operational overhead
- Overkill for current dataset size
- Additional infrastructure complexity
- Would need hosting for database server

**Why rejected:** The deployment complexity and infrastructure requirements are not justified for the application's current scale and use case. SQLite's simplicity is more appropriate.

### Alternative 2: MongoDB
**Description:** Use MongoDB with document storage for nodes and edges

**Pros:**
- Flexible schema (NoSQL)
- Native JSON/BSON support
- Good for hierarchical data
- Horizontal scalability
- Rich query language

**Cons:**
- Requires separate database server
- No ACID guarantees (depending on configuration)
- More complex queries for graph traversal
- Steeper learning curve
- Larger resource footprint
- Not ideal for relational graph data

**Why rejected:** Graph data is inherently relational, making SQL a better fit. MongoDB's schema flexibility is not needed, and the operational overhead is too high for this use case.

### Alternative 3: Neo4j or Graph Database
**Description:** Use a dedicated graph database like Neo4j, ArangoDB, or Amazon Neptune

**Pros:**
- Optimized for graph queries
- Native support for traversals and path finding
- Powerful query languages (Cypher, Gremlin)
- Excellent for complex graph algorithms
- Better performance for deep graph traversals

**Cons:**
- Requires separate database server
- More complex setup and deployment
- Steeper learning curve
- Higher resource requirements
- Overkill for simple parent-child relationships
- Limited embedding options

**Why rejected:** The application only needs simple parent-child relationships, not complex graph traversals. A full graph database is over-engineered for this use case.

### Alternative 4: In-Memory JavaScript Store
**Description:** Store all graph data in JavaScript objects/arrays in application memory

**Pros:**
- No database dependency
- Fastest possible reads
- Simple to implement
- No I/O overhead

**Cons:**
- Data lost on application restart
- Limited by available memory
- No persistence without manual serialization
- No transaction support
- Difficult to maintain data consistency
- No standard query interface

**Why rejected:** Lack of persistence makes this unsuitable. While could add file serialization, would essentially be rebuilding database features.

## Consequences

### Positive
- **Simple Deployment**: Database file can be committed to repository or easily distributed
- **No Infrastructure**: No need to manage separate database servers
- **Easy Development**: Developers can start working immediately with sample database
- **Fast Queries**: SQLite is very fast for the application's query patterns
- **Portability**: Database file can be easily backed up, shared, or moved
- **Standard SQL**: Familiar query language for most developers
- **Testing**: Easy to create test databases and clean them up

### Negative
- **Scalability Limits**: Not suitable if dataset grows to millions of records
- **Concurrency**: Limited support for high-concurrency write scenarios
- **No Built-in Replication**: Must implement custom backup/replication if needed
- **Query Limitations**: Complex graph traversals would be inefficient
- **File Lock**: Database file must be accessible to application
- **Network Access**: Can't easily share database across multiple servers

### Neutral
- **File-Based**: Database is a single file, which is both an advantage and limitation
- **Schema Changes**: Requires migration scripts for schema evolution
- **Backup**: Simple file copy for backup, but must ensure database is not in use

## Implementation

### Action Items
- [x] Create database schema in `trains.sql`
- [x] Set up sqlite3 npm package
- [x] Create `db.js` module with promisified query functions
- [x] Implement `getNode(id)` function
- [x] Implement `getChildren(id)` function
- [x] Add sample data (trains.db)
- [x] Document database setup in README

### Timeline
Completed in initial project setup

### Dependencies
- sqlite3 npm package
- Node.js runtime

### Risks
- **Risk**: Dataset grows beyond SQLite's practical limits
  - **Mitigation**: Monitor database size, consider migration to PostgreSQL if needed (abstraction layer makes this easier)
- **Risk**: Need for concurrent write access
  - **Mitigation**: Current application is read-heavy, write concurrency not expected to be an issue
- **Risk**: Database file corruption
  - **Mitigation**: Regular backups, SQLite's ACID compliance minimizes corruption risk

## Validation

### Success Criteria
- ✅ Database queries return results in < 100ms for typical operations
- ✅ Database file size remains manageable (< 100MB)
- ✅ New developers can set up database in < 5 minutes
- ✅ No data corruption or loss
- ✅ Application can run without external database installation

### Review Date
2024-06-01 (Review if dataset size or access patterns change significantly)

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [sqlite3 npm package](https://www.npmjs.com/package/sqlite3)
- [When to Use SQLite](https://www.sqlite.org/whentouse.html)
- [SQLite Performance](https://www.sqlite.org/speed.html)

## Notes

The current schema is intentionally simple:
```sql
CREATE TABLE nodes (
  id INTEGER PRIMARY KEY,
  name TEXT,
  data TEXT  -- JSON blob
);

CREATE TABLE edges (
  source INTEGER,
  target INTEGER,
  FOREIGN KEY (source) REFERENCES nodes(id),
  FOREIGN KEY (target) REFERENCES nodes(id)
);
```

This schema can be extended with additional columns or tables as needed without changing the core architecture. The `data` field stores additional node information as JSON, providing flexibility without schema changes.

If the application needs to scale beyond SQLite's capabilities, the database abstraction in `db.js` makes it relatively straightforward to swap in a different database backend (PostgreSQL, MySQL, etc.) without changing the API layer.

---

**Related ADRs:**
- None

**Supersedes:**
- None

**Superseded by:**
- None
