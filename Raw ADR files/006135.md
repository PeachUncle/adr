# ADR-004: CV Indexing

## Date:
2024-09-25

## Status:
Accepted

## Context:
We are designing an application that requires fast querying of the CVs and a performant tool to efficiently retrieve and rank results, assigning a score to each based on relevance.

## Decision:
The decision has been made to utilize ElasticSearch as an indexing/search engine. This decision is motivated by its design for high-performance, full-text searching and is optimized for querying large datasets in real-time.

## Consequences:

### PROS:
- **High Performance and Scalability:** Elasticsearch is built for high-speed searches and scales horizontally, allowing you to index and search across massive datasets with low latency. It's optimized for near real-time data retrieval.
- **Full-Text Search:** Elasticsearch excels at full-text search, making it ideal for use cases that require searching through large amounts of unstructured text, such as CVs, logs, or articles.
- **Relevance Scoring and Ranking:** Elasticsearch provides powerful relevance scoring based on search term matches and can be customized using factors like boosting, weights, and custom scoring functions to rank search results according to your needs.
- **Distributed Architecture:** Elasticsearch is a distributed system by design, meaning it can handle large-scale deployments with multiple nodes and shards, providing high availability and fault tolerance.
- **Complex Queries and Filtering:** It supports a wide range of queries, including full-text, fuzzy searches, boolean queries, and filtering, which allows for complex data retrieval scenarios.

### Cons:
- **Operational Complexity:** Running and maintaining Elasticsearch clusters can be complex, requiring careful configuration of nodes, shards, and replicas. Proper monitoring and tuning are essential to ensure performance and reliability.
- **Memory and Resource Intensive:** Elasticsearch requires significant system resources, especially memory. It stores data in-memory for fast querying, so large datasets or heavy traffic can quickly consume RAM and CPU, leading to performance bottlenecks.
- **Eventual Consistency:** Elasticsearch operates on eventual consistency, meaning there can be slight delays in data synchronization across nodes. This might be a problem for applications that need strict consistency guarantees.
- **Index Management Overhead:** Maintaining efficient indices, especially as data grows or changes, can be challenging. Misconfigured indices (e.g., too few or too many shards) can lead to performance degradation and require regular tuning.