# ADR 006 - Way of handling connections to the database

**Date**: 15-04-2025

## Status

Accepted

## Context

For my first Proof of Concept (PoC), I used a single database connection to interact with the MySQL database. However, after reviewing the code and considering scalability and long-term maintainability, I am exploring alternative strategies for handling database connections. Specifically, I am evaluating approaches that provide better management of database connections, such as connection pooling or using a singleton pattern to handle database connections more efficiently.

## Decision

**Use connection pooling** (as provided by `mysql.connector` or another pooling library) for managing database connections in the production environment. Pooling allows for efficient reuse of connections, which is critical for performance when the application scales.

## Alternatives Considered

- **Singleton (one connection instance for all operations)**:
A singleton pattern ensures that only one database connection is used throughout the entire application, which simplifies connection management in environments with low database traffic.
  - **Pros**:
   - Simple to implement.  
   - Works well in low-traffic, single-user scenarios.
  - **Cons**:
   - Not scalable for multi-user or high-load environments.
   - Tightly couples the database connection to the rest of the application, making it less flexible and harder to maintain in the long run.

## Consequences

- **Using Connection Pooling**:
  - **Performance**: Pooling improves performance by reusing connections rather than establishing new ones for each query, which will be particularly useful as the application scales.
  - **Maintainability**: The connection pool abstraction encapsulates the connection management logic, allowing future updates or replacements of the database without affecting the business logic.
  - **Scalability**: Pooling makes the application more scalable, as it can handle a higher volume of concurrent database operations without needing to establish new connections for every query.

