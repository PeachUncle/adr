# 6. persistency data layer selection

Date: 2024-05-08

## Status

Accepted

## Context

We need to choose a persistency layer for managing user sessions in our FastAPI application.

# ADR: Selecting Persistency Component and Comparing Database with ORM, Redis, and In-Memory Dictionary

## Context
In the context of storing data that needs to be persisted, accessed very quickly, and stored as key-value with indexes, we need to select the appropriate persistency component. The options considered are using a Database with ORM, Redis, and an in-memory dictionary.

## Decision
After evaluating the options, the decision is to use Redis as the persistency component for storing the data.

## Pros and Cons

### Database with ORM
#### Pros:
- **Data Integrity**: ORM frameworks ensure data integrity and provide a structured way to interact with the database.
- **Query Flexibility**: Supports complex queries and relationships between entities.
- **Transaction Support**: Provides transactional support for maintaining data consistency.

#### Cons:
- **Performance Overhead**: ORM layers can introduce performance overhead compared to direct database access.
- **Complexity**: ORM configurations and mappings can add complexity to the application.

### Redis
#### Pros:
- **In-Memory Storage**: Redis stores data in memory, enabling fast data access and retrieval.
- **Key-Value Store**: Supports key-value storage with indexes for efficient data retrieval.
- **Persistence Options**: Offers persistence mechanisms like RDB and AOF for data durability.
- **Scalability**: Redis is highly scalable and can handle large datasets efficiently.
- **Data Structures**: Supports various data structures like strings, lists, sets, and sorted sets for different use cases.
- **Support for sync multiple instances**: Scheduler jobs and circuit breaker can use Redis to sync across multiple instances.

#### Cons:
- **Memory Usage**: Storing data in memory can lead to higher memory usage compared to disk-based storage.
- **Limited Querying**: Limited querying capabilities compared to relational databases. More manual handling of data relationships.
- **Manual Indexing**: Requires manual indexing and management of data relationships.

### In-Memory Dictionary
#### Pros:
- **Speed**: Provides the fastest data access as data is stored in memory.
- **Simplicity**: Simple key-value storage with indexes for quick data retrieval.
- **Low Latency**: Offers low latency for data access and manipulation.

#### Cons:
- **Data Durability**: Data is volatile and not persisted, making it susceptible to data loss.
- **Limited Storage**: Limited by available memory, which may restrict the amount of data that can be stored.
- **Scalability**: Limited scalability compared to Redis or databases for large datasets.

## Selected Decision
The decision to use Redis as the persistency component is made based on its in-memory storage,
key-value store capabilities, and persistence options. Redis provides fast data access,
supports key-value storage with indexes, and offers mechanisms for data durability, m
aking it a suitable choice for storing and accessing data that needs to be persisted and accessed very quickly.
