# ADR-001: PostgreSQL as Primary Database

## Status
**Accepted**

## Date
2025-01-XX

## Context

MyUglyRocks needs a primary database to store:
- User accounts and authentication data
- Cycles, stages, and tumbling run history
- Photos metadata and references
- Community posts, comments, and votes
- Reference data (specimens, materials)
- User settings and preferences

### Requirements
1. **Relational data model** - Strong relationships between entities (User → Cycles → Stages → Photos)
2. **ACID compliance** - Data integrity is critical for user content
3. **Full-text search** - Search across specimens, materials, and posts
4. **JSON support** - Store flexible data like stage configurations in templates
5. **Mature ecosystem** - Reliable tooling, ORMs, and hosting options
6. **Cost-effective** - Reasonable hosting costs for a hobby project scaling to small business

### Options Considered

#### Option A: PostgreSQL
- Open-source, mature, battle-tested
- Excellent JSON/JSONB support
- Built-in full-text search
- Strong EF Core support
- Available on Railway, Supabase, Neon, etc.

#### Option B: SQL Server
- Excellent .NET integration
- Azure-focused ecosystem
- Higher hosting costs for non-Azure deployments
- Licensing considerations

#### Option C: MySQL/MariaDB
- Popular, well-supported
- Less robust JSON support than PostgreSQL
- Full-text search less sophisticated

#### Option D: MongoDB
- Flexible schema for evolving data
- Not ideal for relational data with many joins
- Different query paradigm from team experience

#### Option E: SQLite
- Zero configuration, embedded
- Not suitable for multi-instance deployments
- Limited concurrent write performance

## Decision

**Use PostgreSQL as the primary database.**

### Rationale

1. **Best-in-class for our use case**: PostgreSQL excels at relational data with complex queries, which matches our domain model (cycles with stages, stages with materials, posts with comments, etc.).

2. **JSONB for flexible data**: Template `stageData` and user settings benefit from JSONB columns, allowing structured but flexible storage without separate tables.

3. **Built-in full-text search**: We can implement specimen/material search without adding a dedicated search service like Elasticsearch or Meilisearch in MVP.

4. **Railway hosting**: Railway provides managed PostgreSQL with:
   - Automatic backups
   - Connection pooling (PgBouncer)
   - Easy scaling
   - Reasonable pricing ($5/month starter)

5. **EF Core maturity**: The Npgsql provider for EF Core is mature and well-maintained, supporting all PostgreSQL-specific features.

6. **Team familiarity**: PostgreSQL is widely known, making it easier to onboard contributors.

## Consequences

### Positive
- **Reliable data integrity** with ACID transactions
- **No additional services** needed for search in MVP
- **Flexible JSON storage** for template data and settings
- **Strong community** and documentation
- **Multiple hosting options** prevent vendor lock-in

### Negative
- **Not the simplest option** - SQLite would be simpler for local development
- **Requires managed hosting** - Need to pay for database hosting (vs. SQLite)
- **Full-text search limitations** - May need dedicated search service at scale (1000+ posts)

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance at scale | Low | Medium | Use proper indexing, read replicas if needed |
| Full-text search inadequate | Medium | Low | Can add Meilisearch/Typesense later |
| Railway pricing increases | Low | Medium | Easy migration to other PostgreSQL hosts |

## Alternatives Rejected

### SQL Server
Rejected due to higher hosting costs outside Azure ecosystem. While .NET integration is excellent, PostgreSQL's EF Core support is nearly equivalent, and hosting flexibility is more important for this project.

### MongoDB
Rejected because our data model is inherently relational. The overhead of managing denormalized data and losing referential integrity doesn't justify the flexibility benefits.

### SQLite
Rejected because the application will run multiple instances (Railway containers for frontend and backend). SQLite's file-based storage doesn't support concurrent writes from multiple processes.

## Related Decisions
- [ADR-004-frontend-framework.md](./ADR-004-frontend-framework.md) - Next.js deployment affects database connection patterns

## References
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Npgsql EF Core Provider](https://www.npgsql.org/efcore/)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)
