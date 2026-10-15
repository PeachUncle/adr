# ADR-008: Entity Framework Core

## Status
**Accepted**

## Context
Nucleus needs a robust data access layer that integrates well with our .NET ecosystem and PostgreSQL database. The ORM must support our clean architecture principles, provide good performance, and handle our hybrid relational/JSONB data model effectively.

Forces at play:
- Need for seamless .NET integration
- Requirement for PostgreSQL JSONB support
- Support for clean architecture patterns
- Migration and schema management
- Performance and query optimization
- Team expertise and familiarity

## Decision
We will use Entity Framework Core as our primary ORM for data access in Nucleus.

Key aspects of this decision:
- **Entity Framework Core 8.0+**: Latest LTS version with performance improvements
- **PostgreSQL Provider**: Npgsql.EntityFrameworkCore.PostgreSQL for PostgreSQL support
- **JSONB Support**: Native support for PostgreSQL JSONB columns
- **Code-First Approach**: Entity classes drive database schema
- **Migrations**: EF Core migrations for schema versioning
- **Repository Pattern**: EF Core DbContext with repository abstractions

## Consequences

### Positive
- **.NET Integration**: Native integration with ASP.NET Core and .NET ecosystem
- **Productivity**: Rich tooling and IntelliSense support
- **Type Safety**: Strongly-typed entities and queries
- **Migrations**: Automated schema migration management
- **JSONB Support**: Excellent support for PostgreSQL JSONB operations
- **Performance**: Query optimization and caching capabilities
- **Community**: Large, active community and documentation
- **Tooling**: Excellent Visual Studio and VS Code support

### Negative
- **Learning Curve**: Team must understand EF Core concepts and patterns
- **Performance**: Potential N+1 query issues if not used carefully
- **Complexity**: Additional abstraction layer over raw SQL
- **Memory Usage**: Change tracking and entity state management overhead
- **Query Limitations**: Some complex queries may require raw SQL

### Neutral
- **Licensing**: Open source with MIT license
- **Maturity**: Well-established ORM with proven track record

## Rationale
Entity Framework Core was chosen over alternatives like:
- **Dapper**: More manual work, less productivity
- **NHibernate**: Less active development, smaller community
- **Raw ADO.NET**: Too much boilerplate, no type safety
- **Other ORMs**: Less integration with .NET ecosystem

The decision leverages EF Core's excellent .NET integration and PostgreSQL support while providing the productivity benefits of a modern ORM. The code-first approach aligns well with our clean architecture principles.

## Related Decisions
- [ADR-003: PostgreSQL with JSONB](ADR-003-postgresql-jsonb.md)
- [ADR-001: Clean Architecture Pattern](ADR-001-clean-architecture.md)

## References
- [Entity Framework Core Documentation](https://docs.microsoft.com/en-us/ef/core/)
- [Npgsql Entity Framework Provider](https://www.npgsql.org/efcore/)
- [EF Core Performance Best Practices](https://docs.microsoft.com/en-us/ef/core/performance/) 