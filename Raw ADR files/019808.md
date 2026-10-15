# ADR-009: Local Database Development Strategy

## Status
ACCEPTED

## Context
Developers often struggle with setting up local database environments. Using a shared cloud development database introduces risks of data collision and connectivity dependencies. Setting up a full local PostgreSQL instance can be heavy for simple prototypes. We use Prisma as our ORM, which supports multiple providers.

## Decision
We adopt a standardized approach for local database development:

1.  **Default to SQLite for Simplicity:**
    For simple applications, prototypes, or services with standard relational data, developers SHOULD use **SQLite** locally. It requires no infrastructure and is fully supported by Prisma.

2.  **Dockerized PostgreSQL for Parity:**
    If the application uses PostgreSQL-specific features (e.g., Vector embeddings with `pgvector`, extensive JSONB queries, specific extensions), developers **MUST** use a local Dockerized PostgreSQL instance.
    - A `docker-compose.yml` MUST be provided in the repository root.

3.  **Prisma Migration Workflow:**
    - Schema changes must be applied via `npx prisma migrate dev`.
    - Generated migration SQL files must be committed to Git.
    - Manual SQL execution is prohibited for schema changes.

4.  **Configuration:**
    - The application must use the `DATABASE_URL` environment variable.
    - The `schema.prisma` file should default to the production provider (e.g., `postgresql`), but developers may override this locally if using SQLite (note: switching providers in Prisma usually requires changing the provider string in schema, making the Docker-Postgres route preferred for consistency).

## Consequences
- **Positive:** Faster onboarding (npm install -> ready). reproducible environments via Docker.
- **Negative:** SQLite implies slight feature mismatch with production PostgreSQL.
- **Mitigation:** CI/CD pipeline runs tests against a service container (Postgres) to ensure production compatibility.

## Compliance
- All repositories must include a valid `prisma/schema.prisma`.
- If using Docker, a `docker-compose.yml` is mandatory.
