---
date: { 2024-10-13 }
written-by: { Ahmed Sulaimon }
decision-makers: { Ahmed Sulaimon, Ayman Sammo, Nayan Stanley }
---

# Database choice

## Context and Problem Statement

- What type of database should be used for application development

## Considered Options

- [Relational Database (RDBMS)](<#Relational-Database(RDBMS)>)
- [NoSQL Database (Document-Based)](<#NoSQL-Database(Document-Based)>)
- [Key-Value Store (In-Memory Database))](#Key-Value-Store)
- [Graph Database](#Graph-Database)

## Decision Outcome

**Chosen option:** Relational Database (RDBMS) and NoSQL Database (Document-Based)

**Rationale:**

- A relational database is ideal for structured data that requires consistency and transactional integrity. This database can handle core functionalities like user management, inventory management, and transactional operations (borrowing/returning media, payments).

- NoSQL Database offers flexibility and scalability, making it ideal for managing media-related data and rapid data retrieval.

[See below for pros and cons](#pros-cons).

### Consequences

- **Positive:** Strict data consistency (Relational Database).
- **Positive:** Ideal for handling Complex queries (Relational Database)
- **Positive:** Flexibility: Supports storing a variety of media types (books, movies, journals) (No SQL Database).
- **Positive:** Performance: High read/write speeds, especially useful for handling media search queries across branches (No SQL Database).

- **Negative:** opposite case of the positives of the selected Databases

### Confirmation

<!-- Is this valid option for the project & why -->

<a name="pros-cons"></a>

Pros and Cons of the Database Options
<a name="postgresql"></a>

### PostgreSQL (Relational Database)

**Pros:**

- Supports advanced SQL features like complex queries, triggers, and procedures.

- ACID-compliant ensuring strong transactional consistency.

- Extensible with support for JSON, GIS, and custom data types.

- Highly scalable and suitable for large-scale applications.

- Strong community support and actively developed.

**Cons:**

- Can be slower compared to NoSQL databases for large datasets or heavy read/write operations.

- More complex to manage and optimize for large-scale deployments.
- Requires tuning for high-performance scenarios, especially with large datasets.

<a name="mysql"></a>

<a name="mongodb"></a>

### MongoDB (NoSQL Document Database)

**Pros:**

- Schema-less, allowing flexibility to store various types of media data.

- Horizontal scaling makes it suitable for handling large datasets.

- Fast read and write operations, especially for high-traffic applications.

- Excellent for managing unstructured or semi-structured data.

**Cons:**

- Eventual consistency by default can lead to stale data in some read operations.

- No support for ACID transactions (prior to version 4.0, and even then, limited).

- Less efficient for complex multi-table joins or heavily relational data.

<a name="redis"></a>

### Redis (In-Memory Key-Value Store)

**Pros:**

- Extremely fast read/write operations due to in-memory data storage.

- Supports various data structures, like strings, hashes, lists, and sets.

- Ideal for caching and session management, which improves system performance.

- Can persist data to disk for durability.

**Cons:**

- Limited to key-value pairs and data structures, not ideal for complex queries.

- Memory-intensive, which can lead to higher infrastructure costs as datasets grow.

- Not suited for storing large volumes of data persistently.

<a name="neo4j"></a>

### Neo4j (Graph Database)

**Pros:**

- Optimized for relationship-based queries (e.g., recommendations, social graphs).

- Efficient for navigating and querying complex relationships between entities.

- Cypher query language is intuitive and well-suited for graph queries.

- Excellent for building recommendation engines and handling complex user-media relationships.

**Cons:**

- Not designed for handling high-throughput transactional workloads.

- Limited scalability compared to document or relational databases for other types of data.

- More expensive to implement and maintain, especially for smaller datasets.

## More Information

<!-- How did the team come up with the decision -->
