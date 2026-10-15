# ADR-0016: Database Migrations

## Status

Accepted

Date of decision: 2024 Q4

## Context and Problem Statement

What tools are we going to use to manage migrations for the RDS Postgres database, and where should they live?

## Considered Options

* Migration tool:
    * Flyway
    * Liquibase
* Migrations strategy:
    * Separate repository
    * WebApp repository with separate CD pipeline

## Decision Outcome

Migration tool: Flyway, because it is the simplest option to configure, ramp up on, and use while meeting the straight
forward needs of the project.

Migrations strategy: WebApp repository with separate CD pipeline, because it balances creating a separation between the
application and the database schema, and not unduly adding barriers or manual steps to the deployment process.

## Pros and Cons of the Options

### Migration tool: Flyway

Flyway is one of the two most commonly mentioned tools for managing database migrations. Migrations are pure SQL files,
and migration order is determined by the naming of those migration files. Versioning information is stored in a separate
table in the target database. There is a free version with most of the core functionality, and an enterprise edition
that adds features such as down / rollback migrations. Integration with Spring Boot is straight forward with minimal.

* Good, because it is widely used.
* Good, because migrations are written in SQL which most developers will already be familiar with.
* Good, because it requires minimal configuration to integrate with Spring Boot.
* Neutral, because controlling the order of migrations is simple but inflexible.
* Neutral, because while some features provided for free by other options are only available in the Enterprise edition,
  it is unclear that these are needed for this project.

### Migration tool: Liquibase

Liquibase is the other most commonly cited database migration management tool alongside Flyway. Migrations can be
defined in a number of languages, including SQL, JSON, Yaml, and XML. Configuration is managed using XML configuration
files – in particular, the selection and ordering of migrations to apply is controlled through a XML file known as the
‘master changelog’. Like Flyway, versioning information is stored in the target database. The free version has a few
additional features vs. Flyway, for example down migrations to rollback to a specific point in the schema history, and
support for adding logic to determine whether to apply migrations based on the current state of the database.

* Good, because it is widely used.
* Good, because it provides a choice of methods for defining migrations, including SQL.
* Neutral, because the free edition offers a wider feature set, including some ‘nice to haves’, but it’s not clear
  whether these are really needed.
* Neutral, because while the configuration and application of migrations is more flexible, it is more complex to manage
  via XML

### Migrations strategy: Separate repository

Storing database migrations in their own repository forces the separation of changes to the schema and changes to the
application’s code.

* Good, because it prevents the temptation to use convenience functionality like always running the migrations on
  startup for the application which may not be desirable in production.
* Good, because it helps prevent the database being thought of as ‘owned’ by the application instead of being a service
  that the application (and potentially other applications or services) consumes.
* Neutral, because it requires setting up and managing a separate repository and the overheads that come with that.
* Bad, because it makes it harder to ensure that the code in the main consumer of the database (the WebApp) is being
  kept in sync with the database schema.

### Migrations strategy: WebApp repository, separate pipeline

A less extreme alternative to storing the database migrations in a separate repository is to keep them in the WebApp
repository and instead enforce separation at deployment time by having a separate pipeline (or an optional pipeline
stage) that runs the migrations at deployment time.

* Good, because it allows the use of convenience functionality like always running the migrations on startup for the
  application when running locally.
* Good, because it can still gives complete control and transparency of when the migrations are run in each environment
  via pipelines, while allowing this to be automated where appropriate.
* Good, because it allows schema changes to be included in the same PRs as any downstream code changes for the WebApp,
  making it easier to ensure that they are kept in sync.
* Neutral, because it doesn’t help developers take the proper view of the database being a service that’s consumed by
  the application rather than being a part of it, (but the practical implications are mitigated by having separate
  pipelines/ stages).

## More Information

* Flyway free vs paid versions: https://www.red-gate.com/products/flyway/editions
* Liquibase free vs paid versions: https://www.liquibase.com/pricing  