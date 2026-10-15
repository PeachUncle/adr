# ADR 0004: Database Specification

## Status

Accepted

## Context

OpsCore requires persistent storage for various data, including but not limited to:

* External repository configurations (URL, provider type, access credentials as defined in ADR 0002).
* User information and authentication details (if user accounts are implemented).
* Potentially caching mechanisms or other application state.
A robust database solution is needed to manage this data reliably and securely.

## Decision

We will use **PostgreSQL** as the primary database for OpsCore.

**Rationale:**

* **Familiarity:** The team has existing experience with PostgreSQL, reducing the learning curve and speeding up development.
* **Reliability and Robustness:** PostgreSQL is well-regarded for its data integrity, ACID compliance, stability, and performance.
* **Features:** It offers a rich feature set, including support for JSONB, full-text search, various indexing options, and extensibility, which could be beneficial for future enhancements.
* **Open Source:** PostgreSQL is a mature, open-source project with a strong community, extensive documentation, and a wide ecosystem of tools and libraries.

While PostgreSQL will be the initial and primary database, the application architecture (particularly the data access layer) should be designed with consideration for potentially supporting other database systems in the far future if a compelling need arises. This might involve using an Object-Relational Mapper (ORM) or abstracting database interactions.

**Schema Definition:**
The initial database schema, starting with the `repository_configurations` table, is defined in **ADR 0005: Database Schema for Repository Configurations**.

## Consequences

* **Pros:**
  * Provides a reliable, transactional, and standard SQL interface for data management.
  * Leverages existing team expertise with PostgreSQL.
  * Benefits from PostgreSQL's mature features, performance, and strong community support.
  * Ensures high data integrity.
* **Cons:**
  * Requires setting up, configuring, and managing a PostgreSQL instance (either self-hosted or via a managed cloud service).
  * Introduces a dependency on PostgreSQL. While abstraction is planned, fully switching databases later would still require significant effort.
  * Requires implementing a robust strategy for managing database schema migrations (as detailed in ADR 0005).
  * Secure handling of sensitive data (like credentials defined in the schema) is paramount and adds implementation complexity.
