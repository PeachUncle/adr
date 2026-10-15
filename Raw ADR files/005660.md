# ADR-003: Database Architecture & Schema

## Status

Accepted

## Context

AutoFund AI needs a robust database architecture to support:

- **User Management**: Authentication, subscriptions, and user profiles
- **Processing History**: Track IES processing tasks and results
- **Financial Data**: Store extracted financial information and analysis results
- **Audit Trail**: Complete audit logging for compliance
- **Performance**: Handle concurrent processing and queries efficiently
- **Scalability**: Support growth from startup to enterprise scale
- **Data Privacy**: GDPR-compliant data handling and storage

Key requirements include transaction integrity, backup capabilities, and the ability to handle complex financial data relationships.

## Decision

We selected PostgreSQL as the primary database with the following architecture:

### Database Choice: PostgreSQL 15
- **ACID Compliance**: Strong transaction guarantees
- **JSON Support**: Native JSONB for flexible financial data storage
- **Full-Text Search**: Built-in search capabilities
- **Performance**: Excellent query performance and indexing
- **Extensions**: Rich ecosystem of extensions
- **Maturity**: Proven reliability and extensive tooling

### Schema Design

#### Core Tables

```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    nif VARCHAR(9),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- IES Processing Jobs
CREATE TABLE ies_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_nif VARCHAR(9) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    checksum VARCHAR(64),
    status job_status DEFAULT 'pending',
    metadata JSONB,
    processing_started TIMESTAMP,
    processing_completed TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Financial Analysis Results
CREATE TABLE financial_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES ies_jobs(id) ON DELETE CASCADE,
    financial_data JSONB NOT NULL,
    analysis_data JSONB NOT NULL,
    risk_level VARCHAR(20) CHECK (risk_level IN ('BAIXO', 'MÉDIO', 'ALTO', 'CRÍTICO')),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logging
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_status INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Enums and Types
```sql
CREATE TYPE job_status AS ENUM (
    'pending',
    'uploading',
    'extracting',
    'analyzing',
    'generating',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE subscription_tier AS ENUM (
    'free',
    'professional',
    'enterprise'
);
```

### Indexing Strategy

```sql
-- Performance Indexes
CREATE INDEX idx_ies_jobs_user_id ON ies_jobs(user_id);
CREATE INDEX idx_ies_jobs_status ON ies_jobs(status);
CREATE INDEX idx_ies_jobs_created_at ON ies_jobs(created_at DESC);
CREATE INDEX idx_financial_analyses_risk_level ON financial_analyses(risk_level);
CREATE INDEX idx_financial_analyses_created_at ON financial_analyses(created_at DESC);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

-- JSONB Indexes for financial data
CREATE INDEX idx_financial_data_volume ON financial_analyses
    USING GIN ((financial_data->'volume_negocios'));
CREATE INDEX idx_analysis_data_rating ON financial_analyses
    USING GIN ((analysis_data->'rating'));
```

## Consequences

### Positive Consequences
- **Data Integrity**: ACID properties ensure data consistency
- **Flexibility**: JSONB allows for evolving financial data structures
- **Performance**: Optimized indexes and query performance
- **Scalability**: PostgreSQL scales well with growth
- **Tooling**: Rich ecosystem of tools and extensions
- **Compliance**: Built-in audit logging and security features

### Negative Consequences
- **Complexity**: More complex than NoSQL alternatives
- **Resource Usage**: Higher memory and CPU requirements
- **Migration Overhead**: Schema migrations require careful planning
- **Operational Overhead**: Database maintenance and tuning required

### Risks
- **Scaling Limits**: May need sharding at very large scale
- **Performance Bottlenecks**: Complex queries could become slow
- **Data Growth**: JSONB columns could become large
- **Backup Complexity**: Large database backups and restores

## Alternatives Considered

### Alternative 1: MongoDB
**Pros**: Flexible schema, good for unstructured data
**Cons**: Limited transaction support, less mature financial tooling
**Rejected**: ACID requirements and complex relationships favor PostgreSQL

### Alternative 2: MySQL
**Pros**: Familiar to many developers, good performance
**Cons**: Limited JSON capabilities, less advanced features
**Rejected**: PostgreSQL's JSONB and extension support superior

### Alternative 3: SQLite
**Pros**: Simple setup, zero-config deployment
**Cons**: Not suitable for concurrent multi-user access
**Rejected**: Insufficient for multi-user SaaS application

### Alternative 4: Hybrid Approach (PostgreSQL + MongoDB)
**Pros**: Best of both worlds for different data types
**Cons**: Increased complexity, operational overhead
**Rejected**: PostgreSQL alone provides sufficient capabilities

## Implementation Notes

### Connection Management
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost/autofund_ai"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(bind=engine)
```

### Migration Strategy
```python
# Alembic for database migrations
from alembic import command
from alembic.config import Config

def create_migration(message: str):
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

### Backup Strategy
```bash
#!/bin/bash
# backup_database.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/backups/autofund_ai_${TIMESTAMP}.sql"

pg_dump -h localhost -U autofund -d autofund_ai > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep last 30 days of backups
find /backups -name "autofund_ai_*.sql.gz" -mtime +30 -delete
```

### Performance Monitoring
```sql
-- Monitoring query performance
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Monitoring table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Data Retention Policy
```python
def cleanup_old_data():
    """Clean up old data according to retention policy"""
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # Delete old failed jobs
    session.query(IESJob).filter(
        IESJob.status == 'failed',
        IESJob.created_at < thirty_days_ago
    ).delete()

    # Archive old audit logs
    ninety_days_ago = datetime.now() - timedelta(days=90)
    archive_audit_logs(ninety_days_ago)
```

### GDPR Compliance
```sql
-- Right to be forgotten
CREATE OR REPLACE FUNCTION delete_user_data(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    -- Delete user data
    DELETE FROM audit_log WHERE user_id = user_uuid;
    DELETE FROM financial_analyses
    WHERE job_id IN (SELECT id FROM ies_jobs WHERE user_id = user_uuid);
    DELETE FROM ies_jobs WHERE user_id = user_uuid;
    DELETE FROM users WHERE id = user_uuid;
END;
$$ LANGUAGE plpgsql;
```

## Testing Strategy

### Unit Tests
```python
def test_user_creation():
    user = User(email="test@example.com", subscription_tier="free")
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.created_at is not None
```

### Integration Tests
```python
def test_ies_processing_workflow():
    user = create_test_user()
    job = IESJob(user_id=user.id, company_nif="123456789", status="pending")
    session.add(job)
    session.commit()

    assert job.id is not None
    assert job.status == "pending"
```

### Performance Tests
```python
def test_query_performance():
    start_time = time.time()

    # Test complex query
    results = session.query(IESJob, FinancialAnalysis).join(
        FinancialAnalysis, IESJob.id == FinancialAnalysis.job_id
    ).filter(
        IESJob.status == 'completed',
        FinancialAnalysis.risk_level == 'MÉDIO'
    ).all()

    query_time = time.time() - start_time
    assert query_time < 1.0  # Should complete in under 1 second
```

## Scaling Strategy

### Read Replicas
```python
# Configure read replicas for analytics queries
DATABASE_URL_READ = "postgresql://user:password@replica-host/autofund_ai"

read_engine = create_engine(DATABASE_URL_READ)
read_session = sessionmaker(bind=read_engine)
```

### Partitioning
```sql
-- Partition audit log by date
CREATE TABLE audit_log_y2024m01 PARTITION OF audit_log
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### Connection Pooling
```python
# PgBouncer for connection pooling
DATABASE_URL = "postgresql://user:password@localhost:6432/autofund_ai"
```

---

## Related ADRs

- [ADR-001](./001-technology-stack.md): Choose Technology Stack
- [ADR-004](./004-api-design.md): REST API Design Principles
- [ADR-005](./005-file-storage.md): File Storage Strategy

---

### Implementation Status

✅ **Completed**: Database schema implemented and deployed
✅ **Migrated**: All existing data migrated to new schema
✅ **Indexed**: Performance indexes created and tested
✅ **Backed Up**: Automated backup strategy implemented
✅ **Monitored**: Database performance monitoring in place

### Next Steps

- Monitor performance and optimize queries
- Implement read replicas for analytics
- Consider partitioning for large tables
- Evaluate database connection pooling solutions

---

**Decision Made**: 2024-01-17
**Decision By**: Database Architecture Team
**Review Date**: 2024-02-01