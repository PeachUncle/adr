# ADR 0001: Use Cloudflare D1 for Database

## Status
Accepted

## Date
2024-01-15

## Context

We need a database solution for the Shajara family tree application that:
- Works well with Cloudflare Pages/Workers
- Supports relational data (family relationships)
- Provides low latency globally
- Is cost-effective for a new project
- Requires minimal operational overhead

### Options Considered

1. **Cloudflare D1** (SQLite-based)
   - Pros: Native Cloudflare integration, edge-local, SQL support, free tier
   - Cons: Beta status, size limits, no real-time sync

2. **PlanetScale** (MySQL)
   - Pros: Mature, serverless, branching
   - Cons: Requires external connection, higher latency, paid

3. **Supabase** (PostgreSQL)
   - Pros: Full-featured, real-time, auth included
   - Cons: Requires external connection, more complex setup

4. **Turso** (SQLite/libSQL)
   - Pros: Edge-native, SQLite compatible
   - Cons: Less integrated with Cloudflare, another vendor

## Decision

We will use **Cloudflare D1** as our primary database.

## Rationale

1. **Native Integration**: D1 is a first-class Cloudflare product, meaning:
   - Zero-configuration binding to Workers
   - No connection pooling issues
   - Consistent API with other Cloudflare services

2. **Edge Performance**: D1 data is replicated to edge locations, reducing latency for users worldwide - critical for our global Arabic-speaking audience.

3. **SQLite Compatibility**: SQLite is battle-tested, and D1's SQL support allows us to:
   - Use familiar SQL syntax
   - Leverage existing SQLite knowledge
   - Port to other SQLite-compatible systems if needed

4. **Cost Efficiency**: D1's free tier includes:
   - 5 million reads/day
   - 100,000 writes/day
   - 5 GB storage
   This is sufficient for initial launch and scale.

5. **Operational Simplicity**: No servers to manage, automatic backups, built-in migrations.

## Consequences

### Positive

- Simplified architecture with all infrastructure on Cloudflare
- Low latency for database operations
- Reduced costs during early growth phase
- Easy local development with Miniflare

### Negative

- D1 is still in beta (though increasingly stable)
- Limited to 10GB per database (sufficient for our use case)
- No built-in real-time subscriptions
- Must design around eventual consistency

### Mitigations

- Implement KV caching for frequently accessed data
- Design schema to minimize write contention
- Add monitoring for D1-specific errors
- Document backup and restore procedures

## Related Decisions

- ADR 0002: Use KV for Session Storage (pending)
- ADR 0003: Use R2 for Media Storage (pending)

## References

- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [D1 Pricing](https://developers.cloudflare.com/d1/platform/pricing/)
- [SQLite Documentation](https://sqlite.org/docs.html)
