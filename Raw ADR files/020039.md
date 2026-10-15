# 10. Couchbase as database

Date: 2024-10-17

## Status

Accepted on 2024-10-17
 
Builds on [0009-vulnerability-data-ingestion-process.md](0009-vulnerability-data-ingestion-process.md) on 2024-10-17

## Context

Following our decision in [ADR 0009](0009-vulnerability-data-ingestion-process.md) to implement a hybrid approach combining elements of options 2 and 3 for our vulnerability data ingestion process, we need to select an appropriate database solution. Key considerations include:

1. Flexibility in data structure: We want to keep the vulnerability object flexible until we determine how strict it can or should be.
2. Support for document storage: To accommodate the evolving nature of our data model.
3. Full-text search capabilities: To enable efficient querying and analysis of vulnerability data.
4. ACID transactions: To ensure data integrity across operations.
5. Potential for time-series data: To support possible future requirements for temporal analysis.

We considered various database types, including relational, graph, and document-based databases.

## Decision

We have decided to use Couchbase as our database solution for the vulnerability data ingestion and processing system.

Rationale:
1. Document store: Couchbase's document-oriented nature aligns with our need for flexibility in the vulnerability object structure.
2. Full-text search: Couchbase provides built-in full-text search capabilities, which are crucial for efficient querying of vulnerability data.
3. ACID transactions: Couchbase supports ACID transactions, ensuring data consistency across operations.
4. Time-series support: Couchbase offers features that can be leveraged for time-series data if needed in the future.
5. Scalability: Couchbase's distributed architecture allows for horizontal scaling, which may be beneficial as our data volume grows.
6. Hybrid capabilities: Couchbase combines features of document stores and key-value stores, providing versatility for different use cases within our system.

While other document-based databases like MongoDB were considered, Couchbase's combination of features makes it the most suitable choice for our current needs and potential future requirements.

## Consequences

1. Risk: Over-reliance on Couchbase-specific features may lead to vendor lock-in.
2. Risk: Performance issues due to improper use of Couchbase features.
3. Risk: Data model becomes too unstructured, leading to difficulties in querying and maintaining consistency.

