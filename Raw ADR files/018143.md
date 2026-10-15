# ADR 002: Simplified Database Architecture with PostgreSQL

## Status
Accepted

## Context
The electronics recycling system has diverse data storage requirements:
- Need to store structured customer and transaction data
- Need to handle flexible device specifications and assessment rules
- Need to store and query business data efficiently
- Need both strong consistency for financial transactions and good query performance for analytics

## Decision
We will implement a simplified database architecture using PostgreSQL as our primary database, complemented by Redis for caching and Elasticsearch for search capabilities:

1. **PostgreSQL**
   - Primary database for all persistent data
   - Utilizing schemas for logical separation:
     - Device Schema (catalog, specifications)
     - Assessment Schema (rules, results)
     - Customer Schema (profiles, transactions)
   - Using JSONB for flexible attributes where needed
   - Implementing table partitioning for large datasets

2. **Redis**
   - Caching layer for frequent queries
   - Session management
   - Rate limiting
   - Temporary data storage

3. **Elasticsearch**
   - Full-text search capabilities
   - Analytics and reporting
   - Log aggregation

## Consequences

### Positive
- Simplified database management and maintenance
- Single source of truth for transactional data
- Strong consistency where needed
- Reduced operational complexity
- Easier backup and recovery
- Better development experience (single database technology)

### Negative
- Potential performance trade-offs for some specific use cases
- Need for careful schema design and indexing
- May require more vertical scaling

## Technical Details

### PostgreSQL Configuration
```sql
-- Example of flexible device attributes
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(100),
    attributes JSONB,
    assessment_rules JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Partitioning for analytical data
CREATE TABLE analytics_events (
    timestamp TIMESTAMP,
    event_type VARCHAR(100),
    data JSONB
) PARTITION BY RANGE (timestamp);
```

### Redis Usage
- Cache TTL settings based on data type
- Cache invalidation strategy through events
- Session storage configuration

### Elasticsearch Integration
- Real-time indexing through Kafka events
- Custom mappings for device and assessment data
- Periodic reindexing strategy

## Review Trigger
This decision should be reviewed if:
- Query performance becomes problematic
- Data volume exceeds PostgreSQL's efficient handling capacity
- New requirements demand specific database features
- Operational costs become too high 