# [ADR-DATA-001] Data Persistence Strategy

## Context and Problem Statement
We need to select the primary data storage technology for the Core Database (Tenants, Users, Config).
While the domain has some relational aspects, the system prioritizes "Serverless" characteristics (scale-to-zero, minimal operations) and consistent performance at scale.

### Decision Drivers
* **Operational Overhead**: Must minimize database management (NoOps).
* **Scaling Characteristics**: Must handle "bursty" traffic and scale to zero (Cost efficiency).
* **Performance**: Consistent single-digit millisecond latency regardless of scale.
* **Ecosystem**: Integration with AWS Lambda and EventBridge (Event-Driven Architecture).

## Considered Options
* **Amazon DynamoDB** (NoSQL, Serverless)
* **Amazon Aurora Serverless v2** (PostgreSQL, Relational)
* **Amazon RDS for PostgreSQL** (Provisioned Relational)

## Decision Outcome
**Chosen Option**: **Amazon DynamoDB**

**Justification**:
DynamoDB is the only option that fully aligns with our **Serverless First** strategy ([architecture-style](architecture-style.md)).
Unlike Aurora Serverless, DynamoDB offers true "pay-per-request" pricing and eliminates connection management overhead common with Lambda + RDBMS.
We accept the trade-off of "Eventual Consistency" (see [../../arch/views/cross-cutting-concepts](../../arch/views/cross-cutting-concepts.md) [CC-DAT-002]) and lack of joins in exchange for predictable performance and operational simplicity.

### Positive Consequences
* **True Serverless**: No instance provisioning or scaling management.
* **Performance**: Consistent low latency at any scale.
* **Event Integration**: Native DynamoDB Streams integration for Event Sourcing patterns.

### Negative Consequences
* **Modeling Complexity**: Requires "Single Table Design" or denormalization; no SQL joins.
* **Consistency**: Strong consistency requires explicit configuration (Read consistency).
* **Query Flexibility**: Limited ad-hoc query capabilities compared to SQL.
