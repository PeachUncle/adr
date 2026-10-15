## ADR 003: Database Engine - PostgreSQL

## Context

Considering we are using Django as our backend framework, it is most reasonable to use a database supported officially by Django. These are PostgreSQL, MariaDB, MySQL, Oracle, and SQLite [1].

### Options
- Oracle: This is considered the *de facto* standard of RDBMSs for large enterprises. For a long time, no other RDBMS could compare to it in performance on more complex queries, and it had many more features with respect to governance, security, and other things highly desirable for large enterprises. That said, it is very expensive, as the standard edition starts at $17500 USD, and enterprise edition at $47500 [2].
- MySQL: This has an LGPLv2-licensed community edition, and paid standard and enterprise editions. Standard edition starts at $2140 USD annually, and enterprise edition at $5350 [3]. The primary benefit to the standard edition over the free one is the customer support, but many people consider Oracle support to be rather unpleasant to work with. The enterprise edition offers a few additional backup, security, and scalability features [4]. It is worth noting that as MySQL is also an Oracle product, the pricing can be considered to reflect the feature richness and performance of MySQL vs Oracle DB.
- MariaDB: This is a GPLv2-licensed fork of MySQL that for a while lagged behind it in performance, but at present is slightly faster and more scalable than MySQL enterprise edition [5].
- SQLite: This is an RDB that serves a different purpose than the others in this list. Specifically, can be run locally and generally requires no administration. That said, it is not designed to scale well to heavy workloads [6].
- PostgreSQL: The most popular free RDB, by a fairly large margin [7]. Many people consider this to be the only free RDBMS comparable to the industry standards, which are Oracle and Microsoft SQL Server, and at present its feature richness and performance can be considered comparable to them [8].

## Decision
At present, there is no good reason to use anything other than PostgreSQL. While being free it is comparable to the best paid RDBMSs. The only other option that would be worth considering would be SQLite, mainly due to the ease of setup and administration (or rather, the lack thereof), but the difference in performance and feature richness more than makes up for the small amount of extra time needed to set up and maintain a PostgreSQL server.

## Status
Accepted

## Consequences
PostgreSQL is an RDBMS, which dictates to a degree the structure of our data. This is in comparison to things like document databases, key-value stores, or graph databases.

## References

- [1]: https://docs.djangoproject.com/en/5.1/ref/databases/
- [2]: https://www.oracle.com/a/ocom/docs/corporate/pricing/technology-price-list-070617.pdf
- [3]: https://www.oracle.com/in/a/ocom/docs/corporate/pricing/mysql-pricelist-183985.pdf
- [4]: https://www.mysql.com/products/enterprise/compare/
- [5]: https://aws.amazon.com/compare/the-difference-between-mariadb-vs-mysql/
- [6]: https://www.sqlite.org/whentouse.html
- [7]: https://db-engines.com/en/ranking
- [8]: https://scalegrid.io/blog/postgresql-vs-oracle-difference-in-costs-ease-of-use-functionality/
