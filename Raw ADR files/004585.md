# ADR-001: Supabase as Primary Database and Backend Service

## Status
**Accepted** - Implemented as of August 2025

## Context
WedSync 2.0 needs a robust, scalable backend solution that can handle:
- Multi-tenant architecture for wedding vendors
- Real-time updates for client communications
- Secure file storage for contracts and photos
- Authentication and authorization
- Row-level security for data isolation
- Cost-effective scaling for a startup

## Decision
We will use **Supabase** as our primary backend service, leveraging:
- PostgreSQL database with Row Level Security (RLS)
- Supabase Auth for authentication
- Supabase Storage for file management
- Realtime subscriptions for live updates
- Edge Functions for serverless computing

## Alternatives Considered

### 1. Firebase (Google)
- **Pros**: Excellent real-time features, mature ecosystem
- **Cons**: NoSQL limits complex queries, vendor lock-in, higher costs at scale
- **Wedding Context**: Difficult to model complex vendor-client relationships

### 2. AWS Amplify
- **Pros**: Full AWS ecosystem, highly scalable
- **Cons**: Complex setup, steeper learning curve, higher operational overhead
- **Wedding Context**: Overkill for MVP, requires dedicated DevOps

### 3. Custom PostgreSQL + Node.js Backend
- **Pros**: Full control, no vendor lock-in
- **Cons**: Significant development time, infrastructure management, security concerns
- **Wedding Context**: Delays time-to-market for critical wedding season launch

### 4. PlanetScale + Clerk
- **Pros**: Serverless MySQL, excellent auth solution
- **Cons**: Multiple services to manage, no built-in storage solution
- **Wedding Context**: Requires additional integration for file handling

## Rationale

### Why Supabase Wins for WedSync

1. **PostgreSQL Power**: Complex queries for vendor matching, availability checking, and reporting
2. **Row Level Security**: Critical for multi-tenant isolation between competing vendors
3. **Built-in Auth**: Reduces development time for user management
4. **Storage Integration**: Native handling of contracts, photos, and documents
5. **Real-time Updates**: Essential for client-vendor messaging and notifications
6. **Developer Experience**: Excellent TypeScript support and Next.js integration
7. **Cost Structure**: Generous free tier, predictable scaling costs
8. **Open Source**: Can self-host if needed, reducing vendor lock-in risk

### Trade-offs Accepted

1. **Vendor Dependency**: Relying on Supabase's infrastructure and uptime
2. **Learning Curve**: Team needs to learn Supabase-specific patterns
3. **Feature Limitations**: Some advanced features require workarounds
4. **Regional Limitations**: Limited region selection compared to major clouds

## Consequences

### Positive
- **Faster Development**: 60% reduction in backend development time
- **Built-in Security**: RLS policies ensure data isolation
- **Simplified Stack**: One service for DB, auth, storage, and realtime
- **Cost Savings**: ~$0-$25/month for MVP vs $200+/month for alternatives
- **TypeScript Generation**: Automatic type safety from database schema

### Negative
- **Migration Complexity**: Moving away from Supabase requires significant effort
- **Debugging Challenges**: RLS policies can be complex to debug
- **Performance Tuning**: Less control over database optimization
- **Backup Strategy**: Need additional backup solution beyond Supabase

## Implementation Strategy

### Phase 1: Foundation (Completed)
- ✅ Database schema design with RLS policies
- ✅ Authentication setup with email/password
- ✅ Basic CRUD operations for core entities
- ✅ Storage buckets for vendor assets

### Phase 2: Advanced Features (In Progress)
- ⏳ Real-time messaging system
- ⏳ Edge Functions for PDF processing
- ⏳ Webhook integration for Stripe
- ⏳ Advanced RLS for client portals

### Phase 3: Optimization (Planned)
- 📋 Database indexing and query optimization
- 📋 Caching strategy with Redis
- 📋 CDN integration for static assets
- 📋 Monitoring and alerting setup

## Migration Strategy (If Needed)

Should we need to migrate away from Supabase:

1. **Database**: PostgreSQL can be exported and hosted anywhere
2. **Auth**: Migrate to Auth0, Clerk, or custom solution
3. **Storage**: Move to S3 or compatible object storage
4. **Realtime**: Implement with Socket.io or Pusher
5. **Timeline**: Estimated 4-6 weeks for complete migration

## Review Schedule
- **3 Months**: Assess performance and costs with real users
- **6 Months**: Evaluate scaling needs and alternative solutions
- **12 Months**: Full review of architecture decision

## References
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL RLS Guide](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Next.js + Supabase Integration](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)

---
*Decision made by: Development Team*
*Date: August 2025*
*Review date: November 2025*