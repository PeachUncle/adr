---
doc_id: "ADR-007"
tech_stack: ["mongodb", "spring"]
title: "ADR-007: MongoDB as Database"
version: "1.0.0"
last_updated: "2025-12-19"
status: "accepted"
category: "Architecture Decision"
audience: ["Backend Developers", "Architects", "Database Administrators"]
prerequisites: ["ADR-006-Spring-Boot-Framework.md"]
related_docs: ["Specifications/Database-Specification.md", "Architecture/Backend-Refactoring.md"]
maintainer: "Development Team"
---

# <ADR-007-MongoDB as Database>

## Status

**Accepted** - MongoDB is the primary database for the portfolio application.

## Context

The MyTechPortfolio application required a database that could:
- Store flexible, evolving portfolio data structures
- Support document-based data model
- Handle read-heavy workloads (portfolio display)
- Allow schema changes without migrations
- Integrate well with Spring Boot
- Support nested objects and arrays
- Scale horizontally if needed

### Alternatives Considered

1. **PostgreSQL**
   - Pros: ACID compliance, SQL queries, mature ecosystem
   - Cons: Rigid schema, requires migrations, relational model may be overkill

2. **MySQL**
   - Pros: Mature, widely used, SQL support
   - Cons: Schema rigidity, migration overhead, relational model

3. **DynamoDB**
   - Pros: Serverless, auto-scaling, AWS integration
   - Cons: Vendor lock-in, cost, learning curve

4. **MongoDB**
   - Pros: Flexible schema, document model, Spring Data support
   - Cons: No joins, eventual consistency considerations

5. **H2 (In-Memory)**
   - Pros: Fast, no setup
   - Cons: Not suitable for production, data loss on restart

## Decision

We chose **MongoDB** as the primary database.

### Rationale

1. **Flexible Schema**
   - Portfolio data structures evolve over time
   - Easy to add new fields without migrations
   - No need to predefine all fields
   - Supports nested objects and arrays naturally

2. **Document Model**
   - Portfolio entities (Projects, Academics, etc.) map naturally to documents
   - Rich data structures (nested objects, arrays)
   - No need for complex joins
   - Self-contained documents

3. **Spring Data Integration**
   - Excellent Spring Data MongoDB support
   - Repository pattern out of the box
   - Query methods and custom queries
   - Type-safe queries

4. **Read-Heavy Workload**
   - Portfolio is primarily read-heavy
   - MongoDB performs well for reads
   - Indexing support for fast queries
   - Caching can be added if needed

5. **Development Speed**
   - No schema migrations during development
   - Quick iteration on data models
   - Easy to prototype and test

6. **Scalability**
   - Can scale horizontally with sharding
   - Replica sets for high availability
   - Good performance for portfolio use case

## Consequences

### Positive

- **Schema Flexibility**: Easy to evolve data models
- **Development Speed**: Faster iteration without migrations
- **Natural Fit**: Document model fits portfolio entities well
- **Spring Integration**: Seamless Spring Data MongoDB integration
- **Rich Data Structures**: Support for nested objects and arrays
- **Horizontal Scaling**: Can scale with sharding if needed

### Negative

- **No Joins**: Must denormalize or fetch separately
- **No Transactions**: Limited transaction support (though improved in recent versions)
- **Consistency**: Eventual consistency considerations
- **Query Complexity**: Complex queries may require aggregation pipeline
- **Learning Curve**: Team needs MongoDB knowledge

### Neutral

- **ACID Compliance**: Limited compared to relational databases (sufficient for portfolio)
- **SQL**: No SQL queries (use MongoDB query language)

## Implementation Details

### Database Configuration

```properties
# application.properties
spring.data.mongodb.uri=mongodb://localhost:27017/portfolio
spring.data.mongodb.database=portfolio
spring.data.mongodb.auto-index-creation=true
```

### Domain Entity Example

```java
@Document(collection = "projects")
public class Project {
    @Id
    private String id;
    
    @Indexed
    private String title;
    
    private String description;
    
    @Indexed
    private LocalDate startDate;
    
    private List<String> techStack; // Array support
    
    private ProjectMetadata metadata; // Nested object
}
```

### Repository Pattern

```java
@Repository
public interface ProjectRepository extends MongoRepository<Project, String> {
    List<Project> findByTitleContaining(String title);
    List<Project> findByStartDateBetween(LocalDate start, LocalDate end);
}
```

### Collections

- `projects`: Portfolio projects
- `academics`: Academic records
- `journeyMilestones`: Career milestones
- `techStacks`: Technology stacks
- `testimonials`: Testimonials
- `contacts`: Contact form submissions
- `adminUsers`: Admin user accounts

### Indexing Strategy

- Index on frequently queried fields (`title`, `startDate`, `endDate`)
- Index on foreign key-like fields
- Compound indexes for common query patterns
- Auto-index creation enabled

## Best Practices

1. **Schema Design**: Design documents to be self-contained
2. **Indexing**: Index frequently queried fields
3. **Denormalization**: Denormalize when it improves read performance
4. **Validation**: Use application-level validation
5. **Migrations**: Use Flyway for schema changes if needed
6. **Backups**: Regular backups for production data

## Migration Considerations

If migrating to relational database:
- Would require schema design
- Data migration scripts
- Query rewriting
- Transaction support changes

## Related Decisions

- [ADR-006: Spring Boot Framework](./ADR-006-Spring-Boot-Framework.md)
- [ADR-008: Layered Architecture Pattern](./ADR-008-Layered-Architecture.md) (to be created)
- [Database Specification](../Specifications/Database-Specification.md)

## References

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Spring Data MongoDB](https://spring.io/projects/spring-data-mongodb)
- [Database Specification](../Specifications/Database-Specification.md)

---

**Decision Date**: 2025-11-17  
**Decided By**: Development Team  
**Review Date**: TBD (review if data complexity requires relational model)

