# Using In-Memory Caching for fast alert determination
## Context
MonitorMe needs to be able to determine fast if a patient vital signs has degrated and send alert towards the medical professionals. In order to do that, we consider using an In-Memory Caching for the latest vital signs. 
This way, when a vital sign comes in from a device, we can easily access other vital sign data needed to decide if the current vital sign is outside an expected range (which will trigger the alert). 

## Decision: 
We have decided to implement an in-memory caching system to store frequently accessed data. 
This decision is based on the following considerations:
  * Performance: In-memory caching allows for extremely fast read and write access, significantly improving the performance of our system.
  * Reduced Load on Main Datastore: By caching frequently accessed data in-memory, we can reduce the load on our main datastores, which can be particularly important for scaling our system.
  * Scalability: In-memory caching systems can easily scale horizontally by adding more caching nodes, making it an excellent choice for our growing system.
  * Cost-Effectiveness: In-memory caching systems are generally more cost-effective than traditional storage solutions for frequently accessed data.

## Status
Proposed

## Consequences
 * Data Consistency: In-memory caching systems generally prioritize performance over data consistency, so we must carefully consider how this affects our data and implement strategies to ensure consistency when necessary.
 * Memory Management: We will need to carefully manage memory usage, as an in-memory caching system can consume significant amounts of memory depending on the size of the cached data.
 * Backup and Recovery: We will need to implement backup and recovery strategies for the cached data to prevent data loss in the event of a failure.
 * Monitoring: We will need to implement monitoring to ensure the health and performance of our in-memory caching system.
 * Cache Invalidation: We will need to implement strategies for cache invalidation to ensure that stale data is not returned to users.

## Options
 * Disk-based Caching: Instead of using an in-memory caching system, we could implement a disk-based caching solution. This involves storing frequently accessed data on disk rather than in memory. While disk-based caching may not offer the same level of performance as in-memory caching, it can still provide significant performance improvements compared to accessing data from the main data store.
 * Database Materialized Views: Materialized views are precomputed tables that store the results of a query. We could use database materialized views to store snapshots of frequently accessed data. This allows us to efficiently retrieve and query the snapshot data without the need for additional caching layers.
 * Data Warehousing: Data warehousing involves storing large volumes of data in a centralized repository optimized for analytical queries. We could use a data warehousing solution to store snapshots of frequently accessed data, allowing for efficient querying and analysis of historical data.
 * Distributed Cache: Instead of using a single in-memory caching system, we could implement a distributed cache solution. Distributed caches replicate data across multiple nodes, providing fault tolerance and scalability. This allows us to store and access snapshots of frequently accessed data across a distributed network of cache nodes.

## Usefull links 
- [C4 Diagram](https://github.com/ArchitectsEvolutionZone/MonitorMe/blob/main/2.ArchitectureVisualization/C4Diagram.md)
