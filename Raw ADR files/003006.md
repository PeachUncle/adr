# ADR-0001: Use FastAPI + PostgreSQL for API Gateway

## Status
**Accepted** - 2024-01-XX

## Context
The OpenPolicy platform needs a robust, scalable API gateway to serve parliamentary and civic data from multiple jurisdictions. The system must handle:

- High concurrency from web, mobile, and admin clients
- Complex data relationships between bills, members, votes, and sessions
- Full-text search capabilities for legislative content
- Real-time data updates from ETL pipelines
- Comprehensive API documentation and validation

## Decision
We will use **FastAPI** as the web framework and **PostgreSQL 15+** as the primary database for the API Gateway service.

### FastAPI
- **Modern Python framework** with automatic OpenAPI 3.1 documentation
- **Type safety** with Pydantic models and Python type hints
- **High performance** comparable to Node.js and Go frameworks
- **Async support** for handling concurrent requests efficiently
- **Automatic validation** of request/response data
- **Built-in testing support** with TestClient

### PostgreSQL 15+
- **Mature relational database** with excellent JSON support
- **Full-text search** capabilities via tsvector/tsquery
- **Advanced indexing** including GIN indexes for search
- **ACID compliance** for data integrity
- **Rich ecosystem** of tools and extensions
- **Horizontal scaling** options when needed

## Consequences

### Positive
- **Developer Experience**: FastAPI provides excellent tooling and documentation
- **Performance**: Both FastAPI and PostgreSQL are highly performant
- **Ecosystem**: Mature libraries and community support
- **Type Safety**: Reduces runtime errors and improves code quality
- **Search**: PostgreSQL FTS provides good search performance initially
- **Flexibility**: Easy to extend and modify as requirements evolve

### Negative
- **Python Ecosystem**: Requires Python dependency management and virtual environments
- **Learning Curve**: Team needs to be familiar with FastAPI patterns
- **Scaling**: PostgreSQL may require additional work for very high concurrency
- **Search Limitations**: PostgreSQL FTS has limitations compared to dedicated search engines

### Neutral
- **Deployment**: Both technologies work well in containers
- **Monitoring**: Standard observability tools work with both
- **Testing**: Good testing frameworks available for both

## Alternatives Considered

### Web Framework Alternatives
1. **Django REST Framework**
   - Pros: Mature, extensive ecosystem, admin interface
   - Cons: Heavier, less performant, more opinionated
   - Decision: Too heavy for our API-focused needs

2. **Flask + Marshmallow**
   - Pros: Lightweight, flexible, familiar
   - Cons: Manual setup, no automatic validation, less performant
   - Decision: Requires too much boilerplate code

3. **Node.js/Express**
   - Pros: JavaScript ecosystem, high performance
   - Cons: Different language, less type safety
   - Decision: Team expertise and type safety requirements

### Database Alternatives
1. **MongoDB**
   - Pros: Schema flexibility, JSON-native
   - Cons: Less mature for complex relationships, ACID limitations
   - Decision: Relational data model is more appropriate

2. **Elasticsearch**
   - Pros: Excellent search capabilities
   - Cons: Not a primary database, additional complexity
   - Decision: Can be added later for advanced search needs

3. **SQLite**
   - Pros: Simple, embedded
   - Cons: Limited concurrency, no network access
   - Decision: Not suitable for production API service

## Implementation Notes

### FastAPI Setup
- Use Pydantic for request/response models
- Implement dependency injection for database sessions
- Add CORS middleware for web client access
- Use background tasks for long-running operations

### PostgreSQL Setup
- Use SQLAlchemy as ORM with Alembic for migrations
- Implement connection pooling for high concurrency
- Add full-text search indexes on bill content
- Use JSONB for flexible metadata storage

### Migration Path
- Start with PostgreSQL FTS for search
- Document upgrade path to OpenSearch/Elasticsearch
- Plan for read replicas when scaling is needed

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Related ADRs
- None yet - this is the foundational ADR
