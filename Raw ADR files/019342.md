# 0001. Use Supabase for Backend Services

**Date:** 2024-10-15  
**Status:** Accepted  
**Deciders:** TrustWork Engineering Team  
**Tags:** architecture, backend, infrastructure, database

---

## Context

The TrustWork platform requires a robust backend infrastructure to handle:

- User authentication and authorization
- PostgreSQL database for structured data
- Real-time subscriptions for live updates (notifications, chat)
- File storage for user avatars and project attachments
- RESTful API for CRUD operations
- Serverless functions for complex business logic

We needed to decide between:

1. **Building a custom backend** (Node.js/Express + PostgreSQL + Redis + S3)
2. **Using Firebase** (Google's BaaS platform)
3. **Using Supabase** (Open-source Firebase alternative)

### Constraints

- Small team (2-3 developers)
- Limited budget for infrastructure
- Need to ship MVP quickly (6-8 weeks)
- Require full control over data (no vendor lock-in)
- Need PostgreSQL for relational data and RLS policies
- Must support real-time features

### Evaluation Criteria

- **Time to Market**: How quickly can we build and deploy?
- **Developer Experience**: How easy is it to work with?
- **Cost**: What are the ongoing operational costs?
- **Scalability**: Can it handle growth to 100K+ users?
- **Data Ownership**: Can we export and self-host if needed?
- **Feature Set**: Does it cover all our needs?

## Decision

We will use **Supabase** as our primary backend infrastructure.

### Reasoning

**Supabase Advantages:**

1. **PostgreSQL Foundation**: Industry-standard relational database with full SQL support
2. **Row-Level Security (RLS)**: Built-in authorization at the database level
3. **Real-time Subscriptions**: WebSocket support for live updates out of the box
4. **Authentication**: Built-in auth with email/password, OAuth (Google, GitHub), magic links
5. **Storage**: S3-compatible object storage with RLS policies
6. **Edge Functions**: Serverless Deno functions for custom logic
7. **Open Source**: Can self-host if needed, no vendor lock-in
8. **Generous Free Tier**: 500MB database, 1GB file storage, 50K monthly active users
9. **TypeScript Support**: Auto-generated types from database schema
10. **Excellent Documentation**: Comprehensive guides and examples

**Compared to Alternatives:**

| Feature | Supabase | Firebase | Custom Backend |
|---------|----------|----------|----------------|
| Database | PostgreSQL | NoSQL (Firestore) | PostgreSQL |
| Auth | ✅ Built-in | ✅ Built-in | ❌ Build from scratch |
| Real-time | ✅ Built-in | ✅ Built-in | ❌ Build from scratch |
| Storage | ✅ Built-in | ✅ Built-in | ❌ Integrate S3 |
| RLS | ✅ Native | ⚠️ Security Rules | ❌ Build from scratch |
| SQL Support | ✅ Full SQL | ❌ NoSQL only | ✅ Full SQL |
| Open Source | ✅ Yes | ❌ No | ✅ Yes |
| Time to MVP | 2-3 weeks | 2-3 weeks | 6-8 weeks |
| Monthly Cost (MVP) | $0-25 | $0-50 | $50-100+ |

**Why Not Firebase:**

- Firestore's NoSQL model doesn't fit our relational data structure
- Security rules are complex compared to SQL-based RLS
- Vendor lock-in concerns (proprietary platform)
- Higher cost at scale

**Why Not Custom Backend:**

- 3-4x longer development time
- More ongoing maintenance burden
- Need to build auth, real-time, storage from scratch
- Higher infrastructure costs initially

## Consequences

### Positive Consequences

- ✅ **Faster MVP Delivery**: Shipped in 4 weeks instead of 8-10 weeks
- ✅ **Reduced Maintenance**: Supabase handles infrastructure, backups, scaling
- ✅ **Better Security**: RLS policies at database level, hard to bypass
- ✅ **Type Safety**: Auto-generated TypeScript types from database schema
- ✅ **Real-time Features**: Built-in WebSocket subscriptions for notifications and chat
- ✅ **Cost Effective**: $0/month for MVP, scales to $25/month for first 50K users
- ✅ **Developer Experience**: Clear documentation, intuitive API, helpful community

### Negative Consequences

- ⚠️ **Learning Curve**: Team needed to learn RLS policies and Supabase patterns
- ⚠️ **Limited Customization**: Some edge cases require workarounds
- ⚠️ **Database Vendor Lock-in**: PostgreSQL-specific features (though portable)
- ⚠️ **Cold Starts**: Edge Functions have ~100ms cold start latency
- ⚠️ **Regional Limitations**: Database hosted in single region (US East by default)

### Neutral Consequences

- 🔄 **SQL Knowledge Required**: Team must be comfortable writing SQL and RLS policies
- 🔄 **Supabase Updates**: Need to track Supabase releases for breaking changes
- 🔄 **Self-Hosting Option**: Can migrate to self-hosted Supabase if needed (exit strategy)

## Implementation

### Migration Plan

1. ✅ Set up Supabase project (October 15, 2024)
2. ✅ Define database schema (`supabase/schema.sql`)
3. ✅ Implement RLS policies for all tables
4. ✅ Configure authentication providers (email, Google, GitHub)
5. ✅ Set up storage buckets for avatars and attachments
6. ✅ Create Supabase client singleton (`src/lib/supabaseClient.ts`)
7. ✅ Implement SupabaseProvider context for auth state
8. ✅ Test real-time subscriptions for notifications

### Key Files

- `src/lib/supabaseClient.ts` - Supabase client singleton
- `src/providers/SupabaseProvider.tsx` - Auth context provider
- `supabase/schema.sql` - Database schema definition
- `supabase/storage-setup.sql` - Storage bucket configuration

## Related Decisions

- [ADR-0003: Implement Row-Level Security](./0003-implement-row-level-security.md)
- [ADR-0002: Adopt TanStack Query for State Management](./0002-adopt-tanstack-query-for-state-management.md)

## Notes

### Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Pricing](https://supabase.com/pricing)
- [Supabase GitHub](https://github.com/supabase/supabase)

### Future Considerations

- **Self-Hosting**: If we reach scale where self-hosting is cost-effective, Supabase provides migration path
- **Multi-Region**: May need to replicate database for global low-latency access
- **Edge Functions**: Evaluate Deno vs. other serverless options for compute-heavy tasks
- **Caching Layer**: Consider Redis/Upstash for caching if database queries become bottleneck

---

**ADR Version:** 1.0  
**Last Updated:** November 3, 2025
