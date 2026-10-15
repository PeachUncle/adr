---
status: proposed
date: 2024-12-02
decision-makers: Michael Ogunrinde, James Bateman, Cory-Newman
---

# Database Design for AML Membership and Payment Management

## Context and Problem Statement

The AML system requires a robust database design to manage membership and payments information effectively. Membership details must include registration, subscription types and statuses, while payments management must track transactions, amounts, due dates and an adjustment tool to amend underpaid or overpaid payments. Without a well-structured database, the system may face issues like inconsistent membership statuses, errors in payment records, and difficulties generating reports for accountants.

## Decision Drivers

* The database must support scaling to accommodate future growth
* Must ensure high data integrity and minimal chances of errors in membership or payment records
* Should integrate easily with the borrowing and notification systems
* Must protect sensitive payment data from unauthorized access through encryption and access control
* Must be flexible to allow non-members to use some of the key functionalities of the website

## Considered Options

* Relational database management system (MySQL/PostgreSQL)
* Separate tables for membership and payment information
* Combined single table approach
* NoSQL database (MongoDB)
* Hybrid approach (Relational + NoSQL)

## Decision Outcome

Chosen option: "Separate tables for membership and payment information with RDBMS", because:

1. Ensures modularity, making it easier to scale and maintain
2. Payment records are isolated from membership details for better performance when querying large transaction datasets
3. Enforces better security through data isolation
4. Allows for independent scaling of membership and payment tables
5. Clear separation reduces risk of data corruption and simplifies validation
6. Sensitive payment data is isolated, allowing focused access control and encryption strategies
7. Team's familiarity with relational database schemas ensures easier implementation and maintenance

### Planned Implementation Details

1. Database Structure:
   * Separate membership table for user details
   * Separate payment table linked by foreign key
   * Auxiliary tables for subscription types and status
   * Clear indexing strategy for performance

2. Security Measures:
   * Encryption for sensitive payment data
   * Role-based access control
   * Audit logging for sensitive operations

3. Performance Optimisation:
   * Proper indexing strategy
   * Efficient query design
   * Regular maintenance plans

### Consequences

* Good, because it allows for efficient queries and modular design
* Good, because it provides clear separation of concerns
* Good, because it enables focused security measures for sensitive data
* Bad, because it slightly increases complexity when joining tables
* Bad, because it requires careful index management

### Confirmation

The decision will be validated through:

1. Implementation of database schema with test dataset
2. Team review of schema design
3. Performance testing of common queries
4. Security audit of data access patterns
5. Integration testing with other system components

## Pros and Cons of the Options

### Relational Database (MySQL/PostgreSQL)

* Good, because of clear separation of concerns and efficient queries
* Good, because of strong data integrity through normalisation
* Good, because of mature ecosystem and tools
* Bad, because of potentially complex joins for related data
* Bad, because of schema rigidity requiring careful planning

### NoSQL Database (MongoDB)

* Good, because of high flexibility for changing requirements
* Good, because of excellent scalability for large datasets
* Bad, because of potential consistency issues
* Bad, because of higher learning curve for the team
* Bad, because of poor fit for relational data

### Hybrid Approach

* Good, because of flexibility in data storage
* Good, because of optimized storage per data type
* Bad, because of increased system complexity
* Bad, because of maintenance overhead
* Bad, because of potential synchronisation issues

## More Information

Implementation requirements:

1. Development of detailed ERD
2. Creation of migration scripts
3. Documentation of:
   * Schema design
   * Access patterns
   * Security measures
   * Backup procedures
4. Performance benchmarking plan
5. Monitoring strategy

Next steps:

1. Finalize ERD design
2. Create test implementation
3. Develop migration strategy
4. Set up monitoring tools
5. Document maintenance procedures
