# ADR-006: Hybrid Storage Architecture (Parquet + Blob Storage)

## Status
Accepted

## Context
The Payments Ingestion system needs to store raw transaction events efficiently while maintaining fast access to processed metrics. Initial design proposed storing normalized transactions in PostgreSQL, but this approach has limitations:

- **Volume**: Raw events can be extremely high volume (millions per day)
- **Cost**: PostgreSQL storage costs scale linearly with data volume
- **Performance**: Insert-heavy workloads can impact query performance for metrics
- **Retention**: Long-term archival of raw events is expensive in relational databases
- **Analytics**: Columnar formats (Parquet) are better suited for analytical workloads

We need a storage strategy that:
- Efficiently stores high-volume raw events
- Maintains fast access to processed metrics
- Supports long-term archival
- Enables efficient analytics queries
- Minimizes costs

## Decision
We will implement a **hybrid storage architecture**:

1. **Raw Events**: Store in Azure Blob Storage as Parquet files
   - Columnar format optimized for analytics
   - Cost-effective long-term storage
   - Automatic lifecycle management (tiering, deletion)
   - Partitioned by date/hour for efficient querying

2. **Processed Metrics**: Store in PostgreSQL
   - Dynamic metrics (real-time calculations)
   - Aggregate metrics (5-minute windows, histograms)
   - Fast query access for dashboards and APIs
   - Relational structure for complex queries

3. **Failed Messages**: Store in PostgreSQL
   - Dead-letter queue for invalid transactions
   - Enables reprocessing and analysis

## Consequences

### Positive
- **Cost Efficiency**: Blob Storage is significantly cheaper than PostgreSQL for large volumes
- **Scalability**: Blob Storage scales to petabytes without performance degradation
- **Analytics Performance**: Parquet format enables efficient columnar queries
- **Separation of Concerns**: Raw data storage separated from processed metrics
- **Lifecycle Management**: Automated tiering (Hot → Cool → Archive) and deletion policies
- **Query Flexibility**: Can query raw events directly from Blob Storage or load into analytics tools
- **PostgreSQL Performance**: Reduced load on PostgreSQL improves metrics query performance
- **Compliance**: Long-term retention policies easier to implement with Blob Storage

### Negative
- **Complexity**: Two storage systems to manage and maintain
- **Query Overhead**: Querying raw events requires different tools/APIs than PostgreSQL
- **Consistency**: Need to ensure data consistency across both storage systems
- **Migration**: Existing systems expecting PostgreSQL-only need updates
- **Tooling**: Requires familiarity with both PostgreSQL and Blob Storage APIs
- **Latency**: Blob Storage queries may have higher latency than PostgreSQL for small datasets

## Alternatives Considered

### PostgreSQL Only
**Pros**: Single storage system, simpler queries, ACID guarantees
**Cons**: High cost at scale, performance degradation with volume, expensive long-term retention
**Reason rejected**: Cost and scalability concerns outweigh simplicity benefits

### Blob Storage Only
**Pros**: Lowest cost, best scalability, optimized for analytics
**Cons**: No fast access to processed metrics, complex query patterns, no relational structure
**Reason rejected**: Need fast access to processed metrics for real-time dashboards

### Azure Data Lake Storage Gen2
**Pros**: Optimized for analytics, hierarchical namespace, better integration with analytics tools
**Cons**: Additional complexity, may be overkill for current needs
**Reason rejected**: Blob Storage provides sufficient capabilities with simpler setup

### Time-Series Database (e.g., TimescaleDB)
**Pros**: Optimized for time-series data, automatic partitioning
**Cons**: Additional database to manage, migration complexity
**Reason rejected**: PostgreSQL with proper indexing provides sufficient performance

## Implementation Details

### Parquet Schema
- Columnar format with schema matching RawEvent data model
- Partitioned by date/hour: `raw-events/YYYY/MM/DD/HH/`
- Compression: Snappy (balance of speed and size)
- Metadata: Includes correlation_id, transaction_id for efficient lookups

### Blob Storage Configuration
- Container: `raw-events`
- Lifecycle policies:
  - Hot tier: 7 days
  - Cool tier: 30 days
  - Archive tier: 90+ days
  - Deletion: After retention period

### PostgreSQL Tables
- `dynamic_metrics`: Real-time calculated metrics
- `payment_metrics_5m`: 5-minute aggregated metrics
- `aggregate_histograms`: Distribution histograms
- `failed_items`: Dead-letter queue

## References
- [Parquet Schema Design](./PARQUET-SCHEMA-DESIGN.md)
- [Storage Architecture Analysis](./STORAGE-ARCHITECTURE-ANALYSIS.md)
- [Blob Storage Implementation Summary](./BLOB-STORAGE-IMPLEMENTATION-SUMMARY.md)
- Azure Blob Storage Documentation: https://docs.microsoft.com/en-us/azure/storage/blobs/
- Apache Parquet Format: https://parquet.apache.org/

