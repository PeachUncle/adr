# Database

* Status: Accepted
* Deciders: Name1, Name2, Name3
* Date: 2024-11-12

Technical Story: A relational database system is needed to handle structured data for user accounts, media inventory, borrowed media and subscription history.

## Context and Problem Statement

The database must efficiently store and manage structured data while ensuring data integrity and supporting complex queries.

## Decision Drivers

* Support for relational data models to manage structured and connected data.
* Connects well with existing backend frameworks like Node.js.
* Performance requirements for handling AML operations efficiently and effectively.

## Considered Options

* MongoDB
* MySQL

## Decision Outcome

Chosen option: "MySQL", because We selected MySQL as the database solution because it provides excellent support for the structured and transactional data that the AML system needs. MySQL's relational model fits great with the core requirements, such as user accounts, borrowing history, and keeping a track of library inventory.

### Positive Consequences

* Easy to use with strong support for relational operations.
* Suitable for structured, relational data

### Negative Consequences

* May face performance bottlenecks for larger-scale deployments.

## Pros and Cons of the Options

### MongoDB

A NoSQL database designed for unstructured and semi-structured data.

* Good, because - High performance for document-based queries.
- Schema-less design allows flexibility.
* Bad, because - Lacks robust support for relational operations.
- Additional complexity when handling transactions.

### MySQL

A relational database management system.

* Good, because - Large community and support base.
- Well-structured for multiple models.
* Bad, because - Not as flexible with data types like JSON.
- Limited functionality for modern NoSQL-like operations.

## Links

* Oracle. (n.d.). MySQL documentation. Retrieved November 12, 2024, from https://dev.mysql.com/doc/
* MongoDB, Inc. (n.d.). MongoDB documentation. Retrieved November 12, 2024, from https://www.mongodb.com/docs/
