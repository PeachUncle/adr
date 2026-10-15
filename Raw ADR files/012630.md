# ADR-003: PostgreSQL with JSONB

## Status
**Accepted**

## Context
Nucleus needs to store workflow execution data, model inputs/outputs, and evaluation results. The data structure must be flexible to accommodate different workflow platforms and AI model outputs while maintaining queryability and performance.

Forces at play:
- Need for flexible schema to handle various workflow platforms
- Requirement for structured querying of evaluation data
- Performance requirements for high-volume logging
- Data consistency and ACID compliance
- Integration with Entity Framework Core
- Future extensibility for new data types

## Decision
We will use PostgreSQL with JSONB for data storage in Nucleus.

Key aspects of this decision:
- **PostgreSQL 14+**: Latest stable version with advanced JSONB features
- **JSONB for flexible data**: Store model inputs/outputs as structured JSON
- **Relational structure**: Core entities (workflow_run, model_run, evaluation) as proper tables
- **Hybrid approach**: Structured columns for common fields, JSONB for variable data
- **Entity Framework Core**: Use EF Core with PostgreSQL provider
- **Migrations**: Use EF Core migrations for schema management

## Consequences

### Positive
- **Flexibility**: JSONB allows storing any structure without schema changes
- **Performance**: JSONB is indexed and queryable, unlike regular JSON
- **Reliability**: PostgreSQL provides ACID compliance and data integrity
- **Queryability**: Can query both structured columns and JSONB content
- **Ecosystem**: Excellent .NET integration with Npgsql
- **Scalability**: PostgreSQL handles high-volume workloads well
- **JSONB Features**: Advanced operators for querying nested data

### Negative
- **Complexity**: JSONB queries are more complex than pure relational
- **Learning Curve**: Team must understand JSONB operators and indexing
- **Storage Overhead**: JSONB has some storage overhead compared to normalized tables
- **Query Performance**: Complex JSONB queries may be slower than relational queries
- **Tooling**: Some database tools have limited JSONB support

### Neutral
- **Licensing**: PostgreSQL is open source
- **Maturity**: Well-established database with proven track record

## Rationale
PostgreSQL with JSONB was chosen over alternatives like:
- **Pure Relational**: Would require complex schema changes for new data types
- **NoSQL (MongoDB)**: Less ACID compliance, different query model
- **SQL Server**: More expensive, less flexible JSON support
- **SQLite**: Limited concurrent access, not suitable for production

The hybrid approach provides the best balance of flexibility and structure. Core entities remain relational for consistency and performance, while variable data (model inputs/outputs) uses JSONB for flexibility.

## Related Decisions
- [ADR-008: Entity Framework Core](ADR-008-entity-framework.md)
- [ADR-001: Clean Architecture Pattern](ADR-001-clean-architecture.md)

## References
- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [Npgsql Entity Framework Provider](https://www.npgsql.org/efcore/)
- [JSONB Performance Best Practices](https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING) 