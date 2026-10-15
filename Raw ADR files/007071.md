# ADR 004: Row-Level Multi-Tenancy

**Status:** Accepted

**Date:** 2024-11-12

**Deciders:** Piotr Świderski

**Technical Story:** BuildFlow is a SaaS application where each organization (tenant) must have complete data isolation while sharing the same application instance and database.

---

## Context

BuildFlow serves multiple organizations (construction businesses) in a SaaS model. We need to ensure:

### Current Situation
- SaaS business model with multiple customers
- Each organization has: clients, quotes, projects, invoices
- Complete data isolation required (legal requirement)
- Single application deployment
- Cost-effective scaling

### Requirements
- **Security**: Organization A cannot see Organization B's data
- **Performance**: Queries must be fast despite multi-tenancy
- **Simplicity**: Easy to implement and maintain
- **Cost**: Single database to reduce infrastructure costs
- **Compliance**: GDPR data isolation requirements
- **Scalability**: Support thousands of organizations
- **Development**: Easy to test and develop

---

## Decision

**We will use row-level multi-tenancy with `organization_id` foreign key on all tenant-scoped tables.**

### Implementation Details

1. **Database Schema**
   ```sql
   -- Tenant table
   CREATE TABLE organizations (
       id BIGINT PRIMARY KEY,
       name VARCHAR(255),
       subscription_tier ENUM('starter', 'pro', 'business'),
       created_at TIMESTAMP
   );
   
   -- Tenant-scoped tables
   CREATE TABLE clients (
       id BIGINT PRIMARY KEY,
       organization_id BIGINT NOT NULL,
       name VARCHAR(255),
       email VARCHAR(255),
       FOREIGN KEY (organization_id) REFERENCES organizations(id),
       INDEX idx_organization_id (organization_id)
   );
   
   -- All data tables include organization_id
   ```

2. **Application Layer**
   
   **Laravel - Global Scopes:**
   ```php
   // app/Models/Client.php
   class Client extends Model
   {
       protected static function booted()
       {
           static::addGlobalScope('organization', function ($query) {
               if (auth()->check()) {
                   $query->where('organization_id', auth()->user()->organization_id);
               }
           });
       }
   }
   
   // All queries automatically filtered:
   Client::all(); // Only returns current org's clients
   ```
   
   **Symfony - Doctrine Filters:**
   ```php
   // src/Filter/OrganizationFilter.php
   class OrganizationFilter extends SQLFilter
   {
       public function addFilterConstraint(ClassMetadata $meta, $alias)
       {
           if (!$meta->hasField('organization_id')) {
               return '';
           }
           return $alias . '.organization_id = ' . $this->getParameter('org_id');
       }
   }
   ```

3. **Request Flow**
   ```
   1. User authenticates
   2. JWT token includes organization_id
   3. Middleware extracts organization_id from token
   4. Global scope/filter applied to all queries
   5. All queries automatically filtered by organization_id
   6. Results returned only for user's organization
   ```

4. **Indexes**
   - Primary key on all tables
   - Index on `organization_id` for all tenant-scoped tables
   - Composite indexes where needed: `(organization_id, created_at)`

5. **Unscoped Queries**
   - Admin operations may need to bypass scope
   - Explicit `withoutGlobalScope()` in Laravel
   - Disable filter in Symfony
   - Logged and audited

---

## Consequences

### Positive
- ✅ **Simple**: Standard SQL, familiar patterns
- ✅ **Cost-Effective**: Single database, shared resources
- ✅ **Performance**: Indexed properly, queries are fast
- ✅ **Portable**: Works with any SQL database
- ✅ **Development**: Easy to test with local database
- ✅ **Backups**: Single backup process
- ✅ **Migrations**: Single migration path
- ✅ **Monitoring**: Single database to monitor

### Negative
- ⚠️ **Query Overhead**: Every query includes organization_id filter
- ⚠️ **Index Size**: More indexes needed
- ⚠️ **Mistakes Possible**: Developer could forget to scope query
- ⚠️ **Cross-Tenant Queries**: Harder to do analytics across tenants
- ⚠️ **Backup Granularity**: Can't backup single tenant easily
- ⚠️ **Deletion**: Can't easily drop single tenant's data

