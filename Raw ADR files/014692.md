# ADR-0006: Data Store

## Status

Accepted

Date of decision: 2024-08-23

## Context and Problem Statement

The Private Rented Sector Database (PRSDB) will need to hold data records. The data model is not yet fully understood,
but at a minimum the PRSDB will need to hold data on landlords, dwellings, offences, and penalties, as well as user
account data (e.g. details of delegations from landlords to letting agents).

Where will we store this data?

## Considered Options

* Amazon RDS for PostgreSQL
* Amazon RDS for MySQL 
* Amazon DocumentDB

## Decision Outcome

Amazon RDS for PostrgreSQL, because it is a managed service, relational SQL is a good fit, and it is slightly more
popular than MySQL.

## Pros and Cons of the Options

### Amazon RDS for PostgreSQL

Amazon Relational Database Service (RDS) is a managed, scalable database service provided by AWS. It offers several
database engines, including PostgreSQL. PostgreSQL is a popular relational SQL database.
* Good, because as a managed service it reduces the operational burden on MHCLG.
* Good, because PostgreSQL is arguably the most popular database in use today (49% of professional developers responding
  to the Stack Overflow survey 2023 used it).
* Good, because relational SQL databases are well-suited to operational workloads (which is the primary expected
  workload of PRSDB).
* Good, because relational SQL databases are well-suited to predictable, structured data (such as the data collected by
* PRSDB).
* Good, because SQL is very widely understood.
* Good, because it is used by modern MHCLG services.

### Amazon RDS for MySQL

Amazon RDS for MySQL uses MySQL as the database engine. MySQL is another popular relational SQL database. 
* Good, because as a managed service it reduces the operational burden on MHCLG.
* Neutral, because MySQL is still commonly used, but arguably in decline (41% of professional developers responding to
  the Stack Overflow survey 2023 used it).
* Good, because relational SQL databases are well-suited to operational workloads (which is the primary expected
  workload of PRSDB).
* Good, because relational SQL databases are well-suited to predictable, structured data (such as the data collected by
  PRSDB).
* Good, because SQL is very widely understood.
* Good, because it is used by modern MHCLG services.

### Amazon DocumentDB

Amazon DocumentDB is a fully managed, scalable JSON document database. As a document database, it is a type of “NoSQL”
database solution.
* Good, because as a managed service it reduces the operational burden on MHCLG.
* Bad, because use of DocumentDB, and document databases in general, can benefit from skills which are less commonplace
  than skills with traditional relational databases.
* Good, because document databases are well-suited to operational workloads (which is the primary expected workload of
* PRSDB).
* Bad, because the flexibility of a document database is not required to store the structured data that PRSDB is
  expected to collect.
* Bad, because we are not aware of other MHCLG services using it.

## More Information

* Stack Overflow Survey 2023 results: https://survey.stackoverflow.co/2023/#most-popular-technologies-language-prof
* Review of the MHCLG technical landscape: [DLUHC Tech Landscape Review.docx](https://mhclg.sharepoint.com/:w:/s/PrivateRentedSector/EZp45cVALmBDl-MmTf5gd9cBajXyR87tPoGDom_OZFiMgg?e=GgSSh6)