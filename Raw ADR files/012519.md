# Choosing the Database Technology for the Nordic Bank Core System
- Status: accepted
- Deciders: @hansen1904
- Date: 2024-12-08

## Context and Problem Statement
We need to select the most appropriate database technology for the core banking system of Nordic Bank. The database must meet our requirements for data integrity, performance, scalability, security, and ease of maintenance. This decision is critical as it will affect the storage, retrieval, and management of sensitive financial data.

## Decision Drivers
- Data Integrity: The database must ensure high data integrity and support ACID transactions.
- Performance: The database must deliver high performance for read and write operations.
- Scalability: The database must support horizontal and vertical scaling to accommodate future growth.
- Security: The database must offer robust security features to protect sensitive financial data.
- Ease of Maintenance: The database should be easy to maintain and have strong community and commercial support.

## Considered Options
- PostgreSQL
- MySQL
- Microsoft SQL Server
- MongoDB

## Decision Outcome
Chosen option: "PostgreSQL", because it offers strong support for ACID transactions, high performance, excellent scalability, robust security features, and has a strong community and commercial support.

### Positive Consequences
- High data integrity and support for ACID transactions.
- Excellent performance for complex queries and large datasets.
- Strong security features, protecting sensitive financial data.
- Robust community and commercial support, ensuring ease of maintenance.
- Flexibility and scalability, supporting both horizontal and vertical scaling.

### Negative Consequences
- May require additional tuning and optimization for very high transaction volumes.
- Steeper learning curve for developers not familiar with PostgreSQL.

## Pros and Cons of the Options

### PostgreSQL
- **Pros**:
    - Ensures high data integrity and supports ACID transactions.
    - Delivers excellent performance for complex queries.
    - Offers robust security features.
    - Strong community and commercial support.
- **Cons**:
    - Require additional tuning for very high transaction volumes.
    - Steeper learning curve for developers not familiar with it.

### MySQL
- **Pros**:
    - Widely used and has strong community support.
    - Easy to set up and use.
- **Cons**:
    - Limited support for complex queries compared to PostgreSQL.
    - May not perform as well under very high transaction volumes.

### Microsoft SQL Server
- **Pros**:
    - Offers strong support for ACID transactions and high performance.
    - Integrates well with other Microsoft products.
- **Cons**:
    - Higher licensing costs compared to open-source options.
    - May not be as flexible for scaling in cloud environments.

### MongoDB
- **Pros**:
    - Offers high performance for read-heavy operations.
    - Highly scalable for horizontal scaling.
- **Cons**:
    - Limited support for ACID transactions.
    - May not provide the same level of data integrity as relational databases.
