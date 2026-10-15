# ADR: Database Selection

## Context
Selecting a database for the AML system to handle reading and writing data.

## Problem Statement
The system needs a database that supports large amounts of data, diverse types of data, and can grow with our microservices architecture. It should also be fast for read operations, as each service will have its own isolated database.

## Considered Options
- MySQL  
- Oracle Database  
- MongoDB  

## Decision Outcome Confirmation
We’ve chosen MongoDB. Its flexible, document-based structure and ability to scale make it perfect for a microservices system. One key reason we selected MongoDB is that it is very fast for read operations, which is crucial as each service will have its own database and need to do many additional read queries.

## Consequences
MongoDB’s flexible schema and scalability will allow the system to grow and adapt easily. It can handle large amounts of data and support changes in data structure without needing major changes to the database.

With MongoDB’s flexible schema, the system can adapt to changes in data structure without requiring extensive modifications, providing a more agile solution as services evolve.

## Pros
- MongoDB is optimized for fast read operations, which is important for microservices that need to read data quickly.
- It works well with both structured and unstructured data, making it easy to adjust as services evolve.
- MongoDB can handle growing data across multiple servers, making it great for a system that will expand over time.
- It supports schema changes without downtime, allowing for continuous development.

## Cons
- MongoDB supports transactions, but its capabilities are not as strong as relational databases for complex, cross-service operations.
- MongoDB’s query language can be complex for users used to SQL, adding a learning curve for teams transitioning from relational databases.

## Confirmations
MongoDB is the best choice for the AML system due to its flexibility, scalability, and speed, especially for read-heavy workloads in a microservices setup.

## Pros and Cons of Options

### Oracle Database

**Pros**:  
- Advanced security, analytics, and extensive data type support.  
- Handles large volumes of transactions efficiently.  
- Manages growing data and user loads effectively.  

**Cons**:  
- Licensing and operational expenses are significant.  
- Requires specialized expertise
- Demands high hardware resources, increasing infrastructure costs.  

### MySQL  

**Pros**:  
- Consistently fast with high uptime.  
- Cost-effective with a robust community support.  
- Ensures consistency across all transactions.  

**Cons**:  
- Primarily designed for structured data, limiting flexibility in a microservices architecture.  
- Transitioning to or from MySQL can be complex.  
- Large datasets may require performance tuning, increasing maintenance efforts.  
