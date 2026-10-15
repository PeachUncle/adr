# Frontend

|          |                                                   |
| -------- |---------------------------------------------------|
| status   | accepted                                          |
| date     | 2024-05-28                                        |
| deciders | [Joshua Gawenda](https://github.com/gutentag2012) |

## Context and Problem Statement

When working with different projects in the frontend and async processes, there needs to be a way to store the data.

## Decision Drivers

* Time to implement
* Ease of use
* Performance
* Project Complexity

## Considered Options

* SQLite
* Minio
* MySQL

## Decision Outcome

Chosen option: "Minio", because it is already integrated in the project and offers a good representation of the projects and image stacks without the need to implement more complex database logic in the go service and backend.

### Consequences

There is no way to store any additional or more complex data and as long as the project stays simple, this is not a problem.

## Pros and Cons of the Options

### SQLite

SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.

* Good, because it is straightforward to use
* Good, because it is fast
* Good, because it can be used without setting up an extra environment
* Bad, because a lot of additional work is required
* Bad, because there could be a mismatch between project data in Minio and SQLite

### Minio

Minio is an open-source object storage server with an Amazon S3 compatible API.

* Good, because not a lot of additional work is required
* Good, because no addition environment is needed
* Good, because there is a direct connection between projects and the minio storage, so a mismatch cannot cause issues
* Bad, because additional data cannot be stored
* Bad, because async processes state cannot be stored

### MySQL

MySQL is an open-source relational database management system.

* Good, because it is a well-known and widely used database system
* Neutral, because it requires setup of an additional environment
* Bad, because a lot of additional work is required
* Bad, because there could be a mismatch between project data in Minio and MySQL

## More Information

This decision might get revisited once the requirements grow and require a more complex database setup.
