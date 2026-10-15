# 5. Use DynamoDB single-table design for data storage

Date: 2024-06-14

## Status

Accepted

## Context

We require a solution to storing application state within Big Transit.

## Decision

After toying with the pros and cons of a traditional RDBMS schema, it became apparent that a DynamoDB single-table design would be a sensible choice for the storage of Team, Pipeline and Stage data within Big Transit. This decision is mostly due to being in the early stages of development and exploiting the flexibility that DynamoDB provides around schema design, along with the support within SST to configure and deploy the DynamoDB configuration. Additionally we have a good understanding of the access patterns required for the API which makes the single-table design relatively simple to implement.

## Consequences

### Pros
Efficient Queries: The use of composite keys allows for efficient querying based on different access patterns, such as retrieving pipelines for a given team or stages for a specific pipeline execution.

Flexibility: The schema allows for easy expansion and modification as the application requirements evolve. You can add new attributes or access patterns without needing to redesign the entire database.

Strong Consistency: DynamoDB offers strong consistency options, ensuring that read operations reflect the latest write.

Testing: It's relatively trivial to mock out calls to DyanmoDB within our data access layer, allowing for unit test to be completely decoupled from the implementation and importanly execute rapidly for fast developer feedback. 

Additionally. 
Scalability: DynamoDB can handle high throughput and large datasets, making it suitable for applications with heavy read and write workloads.

### Cons
Limited Query Flexibility: While DynamoDB is efficient for specific access patterns supported by its primary keys, it can be challenging to perform complex queries that are not well-suited to its schema design.

Cost: DynamoDB can become expensive for applications with unpredictable workloads or those requiring high provisioned throughput to handle spikes in traffic.

Complexity of Composite Keys: Managing composite keys can add complexity to the application logic, especially when dealing with hierarchical data structures like pipelines, executions, and stages.

No Joins: DynamoDB does not support joins between tables, so you'll need to denormalize data to meet query requirements, potentially leading to data redundancy and increased storage costs.
