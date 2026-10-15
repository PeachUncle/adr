# ADR-004: Use PostgreSQL as Primary Database

## Status
Accepted

## Context
The SMS messaging platform needs a reliable database to store message data with the following requirements:

- ACID transactions for data consistency
- Good performance for read/write operations
- JSON support for flexible message metadata
- Full-text search capabilities for message content
- Horizontal scaling options
- Strong ecosystem and tooling support
- Cost-effective for both development and production

The system primarily stores SMS messages with metadata, requiring both relational structure and some document-like flexibility.

## Decision
We will use PostgreSQL as the primary database for the SMS Service.

**Version**: PostgreSQL 16 (latest stable)
**Deployment**: Containerized using official PostgreSQL Alpine image
**Migration Tool**: Flyway for database schema management
**Connection Pooling**: Quarkus Agroal connection pool

## Consequences

### Positive
- **ACID Compliance**: Strong consistency guarantees for message data
- **JSON Support**: Native JSON and JSONB types for flexible metadata storage
- **Full-Text Search**: Built-in text search capabilities for message content
- **Mature Ecosystem**: Extensive tooling, monitoring, and operational knowledge
- **Performance**: Excellent performance for both OLTP and analytical workloads
- **Standards Compliance**: SQL standard compliance with PostgreSQL extensions
- **Replication**: Built-in streaming replication for high availability
- **Extensions**: Rich extension ecosystem (PostGIS, pgcrypto, etc.)
- **Open Source**: No licensing costs, strong community support

### Negative
- **Operational Complexity**: Requires database administration knowledge
- **Memory Usage**: Higher memory requirements compared to embedded databases
- **Scaling Limitations**: Vertical scaling has limits, horizontal scaling requires effort
- **Backup Complexity**: Need proper backup and recovery procedures

### Neutral
- **Resource Requirements**: Need dedicated database resources
- **Configuration Tuning**: Requires performance tuning for optimal results
- **Monitoring**: Need database-specific monitoring and alerting

## Implementation Details

### Database Schema

**Messages Table**:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender VARCHAR(20) NOT NULL,
    recipient VARCHAR(20) NOT NULL, 
    text TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    failure_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_recipient ON messages(recipient);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Full-text search index
CREATE INDEX idx_messages_text_search ON messages USING gin(to_tsvector('english', text));
```

### Configuration

**Docker Compose Setup**:
```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: smsdb
    POSTGRES_USER: smsuser
    POSTGRES_PASSWORD: smspass
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U smsuser -d smsdb"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Quarkus Configuration**:
```properties
# Database connection
quarkus.datasource.db-kind=postgresql
quarkus.datasource.jdbc.url=jdbc:postgresql://postgres:5432/smsdb
quarkus.datasource.username=smsuser
quarkus.datasource.password=smspass

# Connection pool
quarkus.datasource.jdbc.min-size=5
quarkus.datasource.jdbc.max-size=20

# Hibernate ORM
quarkus.hibernate-orm.database.generation=none
quarkus.hibernate-orm.log.sql=false

# Flyway migrations
quarkus.flyway.migrate-at-start=true
quarkus.flyway.locations=classpath:db/migration
```

### Data Access Layer

**Entity Definition**:
```java
@Entity
@Table(name = "messages")
public class Message extends PanacheEntityBase {
    
    @Id
    @GeneratedValue
    public UUID id;
    
    @Column(nullable = false, length = 20)
    public String sender;
    
    @Column(nullable = false, length = 20) 
    public String recipient;
    
    @Column(nullable = false, columnDefinition = "TEXT")
    public String text;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    public MessageStatus status = MessageStatus.PENDING;
    
    @Column(name = "failure_reason")
    public String failureReason;
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false)
    public LocalDateTime createdAt;
    
    @UpdateTimestamp  
    @Column(name = "updated_at", nullable = false)
    public LocalDateTime updatedAt;
}
```

**Repository Pattern**:
```java
@ApplicationScoped
public class MessageRepository implements PanacheRepositoryBase<Message, UUID> {
    
    public List<Message> findByStatus(MessageStatus status, Page page) {
        return find("status", status).page(page).list();
    }
    
    public List<Message> findByUser(String phoneNumber, Page page) {
        return find("sender = ?1 or recipient = ?1", phoneNumber)
               .page(page).list();
    }
    
    public long countByStatus(MessageStatus status) {
        return count("status", status);
    }
}
```

### Migration Management

