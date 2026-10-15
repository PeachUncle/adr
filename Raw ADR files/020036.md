# Decision Record: Backing Services Technology Selection

**ID:** 03  
**Date:** 2024-06-07  
**Status:** Accepted  
**Author:** hoangpt  
**Reviewer:** lam

## Context

The project requires reliable, scalable, and maintainable backing services to support microservices, AI integration, and high-performance data processing. This includes the selection of database, message queue, and caching technologies.

## Database Options

| Technology         | Pros                                                                 | Cons                                      |
|--------------------|----------------------------------------------------------------------|-------------------------------------------|
| **PostgreSQL**     | - Open-source, robust, ACID compliant<br>- Rich features (JSONB, GIS)<br>- Strong community support | - Slightly more complex to operate than MySQL |
| **MySQL/MariaDB**  | - Widely used, easy to set up<br>- Good performance for OLTP         | - Fewer advanced features than PostgreSQL |
| **MongoDB**        | - Flexible schema, good for unstructured data<br>- Scalable          | - Not ACID by default (except transactions in replica sets)<br>- Less suitable for complex joins |
| **Azure Cosmos DB**| - Fully managed, multi-model<br>- Global distribution, scalable      | - Cost can be high<br>- Vendor lock-in    |

**Decision:**  
- Use **PostgreSQL** as the primary relational database for its robustness, features, and open-source nature.
- For vector search and AI integration, leverage **Azure Cosmos DB** (with vector support) as a secondary, specialized store.

---

## Message Queue Options

| Technology         | Pros                                                                 | Cons                                      |
|--------------------|----------------------------------------------------------------------|-------------------------------------------|
| **RabbitMQ**       | - Mature, reliable, supports multiple protocols<br>- Good for complex routing | - Operational overhead, needs management  |
| **Apache Kafka**   | - High throughput, scalable, persistent<br>- Good for event sourcing | - Steeper learning curve, heavier setup   |
| **Azure Service Bus** | - Fully managed, integrates with Azure ecosystem<br>- Supports advanced messaging patterns | - Vendor lock-in, cost                    |

**Decision:**  
- Use **RabbitMQ** for service-to-service communication due to its maturity, flexibility, and open-source nature.
- For cloud-native or high-scale scenarios, consider **Azure Service Bus** as a managed alternative.

---

## Caching Options

| Technology         | Pros                                                                 | Cons                                      |
|--------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Redis**          | - Extremely fast, supports various data structures<br>- Widely adopted, easy to use | - In-memory only (unless using persistence)<br>- Needs separate management |
| **Memcached**      | - Simple, very fast for key-value caching                            | - Limited features compared to Redis      |
| **Azure Cache for Redis** | - Fully managed, scalable<br>- Integrates with Azure           | - Vendor lock-in, cost                    |

**Decision:**  
- Use **Redis** for caching due to its performance, features, and community support.
- In production on Azure, use **Azure Cache for Redis** for managed operations and scalability.

---

## Summary Table

| Component      | Chosen Technology         | Rationale                                      |
|----------------|--------------------------|------------------------------------------------|
| Database       | PostgreSQL, Azure Cosmos DB (vector) | Robust, open-source, vector support for AI     |
| Message Queue  | RabbitMQ (or Azure Service Bus)      | Mature, flexible, managed option on Azure      |
| Caching        | Redis (or Azure Cache for Redis)     | Fast, feature-rich, managed option on Azure    |

---

## Consequences

- The team should standardize data access patterns and messaging protocols.
- Ensure proper monitoring, backup, and scaling strategies for each component.
- Be mindful of vendor lock-in and cost when using managed Azure services.