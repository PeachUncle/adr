# ADR-001: Database Selection

**Status**: Accepted
**Date**: 2025-10-21
**Decision Makers**: System Architecture Designer
**Context**: Love Rank Pulse requires a robust, scalable database for competitive ranking system

## Context and Problem Statement

The application needs to handle:
- Player profiles with authentication
- Match records and results
- Real-time ELO rating calculations
- Leaderboard rankings with frequent updates
- High-performance read operations for leaderboards
- ACID compliance for match result transactions

## Decision Drivers

- **Data Integrity**: Critical for competitive rankings (ELO ratings)
- **Transaction Support**: Atomic updates for match results affecting multiple players
- **Query Performance**: Fast leaderboard queries with sorting and pagination
- **Scalability**: Support for growing player base and match volume
- **Developer Experience**: Type-safety and modern tooling
- **Cost**: Infrastructure and operational expenses

## Considered Options

### Option 1: PostgreSQL + Prisma ORM ✅ SELECTED

**Pros:**
- Full ACID compliance for transactional integrity
- Excellent support for complex queries with indexes
- Native JSON support for flexible metadata
- Mature ecosystem with proven scalability
- Prisma provides type-safe queries and migrations
- Strong community support and documentation

**Cons:**
- Requires managed hosting (added infrastructure cost)
- Vertical scaling limitations (horizontal requires read replicas)

### Option 2: MongoDB + Mongoose

**Pros:**
- Flexible schema for rapid iteration
- Horizontal scaling through sharding
- Good for unstructured data

**Cons:**
- Weaker transaction support (critical for ELO calculations)
- No native join support (requires application-level joins)
- Eventual consistency can cause ranking discrepancies
- Less suited for complex relational queries

### Option 3: SQLite + Better-SQLite3

**Pros:**
- Zero infrastructure cost
- Simple deployment
- Fast for single-node operations

**Cons:**
- Limited concurrent write support
- Not suitable for production scale
- No built-in replication
- Single point of failure

## Decision Outcome

**Chosen Option**: PostgreSQL + Prisma ORM

### Justification

PostgreSQL provides the transactional integrity required for competitive ranking systems. The combination with Prisma delivers:

1. **Type Safety**: Compile-time query validation prevents runtime errors
2. **Migration Management**: Version-controlled schema evolution
3. **Transaction Support**: Atomic match result submissions with multi-player updates
4. **Performance**: Optimized indexes for leaderboard queries
5. **Developer Experience**: Auto-generated types and intuitive query API

### Implementation Details

**Schema Design:**
- Players: Core user entity with ELO ratings
- Matches: Game records with player references
- MatchResults: Outcome data with rating changes
- LeaderboardEntries: Denormalized ranking data for performance

**Key Optimizations:**
- B-tree indexes on `elo_rating DESC` for fast leaderboard queries
- Composite indexes on `(is_active, elo_rating)` for filtering
- Unique constraints on `username` and `email`
- Cascading deletes for referential integrity

**Connection Pooling:**
```typescript
// prisma/client.ts
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  log: ['query', 'error', 'warn'],
});
```

## Consequences

### Positive
- Reliable transactional semantics for match results
- Fast leaderboard queries with proper indexing
- Type-safe database access across application
- Automated migration workflow
- Production-ready scalability

### Negative
- Infrastructure cost for managed PostgreSQL
- Learning curve for team members unfamiliar with SQL
- Migration overhead for schema changes

### Risks and Mitigation
- **Risk**: Database becomes bottleneck under load
  - **Mitigation**: Redis caching layer (see ADR-006)
- **Risk**: Complex migrations cause downtime
  - **Mitigation**: Blue-green deployment strategy (see ADR-004)

## Related Decisions
- ADR-002: ORM Selection (Prisma)
- ADR-006: Caching Strategy (Redis)
- ADR-004: Deployment Strategy

## References
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Prisma Documentation](https://www.prisma.io/docs)
- Schema: `/workspaces/love-rank-pulse/prisma/schema.prisma`
