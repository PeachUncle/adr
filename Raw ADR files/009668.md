# Selection of Database System Architectural Decision Record

* Status: accepted
* Date: 2024-11-17
* Decision-Makers: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz
* Consulted: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz
* Informed: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz

## Context and Problem Statement

AML requires a robust database system to manage library operations across England, handling 11.2M+ users with 10% annual growth. The system must maintain data consistency, support complex queries, and ensure secure transactions for operations like media management, user accounts, and branch activities.

## Decision Drivers

* Data integrity and consistency to prevent transactional errors.
* High transaction volume support (500K+ daily transactions).
* Complex query handling for reporting and analytics.
* Integration compatibility with Laravel framework.
* Security and compliance for sensitive data protection.
* Team expertise and learning curve for efficient adoption.
* Total cost of ownership including licensing, support, and scalability.
* Backup and disaster recovery to ensure data availability.

## Considered Options

### 1. Microsoft SQL Server
* Enterprise-grade relational database.
* Strong integration with Microsoft ecosystem.
* Built-in replication and reporting features.

### 2. MySQL
* Open-source relational database.
* Widely used for web-based applications.
* Large community support for troubleshooting.

### 3. PostgreSQL
* Open-source object-relational database.
* Advanced features like JSON support and extensibility.
* Suitable for highly customized setups.

## Decision Outcome

Chosen option: Microsoft SQL Server

Justification:
Microsoft SQL Server provides the enterprise-grade features, security capabilities, and performance required for AML. It excels in handling high transaction volumes and complex queries, while offering robust backup and recovery features. Additionally, its strong replication tools and native integration with Microsoft services streamline distributed library operations. Although the higher cost is a drawback, its benefits justify the investment.

## Consequences

Good:
* Enterprise-level reliability and robust security features.
* Excellent performance for complex queries and analytics.
* Built-in tools for reporting and replication.
* Strong backup and recovery capabilities.
* Row-level security to protect sensitive user data.

Bad:
* Higher licensing costs compared to open-source options.
* Increased hardware requirements for optimal performance.
* More complex administration needs.

## Confirmation

The implementation will be validated through:
* Performance Testing: Simulating peak transaction loads.
* Security Audits: Ensuring compliance with data protection standards.
* Backup and Recovery Testing: Confirming system resilience.
* Query Optimization Reviews: Ensuring efficient database operations.
* Production Monitoring: Continuous evaluation of performance and reliability.

## Pros and Cons of Options

### Microsoft SQL Server
* Good: Enterprise-grade features, strong security, high performance.
* Neutral: Administration complexity balanced by extensive tools.
* Bad: High licensing costs, increased resource requirements.

### MySQL
* Good: No licensing costs, strong community support.
* Neutral: Adequate for basic operations, not feature-rich.
* Bad: Limited enterprise features, complex replication setup.

### PostgreSQL
* Good: Advanced features, high flexibility.
* Neutral: Steeper learning curve mitigated by extensive customization options.
* Bad: Performance overhead in large-scale deployments.

## More Information

References:
1. [https://learn.microsoft.com/en-us/sql/sql-server/?view=sql-server-ver16](https://learn.microsoft.com/en-us/sql/sql-server/?view=sql-server-ver16)
2. [https://www.altexsoft.com/blog/comparing-database-management-systems-mysql-postgresql-mssql-server-mongodb-elasticsearch-and-others/](https://www.altexsoft.com/blog/comparing-database-management-systems-mysql-postgresql-mssql-server-mongodb-elasticsearch-and-others/)
3. [https://www.syteca.com/en/blog/data-security-best-practices](https://www.syteca.com/en/blog/data-security-best-practices)
4. [https://laravel.com/docs/11.x/database](https://laravel.com/docs/11.x/database)

Review:
This architecture choice will be reassessed if:
* Data growth exceeds projected rates.
* Performance metrics fall below acceptable thresholds.
* Licensing costs become unsustainable.
* Security requirements change significantly.