# ADR-003: Use PostgreSQL over NoSQL

**Status**: Accepted

**Date**: 2024-01-11

**Deciders**: Engineering Team, Database Architect

## Context

We need to choose a database for our application. The data model includes:

- **Users**: Profile information, authentication credentials
- **Families**: Groups of users with hierarchical relationships
- **Tasks**: Assignments with due dates, points, status tracking
- **Chores**: Recurring tasks with rotation schedules
- **Points**: Transaction history and leaderboards
- **Notifications**: Event-driven messages

Key requirements:
- Strong data consistency (task assignments must be atomic)
- Complex queries (leaderboards, filtering, aggregations)
- Transactions (awarding points when task completed)
- Relational data (users belong to families, tasks assigned to users)
- Moderate write volume (~1000 writes/second)
- High read volume (~10,000 reads/second)
- Data integrity (foreign keys, constraints)
- Audit trail and history tracking

## Decision

We will use **PostgreSQL 16** as our primary database.

## Consequences

### Positive

- **ACID Transactions**: Strong consistency guarantees
  - Task completion and point awarding happen atomically
  - No risk of partial updates or inconsistent state
  - Rollback support for error scenarios
  
- **Relational Model Fits Well**: Natural representation of our domain
  - Users → Families (many-to-many with roles)
  - Tasks → Users (assigned_to relationship)
  - Points → Tasks → Users (full audit trail)
  - Foreign keys enforce referential integrity
  
- **Rich Query Capabilities**:
  - Complex JOINs for aggregations (leaderboards, family stats)
  - Window functions for rankings
  - CTEs (Common Table Expressions) for complex logic
  - Full-text search for task searching
  - JSON/JSONB for flexible metadata storage
  
- **Data Integrity**: Constraints prevent invalid data
  - NOT NULL constraints
  - CHECK constraints (e.g., points >= 0)
  - UNIQUE constraints (e.g., email)
  - Foreign keys prevent orphaned records
  
- **Mature Ecosystem**:
  - Battle-tested (30+ years)
  - Excellent tooling (pgAdmin, psql, DBeaver)
  - Rich monitoring (pg_stat_statements, pg_stat_activity)
  - Strong backup/restore tools
  
- **Performance Features**:
  - Advanced indexing (B-tree, GiST, GIN, BRIN)
  - Query planner and optimizer
  - Partitioning for large tables
  - Parallel query execution
  - Connection pooling (PgBouncer)
  
- **Extensions**:
  - PostGIS for future location features
  - pg_cron for scheduled tasks
  - pg_stat_statements for query analysis
  
- **Cloud Support**: Fully managed options available
  - AWS RDS PostgreSQL
  - AWS Aurora PostgreSQL (MySQL-compatible)
  - Easy scaling (vertical and read replicas)

### Negative

- **Vertical Scaling Limitations**: Single-node writes can become bottleneck
  - Mitigation: Read replicas for read scaling
  - Mitigation: Connection pooling (PgBouncer)
  - Mitigation: Caching layer (Redis) for hot data
  
- **Schema Changes**: Migrations can be complex
  - ALTER TABLE can lock table during migration
  - Mitigation: Use tools like gh-ost or pt-online-schema-change for large tables
  - Mitigation: Plan migrations carefully
  
- **Memory Usage**: Requires tuning for optimal performance
  - Need to configure shared_buffers, work_mem, etc.
  - Mitigation: Use AWS RDS with recommended settings
  
- **Replication Complexity**: Multi-master setups are complex
  - PostgreSQL primarily single-master
  - Mitigation: Not needed for our scale (10K families)

### Neutral

- **SQL Knowledge Required**: Team needs SQL expertise
  - Most developers already know SQL
  - Learning curve lower than some NoSQL query languages

## Alternatives Considered

### MongoDB (Document Database)

**Pros**:
- Flexible schema (schema-less)
- Good horizontal scaling
- Easy to get started
- Native JSON storage

**Cons**:
- Lack of transactions across documents (until recently, and still limited)
- No foreign keys or referential integrity
- Complex queries (aggregation pipeline) less intuitive than SQL
- Eventual consistency by default can cause issues
- Our data is highly relational, poor fit for document model

**Example Problem**:
```javascript
// Without transactions, this can fail partially:
// 1. Mark task as completed
db.tasks.updateOne({_id: taskId}, {$set: {status: 'completed'}})
// 2. Award points (what if this fails?)
db.points.insertOne({userId: userId, points: 10, taskId: taskId})
// 3. Task marked complete but no points awarded = inconsistent state
```

**Why Rejected**: 
- Lack of strong transactions critical for point system
- Relational data model doesn't fit document paradigm
- No foreign keys makes maintaining integrity difficult

### DynamoDB (Key-Value Store)

**Pros**:
- Excellent scalability
- Fully managed by AWS
- Predictable performance
- Pay-per-request pricing

