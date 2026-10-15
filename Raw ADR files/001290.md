# Specification of Database Removal

* Status: proposed
* Deciders: Jaime Ochoa de Alda Cerdán
* Date: 2025-11-12

## Context and Problem Statement

During the initial architectural design, several decisions were made regarding the use of a relational database, the communication layer between the logic and data tiers, and the encryption of that communication (0003, 0004, 0009).

However, after further analysis of the client's requirements, it became clear that the system is not required to persist information. The application processes operational data in memory and communicates with external services, without storing internal datasets.

Therefore, the previous database-related decisions are no longer aligned with the actual business and functional requirements, and must be revoked.

## Decision Drivers

* The client explicitly stated that no persistent data storage is required.
* Security and compliance concerns related to stored data are irrelevant.

## Considered Options

* 0010-1-Remove-Database-Layer-Entirely

## Decision Outcome

Chosen option: 0010-1-Remove-Database-Layer-Entirely, because the client's updated specifications confirm that no data persistence or storage of customer, order, or delivery information is required.

This decision supersedes and invalidates the following:

- 0003-Database Type (Relational or Non-relational)
- 0004-Communication Between Logic and Database
- 0009-Database Communication Encryption

The system specification will remain independent of data storage mechanisms, focusing only on process and interaction design between modules. This simplifies the architecture and eliminates unnecessary database configuration, ORM logic, and encryption overhead.

### Positive Consequences

* Reduces system complexity and infrastructure costs.
* Simplifies the current architecture by removing unnecessary assumptions about the database layer.

### Negative Consequences

* Persistent data handling is postponed, limiting the system's ability to demonstrate long-term behavior within the current scope.
* Real-time dependencies increase system availability now depends more strongly on external service uptime.

## Pros and Cons of the Options

### 0010-1-Remove-Database-Layer-Entirely

This option proposes completely removing the database component from the system architecture.
All data would be processed and exchanged in real time between the application’s modules and external APIs without any form of persistence. This approach simplifies the infrastructure and aligns strictly with the client’s updated specifications, which exclude the need for stored data.

* Good, because it aligns precisely with the client’s clarified requirements.
* Good, because it eliminates redundant architectural components.
* Bad, because it prevents future extensibility in case persistence becomes required.
* Bad, because removing the data layer makes it harder to simulate real scenarios for testing.