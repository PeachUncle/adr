### **Status:** Selected

### **Date:** 22.05.2025

### **Author:** Pohorilets Vladyslav

## **Context**:

We need to choose a primary database engine that:

- scales together with the product growth;
- is well-known, well-documented, and easy to host in the cloud;
- has good tooling for backups, monitoring, and migrations;
- works nicely with the chosen tech-stack (Node.js + planned ORM).

## Reviewed options:

1. PostgreSQL
   Pros:

    - Fully open-source, permissive licence
    - Strong ACID compliance and rich SQL support
    - Advanced features (JSONB, full-text search, extensions, partitioning)
    - Active community, long-term stability
    - Supported by every major cloud provider

    Cons:

    - Slightly steeper learning curve for newcomers
    - Heavier memory footprint than "lighter" engines

2. MySQL / MariaDB
   Pros:

    - Very popular and easy to start
    - Low memory usage on small setups

    Cons:

    - Weaker strictness (silent data truncation, looser types)
    - Fewer modern SQL features (CTEs, window functions older versions)
    - Dual licences for MySQL can be confusing

3. MongoDB
   Pros:

    - Flexible schema, quick prototyping
    - Good for unstructured documents

    Cons:

    - Not a relational database joins are limited or expensive
    - Historically weaker transaction support
    - Requires different query language and mindset

4. SQLite
   Pros:

    - Zero-config, file-based, tiny footprint

    Cons:

    - Single-file lock limits concurrent writes
    - Not intended for server-side workloads with many users

## Decision taken:

Choose PostgreSQL as the main relational database for the project.

## Arguments

- PostgreSQL gives us both classic SQL and modern NoSQL-like JSONB in one engine
- Rich extensions (PostGIS) open doors for future features without switching DBs
- Fully open-source, no licence headaches, big and friendly community
- Easy to host: all major clouds offer managed Postgres with automatic backups and scaling
- Mature tooling (CLI, GUI, migration libraries) speeds up development and CI/CD

## Consequences:

Positive

- Clear, proven path for modelling complex business data
- Stable performance and predictable behaviour under load
- Seamless integration with the chosen ORM and analytics tools
- Long-term support and large talent pool for hiring

Negative

- Need to allocate a bit more RAM/CPU compared to lighter engines
- Team must follow best practices to avoid overusing advanced features that could complicate future migrations
