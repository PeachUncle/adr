# ADR 004: Polyglot Persistence Strategy (PostgreSQL + Redis + ElasticSearch)

## Status
Accepted

## Context
The Ticketeer application faces three distinct data challenges that a single database engine cannot solve efficiently:
1.  **Transactional Integrity**: Financial transactions (ticket purchases) require ACID compliance and strong consistency.
2.  **Complex Search**: Users need to search movies by title, genre, or description with fuzzy matching and relevance scoring. Relational databases (`LIKE %...%`) perform poorly here.
3.  **High Concurrency State**: Managing seat availability during a blockbuster premiere involves thousands of concurrent read/write operations per second. Relational locks can cause bottlenecks.

## Decision
We decided to adopt a **Polyglot Persistence** strategy, using specialized data stores for specific use cases:

### 1. PostgreSQL (The Source of Truth)
*   **Role**: Primary Database.
*   **Responsibility**: Stores the authoritative state of all entities (Movies, Cinemas, Sessions, Sold Tickets).
*   **Justification**: Robust relational engine, ACID compliance, and excellent support for structured data.

### 2. ElasticSearch (The Search Engine)
*   **Role**: Read-Optimized Search Index.
*   **Responsibility**: Stores a denormalized copy of the Movie Catalog optimized for full-text search.
*   **Justification**: Provides sub-second search results with features like fuzzy matching, faceting, and relevance scoring.
*   **Synchronization**: Updates will be propagated from PostgreSQL to ElasticSearch (likely via Domain Events/MassTransit) to ensure eventual consistency.

### 3. Redis (The Cache & Real-Time State)
*   **Role**: Distributed Cache & Ephemeral State Store.
*   **Responsibility**:
    *   **Caching**: Storing hot data (e.g., "Movies Now Showing") to reduce load on PostgreSQL/ElasticSearch.
    *   **Concurrency Control**: Managing temporary "seat locks" during the checkout process using atomic operations (e.g., `SETNX`).
*   **Justification**: In-memory speed is required for high-concurrency scenarios where disk I/O would be a bottleneck.

## Consequences

### Positive
*   **Performance**: Each component handles the workload it was designed for (Search, Transaction, or Speed).
*   **Scalability**: We can scale the Search (Elastic) or Cache (Redis) layers independently of the Transactional (Postgres) layer.

### Negative
*   **Infrastructure Complexity**: We must maintain and monitor three different database technologies.
*   **Data Synchronization**: We introduce the challenge of keeping data consistent across stores (e.g., ensuring a movie update in Postgres reflects in ElasticSearch). We accept **Eventual Consistency** for the search index.
