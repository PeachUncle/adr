# ADR-7 Use PostgreSQL for Application Data Persistence

## Context

The application stores structured data such as user accounts, tunes,
and rehearsal entries. This data must be persisted in a self-hostable
database that can run in both local development and production
environments, and meet requirements for EU data residency,
reliability, and compatibility with the hosting setup.

## Decision

Adopt **PostgreSQL** as the primary database for application data.

PostgreSQL can be run on the same EU-based VM as the application, or
use an EU-based managed PostgreSQL service if operational convenience
outweighs self-hosting.

## Expected Consequences

Using PostgreSQL from the start allows the application to take
advantage of its rich data type support, enabling more expressive
schemas and reducing the need for application-level
workarounds. PostgreSQL’s mature ecosystem, strong tooling, and wide
hosting support make it a reliable foundation for the persistence
layer.

PostgreSQL does not depend on a writable local filesystem in the same
way file-based databases do. This flexibility helps keep hosting
options open, e.g. in cases where the application would be run in
"cattle" containers without a traditional local filesystem.

On the downside, PostgreSQL introduces some operational complexity.
Running it locally for development requires either a local
installation or a containerized setup, and in production it will
require service management, backups. It has a higher baseline resource
usage than lightweight embedded databases. These trade-offs are
considered acceptable given the benefits.

## Candidate Comparison

1. **PostgreSQL (chosen)**
   - **Pros**:
     - Rich data type support (`timestamptz`, `JSONB`, arrays, full-text search)
     - Possibility of running without reliance on a local filesystem
     - Mature ecosystem and tooling
     - Better concurrency handling
   - **Cons**:
     - Operational complexity (service management, backups)
     - Higher baseline resource usage
     - Requires local install or container for development

2. **SQLite**
   - **Pros**:
     - Extremely simple setup (single file)
     - Minimal resource usage
     - Easy to run locally without extra services
     - In-memory database very convenient for testing
   - **Cons**:
     - Requires reliable local filesystem, which may not be available
       in all hosting setups
     - Limited data type support compared to PostgreSQL
     - Weaker concurrency handling
     - Migration to a server-based database later is non-trivial

3. **Other self-hostable databases** (e.g., MariaDB, MySQL)
   - **Pros**:
     - Some options have simpler setup or lower resource usage than PostgreSQL
     - Broad hosting support
   - **Cons**:
     - May lack advanced data types or features
     - Different SQL dialects may require rewriting queries
