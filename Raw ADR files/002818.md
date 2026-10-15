# ADR-004: Multi-Database Strategy

## Status
Accepted

## Date
2024-01-17

## Context

NEURECTOMY has diverse data storage requirements:
1. **Relational data**: Users, agents, configurations (ACID transactions)
2. **Graph relationships**: Agent connections, knowledge graphs, workflows
3. **Time-series data**: Metrics, events, audit logs
4. **Vector embeddings**: Semantic search, similarity matching
5. **Cache/Sessions**: Fast ephemeral data access

No single database optimally handles all these use cases.

## Decision

We will use a **polyglot persistence** strategy with specialized databases:

| Database | Purpose | Use Cases |
|----------|---------|-----------|
| **PostgreSQL** | Primary relational store | Users, agents, configs, auth |
| **PostgreSQL + pgvector** | Vector similarity | Embeddings, semantic search |
| **Neo4j** | Graph relationships | Knowledge graphs, agent networks |
| **TimescaleDB** | Time-series data | Metrics, events, telemetry |
| **Redis** | Cache & sessions | Session storage, rate limiting, pub/sub |

### Data Flow Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │PostgreSQL│  │  Neo4j  │  │Timescale│  │     Redis       │ │
│  │+ pgvector│  │         │  │   DB    │  │                 │ │
│  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────────────┤ │
│  │• Users  │  │• Graphs │  │• Metrics│  │• Cache          │ │
│  │• Agents │  │• Rels   │  │• Events │  │• Sessions       │ │
│  │• Config │  │• Paths  │  │• Audit  │  │• Rate limits    │ │
│  │• Vectors│  │         │  │         │  │• Pub/Sub        │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Consistency Model
- **PostgreSQL**: Strong consistency (ACID)
- **Neo4j**: Causal consistency
- **TimescaleDB**: Strong consistency (based on PostgreSQL)
- **Redis**: Eventual consistency (with persistence options)

## Consequences

### Positive
- **Optimal Performance**: Each database excels at its use case
- **Scalability**: Scale databases independently
- **Flexibility**: Can swap implementations without full rewrite
- **Rich Features**: Access to specialized features (graph traversals, time-series aggregations)

### Negative
- **Operational Complexity**: Multiple databases to maintain
- **Data Consistency**: Cross-database transactions require saga pattern
- **Learning Curve**: Team needs expertise in multiple databases
- **Infrastructure Cost**: More services to run and monitor

### Mitigations
- Use managed database services where possible
- Implement robust health checks and monitoring
- Create abstraction layers for each data access pattern
- Document data ownership clearly

## Data Ownership

| Domain | Primary Database | Secondary/Cache |
|--------|-----------------|-----------------|
| User Management | PostgreSQL | Redis (sessions) |
| Agent Configuration | PostgreSQL | Redis (hot config) |
| Agent Relationships | Neo4j | - |
| Knowledge Base | PostgreSQL (content) + pgvector (embeddings) | Redis (hot items) |
| Metrics/Telemetry | TimescaleDB | - |
| Audit Logs | TimescaleDB | - |
| Real-time State | Redis | - |

## Alternatives Considered

### 1. PostgreSQL Only
- ✅ Simpler operations
- ❌ Suboptimal for graphs (recursive CTEs slow)
- ❌ No native time-series optimization
- ❌ Redis-like caching requires extensions

### 2. MongoDB (Document Store)
- ✅ Flexible schema
- ❌ Weaker transactions (improved in v4+)
- ❌ No graph capabilities
- ❌ No native vector search

### 3. Single Graph Database (Neo4j for all)
- ✅ Unified data model
- ❌ Not optimal for relational queries
- ❌ No native vector search
- ❌ Higher storage costs for non-graph data

## Migration Strategy

1. **Phase 1**: PostgreSQL as primary (MVP)
2. **Phase 2**: Add pgvector for embeddings
3. **Phase 3**: Add Neo4j for knowledge graphs
4. **Phase 4**: Add TimescaleDB for metrics
5. **Continuous**: Redis for caching throughout

## References
- [Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Neo4j Best Practices](https://neo4j.com/developer/guide-data-modeling/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
