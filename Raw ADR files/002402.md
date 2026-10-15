# 11. Use YugabyteDB for large relation databases

Date: 2023-05-21

## Status

Accepted

10 [10. Use PostgreSQL for relational databases](0010-use-postgresql-for-relational-databases.md)

## Context

In the context of selecting a distributed SQL database for large volume relational databases in Kwetter's architecture,
we needed to choose a solution that could handle high data volumes, provide scalability, and ensure transactional
consistency. Additionally, compatibility with existing PostgresSQL drivers and adherence to cloud-native principles were
important considerations.

## Decision

We have decided to use YugabyteDB as the distributed SQL database for large volume relational databases in Kwetter.
YugabyteDB is an open-source distributed SQL database designed specifically for cloud-native transactional applications.
It offers linear scalability, high availability, and fault tolerance while maintaining strong data consistency.
YugabyteDB is compatible with the PostgreSQL wire protocol, supports the PostgreSQL API, and provides ACID transactions.
These features make it a suitable choice for our requirements. Furthermore, YugabyteDB aligns with our cloud-native
focus and can be seamlessly integrated with our existing ecosystem, thanks to its compatibility with PostgresSQL drivers
and libraries. The active and supportive community around YugabyteDB ensures timely bug fixes, enhancements, and
knowledge sharing.

## Consequences

By choosing YugabyteDB as the distributed SQL database for large volume relational databases in Kwetter, we expect the
following benefits:

- Scalability and Performance: YugabyteDB's distributed architecture enables horizontal scaling, allowing us to handle
  large data volumes and increasing workloads efficiently. This ensures optimal system performance and the ability to
  accommodate future growth.

- Transaction Consistency: YugabyteDB's support for ACID transactions ensures transactional consistency, maintaining
  data integrity and reliability in Kwetter's relational databases.

- Compatibility with Postgres Ecosystem: YugabyteDB's compatibility with PostgresSQL drivers, libraries, and tools
  simplifies integration with our existing ecosystem. This compatibility reduces migration efforts and allows us to
  leverage our existing knowledge and tools, facilitating a smooth transition.

- Cloud-Native Alignment: By choosing YugabyteDB, we align with cloud-native principles and leverage its features
  designed for cloud environments. This allows us to deploy, manage, and integrate the database seamlessly into our
  existing cloud infrastructure and microservices architecture.

- Community Support: YugabyteDB benefits from an active and supportive community of users and contributors. Engaging
  with this community provides access to resources, best practices, and timely updates, enhancing the stability and
  reliability of the database.

It is important to note that adopting YugabyteDB may require some learning and adjustment for developers and
administrators who are new to distributed SQL databases. Adequate training and resources should be provided to ensure a
smooth transition and effective utilization of YugabyteDB.
