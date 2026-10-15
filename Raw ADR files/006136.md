# ADR-005: Async Notifications

## Date:
2024-09-26

## Status:
Accepted

## Context:
We are designing an application with heavy traffic, therefore we expect to have a very large number of notifications which must be delivered in a short period of time.

## Decision:
The decision has been made to utilize Kafka as an intermediary queueing system for delivering notifications to enhance throughput of the application by scaling horizontally when needed.

## Consequences:

### PROS:
- **High Throughput and Scalability:** Kafka can handle large volumes of data with very low latency, making it ideal for real-time data streaming and processing. It is designed to scale horizontally by adding more brokers.
- **Fault Tolerance:** Kafka is distributed and replicates data across multiple nodes. This ensures that even if some nodes fail, the system remains available and can recover automatically.
- **Durability:** Kafka provides durable message storage. Data is persisted on disk and replicated across brokers, allowing consumers to read messages even if they go offline temporarily.
- **Decoupling:** Kafka acts as an intermediary between producers and consumers, allowing them to work independently. This decouples systems and improves flexibility, making it easier to add or modify services without impacting others.

### Cons:
- **Operational Complexity:** Managing a Kafka cluster involves complexity in setup, configuration, monitoring, and maintenance. Balancing partitions, ensuring replication, and handling failures require expertise and significant operational overhead.
- **Data Retention and Storage Costs:** Kafka’s ability to retain large amounts of data on disk comes with increased storage costs, especially if retention periods are long or if data is replicated across many brokers.
- **Learning Curve:** Kafka has a steep learning curve. Developers and DevOps teams need to invest time in understanding topics, partitions, offsets, consumer groups, and the intricacies of Kafka’s behavior.