**Cons**:
- Limited query capabilities (only primary key and sort key)
- No JOINs (must denormalize data heavily)
- No transactions across partition keys (limited to single partition)
- Difficult to model complex relationships
- Query patterns must be known upfront
- Expensive for secondary indexes

**Example Problem**:
```
Query: "Get all pending tasks for a user across all families"

With DynamoDB: Need to:
- Create GSI (Global Secondary Index) for user_id + status
- OR query each family separately (multiple queries)
- OR denormalize data into user's record (data duplication)

With PostgreSQL: Single query
SELECT * FROM tasks WHERE assigned_to = $1 AND status = 'pending'
```

**Why Rejected**:
- Query patterns too restrictive for our use cases
- Complex relationships difficult to model efficiently
- No native support for aggregations (leaderboards)

### Cassandra (Wide Column Store)

**Pros**:
- Excellent write scalability
- High availability
- Linear scalability

**Cons**:
- Eventual consistency
- No JOINs
- Query patterns must be designed upfront
- More complex to operate
- Overkill for our scale (10K families)
- Limited support for complex queries

**Why Rejected**: 
- Over-engineered for our needs
- Eventual consistency problematic for point system
- Query limitations too restrictive

### MySQL

**Pros**:
- Very similar to PostgreSQL
- Slightly simpler to operate
- Good ecosystem

**Cons**:
- Less advanced features (window functions added later)
- Weaker JSON support
- Less extensible
- Not as good for complex queries

**Why Rejected**: 
- PostgreSQL's advanced features (CTEs, window functions, JSONB) valuable
- PostgreSQL better for complex analytical queries (leaderboards, stats)
- Team preference for PostgreSQL

## Database Schema Design

### Core Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(512),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Families
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Family Members (Junction Table)
CREATE TABLE family_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'member', 'child')),
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(family_id, user_id)
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    due_date TIMESTAMP,
    points INTEGER NOT NULL DEFAULT 0 CHECK (points >= 0),
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Points (Audit Trail)
CREATE TABLE points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    points INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_tasks_family_status ON tasks(family_id, status);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_points_user_family ON points(user_id, family_id);
CREATE INDEX idx_points_created_at ON points(created_at);
```

### Example Complex Query (Leaderboard)

```sql
-- Monthly family leaderboard with rankings
SELECT 
    u.id,
    u.name,
    SUM(p.points) as total_points,
    COUNT(DISTINCT p.task_id) as tasks_completed,
    RANK() OVER (ORDER BY SUM(p.points) DESC) as rank
FROM users u
JOIN points p ON u.id = p.user_id
WHERE 
    p.family_id = $1
    AND p.created_at >= date_trunc('month', NOW())
    AND p.points > 0
GROUP BY u.id, u.name
ORDER BY total_points DESC;
```

## Performance Optimization

### Caching Strategy

Use Redis for hot data:
- User sessions (JWT tokens)
- Recent tasks for a family
- Current leaderboard standings
- Frequently accessed user profiles

Cache invalidation on writes.

### Read Replicas

For read-heavy operations:
- Leaderboard queries
- Task list viewing
- Analytics and reporting

### Connection Pooling

Use PgBouncer to manage connections:
- Limit concurrent connections to database
- Pool and reuse connections
- Handle connection spikes gracefully

### Query Optimization

- Use EXPLAIN ANALYZE for slow queries
- Add indexes based on query patterns
- Use materialized views for complex aggregations
- Partition large tables (e.g., points table by month)

## Backup and Recovery

- **Automated Backups**: Daily full backups, 30-day retention
- **Point-in-Time Recovery**: Transaction log archival
- **Backup Testing**: Monthly restore drills
- **RTO**: < 4 hours
- **RPO**: < 1 hour (transaction logs)

## Monitoring

- **Slow Query Log**: Log queries > 1000ms
- **Connection Pool Monitoring**: Track active/idle connections
- **Replication Lag**: Monitor read replica delay
- **Disk Usage**: Alert at 80% capacity
- **Cache Hit Ratio**: Monitor buffer cache efficiency

## Migration Path

If PostgreSQL becomes a bottleneck (unlikely at 10K families):

1. **Vertical Scaling**: Upgrade to larger instance (up to 128 vCPU, 4TB RAM on AWS)
2. **Read Replicas**: Add multiple read replicas for read scaling
3. **Sharding**: Shard by family_id if needed (complex, avoid if possible)
4. **Hybrid Approach**: Move specific workloads to specialized databases
   - Time-series data → TimescaleDB (PostgreSQL extension)
   - Full-text search → Elasticsearch
   - Caching → Redis (already using)

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
- [AWS RDS PostgreSQL Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

## Revision History

- **2024-01-11**: Initial decision
- **2024-01-15**: Added schema design and optimization strategies

---

**Previous ADR**: [ADR-002: Use Flutter for Mobile App](./ADR-002-flutter-for-mobile.md)  
**Next ADR**: [ADR-004: Use Kafka for Event Streaming](./ADR-004-kafka-for-events.md)
