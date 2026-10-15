# ADR-021: Azure Database for PostgreSQL Flexible Server

**Status:** ✅ Accepted  
**Date:** October 20, 2025  
**Context:** Migration from Containerized PostgreSQL

## Context

Initial deployment used containerized PostgreSQL in Azure Container Apps, but encountered critical issues:

- **Azure Files permissions**: PostgreSQL requires chmod operations for initialization, which Azure Files doesn't support
- **Data persistence**: Uncertain durability across container restarts
- **Production readiness**: Containerized databases not recommended for production
- **Backup/HA**: Manual setup required for backups and high availability
- **Performance**: Container resource limits impact database performance

After 3+ hours troubleshooting permission issues, the decision was made to migrate to managed PostgreSQL.

## Decision

Migrated to **Azure Database for PostgreSQL Flexible Server** as the production database solution.

## Rationale

1. **No Permission Issues**: Managed service handles all file permissions
2. **Production Ready**: Microsoft-managed with SLA guarantees
3. **Automatic Backups**: 7-30 day retention, point-in-time restore
4. **High Availability**: Zone-redundant deployment available
5. **Security**: VNet integration, encryption at rest/in-transit, Azure AD auth
6. **Monitoring**: Built-in Azure Monitor integration
7. **Cost Effective**: Basic tier ~$12/month for development

## Consequences

### Positive

- **Immediate reliability**: Works without Azure Files workarounds
- **Enterprise features**: Backups, HA, monitoring out-of-the-box
- **Better performance**: Dedicated resources, not sharing with containers
- **Easier management**: Azure Portal for monitoring, scaling
- **Compliance**: GDPR, HIPAA, SOC 2 certified
- **Patch management**: Automatic security updates

### Negative

- **Higher cost**: $12-200/month vs $0 for containerized (but worth it)
- **Connection string complexity**: Requires FQDN patching (ADR-022)
- **Cold start**: 30-60s startup time (vs instant for container)
- **Less portable**: Tied to Azure (vs Docker-based PostgreSQL)

### Risks Mitigated

- Connection string FQDN patching implemented (ADR-022)
- Network security group rules configured
- Firewall allows Azure services (0.0.0.0/0)
- Connection pooling via Npgsql
- Retry policies for transient failures

## Implementation

**Bicep Infrastructure** (infra/resources.bicep):

```bicep
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: 'psql-${resourceToken}'
  location: location
  sku: {
    name: 'Standard_B1ms'  // Burstable, 1 vCore, 2GB RAM
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: 'edumind_admin'
    administratorLoginPassword: postgresPassword
    storage: {
      storageSizeGB: 32
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'  // Enable for production
    }
    highAvailability: {
      mode: 'Disabled'  // Enable for production
    }
  }
}

// Allow Azure services
resource postgresFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Database
resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: 'edumind'
}

output POSTGRES_CONNECTION_STRING string = 'Host=${postgresServer.properties.fullyQualifiedDomainName};Port=5432;Database=edumind;Username=edumind_admin;Password=${postgresPassword};SSL Mode=Require'
```

**Connection String Example**:

```
Host=psql-abc123.postgres.database.azure.com;Port=5432;Database=edumind;Username=edumind_admin;Password=***;SSL Mode=Require
```

## SKU Tiers

**Development** (Standard_B1ms):

- 1 vCore, 2GB RAM
- Burstable performance
- ~$12/month
- Suitable for 50-500 students

**Production** (Standard_D2ds_v5):

- 2 vCores, 8GB RAM
- Consistent performance
- ~$120/month
- Suitable for 1,000-10,000 students

**Enterprise** (Standard_D8ds_v5):

- 8 vCores, 32GB RAM
- High availability enabled
- ~$500/month
- Suitable for 50,000+ students

## Migration Process

1. **Before**: Containerized PostgreSQL with Azure Files mount
2. **Issues**: Permission errors during initialization
3. **Decision**: Migrate to managed PostgreSQL
4. **Deploy**: azd provision creates PostgreSQL Flexible Server
5. **Migrate**: Run EF Core migrations against new database
6. **Seed**: Re-run seed-demo-data.sql
7. **Update**: Connection string FQDN patching in Program.cs
8. **Verify**: Health checks confirm database connectivity

**Timeline**:

- 11:00 - Discovered Azure Files permission issue
- 11:30 - Attempted multiple workarounds (chmod, emptyDir, etc.)
- 14:30 - Decision to migrate to managed PostgreSQL
- 15:00 - Bicep infrastructure updated
- 15:30 - Successful deployment with managed database

## Monitoring

**Azure Monitor Metrics**:

- CPU utilization
- Memory usage
- Active connections
- IOPS (read/write)
- Replication lag (if HA enabled)

**Query Performance Insights**:

- Slow query log
- Most expensive queries
- Query statistics

## Backup Strategy

**Automated Backups**:

- Daily full backups
- Transaction log backups every 5 minutes
- 7-day retention (configurable 7-35 days)
- Point-in-time restore

**Disaster Recovery**:

- Geo-redundant backups (enable for production)
- Cross-region restore capability
- RTO: 15 minutes
- RPO: 5 minutes

## Alternative Considered: Fix Azure Files Permissions

**Rejected because:**

- Would require complex init containers
- Unreliable across Azure updates
- Not production-recommended by Azure
- Time spent troubleshooting exceeded deployment time for managed service
- No enterprise features (backups, HA, monitoring)

**Quote from analysis**:

> "The time spent fighting Azure Files permissions (3+ hours) could have deployed a managed database 20 times over."

## Related Decisions

- ADR-005: PostgreSQL as Primary Database
- ADR-020: Azure Container Apps for Hosting
- ADR-022: Runtime FQDN Detection (connection string patching)
- ADR-070: Entity Framework Core for ORM

## References

- `infra/resources.bicep` - PostgreSQL Flexible Server definition
- Commit: `252231e` - "Migrate to Azure Database for PostgreSQL"
- Commit: `ec415a5` - Initial migration attempt
- docs/deployment/PRAGMATIC_POSTGRES_SOLUTION.md
- docs/deployment/POSTGRESQL_AZURE_FILES_FIX.md
