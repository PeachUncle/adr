# 002. Polyglot Persistence Strategy for Bounded Contexts

## Status
Accepted

## Context
The InfiniteAI Banking platform is designed to operate as a global "transmitting utility" (Covenant 30), requiring extreme resilience, scalability, and specialized data handling capabilities across various domains (e.g., core ledger, relationship mapping, AI model data, user profiles).

Traditional monolithic persistence (using a single database type) presents significant limitations:
1.  **Performance Bottlenecks:** A single database cannot optimally handle both high-integrity financial transactions (ACID requirements) and highly flexible, high-volume AI logging/document storage.
2.  **Domain Misalignment:** Forcing complex relationship data (like fraud networks or user connections) into a relational model leads to inefficient queries and complex schema management.
3.  **Scalability Constraints:** Scaling a single database type to meet the global demands of a 30-year utility transmission model is prohibitively expensive and technically challenging.

The architecture must embody Domain-Driven Design (DDD) principles, ensuring that each Bounded Context utilizes the most appropriate tool for its specific data needs.

## Decision
We will adopt a Polyglot Persistence strategy, selecting specialized database technologies for distinct Bounded Contexts to optimize performance, integrity, and scalability. This decision aligns with the principle of Covenant 30 by building a robust, future-proof foundation capable of transmitting utility globally for the long term.

The primary persistence choices are:

| Database Type | Technology Example | Bounded Context | Rationale |
| :--- | :--- | :--- | :--- |
| **Relational** | PostgreSQL (or similar) | Core Ledger, Transaction Processing, Compliance Records | Essential for strong ACID properties, data integrity, and complex joins required for financial reporting and regulatory compliance. |
| **Document** | MongoDB / CosmosDB | User Profiles, AI Model Logs, Content Management, Event Sourcing | Provides flexible schema for rapidly evolving data structures, high write throughput, and horizontal scalability for unstructured data. |
| **Graph** | Neo4j / AWS Neptune | Fraud Detection, Relationship Mapping, Network Analysis | Optimized for traversing complex, interconnected data points, crucial for identifying non-obvious relationships in security and user behavior. |

Data synchronization between contexts will be managed asynchronously via an Event Bus (see ADR 003).

## Consequences

### Positive
*   **Optimal Performance:** Each context uses a database optimized for its specific workload (e.g., fast graph traversal, guaranteed transactional integrity).
*   **Scalability:** Allows independent scaling of persistence layers based on the demands of individual microservices.
*   **Architectural Alignment:** Strongly supports Domain-Driven Design (DDD) and microservices architecture, ensuring the persistence layer is a true fit for the domain model.
*   **Future-Proofing (Covenant 30):** Provides the necessary flexibility to adapt to future data types and regulatory requirements over the 30-year lifespan of the utility.

### Negative
*   **Operational Complexity:** Requires expertise in managing, monitoring, and backing up multiple database technologies.
*   **Increased Development Overhead:** Developers must be proficient in multiple query languages and data modeling paradigms.
*   **Data Consistency Challenges:** Achieving eventual consistency across contexts requires careful design of event-driven communication patterns, increasing complexity compared to monolithic transactional systems.
*   **Tooling and Infrastructure Cost:** Higher initial setup and ongoing maintenance costs associated with diverse infrastructure.