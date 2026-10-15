# ADR-002: Use Supabase for Backend

## Status

Accepted

## Context

We need a backend solution that provides:

- Managed PostgreSQL database with real-time capabilities
- Built-in authentication with social login support
- Row-Level Security (RLS) for data privacy
- Vector embeddings support for AI features
- Scalable infrastructure without operational overhead
- Cost-effective for startup/growth phase

The main options considered were:

1. Supabase (PostgreSQL + Auth + Realtime)
2. Firebase (NoSQL + Auth + Realtime)
3. AWS Amplify (Multiple database options + Auth)
4. Custom backend with PostgreSQL + Auth0
5. PlanetScale + Clerk Auth

## Decision

We will use Supabase as our primary backend platform, providing:

- PostgreSQL database with pgvector extension
- Supabase Auth for authentication
- Row-Level Security for data access control
- Realtime subscriptions for live updates

Key factors in this decision:

- **PostgreSQL**: Relational database with ACID compliance and complex query support
- **pgvector**: Native vector embeddings for AI-powered semantic search
- **Integrated Auth**: Built-in authentication with social providers (Google, Apple)
- **RLS**: Fine-grained security policies at the database level
- **Developer Experience**: Excellent TypeScript SDK and auto-generated types
- **Open Source**: Can self-host if needed, avoiding vendor lock-in

## Consequences

### Positive

- **All-in-One Solution**: Database, auth, and realtime in a single platform reduces complexity
- **Type Safety**: Auto-generated TypeScript types from database schema
- **Security**: Row-Level Security ensures data privacy at the database level
- **Scalability**: Managed infrastructure scales automatically with usage
- **Cost Effective**: Generous free tier and predictable pricing
- **AI Ready**: pgvector extension enables semantic search without additional infrastructure
- **Developer Productivity**: Instant APIs, database migrations, and local development support

### Negative

- **PostgreSQL Limitations**: Less flexible than NoSQL for unstructured data
- **Learning Curve**: RLS policies require understanding PostgreSQL security model
- **Vendor Coupling**: While open source, migration would require significant effort
- **Regional Availability**: Limited regions compared to major cloud providers
- **Connection Pooling**: Serverless functions may need connection pooling solution

## References

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [pgvector Extension](https://github.com/pgvector/pgvector)
- Architecture Document: [7-database-schema.md](../architecture/7-database-schema.md)
- Related ADR: ADR-001 (Next.js App Router)
