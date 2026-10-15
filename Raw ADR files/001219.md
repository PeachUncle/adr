# ADR-002: Multi-Tenant Data Isolation Strategy

## Status
Accepted

## Date
2024-01-18

## Context
CoreFlow360 V4 must support multiple businesses (tenants) on a single deployment while ensuring:
- Complete data isolation between tenants
- Performance isolation (one tenant cannot impact another)
- Cost-effective scaling
- Compliance with data privacy regulations
- Easy tenant onboarding and offboarding

## Decision
We will implement a **Hybrid Isolation Strategy** combining:

1. **Logical Isolation** at the application level
2. **Schema Isolation** at the database level
3. **Resource Isolation** using Cloudflare's infrastructure

### Isolation Layers

```
Application Layer    │  Business Context Injection
─────────────────────┼──────────────────────────
Middleware Layer     │  Tenant Router & Validator
─────────────────────┼──────────────────────────
Database Layer       │  Schema Prefixing
─────────────────────┼──────────────────────────
Storage Layer        │  Isolated KV Namespaces
─────────────────────┼──────────────────────────
Infrastructure       │  Cloudflare Isolation
```

### Database Strategy
- **Primary**: Schema isolation with prefixed tables (business_id.table_name)
- **Secondary**: Row-level security for shared tables
- **Future**: Database-per-tenant for enterprise customers

## Consequences

### Positive
- **Security**: Multiple layers of isolation prevent data leaks
- **Performance**: Schema isolation provides good query performance
- **Scalability**: Can handle thousands of tenants
- **Compliance**: Meets GDPR and SOC2 requirements
- **Flexibility**: Can upgrade specific tenants to dedicated resources

### Negative
- **Complexity**: Multiple isolation strategies to maintain
- **Migration**: Moving between isolation levels is complex
- **Testing**: Need to test all isolation boundaries
- **Overhead**: Business context must be passed everywhere

### Risks
- Developer error could expose cross-tenant data
- Performance degradation with many tenants
- Complex debugging across tenant boundaries

## Alternatives Considered

### 1. Single Shared Database
- **Pros**: Simple, cost-effective
- **Cons**: High security risk, performance issues
- **Rejected because**: Insufficient isolation for sensitive business data

### 2. Database per Tenant
- **Pros**: Complete isolation, easy backup/restore
- **Cons**: Expensive, complex management
- **Rejected because**: Not cost-effective for small tenants

### 3. Kubernetes Namespaces
- **Pros**: Strong isolation, resource limits
- **Cons**: High operational overhead
- **Rejected because**: Cloudflare Workers provides sufficient isolation

## Implementation Details

### Tenant Context
```typescript
interface TenantContext {
  businessId: string;
  tenantId: string;
  tier: 'free' | 'starter' | 'professional' | 'enterprise';
  limits: ResourceLimits;
  features: string[];
}
```

### Middleware Chain
1. Extract business ID from JWT/header
2. Validate tenant access
3. Load tenant configuration
4. Inject isolated resources
5. Apply rate limits
6. Execute request
7. Audit log with tenant context

### Database Queries
```sql
-- Automatic prefixing
SELECT * FROM ${businessId}.customers WHERE active = 1;

-- Row-level security fallback
SELECT * FROM shared_table
WHERE business_id = ? AND active = 1;
```

## Security Measures

### Preventing Cross-Tenant Access
1. **Middleware Enforcement**: Every request validated
2. **Database Constraints**: Foreign keys include business_id
3. **Query Validation**: Automatic injection of tenant filters
4. **Audit Logging**: Track all cross-tenant attempts
5. **Penetration Testing**: Regular security audits

### Data Encryption
- Tenant-specific encryption keys
- Field-level encryption for sensitive data
- Encrypted backups per tenant

## Migration Path

### Onboarding New Tenant
1. Create business record
2. Generate tenant ID and encryption keys
3. Initialize database schema
4. Configure KV namespaces
5. Set resource limits
6. Enable features based on tier

### Upgrading Tenant Isolation
```
Shared Tables → Schema Isolation → Dedicated Database → Dedicated Infrastructure
```

## Monitoring

### Key Metrics
- Queries per tenant
- Resource usage per tenant
- Cross-tenant access attempts
- Tenant-specific error rates
- Performance per isolation level

### Alerts
- Suspicious cross-tenant patterns
- Resource limit violations
- Isolation boundary errors
- Unusual data access patterns

## Compliance Considerations

### GDPR
- Data portability via tenant-specific exports
- Right to deletion at tenant level
- Data residency options for EU tenants

### SOC2
- Audit trails per tenant
- Access controls verified
- Regular security assessments

### HIPAA (Future)
- Enhanced encryption
- Dedicated infrastructure option
- Additional audit requirements

## Testing Strategy

### Unit Tests
- Verify tenant context injection
- Test query prefixing
- Validate isolation boundaries

### Integration Tests
- Multi-tenant scenarios
- Cross-tenant attack attempts
- Performance under load

### Security Tests
- Penetration testing
- SQL injection with tenant context
- Authorization bypass attempts

## References
- [Multi-Tenant Architecture Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/overview)
- [Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Cloudflare Durable Objects](https://developers.cloudflare.com/workers/runtime-apis/durable-objects)