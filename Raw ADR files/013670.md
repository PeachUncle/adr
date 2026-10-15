# ADR-004: Use Azure PostgreSQL Flexible Server

## Status
Accepted

## Context
The Payments Ingestion system needs a relational database to store:
- Normalized payment transactions
- Calculated dynamic metrics
- Aggregated time-series metrics (5-minute windows)

Requirements:
- ACID transactions for data consistency
- Complex queries with JOINs and aggregations
- JSON/JSONB support for flexible metadata
- Time-series data optimization
- Scalability to handle growing data volumes
- High availability for production

Options considered: PostgreSQL Flexible Server, MySQL, Cosmos DB, SQL Server

## Decision
We will use **Azure Database for PostgreSQL - Flexible Server** as our primary data store.

## Consequences

### Positive
- **JSONB support**: Native JSON datatype for flexible metadata storage
- **Time-series features**: Excellent support for time-series data and window functions
- **Rich indexing**: GIN indexes for JSONB, partial indexes, covering indexes
- **Flexible Server benefits**: 
  - Better performance than Single Server
  - Zone-redundant high availability
  - Scheduled maintenance windows
  - More configuration options
- **Managed service**: Automated backups, patching, monitoring
- **Compliance**: Built-in compliance certifications
- **Cost-effective**: Lower cost than Single Server at same performance
- **Extensions**: Support for pg_stat_statements, TimescaleDB (if needed)
- **Team expertise**: Team has PostgreSQL experience

### Negative
- **Cost**: More expensive than some NoSQL alternatives
- **Scaling complexity**: Vertical scaling requires downtime
- **Connection limits**: Connection pooling required for many concurrent connections
- **Azure-specific**: Vendor lock-in to Azure
- **Migration effort**: Requires schema migrations for changes

## Alternatives Considered

### Azure Database for MySQL
**Pros**: Lower cost, similar features
**Cons**: Less sophisticated JSON support, fewer analytical features
**Reason rejected**: PostgreSQL's superior JSON and analytical capabilities

### Azure Cosmos DB
**Pros**: Globally distributed, elastic scale, low latency
**Cons**: Higher cost, different query model, no ACID across documents
**Reason rejected**: Relational model better fits our data structure and query patterns

### Azure SQL Database
**Pros**: Enterprise features, excellent tooling
**Cons**: Higher cost, less efficient JSON handling, licensing complexity
**Reason rejected**: PostgreSQL sufficient and more cost-effective

## Implementation Details

### Schema Design

```sql
-- Fact table: Raw transactions
NormalizedTransactions (
    transaction_id PK,
    timestamp,
    amount,
    currency,
    payment_method,
    metadata JSONB,
    ...
)

-- Derived metrics
DynamicMetrics (
    metric_id PK,
    transaction_id FK,
    metric_name,
    metric_value,
    calculated_at,
    ...
)

-- Time-series aggregates
payment_metrics_5m (
    window_start PK,
    payment_method PK,
    currency PK,
    total_count,
    total_amount,
    breakdowns JSONB,
    ...
)
```

### Configuration by Environment

| Feature | Dev | Staging | Production |
|---------|-----|---------|------------|
| SKU | B_Standard_B1ms | GP_Standard_D2s_v3 | GP_Standard_D4s_v3 |
| Storage | 32 GB | 64 GB | 128 GB |
| Backup Retention | 7 days | 14 days | 35 days |
| HA Mode | Disabled | ZoneRedundant | ZoneRedundant |
| Geo-Redundant | No | Yes | Yes |

### Performance Optimizations
- GIN indexes on JSONB columns
- Partial indexes for common filters
- Materialized views for complex aggregations
- Connection pooling with PgBouncer
- Regular VACUUM and ANALYZE

## Monitoring and Maintenance

- **Metrics**: Query performance, connection count, storage usage
- **Alerts**: Slow queries, connection exhaustion, storage threshold
- **Backups**: Automated daily backups with point-in-time restore
- **Maintenance**: Automated minor version updates

## References
- [Azure PostgreSQL Flexible Server Documentation](https://docs.microsoft.com/azure/postgresql/flexible-server/)
- [PostgreSQL JSONB Performance](https://www.postgresql.org/docs/current/datatype-json.html)
- [Flexible Server vs Single Server](https://docs.microsoft.com/azure/postgresql/flexible-server/concepts-compare-single-server-flexible-server)

## Date
2025-12-04

## Author
Infrastructure Team

