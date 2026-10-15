# ADR-021: Choice of Azure Database for PostgreSQL

**Date:** 2025-10-09

**Status:** Accepted

## Context

The PlumbingPOC application requires a managed PostgreSQL database that supports Row Level Security (RLS), complex queries, and real-time capabilities. The current Supabase PostgreSQL provides these features but at a fixed cost regardless of actual usage. For a low-traffic application (50-100 quote requests/month), we need a cost-effective database solution that maintains feature parity.

## Decision

We will use **Azure Database for PostgreSQL Flexible Server** in the Basic tier as the primary database solution. This provides:

1. **Cost Optimization**: Basic tier specifically designed for small applications
2. **PostgreSQL Compatibility**: Full PostgreSQL feature support including RLS
3. **Managed Service**: Automatic backups, patching, and monitoring
4. **Scalability**: Ability to scale up as application grows
5. **Security**: Advanced security features and compliance certifications

## Implementation Details

### Database Configuration

**Basic Tier Specification:**
```json
{
  "serverName": "plumbingpoc-db",
  "resourceGroup": "plumbingpoc-azure-prod",
  "location": "East US",
  "sku": {
    "name": "B_Standard_B1ms",
    "tier": "Burstable",
    "capacity": 1
  },
  "storage": {
    "storageSizeGB": 32
  },
  "backup": {
    "backupRetentionDays": 7,
    "geoRedundantBackup": "Disabled"
  },
  "version": "15",
  "administratorLogin": "plumbingpoc_admin",
  "network": {
    "publicNetworkAccess": "Enabled",
    "firewallRules": [
      {
        "name": "AllowAzureServices",
        "startIpAddress": "0.0.0.0",
        "endIpAddress": "0.0.0.0"
      }
    ]
  }
}
```

### Connection Configuration

**Environment Variables:**
```bash
# Azure Database Connection
DATABASE_URL="postgresql://plumbingpoc_admin:password@plumbingpoc-db.postgres.database.azure.com:5432/plumbingpoc_db?sslmode=require"

# Connection Pool Settings (for Azure Functions)
DATABASE_CONNECTION_TIMEOUT=30
DATABASE_POOL_SIZE=2
DATABASE_SSL=true
```

### Schema Migration Strategy

**From Supabase to Azure PostgreSQL:**
```sql
-- 1. Extract schema from Supabase
pg_dump --schema-only --no-owner --no-privileges \
  "postgresql://user:password@db.supabase.co:5432/postgres" \
  > plumbingpoc_schema.sql

-- 2. Create Azure database
createdb plumbingpoc_db

-- 3. Restore schema to Azure
psql $DATABASE_URL < plumbingpoc_schema.sql

-- 4. Recreate RLS policies for Azure
-- (Manual recreation required due to auth.uid() differences)
```

### Row Level Security Implementation

**Azure PostgreSQL RLS Policies:**
```sql
-- Enable RLS on tables
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_notes ENABLE ROW LEVEL SECURITY;

-- Recreate policies using JWT claims
CREATE POLICY "Users can view their own requests"
ON requests FOR SELECT
USING (auth.jwt() ->> 'sub' = user_id::text);

CREATE POLICY "Admins can view all requests"
ON requests FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id::text = auth.jwt() ->> 'sub'
    AND role = 'admin'
  )
);
```

## Consequences

### Positive

*   **Cost Effective**: Basic tier perfectly suited for low-traffic applications
*   **Feature Complete**: Full PostgreSQL support including advanced features
*   **Managed Service**: Automatic maintenance, backups, and security updates
*   **Scalability**: Easy upgrade path to higher tiers as application grows
*   **Security**: Enterprise-grade security with Azure AD integration
*   **Compliance**: SOC 2, HIPAA, and other compliance certifications available

### Negative

*   **Vendor Lock-in**: Azure-specific service and pricing
*   **Connection Limits**: Basic tier has connection limitations
*   **Backup Retention**: Limited backup retention in Basic tier (7 days)
*   **Network Latency**: Potential latency for globally distributed users
*   **Migration Complexity**: RLS policies require manual recreation

### Mitigation Strategies

**Performance Optimization:**
- Implement connection pooling in Azure Functions
- Use Azure Cache for Redis for frequently accessed data
- Optimize queries and add appropriate indexes

**Cost Management:**
- Monitor usage through Azure Cost Management
- Set up alerts for unexpected usage spikes
- Consider reserved instances for long-term usage

**Backup Strategy:**
- Implement application-level backups for critical data
- Use Azure Backup for additional retention options
- Test restore procedures regularly

## Alternatives Considered

### Azure SQL Database

**Pros:**
- Tightly integrated with Azure ecosystem
- Advanced security features
- Lower cost for basic workloads

**Cons:**
- SQL Server syntax differences from PostgreSQL
- Less mature PostgreSQL feature support
- Migration complexity from existing PostgreSQL schema

**Decision:** Rejected due to PostgreSQL compatibility requirements

### Amazon RDS PostgreSQL

**Pros:**
- Mature PostgreSQL support
- Flexible pricing options
- Good performance characteristics

**Cons:**
- Not Azure native (vendor diversification goal)
- Additional complexity managing cross-cloud architecture
- Higher cost for small workloads

**Decision:** Rejected to maintain Azure ecosystem consistency

### Supabase (Continued)

**Pros:**
- Familiar feature set and developer experience
- Integrated real-time and authentication
- Simple pricing for small applications

**Cons:**
- Fixed cost regardless of usage
- Vendor lock-in concerns
- Less enterprise features and compliance options

**Decision:** Rejected due to cost optimization goals

## Related Decisions

- ADR-001: Choice of Backend Platform (Supabase → Azure)
- ADR-022: Choice of Azure AD B2C for Authentication
- ADR-023: Choice of Azure SignalR Service for Real-time Features

## Success Metrics

### Technical Metrics
- [ ] Database schema successfully migrated from Supabase
- [ ] RLS policies correctly implemented for Azure AD B2C
- [ ] Application connects and performs CRUD operations
- [ ] Query performance meets or exceeds Supabase baseline

### Performance Metrics
- [ ] Average query response time < 100ms
- [ ] Connection pool utilization < 80%
- [ ] Database CPU usage < 50% during peak loads
- [ ] Memory usage within Basic tier limits

### Cost Metrics
- [ ] Monthly database cost < $15 CAD
- [ ] No unexpected charges from scaling
- [ ] Backup and storage costs within budget
- [ ] Network egress costs minimal

### Reliability Metrics
- [ ] Uptime > 99.9% (Azure SLA)
- [ ] Automated backups working correctly
- [ ] Failover and recovery procedures tested
- [ ] Monitoring and alerting configured

## Future Considerations

**Scaling Up:**
- Upgrade to General Purpose or Memory Optimized tiers as traffic grows
- Implement read replicas for high-read workloads
- Consider Azure Database for PostgreSQL Hyperscale for massive scale

**Advanced Features:**
- Implement Azure Defender for SQL for advanced threat protection
- Set up Azure Monitor for comprehensive database monitoring
- Consider Azure Arc for hybrid cloud scenarios

**Cost Optimization:**
- Use Azure Reservations for predictable workloads
- Implement auto-scaling based on usage patterns
- Consider development/staging environment cost optimization

---

**Note:** Azure Database for PostgreSQL Basic tier is ideal for development, testing, and small production applications. For enterprise workloads requiring high availability, consider General Purpose or Memory Optimized tiers.
