# ADR-008: Data Warehouse

## Date:
2024-09-27

## Status:
Accepted

## Context:
We are designing an application that owns lots of data, split in different places: databases, Kafka topics, etc. and we need to efficiently aggregate all that information for analysis and reports.

## Decision:
The decision has been made to utilize Google BigQuery as a Data Warehouse solution which allows storing terabytes of data and efficient querying.

## Consequences:

### PROS:
- **Scalability:** BigQuery is a fully-managed, serverless, and highly scalable data warehouse. It can handle petabytes of data and automatically scales up and down based on the workload.
- **Speed and Performance:** BigQuery is designed for fast query execution over large datasets. Its distributed architecture and support for standard SQL provide high performance, even when running complex analytical queries.
- **Powerful Analytics and Data Modeling:** BigQuery supports advanced analytics, including machine learning (through BigQuery ML), geographic analysis, and partitioning, giving users access to sophisticated analysis without requiring separate tools.

### Cons:
- **BigQuery Query Costs:** Although BigQuery uses a pay-per-query model, costs can escalate quickly if queries are poorly optimized or if large datasets are being queried frequently. For high-frequency usage, this can lead to significant expenses.
- **Complex Setup and Management:** Setting-up a data warehouse requires skilled personnel to handle data architecture, integration, ETL processes, and ongoing management. Setting up complex data transformations, cleansing, and validation rules can be time-consuming and require constant oversight.
- **Latency for Real-Time Data:** While BigQuery supports real-time data ingestion, its architecture is fundamentally batch-oriented.
- **Limited Cross-Platform Capabilities:** BigQuery is tightly integrated within the Google Cloud Platform (GCP) ecosystem, which might lead to vendor lock-in. Switching to another cloud provider or platform could involve significant migration efforts and cost.