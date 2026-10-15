# ADR-002: Database Systems

## Date:
2024-04-03

## Status:
Accepted

## Context:
The context for this decision is to determine the types of database systems to be used for each use case in the Fishy Watch system. We need to consider factors such as data structure, scalability, performance, and data consistency.

## Decision:
After evaluating the requirements and considerations, we have decided to use the following types of database systems for each use case in the Fishy Watch system:

1. **Data Collection and Storage**:
   - **Time-Series Database**: For storing time-series data collected from water monitors, underwater cameras, and fish-ual recognition. Examples include InfluxDB or TimescaleDB, which are optimized for handling time-series data efficiently.

2. **User and Farm Information**:
   - **Relational Database**: For storing user profiles, farm information, and configuration settings. PostgreSQL or MySQL can be used for relational data management and complex queries.

3. **Alerts and Thresholds**:
   - **NoSQL Database**: For storing alerts, thresholds, and event-based data. MongoDB or Cassandra can be suitable for handling unstructured or semi-structured data and providing fast read and write operations.

4. **Historical Data and Analytics**:
   - **Data Warehouse**: For storing historical data, aggregated metrics, and analytics results. Snowflake or Google BigQuery can be used for scalable storage and advanced analytics capabilities.

## Consequences:
### Pros:
- Data Structure Optimization: Using specialized database systems for each use case optimizes data storage and retrieval based on data structure and query requirements.
- Scalability: The chosen database systems are scalable and can handle large volumes of data and concurrent users effectively.
- Performance: Database systems are selected based on performance considerations, ensuring efficient data processing and response times.
- Data Consistency: Each database system is designed to maintain data consistency and integrity according to its data model and transactional capabilities.

### Cons:
- Complexity: Managing multiple types of database systems adds complexity in terms of deployment, maintenance, and data synchronization.
- Integration Challenges: Ensuring seamless integration and data flow between different database systems may require careful design and implementation.
- Training and Expertise: Teams need expertise in managing and optimizing various database systems to ensure optimal performance and reliability.
