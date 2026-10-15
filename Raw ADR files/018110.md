# ADR-0002: Use PostgreSQL as Primary Database

**Status:** Accepted
**Date:** 2025-10-22
**Deciders:** Project maintainers

## Context

The super-claude project needs to recommend a primary database for:

- Database skills (drizzle-maestro)
- Backend API skills (hono-api-builder, elysia-api-builder)
- Authentication integration (better-auth)
- Example code and patterns

Requirements:

- Reliable, production-ready relational database
- Strong TypeScript/Drizzle ORM support
- Good performance for typical app workloads
- Widely adopted (community support, hosting options)
- Support for both local development and production deployment

## Decision

**Use PostgreSQL as the primary recommended database, with Turso (SQLite) and SQLite as alternatives for specific use cases.**

**Database priority:**

1. **PostgreSQL** (primary recommendation) - Production applications, complex queries, team projects
2. **Turso** (edge/distributed) - Edge deployments, distributed replicas, cost-effective scaling
3. **SQLite** (local/embedded) - Local development, testing, embedded applications

## Alternatives Considered

### Option 1: PostgreSQL

**Description:**
Open-source relational database, industry standard for production applications.

**Pros:**

- Production-proven and reliable
- Excellent performance for complex queries
- Rich feature set (JSONB, full-text search, extensions)
- Wide hosting support (Supabase, Neon, Railway, Render)
- Strong Drizzle ORM integration
- Large community and ecosystem
- Free tier options available (Supabase, Neon)

**Cons:**

- Heavier than SQLite for simple apps
- Requires server/hosting (not embedded)
- Connection pooling needed for serverless
- More complex local setup than SQLite

**Decision:** ✅ Selected (Primary)

**Rationale:** PostgreSQL's production-readiness, feature set, and ecosystem make it the best default recommendation. Most applications will benefit from PostgreSQL's capabilities, and the hosting options make deployment straightforward.

### Option 2: MongoDB

**Description:**
NoSQL document database with flexible schema.

**Pros:**

- Flexible schema (good for rapid prototyping)
- Horizontal scaling
- Good for document-heavy data
- MongoDB Atlas hosting

**Cons:**

- Less type-safe with TypeScript (compared to SQL + Drizzle)
- Drizzle ORM doesn't support MongoDB well
- No relational integrity by default
- Not aligned with our type-safety goals
- Different query patterns vs SQL

**Decision:** ❌ Rejected

**Rationale:** MongoDB doesn't align with our type-safety focus and Drizzle ORM integration goals. SQL databases provide better type inference and compile-time safety with Drizzle.

### Option 3: MySQL

**Description:**
Popular open-source relational database, alternative to PostgreSQL.

**Pros:**

- Production-proven
- Good performance
- Wide hosting support
- Large community
- Drizzle ORM support

**Cons:**

- Less feature-rich than PostgreSQL (no JSONB, limited full-text search)
- Licensing complexity (Oracle ownership)
- Less modern feature set
- PostgreSQL generally preferred in modern stacks

**Decision:** ❌ Rejected

**Rationale:** PostgreSQL offers more features and aligns better with modern TypeScript/JavaScript stacks. No compelling reason to choose MySQL over PostgreSQL for our use cases.

### Option 4: Turso (LibSQL)

**Description:**
SQLite-compatible database optimized for edge deployment with distributed replicas.

**Pros:**

- Edge-optimized (low latency globally)
- SQLite-compatible (easy migration)
- Distributed replicas
- Cost-effective
- Good Drizzle support
- Great for edge/serverless

**Cons:**

- Newer/less proven than PostgreSQL
- Limited complex query performance vs PostgreSQL
- Smaller ecosystem
- Not ideal for high-write workloads

**Decision:** ✅ Selected (Secondary - Edge Use Cases)

**Rationale:** Turso is excellent for edge deployments and cost-sensitive applications. We'll recommend it as an alternative to PostgreSQL for specific use cases (edge, distributed, cost-optimization).

### Option 5: SQLite

**Description:**
Embedded SQL database, file-based, no server required.

**Pros:**

- Zero-setup (file-based)
- Perfect for local development
- Fast for simple queries
- Portable (single file)
- Great for testing
- Good Drizzle support

**Cons:**

- Not designed for production web apps
- No built-in networking
- Limited concurrency
- Not cloud-native

**Decision:** ✅ Selected (Tertiary - Local/Testing)

**Rationale:** SQLite is perfect for local development, testing, and embedded use cases. We'll support it but not recommend it for production web applications.

## Consequences

### Positive

- **Industry standard**: PostgreSQL is well-understood and trusted
- **Type safety**: Excellent Drizzle ORM integration for end-to-end types
- **Hosting options**: Many free/low-cost PostgreSQL hosting providers
- **Feature-rich**: JSONB, full-text search, extensions available
- **Flexibility**: Turso/SQLite options for edge and testing use cases
- **Skill focus**: drizzle-maestro can optimize for PostgreSQL specifically

### Negative

- **Setup overhead**: Requires server/hosting vs embedded SQLite
- **Cost**: Production hosting costs money (though free tiers exist)
- **Connection pooling**: Serverless needs additional configuration
- **Multi-DB support**: Need to maintain patterns for PostgreSQL + Turso + SQLite

### Neutral

- **Learning curve**: Developers need PostgreSQL knowledge
- **Local development**: Need Docker or local PostgreSQL install (or use SQLite)
- **Skill complexity**: drizzle-maestro needs to handle multiple DB variants

## Implementation Notes

**How will this be enforced?**

- drizzle-maestro generates PostgreSQL schema by default
- Documentation and examples use PostgreSQL first
- Turso and SQLite documented as alternatives with use-case guidance
- Better-auth integration examples use PostgreSQL

**When does this take effect?**

- Immediately for all new database work
- Existing examples should migrate to PostgreSQL or note they're using alternatives

**What needs to change to comply?**

- Database skills default to PostgreSQL patterns
- Connection pooling patterns for serverless (Neon, Supabase)
- Index optimization advice specific to PostgreSQL
- Migration guides reference PostgreSQL features

**Recommended Hosting:**

- **Supabase** (PostgreSQL + Auth + Storage + Realtime)
- **Neon** (Serverless PostgreSQL, generous free tier)
- **Railway** (Simple PostgreSQL deployment)
- **Render** (Managed PostgreSQL)

## References

**Related ADRs:**

- None yet

**OpenSpec Proposals:**

- [database-plugin](../../../openspec/changes/database-plugin/) - Drizzle ORM implementation with PostgreSQL focus

**External Resources:**

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Drizzle ORM PostgreSQL](https://orm.drizzle.team/docs/get-started-postgresql)
- [Supabase](https://supabase.com/)
- [Neon](https://neon.tech/)
- [Turso](https://turso.tech/)

## Notes

**Multi-Database Support Strategy:**

1. **PostgreSQL** - Full feature support, primary testing, best performance for complex queries
2. **Turso** - SQLite-compatible, edge optimization, distributed replicas
3. **SQLite** - Local development, testing, embedded apps

The drizzle-maestro skill will:

- Default to PostgreSQL
- Provide flags/options for Turso and SQLite
- Document differences and migration paths
- Optimize queries for each database's strengths

If PostgreSQL becomes less suitable (e.g., serverless/edge dominates), we can revisit and potentially make Turso the primary recommendation.
