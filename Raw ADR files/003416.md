# ADR-001: Why Supabase was chosen

**Status:** Accepted  
**Date:** 2025-01-27  
**Deciders:** Architecture Team

## Context

AIDevelo.ai needed a database solution that provides:
- Multi-tenant data isolation
- Real-time capabilities for voice agent features
- Row Level Security (RLS) for data privacy (nDSG compliance)
- PostgreSQL compatibility
- Managed hosting with minimal DevOps overhead
- Built-in authentication

## Decision

We chose **Supabase** as the primary database and authentication provider.

## Rationale

### Advantages

1. **Multi-tenant Architecture**
   - Built-in support for row-level security (RLS)
   - Easy tenant isolation using `org_id` and `location_id`
   - Compliant with Swiss data protection regulations (nDSG)

2. **Authentication**
   - Built-in Supabase Auth with JWT tokens
   - Session management handled by Supabase
   - OAuth providers (Google, etc.) supported out of the box

3. **Real-time Capabilities**
   - WebSocket support for real-time updates
   - Useful for voice agent status updates and call events

4. **Developer Experience**
   - TypeScript client with excellent type safety
   - Auto-generated types from database schema
   - RESTful API (PostgREST) for simple queries

5. **Managed Service**
   - No database server management
   - Automatic backups and scaling
   - Built-in connection pooling

6. **Cost-Effective**
   - Free tier suitable for development
   - Pay-as-you-grow pricing model

### Trade-offs

1. **Vendor Lock-in**
   - Supabase-specific features (RLS, real-time) create dependency
   - Migration to another provider would require significant refactoring

2. **Learning Curve**
   - Team needs to understand Supabase-specific patterns
   - RLS policies require careful design

3. **Legacy Code**
   - Some legacy code still uses direct PostgreSQL pool
   - Migration to Supabase client is ongoing

## Alternatives Considered

1. **Direct PostgreSQL (Railway/Neon)**
   - More control but requires more DevOps
   - No built-in authentication
   - Would need to implement RLS manually

2. **Firebase**
   - NoSQL database (less suitable for relational data)
   - Different query patterns
   - More expensive at scale

3. **PlanetScale**
   - MySQL-based (not PostgreSQL)
   - Would require schema migration
   - Less suitable for multi-tenant RLS

## Consequences

- **Positive:**
  - Faster development with built-in features
  - Better security with RLS
  - Reduced infrastructure management

- **Negative:**
  - Vendor lock-in to Supabase
  - Need to complete migration from legacy PostgreSQL pool
  - Some learning curve for team members

## Migration Status

- ✅ Core services migrated to Supabase client
- ⚠️ Some legacy routes still use PostgreSQL pool
- 🔄 Ongoing migration to full Supabase client usage

## References

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
