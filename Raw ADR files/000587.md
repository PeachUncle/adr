# 3. Dedicated storage for analytics

Date: 2023-09-15

## Status

Accepted

## Context

In our system, analytical metrics are the main source of revenue and aim to provide valuable insights to our users and external parties. Providing analytical data to 3rd parties must be consistent and independent of the growing number of users, bookings, and types of metrics.

## Decision

We have decided to separate the storage for processed analytical metrics from the main storage of the system.

By separating the storage for processed analytical metrics from the main storage of the system, we anticipate significant improvements in performance, scalability, data management, and workload isolation. This decision aligns with our long-term goals for maintaining a robust and high-performance analytics platform.

## Consequences

### Positive 
* Performance: The main storage of our system is optimized for real-time access. Storing processed analytical metrics in the same storage can lead to performance bottlenecks, especially when analytical queries are resource-intensive. Separating the two types of data allows us to choose storage solutions that are specifically optimized for analytical workloads, improving query performance and responsiveness.
* Scalability: As the volume of processed analytical metrics grows, it can put significant strain on our main storage system. By separating the storage, we can independently scale the analytical metrics storage to accommodate the increasing data volume without impacting the performance or scalability of the core data storage.
* Data Management: Separating the storage for processed analytical metrics simplifies data management and reduces the risk of data corruption or loss. It allows us to implement different retention policies, backups, and data lifecycle management strategies for each type of data, ensuring that critical metrics are retained and available for analysis while core data is managed according to its specific requirements.
* Isolation of Workloads: Analytical workloads often involve complex queries that can be resource-intensive. By separating the storage, we can isolate analytical workloads from the core workloads, preventing analytical queries from affecting the performance of core system operations.
* Flexibility: Separating storage provides flexibility in choosing the most suitable storage technologies and architectures for each type of data. We can choose columnar or distributed databases optimized for analytics while continuing to use transactional databases for the main storage, tailoring each to its specific needs.
  
### Negative
* Data consistency: We need to make sure that data is consistent between our storages

| [🏠 home](../../README.md#adr) | [<< **ADR** Microservices vs Event driven architecture style ](./0002-arch-style-microservices-vs-event-driven.md) | [**ADR** Storing agency contact details for help >>](./0004-store-agency-contact-for-help.md) |