**Flyway Migrations** (`src/main/resources/db/migration/`):

**V1__Initial_schema.sql**:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender VARCHAR(20) NOT NULL,
    recipient VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    failure_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_recipient ON messages(recipient);
```

## Performance Optimization

### Indexing Strategy
- **Primary Key**: UUID with proper index
- **Status Queries**: Index on status column for filtering
- **User Queries**: Indexes on sender/recipient for user-specific queries
- **Time-based Queries**: Index on created_at for temporal filtering
- **Full-text Search**: GIN index for text search capabilities

### Connection Pooling
```properties
# Optimized connection pool settings
quarkus.datasource.jdbc.min-size=5
quarkus.datasource.jdbc.max-size=20
quarkus.datasource.jdbc.acquisition-timeout=PT30S
quarkus.datasource.jdbc.validation-query-sql=SELECT 1
```

### Query Optimization
- Use prepared statements (automatic with Hibernate)
- Implement pagination for large result sets
- Use projections for read-only queries
- Batch operations for bulk inserts/updates

## Alternatives Considered

### MySQL
- **Pros**: Very popular, good performance, extensive documentation
- **Cons**: Less advanced JSON support, weaker full-text search
- **Decision**: Good alternative but PostgreSQL offers better feature set

### MongoDB
- **Pros**: Excellent JSON support, horizontal scaling, flexible schema
- **Cons**: No ACID transactions across documents, less SQL expertise in team
- **Decision**: Considered but prefer SQL and ACID guarantees

### H2 Database
- **Pros**: Embedded, zero configuration, good for testing
- **Cons**: Not suitable for production, limited features
- **Decision**: Used only for testing environments

### Amazon RDS/Aurora
- **Pros**: Fully managed, automatic backups, high availability
- **Cons**: Vendor lock-in, higher costs, less control
- **Decision**: Good for cloud deployment but want database-agnostic solution

### CockroachDB
- **Pros**: Distributed SQL, PostgreSQL compatibility, auto-scaling
- **Cons**: Higher operational complexity, newer technology
- **Decision**: Interesting for future scaling but overkill for current needs

## Backup and Recovery

### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
pg_dump -h postgres -U smsuser smsdb | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Point-in-time recovery setup
# Enable WAL archiving for continuous backup
```

### High Availability Options
- **Streaming Replication**: Master-slave setup for read scaling
- **Logical Replication**: For cross-region replication
- **Connection Pooling**: PgBouncer for connection management
- **Load Balancing**: HAProxy for read/write splitting

## Monitoring and Observability

### Key Metrics
- **Connection Pool**: Active connections, wait time, utilization
- **Query Performance**: Slow query log, execution plans
- **Database Size**: Table sizes, index usage, disk space
- **Replication Lag**: For high availability setups

### Monitoring Tools
- **pg_stat_statements**: Query performance analysis
- **Prometheus Exporter**: postgres_exporter for metrics
- **Grafana Dashboards**: PostgreSQL monitoring dashboards
- **Application Metrics**: Connection pool metrics from Quarkus

## Security Considerations

### Authentication and Authorization
```properties
# SSL configuration
quarkus.datasource.jdbc.url=jdbc:postgresql://postgres:5432/smsdb?sslmode=require

# User access control
# Create read-only user for reporting
# CREATE USER readonly_user WITH PASSWORD 'readonly_password';
# GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

### Data Protection
- **Encryption at Rest**: Configure PostgreSQL with encrypted storage
- **Encryption in Transit**: Use SSL/TLS for connections
- **Access Control**: Role-based access control (RBAC)
- **Audit Logging**: Enable PostgreSQL audit logging

## Future Considerations

### Scaling Options
- **Read Replicas**: For read-heavy workloads
- **Partitioning**: Table partitioning for large datasets
- **Sharding**: Application-level sharding if needed
- **Migration Path**: PostgreSQL → distributed databases if needed

### Advanced Features
- **JSON Queries**: Leverage JSONB for metadata storage
- **Full-text Search**: PostgreSQL vs Elasticsearch for search
- **Time Series**: Consider TimescaleDB extension for analytics
- **Geographic Data**: PostGIS for location-based features

## Related Decisions
- [ADR-001: Use Microservices Architecture](001-microservices-architecture.md)
- [ADR-003: Use Quarkus as Java Framework](003-quarkus-framework.md)
- [ADR-005: Use Docker for Containerization](005-docker-containerization.md)
