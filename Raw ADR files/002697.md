# Using NoSQL for Data Storage in On-Premise Server

## Context
Data storage is required in the context of having functionalities like a medical history for pacients, 
build statistics, and automate certain processes like medical emergencies or diagnostics.

## Decision: 
we have decided to use NoSQL databases. 
NoSql is known for its ability to handle unstructured and semi-structured data, 
making them suitable for scenarios where the data structure may evolve over time or where flexibility in data storage is required.

## Status
Proposed

## Consequences

   * Flexibility: NoSQL databases are schema-less, allowing for flexible data storage. This is beneficial when dealing with diverse data types or when the data structure is subject to change.

   * Scalability: NoSQL databases are designed to scale horizontally, making them suitable for scenarios where data volumes may increase rapidly. This scalability can be crucial for handling large amounts of data in real-time.

   * Performance: NoSQL databases are optimized for performance, especially when dealing with large datasets. This can lead to faster query times and improved overall system performance.

   * Cost: NoSQL databases can be more cost-effective than traditional relational databases, especially when dealing with large volumes of data. This can lead to cost savings in terms of storage and maintenance.

   * Complexity: Implementing a NoSQL database may require additional expertise and knowledge compared to traditional relational databases. This complexity should be taken into account when planning and executing the deployment.

   * Data Integrity: NoSQL databases may not offer the same level of data integrity and consistency as traditional relational databases, especially in distributed environments. This should be considered when designing the data storage strategy.
   
## Options
   * Traditional Relational Databases: We could explore using traditional relational databases instead of NoSQL. While NoSQL offers flexibility, relational databases are known for their strong data consistency and integrity features, which might be important for critical medical data storage.
   * Hybrid Approach: We might consider a hybrid approach that combines NoSQL and relational databases. This way, we could leverage the flexibility of NoSQL for certain types of data while relying on the strong consistency guarantees of relational databases for other data types.
   * Evaluate Cloud-Based Solutions: We could evaluate cloud-based database solutions that offer both NoSQL and relational database options. This could provide us with the flexibility to choose the best fit for each use case while offloading maintenance and scalability concerns to the cloud provider.

## Usefull links 
- [C4 Diagram](https://github.com/ArchitectsEvolutionZone/MonitorMe/blob/main/2.ArchitectureVisualization/C4Diagram.md)
