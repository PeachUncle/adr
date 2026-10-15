
# Media Database Technology Decision

## Context and Problem Statement.
Due to the architecutre of the project, and it to be modular, the media database needs to be it's own instance and the same with the API service.

## Decision Drivers:
* A modular driven software and development
* Clear link of data between each related service

## Considered Options:
* sqlite
* MySQL
* Superbase
* SurrealDB

## Pros and Cons:

### sqlite
| **Pros**                              | **Cons**                                     |
|---------------------------------------|---------------------------------------------|
| Lightweight and self-contained       | Limited concurrent write support            |
| Serverless architecture              | Size limitations                            |
| Cross-platform compatibility         | Limited advanced features                   |
| Transactional integrity              | Weak typing system                          |
| Zero configuration                   | Security considerations                     |
| Public domain licensing              | Not ideal for high-concurrency applications |

### MySQL

| **Pros**                              | **Cons**                                     |
|---------------------------------------|---------------------------------------------|
| Open-source and free                 | Limited advanced features                   |
| Cross-platform compatibility         | Performance issues with large-scale databases |
| High performance and scalability     | Licensing considerations                    |
| Robust data security                 | Limited support for NoSQL features          |
| Comprehensive documentation          | Complex configuration for high availability |

### Superbase

| **Pros**                              | **Cons**                                     |
|---------------------------------------|---------------------------------------------|
| Open-source platform                 | Limited integrations                        |
| PostgreSQL integration               | Complexity of row-level security            |
| Real-time capabilities               | Evolving platform causing bugs and missing features |
| User-friendly interface              | Small community support                     |
| Predictable pricing model            | Limited advanced features                   |

### SurrealDB
| **Pros**                              | **Cons**                                     |
|---------------------------------------|---------------------------------------------|
| Multi-model database                  | Maturity and stability                        |
| Schemafull and schemaless operation   | Evolving documentation          |
| Real-time capabilities                | Small community and support |
| Built-in security features            | Performance documentaiton may not be as well documented                     |
| Open-source and community-driven      | Learning curve                 |


## Decision Outcome
We decided on using superbase, down to it being perfectly scable, for future sake of the system and it's running and funding, it's cheap. It has high secuirty implementations and it's well documented and can be quite easy to work with, it also seperated the database and the media API seperatley, decreasing the risk of attacks on the system in case of one. 

## References
* InfoWorld. (n.d.). Why you should use SQLite. Retrieved November 18, 2024, from https://www.infoworld.com/article/2258587/why-you-should-use-sqlite.html
* Wikipedia. (n.d.). SQLite. Retrieved November 18, 2024, from https://en.wikipedia.org/wiki/SQLite
* DevPals. (n.d.). Comparing top database management systems. Retrieved November 18, 2024, from https://devpals.co.uk/blog/comparing_top_database_management_systems
* DigitalOcean. (n.d.). SQLite vs MySQL vs PostgreSQL: A comparison of relational database management systems. Retrieved November 18, 2024, from https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs-postgresql-a-comparison-of-relational-database-management-systems
  
* W3schools. (n.d.). MySQL advantages and disadvantages. Retrieved from https://www.w3schools.blog/mysql-advantages-disadvantages
* AspiringYouths. (n.d.). Advantages and disadvantages of MySQL. Retrieved from https://aspiringyouths.com/advantages-disadvantages/mysql/
* ProsPlusCons. (2024, October). 21 pros and cons of MySQL. Retrieved from https://prospluscons.com/pros-and-cons-of-mysql/
* TechStrikers. (n.d.). MySQL advantages and disadvantages. Retrieved from https://www.techstrikers.com/MySQL/advantages-and-disadvantages-of-mysql.php
* Datamation. (2023, March 15). 8 big advantages of using MySQL. Retrieved from https://www.datamation.com/storage/8-major-advantages-of-using-mysql/
* SmartFile. (2021, May 10). The pros and cons of MySQL. Retrieved from https://www.smartfile.com/blog/the-pros-and-cons-of-mysql
* TrustRadius. (2024). MySQL: Pros and cons. Retrieved from https://www.trustradius.com/products/mysql/reviews?qs=pros-and-cons
* ProjectManagers.net. (2024, January 25). MySQL: 10 cons & disadvantages with 5 alternatives. Retrieved from https://projectmanagers.net/mysql-10-cons-disadvantages-with-5-alternatives/

* TrustRadius. (2024). Pros and cons of Supabase. Retrieved from https://www.trustradius.com/products/supabase/reviews?qs=pros-and-cons
* G2. (2023). Supabase pros and cons. Retrieved from https://www.g2.com/products/supabase-supabase/reviews?qs=pros-and-cons
* Dev.to. (2023). Evaluating Supabase. Retrieved from https://dev.to/leibole/evaluating-supabase-kl4
* LogRocket. (2023). Firebase vs. Supabase: Choosing the right tool for your project. Retrieved from https://blog.logrocket.com/firebase-vs-supabase-choosing-right-tool-project/
* Netguru. (2024). Supabase vs. Firebase: Which BaaS is best for your app?. Retrieved from https://www.netguru.com/blog/supabase-vs-firebase

* StackShare. (n.d.). SurrealDB - Reviews, Pros & Cons | Companies using SurrealDB. Retrieved from https://stackshare.io/surrealdb
* SurrealDB. (2023, August 29). Data Modelling and Performance. Retrieved from https://surrealdb.com/blog/data-modelling-and-performance
* SurrealDB. (2023, May 15). What are Multi-Model Databases?. Retrieved from https://surrealdb.com/blog/what-are-multi-model-databases
* SurrealDB. (2024, February 20). Thinking Inside The Box: Relational Style Joins in SurrealDB. Retrieved from https://surrealdb.com/blog/thinking-inside-the-box-relational-style-joins-in-surrealdb
* Wessel, S. (2023, April 10). SurrealDB - The Magic Database to Keep on Your Radar. Retrieved from https://dev.to/sebastian_wessel/surrealdb-the-magic-database-to-keep-on-your-radar-4a22
