# 2. Use Managed Database Backups for Data Protection

Date: 2024-01-02

## Status

Accepted

## Context

Our application requires a persistent data store, which will be hosted on a managed database service on Azure. We need a reliable, robust, and low-maintenance strategy for data backup and disaster recovery to prevent data loss and ensure business continuity. Building a custom backup solution is complex, error-prone, and operationally intensive.

## Decision

We will exclusively use the native, automated backup and recovery features provided by the Azure managed database service we choose (e.g., Azure Database for PostgreSQL, MySQL, or Cosmos DB).

This strategy includes leveraging features such as:
- Automated full, differential, and transaction log backups.
- Point-in-Time Restore (PITR) capabilities.
- Geo-redundant backup storage for production environments to protect against regional outages.
- Simple, portal-based or CLI-based restoration procedures.

We will not build or maintain any custom scripts or tools for database backups.

## Consequences

### Positive:
- **High Reliability**: Leverages a battle-tested, enterprise-grade backup solution managed by the cloud provider.
- **Reduced Operational Overhead**: No need to design, implement, test, or maintain custom backup scripts. Our team can focus on the application.
- **Point-in-Time Recovery**: Provides granular recovery options, allowing us to restore the database to a specific moment in time just before a data corruption event.
- **Cost-Effective**: Typically more cost-effective than a custom solution when considering engineering time and storage management.
- **Security & Compliance**: Azure's backup solutions are compliant with various industry standards, and data is encrypted at rest.

### Negative:
- **Provider Lock-in**: The backup formats are specific to the cloud provider, making it more difficult to migrate the database and its backups to another cloud or on-premise.
- **Limited Control**: We have less control over the specific timing of automated backups compared to a custom cron job, though the frequency is generally sufficient for most use cases.
- **Cost**: While cost-effective, automated backups are not free. Costs are incurred for storage based on the amount of data and the retention period.
