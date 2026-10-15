# 4. Use Flyway for our migrations

Date: 2025-02-05

## Status

Accepted

## Context
Managing database schema changes effectively is critical for ensuring consistency across different environments, especially as the application evolves. Schema modifications must be version-controlled, repeatable, and easily deployable across development, staging, and production environments. Without a structured migration approach, schema drift can occur, leading to inconsistencies and potential application failures. Given that the application uses PostgreSQL as its primary DBMS, a database migration tool is required to facilitate schema changes while maintaining database integrity and historical traceability.

## Decision
Flyway has been chosen as the database migration tool due to its simplicity, reliability, and seamless integration with both PostgreSQL and .NET applications. It follows a structured migration approach using versioned SQL scripts, ensuring that schema changes are applied in a predictable and controlled manner. By maintaining migration history within the database, Flyway prevents duplicate executions and ensures that all environments remain in sync. It also supports rollback strategies and automated execution during deployments. Flyway aligns well with the application’s infrastructure, allowing schema updates to be deployed alongside application updates with minimal manual intervention.

## Consequences
Using Flyway brings several benefits, including improved version control for database schema changes and reduced risk of schema drift across different environments. It simplifies collaboration among developers by allowing migrations to be written as SQL scripts that can be committed to version control, ensuring transparency and traceability.  However, managing rollbacks can be complex, particularly when dealing with destructive schema changes such as table deletions or modifications to existing constraints. Developers must carefully plan migrations to avoid data loss or inconsistencies. There is also an added responsibility of ensuring that all migration scripts are thoroughly tested before deployment, as Flyway does not inherently validate the impact of schema changes beyond execution order.
