# 📋 ADR-002: MongoDB for Primary Database

## Status

Accepted

## Context

The Reportly application requires a database solution for storing various types of data, including reports, comments, user profiles, and more. We needed to select a primary database that would meet our requirements for:

1. Flexibility in data modeling
2. Scalability for growing data volumes
3. Performance for read and write operations
4. Developer experience and productivity
5. Integration with our technology stack

## Decision

We decided to use MongoDB as the primary database for the Reportly application, with Mongoose as the ODM (Object Document Mapper).

## Rationale

MongoDB provides several advantages that align with our project requirements:

1. **Schema Flexibility**: MongoDB's document model allows for flexible schemas that can evolve over time, which is ideal for our report content that varies in structure.
2. **JSON-Like Documents**: The BSON format aligns well with JavaScript objects, making it natural to work with in a Node.js/Next.js environment.
3. **Scalability**: MongoDB's horizontal scaling capabilities through sharding support our growth projections.
4. **Rich Query Language**: MongoDB's query capabilities support our complex filtering and search requirements.
5. **Indexing**: Support for various index types helps optimize query performance.
6. **Mongoose Integration**: The Mongoose ODM provides schema validation, middleware, and TypeScript support.

## Consequences

### Positive

- Flexible schema design accommodates varying report structures
- JSON-like document model simplifies development
- Mongoose provides schema validation and type safety
- Good performance for our read-heavy workload
- Scalability options for future growth

### Negative

- Less rigid schema enforcement compared to relational databases
- Transaction support is more limited than in traditional RDBMS
- Potential for denormalization leading to data duplication
- Learning curve for developers more familiar with SQL databases

## Alternatives Considered

### PostgreSQL

PostgreSQL would provide stronger schema enforcement and better transaction support, but with less flexibility for evolving data structures and more complex JSON handling.

### Firebase Firestore

Firestore would offer real-time capabilities and managed infrastructure, but with higher costs at scale and less control over data modeling and queries.

### DynamoDB

DynamoDB would provide excellent scalability and performance, but with a more restrictive data model and query capabilities, plus a steeper learning curve.

## References

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Mongoose Documentation](https://mongoosejs.com/docs/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoDB Schema Design Best Practices](https://www.mongodb.com/developer/products/mongodb/schema-design-anti-pattern-massive-arrays/)
