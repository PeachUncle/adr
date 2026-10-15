### **Status:** Selected

### **Date:** 23.05.2025

### **Author:** Pohorilets Vladyslav

## **Context**:

We need an Object-Relational Mapping (ORM) library that:

- connects Node.js services to PostgreSQL with minimum boilerplate;
- keeps domain models clear and readable;
- supports migrations, seeding, and transactions out of the box;
- lets us write both simple CRUD and complex queries when needed;
- is mature, well-documented, and actively maintained;
- plays nicely with TypeScript in case we migrate later.

## Reviewed options:

1. Sequelize
   Pros:

    - Battle-tested, exists since 2011
    - Works with PostgreSQL, MySQL, MariaDB, SQLite, MSSQL
    - Promise-based API fits modern async/await code
    - Built-in migrations, seeders, and CLI
    - Huge amount of examples, tutorials, and StackOverflow answers

    Cons:

    - Some advanced PostgreSQL features exposed via raw queries only

2. TypeORM
   Pros:

    - First-class TypeScript support, decorators for entities
    - Active community, flexible relations handling

    Cons:

    - Reports of breaking changes between minor versions
    - Reflection-based metadata complicates debugging
    - Slower in some benchmarks compared to others

3. Prisma
   Pros:

    - Excellent developer experience and autocompletion
    - Generates typed client from declarative schema

    Cons:

    - Requires separate query engine binary (heavier deploys)
    - Limited support for truly custom SQL
    - Younger project, still polishing edge cases

4. Knex.js (query builder)
   Pros:

    - Lightweight, minimal abstraction over SQL
    - Full control over generated queries

    Cons:

    - Not a full ORM no models, associations, or caching
    - Developer must write more boilerplate for relations and validation

## Decision taken:

Choose Sequelize as the ORM layer for database access.

## Arguments

- Proven stability and large ecosystem lower long-term risk
- Works out-of-the-box with PostgreSQL and other SQL engines if we ever switch
- CLI provides migrations and seed scripts matching our workflow
- Promise-based API is straightforward for the current JavaScript codebase
- Community resources save time when troubleshooting or onboarding new devs
- Allows raw SQL for edge cases so we are not locked into the abstraction

## Consequences:

Positive

- Faster development thanks to high-level model definitions
- Unified style for data access across all modules
- Easy to extend with hooks, scopes, and plugins when the project grows

Negative

- Type definitions are "good enough" but not perfect may require manual tweaks
- Some PostgreSQL-specific features (e.g., partial indexes) need raw queries or custom migrations 