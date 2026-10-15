# 2. Database Provider Switching

Date: 2024-05-14

## Status

Accepted

## Context

The application needs to support both PostgreSQL and SQLite databases to enable easier local development and testing.
PostgreSQL is used in production, but SQLite can be useful for development, testing, and demonstration purposes due to its simplicity and lack of external dependencies.

## Decision

We've implemented a database provider switching mechanism that allows developers to easily switch between PostgreSQL and SQLite through:

1. A new environment variable (`DATABASE_PROVIDER`) that specifies the database type to use
2. A script (`switch-db`) that updates the Prisma schema file to use the desired database provider
3. SQLite support through the addition of the `sqlite3` package

## Implementation

### How to switch between database providers

#### Option 1: Using the script

```bash
# Switch to PostgreSQL
npm run switch-db -- postgresql

# Switch to SQLite
npm run switch-db -- sqlite
```

The script updates the Prisma schema file (`prisma/schema.prisma`) to use the specified database provider.

#### Option 2: Manual configuration

1. Set the `DATABASE_PROVIDER` environment variable to either `postgresql` or `sqlite`
2. Update the `datasource` block in the Prisma schema file manually to use the desired provider
3. Set `DATABASE_URL` appropriately:
   - For PostgreSQL: `postgresql://username:password@host:port/database?schema=public`
   - For SQLite: `file:./dev.db` or another SQLite database file path

### Environment Variables

- `DATABASE_PROVIDER`: The database provider to use (`postgresql` or `sqlite`). Defaults to `postgresql`.
- `DATABASE_URL`: The connection string for the database. Format depends on the provider.

## Consequences

### Positive

- Developers can easily switch between PostgreSQL and SQLite for local development
- Simplified setup for new developers who don't want to install PostgreSQL
- Easier testing and demonstration setups without external dependencies

### Negative

- Need to be careful about database-specific features when writing code
- Migrations might require special handling for SQLite vs PostgreSQL
- Potential for subtle bugs due to differences between SQLite and PostgreSQL behavior
