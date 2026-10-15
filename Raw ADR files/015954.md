# ADR 4: Implementation of CQRS Pattern for Read Operations

Status: Accepted

Date: 2026-01-08

Deciders: Project Lead

## 1. Context and Problem Statement

Our current feature implementation focuses on state changes (Writes). However, the requirements for displaying data (Reads) are often vastly different from the requirements for business logic validation. Using the same Domain Entities for both causes performance bottlenecks (unnecessary data loading) and rigid API structures. We need a way to fetch data quickly, support complex filtering/pagination, and maintain consistency without cluttering our Write models.

## 2. Decision Drivers

* Performance: Read operations should bypass complex domain logic and fetch only necessary columns (Projection).
* Consistency: Multiple queries within a single request must see the same "snapshot" of data.
* Developer Experience (DX): The API for queries should mirror the API for commands to reduce cognitive load.
* Scalability: The ability to use database views or optimized SQL joins without affecting the Domain Entities.

## 3. Considered Options

### Option 1: Unified Model (Traditional CRUD)

Use the same Repositories and Entities for both reading and writing.

* Good, because: Less code; no need for separate DTOs or Read Models.
* Bad, because: Inefficient. Fetching a list of 100 items would instantiate 100 complex Domain Entities even if only the "Name" is needed. It also makes "JOIN" operations difficult to map.

### Option 2: Separate Query System with UoW (The Proposed Design)

Implement a Command Query Responsibility Segregation (CQRS) lite approach. Queries use dedicated "Read Models" and "Query Repositories" but share the same UnitOfWork (UoW) lifecycle as commands.

* Good, because: Provides snapshot isolation (consistent reads). Standardizes the execute(&mut uow) pattern across the entire app. Highly optimized SQL can be used for projections.
* Bad, because: Requires duplicating some structural definitions (Read Models vs. Entities).

### Option 3: Direct Database Access in Commands

Skip the Application and Infrastructure layers for reads and run SQL directly inside the Tauri commands.

* Good, because: Minimal boilerplate; extremely fast to write.
* Bad, because: Zero testability. Business logic or formatting logic leaks into the interface layer. No reuse of query logic across different commands.

## 4. Decision Outcome

Chosen Option: Option 2: Separate Query System with UoW

### Justification

By integrating the Query System into the existing UnitOfWork pattern, we achieve a rare balance of high performance and high architectural integrity. The UoW ensures that even read-only operations are execution-safe and consistent. Using Read Models (DTOs) ensures that our Frontend only receives exactly what it needs, minimizing IPC (Inter-Process Communication) overhead in Tauri.

### Consequences

Positive:
* Consistent Snapshots: By using the UoW's transaction for queries, we avoid "phantom reads" where data changes between two queries in the same handler.
* Unified Interface: Developers use the same pattern for every task: UoW -> Extension -> Repository.
* Optimized SQL: We can use JOINs and Views freely in the Infrastructure layer without worrying about how to map them back to complex Domain Entities.

Negative:
* Increased Trait Count: Every feature now has a Repository trait and a QueryRepository trait.

Neutral:
* Read-only transactions must still be "committed" or dropped to release the connection back to the pool.

## 5. More Information

* Type Generation: All Read Models must be decorated with `#[derive(specta::Type)]` to update the TypeScript frontend automatically.