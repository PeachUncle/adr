---
status: accepted
date: 2022-05-22
---
# Implement a REST API to cover legacy database features

## Context and Problem Statement

The legacy system relies on direct clients of the database. In particular,
there are some PL/SQL functions that embed business logic. We want to decouple
the architecture and implement a service with a clear API, using a generic
protocol that can be open to unprivileged applications using it directly.

We are presented with a modeling and protocol choice for this service.

## Considered Options

* REST with JSON
* GraphQL endpoint
* gRPC

## Decision Outcome

Chosen option: REST with JSON

The ubiquity of REST APIs is undeniable. There are libraries in effectively
every environment for building and consuming REST, and we are familiar with
them. The potential modeling and performance considerations do not outweigh
the learning curve and client-side dependencies of a totally different
approach at this time.

## More Information

This project is not a classical fit for REST, where the resource modeling
offers permissive access to the data model and minimal business rules, allowing
for ad hoc external applications to be built up. In addition, common challenges
with REST are filtering, pagination, and traversing associations. This API will
likely offer some data management, but its primary purpose to offer an
interface to the business rules encoded in the Oracle PL/SQL functions.

Because of this difference in purpose, we considered using a traditional RPC
modeling, with the use cases exposed directly. As for protocol and
serialization, we are not concerned about browser use, where HTTP and JSON are
very convenient. This brought gRPC into consideration, which offers strict data
definition, validation, versioning, and a number of performance benefits.
However, the familiarity of REST/JSON won out in discussion. We want to learn
how to apply BDD more broadly, so having fewer variables is valuable. If we
discover performance problems, we will profile to understand whether they stem
from protocol, serialization, or implementation.

GraphQL entered consideration to address the querying needs (matching, subsets
of fields, joined associations), but as mentioned above, the queries are quite
well known in advance. We do not need an arbitrarily expressive data API now.
However, it may be an interesting experiment to layer a GraphQL endpoint over
this data in the future and gain experience with it.
