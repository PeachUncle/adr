# Specification of database relational or non-relational

* Status: proposed
* Deciders: Jaime Ochoa de Alda Cerdán
* Date: 2025-10-29

## Context and Problem Statement

After selecting a three-tier architecture it is necessary to specify the type of database required for the project, as both relational and non-relational databases bring their advantages and disadvantages.

## Decision Drivers

* RF-03 CRUD de pedidos del cliente
* RF-14 Registro histórico de rutas y entregas

## Considered Options

* 0003-1-Relational Database
* 0003-2-Non-Relational Database

## Decision Outcome

Chosen option: 0003-1-Relational Database, because the project requires strong data consistency, referential integrity between entities (e.g., linking routes and incidents to specific orders), and transactional guarantees during the sequential processing phases of an order. Additionally, retrieving historical order data, delivery records, and statistics benefits from structured relationships and SQL queries.

### Positive Consequences

* Enables reliable enforcement of relationships (e.g., each order must reference a valid client) using referential integrity constraints at the database level.
* ACID guarantees strong consistency across the sequential phases of an order (pre-processing → authorization → acceptance), preventing partial updates or state corruption, unlike BASE models offer eventual consistency, which could allow temporary inconsistencies between order state, payment confirmation, and delivery assignment.
* Structured schema ensures consistency, validation, and controlled evolution of the domain model.


### Negative Consequences

* The rigid schema of relational databases may become a strong limitation in a food-related business domain, which is subject to frequent regulatory updates (e.g., allergen tracking, lot traceability, temperature logging). These changes can require recurring schema migrations, increasing operational effort and deployment complexity.
* Vertical scalability may become a bottleneck under extreme load without additional strategies (sharding, replication, partitioning).
* New data attributes added for product batches, quality incidents, or extended traceability may need careful schema evolution to avoid downtime or inconsistencies.

## Pros and Cons of the Options

### 0003-1-Relational Database

Relational databases organize data into structured tables with predefined schemas and explicitly defined relationships between entities. They rely on the SQL language for querying and provide strong consistency guarantees, making them well-suited for domains where data integrity, transactional correctness, and complex cross-entity queries are essential. Their support for constraints, normalization, and referential integrity helps prevent invalid states and ensures reliable historical tracking across related datasets.

More info: https://en.wikipedia.org/wiki/Relational_database

* Good, because it enforces data integrity through primary keys, foreign keys, and constraints.
* Good, because SQL allows complex queries, joins, and aggregations needed for statistics and historical reports.
* Good, because it simplifies modeling of sequential order states and relationships with deliveries and incidents.
* Bad, because schema evolution requires coordinated migrations that may introduce downtime or complexity.
* Bad, because horizontal scalability is limited compared to some NoSQL solutions.
* Bad, because are less efficient for high-velocity time-series data (e.g., live vehicle telemetry), where specialized database engines or NoSQL document stores perform better.

## 0003-2-Non-Relational Database

A non-relational (NoSQL) database stores data in flexible and schema-less structures (e.g., key-value, documents, column stores). It offers high scalability, flexible data models, and suitability for unstructured or rapidly evolving data.

More info: https://en.wikipedia.org/wiki/NoSQL

* Good, because it allows flexible schemas that can evolve without downtime.
* Good, because it scales horizontally with ease, supporting large amounts of real-time data.
* Good, because While SQL databases can store event-based information, schema rigidity and index overhead may reduce performance and increase operational complexity compared to document or time-series NoSQL stores.
* Bad, because eventual consistency may complicate multi-step workflows requiring strict state integrity.
* Bad, because complex relationships are harder to enforce, increasing application-level complexity.
* Bad, because analytics requiring joins become more inefficient.
