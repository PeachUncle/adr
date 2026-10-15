# ADR-001: Multi-Tenant Data Isolation Strategy

## Status
Accepted

## Context
AdvisorOS is a multi-tenant CPA platform that serves multiple accounting organizations, each with their own clients, documents, and sensitive financial data. Each organization must be completely isolated from others for security, compliance, and operational reasons.

## Decision
We have implemented a **shared database, separate rows** multi-tenancy pattern with organization-based isolation:

### Architecture Components:
1. **Organization as Primary Tenant Boundary**
   - Each organization has a unique `subdomain` for URL-based routing
   - All core entities (Users, Clients, Documents, etc.) include `organizationId` foreign key
   - Prisma schema enforces organization-level relationships with cascade deletion

2. **Data Isolation Mechanisms**
   - Database-level: All queries filtered by `organizationId` at the ORM level
   - Application-level: Middleware validates organization context for all requests
   - Authentication: JWT tokens include `organizationId` for request validation

3. **Tenant Resolution Strategy**
   - Subdomain-based tenant identification (e.g., `acme.advisoros.com`)
   - Organization lookup via subdomain during authentication
   - Session tokens tied to specific organization context

### Implementation Details:
```typescript
// Every major entity includes organizationId
model User {
  id             String       @id @default(cuid())
  organizationId String
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  // ... other fields
}

// Automatic tenant filtering in middleware
requestHeaders.set('x-organization-id', token.organizationId || '')
```

## Alternatives Considered

1. **Database-per-tenant**: Would provide stronger isolation but increase operational complexity
2. **Shared everything**: Insufficient isolation for financial data
3. **Application-per-tenant**: Not cost-effective for SaaS model

## Consequences

### Positive:
- **Strong Data Isolation**: Complete separation of organizational data
- **Cost Efficient**: Single database instance reduces infrastructure costs
- **Compliance Ready**: Meets SOC2 and financial data protection requirements
- **Scalable**: Can handle 10,000+ organizations efficiently
- **Development Velocity**: Single codebase and deployment

### Negative:
- **Query Complexity**: All queries must include organization filter
- **Risk of Data Leakage**: Human error could expose cross-organization data
- **Limited Customization**: Schema changes affect all tenants

### Mitigation Strategies:
1. **Database Constraints**: Foreign key constraints prevent orphaned records
2. **Query Validation**: Prisma middleware validates all organization-scoped queries
3. **Testing**: Comprehensive multi-tenant integration tests
4. **Monitoring**: Audit logs track all cross-organization access attempts
5. **RLS Consideration**: Future migration to Row Level Security for additional protection

## Metrics and Monitoring
- Query performance with organization filters
- Failed organization validation attempts
- Cross-organization access attempts (security metric)
- Database connection pool utilization
- Tenant data size distribution

## Future Considerations
- **Read Replicas**: Implement per-region read replicas for global scale
- **Database Sharding**: Shard by organization hash for 100,000+ organizations
- **Edge Caching**: Cache tenant configuration at CDN edge
- **Disaster Recovery**: Per-tenant backup and restore capabilities