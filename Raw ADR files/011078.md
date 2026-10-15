# Kuzu and DuckDB for Semantic Code Analysis

## Purpose
This document records the decision to use Kuzu (graph database) and DuckDB (analytics database) as the dual-database foundation for semantic code analysis.

## Classification
- **Domain:** Architecture
- **Stability:** Static
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context

For semantic code analysis of TypeScript projects, we needed database solutions that could:

1. **Represent code relationships** (functions call functions, classes extend classes, types reference types)
2. **Enable graph queries** (find all paths, detect circular dependencies, trace impact)
3. **Store metrics and analytics** (complexity scores, file statistics, trends over time)
4. **Perform fast analytical queries** (aggregate metrics, filter by criteria)
5. **Work well with Deno** (TypeScript-native tooling)
6. **Be embeddable** (no separate server process required)
7. **Support concurrent access** (multiple analysis tools)

Key requirements:
- Graph database for semantic relationships
- Analytical database for metrics and aggregations
- Both must be lightweight and embeddable
- Must have good TypeScript/Deno support
- Must handle complex queries efficiently

### Decision

**We will use a dual-database architecture:**

1. **Kuzu for semantic graph storage**
   - Stores AST nodes and their relationships
   - Enables graph traversal queries (find paths, detect cycles)
   - Models code structure as a property graph
   - Uses Cypher query language

2. **DuckDB for metrics and analytics**
   - Stores file metrics, complexity scores, code statistics
   - Enables SQL queries for aggregations and filters
   - Provides time-series analysis of code evolution
   - Handles tabular data efficiently

**Integration Points:**
- Symbol IDs serve as foreign keys between databases
- Deno scripts query both databases and correlate results
- Kuzu answers "what connects to what"
- DuckDB answers "how much" and "how complex"

### Status
Accepted (2025-09-28)

### Consequences

**Positive Consequences:**
- Graph database perfectly models code relationships
- Cypher queries naturally express traversal patterns
- SQL handles metrics and analytics intuitively
- Each database optimized for its specific use case
- DuckDB's columnar storage excellent for analytics
- Kuzu's graph algorithms (shortest path, etc.) built-in
- Both are embeddable (no separate servers)
- Both work well from Deno via bindings
- Can scale to large codebases
- Query performance excellent for both graph and analytical workloads

**Negative Consequences:**
- Managing two databases instead of one
- Need to maintain schema in both systems
- Data synchronization between databases
- More complex backup and recovery
- Developers must learn both Cypher and SQL
- Some queries might need to join across databases

**Risks Introduced:**
- Kuzu is relatively young (possible bugs or limitations)
- Schema evolution requires coordinating both databases
- Complex queries might hit performance limits
- Data consistency issues if updates fail partially

**Trade-offs Made:**
- Simplicity of single database vs. specialized databases for each purpose
- Maturity of traditional databases vs. modern specialized solutions
- All-in-one solution vs. best-tool-for-each-job

### Alternatives Considered

#### Alternative 1: Neo4j for Everything
Use Neo4j as the single graph database for all data.

**Pros:**
- Mature graph database with proven track record
- Rich ecosystem and tooling
- Can store properties for metrics alongside graph
- Strong query optimization
- Well-documented

**Cons:**
- Requires separate server process (not embeddable)
- Heavyweight for a development tool
- Not optimized for analytical queries
- Expensive for aggregations and time-series
- Complex setup and maintenance
- Community edition has limitations

#### Alternative 2: PostgreSQL with Extensions
Use PostgreSQL with graph extensions (Apache AGE) for graph plus tables for metrics.

**Pros:**
- Mature and stable
- Can handle both graph and tabular data
- Rich ecosystem
- Well-known to most developers
- Strong consistency guarantees

**Cons:**
- Requires server process
- Graph queries awkward compared to native graph DBs
- AGE extension is relatively immature
- Heavier weight than needed
- Cypher support via AGE is limited
- Not as performant for graph traversal

#### Alternative 3: SQLite for Everything
Use SQLite with recursive CTEs for graph queries.

**Pros:**
- Single database file
- Embeddable
- Mature and stable
- Everyone knows SQL
- Excellent tooling

**Cons:**
- Recursive CTEs awkward for complex graph queries
- Poor performance for graph traversal
- Schema doesn't naturally model graphs
- No native graph algorithms
- Complex queries become very complex