### Risks & Mitigation
- **Risk**: Developer forgets to scope query, data leakage
  - **Mitigation**: Global scopes automatic, code review, automated tests
  
- **Risk**: Performance degradation with many tenants
  - **Mitigation**: Proper indexes, query optimization, monitoring
  
- **Risk**: One tenant's data volume affects others
  - **Mitigation**: Monitoring, limits enforcement, eventual sharding
  
- **Risk**: Difficult to isolate problematic tenant
  - **Mitigation**: Per-tenant query logging, rate limiting

---

## Alternatives Considered

### Alternative 1: Database-Per-Tenant
**Description:** Each organization gets its own database

**Pros:**
- Complete isolation
- Easy to backup single tenant
- Performance isolation
- Easy to delete tenant (drop database)
- Can customize schema per tenant

**Cons:**
- Expensive (database per tenant)
- Complex connection management
- Harder to scale (100s of databases)
- Migrations complex (run on all databases)
- Cross-tenant analytics difficult
- Development environment complex

**Why rejected:** Cost prohibitive at scale. Too complex for MVP. Over-engineering for security we can achieve simpler.

### Alternative 2: Schema-Per-Tenant
**Description:** Each organization gets its own schema in same database

**Pros:**
- Better isolation than row-level
- Single database connection
- Can delete tenant easily (drop schema)
- Better than separate databases

**Cons:**
- PostgreSQL specific (not MySQL)
- Connection pooling complex
- Schema switching overhead
- Still complex migrations
- Limited by database schema limits

**Why rejected:** Added complexity not worth marginal benefits. Not portable across databases.

### Alternative 3: Hybrid (Hot Tenants Get Own Database)
**Description:** Small tenants share database, large ones get dedicated

**Pros:**
- Optimize for both small and large
- Performance isolation for big clients
- Cost-effective for small clients

**Cons:**
- Two code paths to maintain
- Complex routing logic
- When to promote tenant?
- Data migration needed
- Operational complexity

**Why rejected:** Too complex for MVP. Can add later if needed (unlikely for construction business scale).

### Alternative 4: No Multi-Tenancy (Single Tenant Deployments)
**Description:** Each customer gets their own deployment

**Pros:**
- Complete isolation
- Custom features per customer
- Performance isolation
- Easy to charge premium

**Cons:**
- Expensive infrastructure
- Complex deployment pipeline
- Update all instances for bug fixes
- Not true SaaS
- Doesn't scale

**Why rejected:** Not a SaaS model. Too expensive to operate. Doesn't fit business model.

---

## Related Decisions

- [ADR-003](003-jwt-authentication.md) - Token includes organization_id
- [ADR-007](007-postgresql-primary-database.md) - Database choice supports this
- [ADR-009](009-feature-flags-for-tiers.md) - Feature access per organization

---

## References

- [Multi-Tenant Data Architecture](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/tenancy-models)
- [Laravel Multi-Tenancy Package](https://tenancyforlaravel.com/)
- [Postgres Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Designing Data Intensive Applications - Multi-Tenancy](https://dataintensive.net/)

---

## Notes

### Why Not Row-Level Security (RLS)?
PostgreSQL offers Row-Level Security which could enforce organization_id filtering at database level. We chose application-level scopes because:
- Works with both MySQL and PostgreSQL
- More portable across databases
- Easier to debug (visible in application logs)
- More flexible for complex rules
- RLS can be added later for defense in depth

### Testing Strategy
- Unit tests with multiple organizations
- Integration tests verify data isolation
- Each test creates fresh organization
- Assertions that org A can't see org B data
- Automated security scanning

### Migration Path
If we ever need database-per-tenant:
1. Add tenant database routing layer
2. Migrate large tenants first
3. Keep small tenants on shared database
4. Code works with both models

### Performance Monitoring
- Query performance per tenant
- Index usage statistics
- Slow query log with organization_id
- Alert on missing indexes
- Tenant size limits enforced

---

**Last Updated:** 2024-11-12
