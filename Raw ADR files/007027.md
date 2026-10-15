# ADR 012: Choosing SQLAlchemy as the ORM

- **Date created**: 05/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

For the `box-tracker` backend, we needed a way to interact with the database efficiently while maintaining flexibility and maintainability. A key requirement was to use an Object-Relational Mapper (ORM) to handle database interactions in a structured and type-safe manner.

Since we had already chosen `PostgreSQL` as our database, we evaluated ORM options that provided strong support for relational databases while integrating well with `FastAPI`.

## Alternatives Considered

### SQLAlchemy (Chosen)

- Widely adopted and considered the standard ORM for Python.
- Provides both a declarative ORM API and a low-level Core API for raw SQL access.
- Fully supports `PostgreSQL` and integrates well with `FastAPI`.
- Works seamlessly with `Alembic` for database migrations.

### Tortoise-ORM

- An async-first ORM designed for use with `FastAPI`.
- Lighter-weight than `SQLAlchemy` and more modern.
- Lacks full-featured ecosystem and tooling available with `SQLAlchemy`.
- Limited support for complex queries compared to `SQLAlchemy`.

### Django ORM

- Well-suited for `Django` applications but not ideal for standalone `FastAPI` projects.
- Tightly coupled with the `Django` framework, making it harder to use in a modular API.
- Lacks the flexibility and advanced query capabilities of `SQLAlchemy`.

## Decision

We decided to use `SQLAlchemy` as the ORM for `box-tracker`.

This decision was based on:

- The maturity and ecosystem of `SQLAlchemy`, ensuring long-term maintainability.
- Its flexibility, allowing both high-level ORM features and raw SQL execution.
- Its tight integration with `PostgreSQL` and `FastAPI`.
- First-class support for database migrations using `Alembic`, reducing schema management complexity.

## Consequences

- Using `SQLAlchemy` allows for a structured, type-safe approach to database interactions.
- We have access to both an ORM and a raw SQL API, giving us full control over queries.
- `Alembic` is required for handling database migrations, adding an extra dependency.
- Some additional boilerplate is needed for async support, but this is manageable.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
