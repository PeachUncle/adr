# ADR 010: Choosing PostgreSQL for the Database

- **Date created**: 05/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![superceded] by [ADR 014](./adr-014-replace-fast-api-with-nestjs.md)

## Context

For `box-tracker`, we required a database that would provide strong consistency, scalability, and reliability while also integrating well with our chosen backend framework, [FastAPI](./adr-009-fast-api.md).

Since box-tracker is expected to store structured, relational data (e.g., user accounts, inventory records, and audit logs), we needed a relational database that supports transactions and complex queries.

After evaluating different database options, we decided on `PostgreSQL` due to its strong support for relational features, scalability, and integration with Python’s SQLAlchemy ORM.

## Alternatives Considered

### Relational Databases

#### PostgreSQL (Chosen)

- Open-source and widely adopted in the industry.
- ACID-compliant with strong consistency guarantees.
- Supports JSONB, allowing semi-structured data storage when necessary.
- Native support for SQLAlchemy, making development seamless in Python/FastAPI.
- Strong ecosystem with tools like `pgAdmin`, `pgBouncer`, and `PostGIS` for extensions.

#### MySQL / MariaDB

- Popular and fast for many workloads.
- Lacks some of PostgreSQL’s advanced features (e.g., full-text search, richer JSON support).
- Historically weaker ACID compliance, depending on the storage engine (InnoDB is required for transactions).
- Less strict adherence to SQL standards compared to PostgreSQL.

#### SQLite

- Lightweight and easy to set up.
- Not suited for multi-user applications due to the lack of client-server architecture.
- Limited concurrency makes it unsuitable for production-scale deployments.

### Non-Relational (NoSQL) Databases

None were considered due to a clear requirement for relational data.

## Decision

After evaluating the alternatives, we chose `PostgreSQL` as the primary database.

This decision was based on:

- The need for a strictly relational model with complex joins, transactions, and integrity constraints.
- PostgreSQL's advanced SQL compliance and robust ecosystem.
- Seamless integration with `SQLAlchemy` and `FastAPI`, reducing development friction.

## Consequences

- PostgreSQL provides **scalability, strong consistency, and advanced SQL features**.
- Our application benefits from **strict schema validation and ACID compliance**.
- JSONB allows us to store semi-structured data when necessary.
- Requires more setup and maintenance than SQLite but offers significantly **better long-term scalability**.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
