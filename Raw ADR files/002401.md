# 10. Use PostgreSQL for relational databases

Date: 2023-05-21

## Status

Accepted

10 [11. Use YugabyteDB for large relation databases](0011-use-yugabytedb-for-large-relation-databases.md)

## Context

In the context of selecting a relational database management system (RDBMS) for small-scale databases in Kwetter's
architecture, we needed to choose a suitable solution that could handle vertical scaling or the use of read-only copies.
The goal was to ensure efficient data storage and retrieval while considering the specific needs and constraints of the
system.

## Decision

We decided to use Postgres (PostgreSQL) as the RDBMS for small-scale relational databasesin Kwetter.

1. Proven Reliability and Stability: Postgres is a mature and reliable RDBMS with a strong track record in the industry.
   It has been extensively tested and used in various production environments, ensuring stability and durability for our
   small-scale databases.

2. Vertical Scaling Capability: Postgres supports vertical scaling, allowing us to enhance performance by increasing the
   computing power and resources of a single database instance. This scalability option is suitable for small-scale
   databases with manageable data sizes and moderate load requirements.

3. Read-Only Copies: Postgres enables the creation of read-only replicas or copies of a database. These replicas can be
   used to distribute read traffic and offload the primary database, improving overall performance and allowing for
   horizontal scalability if needed in the future.

4. Rich Functionality and SQL Support: Postgres provides a wide range of features and supports complex SQL queries,
   making it suitable for managing relational data and performing advanced data manipulations. Its extensive ecosystem
   offers various extensions and plugins for additional functionality and integration possibilities.

5. Open-Source Nature: Postgres being an open-source RDBMS played a significant role in our decision. The open-source
   nature of Postgres provides transparency, and encourages community collaboration, fosters innovation, and eliminates
   licensing costs.

6. Community Support and Documentation: Postgres has a vibrant and active community that provides excellent support and
   resources for developers and administrators. Comprehensive documentation, tutorials, and a wealth of online resources
   are available, simplifying development, troubleshooting, and maintenance tasks.

## Consequences

The decision to use Postgres as the RDBMS for small-scale relational databases in Kwetter has the following
consequences:

Efficient Data Storage and Retrieval: Postgres's robustness and reliability ensure the efficient storage and retrieval
of data for small-scale databases. Its support for vertical scaling allows us to handle increasing loads by upgrading
hardware resources as needed.

Flexibility and Extensibility: Postgres offers a rich set of features, including advanced SQL support and a wide range
of data manipulation capabilities. This flexibility allows us to model and manage relational data effectively while
accommodating potential future requirements.

Limited Scalability for Write-Intensive Workloads: Postgres's vertical scaling and read-only replica capabilities are
suitable for small-scale databases with moderate write loads. However, for write-intensive workloads or scenarios
requiring massive horizontal scalability, alternative solutions such as distributed databases or sharding might be more
appropriate.

Maintenance and Administration: Using Postgres requires ongoing monitoring, maintenance, and administration tasks, such
as database backups, query optimization, and security updates. Adequate expertise and resources should be allocated to
ensure the reliable operation and performance of the Postgres databases.

Leveraging Existing Knowledge and Skills: Postgres's popularity and widespread usage mean that many developers and
database administrators are already familiar with its concepts and best practices. This allows for easier knowledge
transfer, team collaboration, and a reduced learning curve for new team members.

Open-Source Advantages: Postgres being an open-source RDBMS provides additional benefits. It grants us the freedom to
customize and extend the database system to meet our specific needs. It also fosters a collaborative community that
contributes to the improvement and evolution of the software.
