# ADR-00003: Database Architecture and Multitenancy

## Status
**Accepted** - 2024-09-28

## Context
The AGoat Publisher system needs to support multiple customers (tenants) with complete data isolation while maintaining performance and scalability. The system must handle both content management and business-specific functionality (Thorne health products) with proper data segregation.

## Decision
Implement a multitenant database architecture using CockroachDB with:
- UUID-based primary keys for even distribution
- Tenant-aware indexing for efficient queries
- Logical partitioning through tenant context
- Optimized key design to avoid hotspots
- Separate schemas for different business domains
- Comprehensive audit trails and data versioning

## Rationale
1. **Scalability**: CockroachDB provides horizontal scaling capabilities
2. **Data Isolation**: Tenant-aware design ensures complete data separation
3. **Performance**: UUID distribution prevents hotspots in distributed database
4. **Flexibility**: Logical partitioning allows flexible tenant management
5. **Reliability**: CockroachDB provides ACID compliance and fault tolerance
6. **Business Domain Support**: Separate schemas support different business needs

## Consequences

### Positive
- **Scalability**: Horizontal scaling with CockroachDB
- **Data Isolation**: Complete tenant separation
- **Performance**: Optimized for distributed queries
- **Reliability**: ACID compliance and fault tolerance
- **Flexibility**: Easy tenant management and configuration
- **Business Support**: Separate domains (content, Thorne products)

### Negative
- **Complexity**: More complex database design
- **Learning Curve**: Team needs CockroachDB expertise
- **Cost**: CockroachDB licensing costs
- **Migration**: Complex migration from existing systems
- **Monitoring**: More complex monitoring and maintenance

## Implementation Details

### Database Schema Design
```sql
-- Core tenant management
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Site management within tenants
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Content management with tenant isolation
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(id),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    slug VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Thorne business domain
CREATE TABLE thorne_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    sku VARCHAR(100) UNIQUE,
    wholesale_price DECIMAL(10,2),
    retail_price DECIMAL(10,2),
    in_stock BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Key Features
1. **Tenant Isolation**: All queries include tenant context
2. **UUID Distribution**: Even distribution across database nodes
3. **Indexing Strategy**: Tenant-aware indexes for performance
4. **Data Versioning**: Complete audit trails for all changes
5. **Business Domains**: Separate schemas for different business needs

### Performance Optimizations
- Tenant-aware indexing on all major tables
- UUID-based primary keys for even distribution
- Logical partitioning through application logic
- Optimized query patterns for tenant isolation
- Connection pooling with tenant context

### Security Measures
- Row-level security through tenant context
- Comprehensive audit logging
- Data encryption at rest and in transit
- Access control through application layer
- Regular security assessments

## References
- [ADR-00001: Multitenancy Database Design for CockroachDB](./00001-multitenancy-database-design.md)
- [Database Requirements](../../requirements-and-user-stories/final-functional/database-requirements.md)
- [Database Schema Analysis](../../technical-implementation/database/database-schema-analysis.md)
- [CockroachDB Best Practices](https://www.cockroachlabs.com/docs/stable/best-practices.html)
- [CockroachDB Performance Tuning](https://www.cockroachlabs.com/docs/stable/performance-tuning.html)