#### Alternative 4: In-Memory with Memgraph
Use Memgraph as an in-memory graph database.

**Pros:**
- Very fast graph queries
- Native Cypher support
- Good for development workflows
- Can persist to disk

**Cons:**
- Requires server process
- Not embeddable
- Memory requirements for large codebases
- Commercial licensing for some features
- Overkill for file-based analysis

#### Alternative 5: DuckDB Only with JSON
Use DuckDB for everything, storing graph as JSON.

**Pros:**
- Single database
- Excellent analytics
- Can query JSON structures
- Embeddable and fast

**Cons:**
- Graph queries very awkward
- No graph algorithms
- JSON queries much slower than native graph
- Schema doesn't express relationships naturally
- Can't leverage graph database optimizations

### Implementation Notes

**Database Locations:**
```
.kuzu/semantic.db    # Kuzu graph database
.duckdb/metrics.db   # DuckDB analytics database
```

**Kuzu Schema (Cypher):**
```cypher
CREATE NODE TABLE Symbol (
  id STRING PRIMARY KEY,
  name STRING,
  kind STRING,
  file STRING,
  line INT32
);

CREATE NODE TABLE Type (
  id STRING PRIMARY KEY,
  name STRING
);

CREATE REL TABLE CALLS (FROM Symbol TO Symbol);
CREATE REL TABLE HAS_TYPE (FROM Symbol TO Type);
```

**DuckDB Schema (SQL):**
```sql
CREATE TABLE file_metrics (
  file_path VARCHAR PRIMARY KEY,
  lines INTEGER,
  complexity_sum INTEGER,
  symbol_count INTEGER
);

CREATE TABLE symbol_complexity (
  symbol_id VARCHAR PRIMARY KEY,
  cyclomatic_complexity INTEGER,
  cognitive_complexity INTEGER
);
```

**Query Patterns:**

*Graph Query (Kuzu)*:
```cypher
// Find all functions that call a specific function
MATCH (caller:Symbol)-[:CALLS]->(callee:Symbol {name: 'targetFunction'})
RETURN caller.name, caller.file;
```

*Analytics Query (DuckDB)*:
```sql
-- Find files with highest complexity
SELECT file_path, complexity_sum
FROM file_metrics
ORDER BY complexity_sum DESC
LIMIT 10;
```

*Cross-Database Query (TypeScript)*:
```typescript
// Get high-complexity symbols and their call graphs
const complexSymbols = await duckdb.query(
  "SELECT symbol_id FROM symbol_complexity WHERE cyclomatic_complexity > 10"
);

for (const symbol of complexSymbols) {
  const callers = await kuzu.query(
    `MATCH (s:Symbol {id: '${symbol.id}'})<-[:CALLS]-(caller) RETURN caller`
  );
}
```

**Access Patterns:**
- `scripts/lib/kuzu-client.ts` - Kuzu database client
- `scripts/lib/duckdb-client.ts` - DuckDB database client
- Both clients handle connection pooling and error recovery
- Transactions are per-database (no distributed transactions)

## Relationships
- **Parent Nodes:**
  - [foundation/project_definition.md] - implements - Enables semantic analysis goals
  - [adr_001_devcontainer_architecture.md] - builds_on - DevContainer includes both databases
- **Child Nodes:**
  - [architecture/data_architecture.md] - implements - Data architecture details this design
- **Related Nodes:**
  - [adr_002_deno_node_runtime_split.md] - complements - Deno scripts access databases
  - [architecture/database_schema.md] - details - Full schema definitions
  - [cross_cutting/query_patterns.md] - implements - Common query patterns

## Navigation Guidance
- **Access Context:** Reference when designing new analysis features or queries
- **Common Next Steps:** Review database schemas and query pattern examples
- **Related Tasks:** Adding new analysis capabilities, optimizing queries, schema evolution
- **Update Patterns:** Revisit if databases prove insufficient or better alternatives emerge

## Metadata
- **Decision Number:** ADR-004
- **Created:** 2025-09-30
- **Last Updated:** 2025-09-30
- **Updated By:** Claude (AI Agent)
- **Deciders:** Development team, based on semantic analysis requirements

## Change History
- 2025-09-30: Initial creation based on implementation guide documentation