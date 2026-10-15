# ADR 07: CQRS and Event Sourcing Backend

[<- Back](../README.md)

## Context

We want to separate read and write operations for scalability and maintain an
immutable log of all the changes to our system state.

## Decision

We will use the Command Query Responsibility Segregation (CQRS) and Event
Sourcing pattern for our backend.

Command Query Responsibility Segregation (CQRS) is an architectural pattern in
software development that separates read operations (queries) from write
operations (commands), thereby allowing them to be handled independently,
optimized separately, and even scaled individually. This pattern emerged from
the principle of Command-Query Separation (CQS), proposed by Bertrand Meyer,
which dictates that an object's methods should be either commands performing an
action, or queries returning data, but not both. CQRS takes this concept a step
further by applying it at the system level. In a CQRS-based system, the data
model for write operations (commands) can be completely different from the data
model for read operations (queries). This separation enhances performance,
simplifies design, and can make the system more resilient and flexible, as it
allows you to tailor your infrastructure, technology stack, and data schema to
the distinct needs of reads and writes. However, it also introduces complexity,
as you must handle synchronization between the different models, and is
therefore not suitable for all types of applications.

Event Sourcing is an architectural pattern in which state changes to an
application are stored as a sequence of events. Instead of modifying the state
of the application directly, changes are captured in an immutable event object
which is appended to an event log. The current state of the application, at any
point in time, can then be derived by replaying this event log from the
beginning. Event Sourcing ensures that all changes to application state are
stored in an event log, providing full auditability and traceability, and
enabling advanced temporal queries. Moreover, it makes it possible to rebuild
the application state as it was at any point in time, and allows for event
replaying in case of errors, bugs, or system crashes. However, implementing an
Event Sourcing architecture can be complex, as it requires dealing with issues
such as event ordering, eventual consistency, and event schema evolution.
Despite these challenges, Event Sourcing can be a powerful tool in systems
where high auditability, temporal queries, or complex business rules are required.

The sub-decisions associated with this ADR include:

- We will ONLY allow write operations to the event stream, which will be
  persisted in an append-only log (or event store). The event stream, using
  Kinesis Data Streams, will retain events for 7 days. The event store, using
  Kinesis Firehose piped events to S3, will be our single source of truth;
  retaining all events indefinitely.

- We will use a separate read model for all read operations using DynamoDB. We
  will enable point-in-time recovery (PITR), so it maintains incremental
  backups of tables for the last 35 days. This allows us to restore a table to
  any point in time within this window. This will reduce the burden on our
  event streaming service.

- We will use Cloud Events >= v1.0 as our base event schema.

- We will use AsyncAPI >= v2.6 to document and version events.

- We will use OpenAPI >= v3.1 to document and version our REST API.

## Consequences

- Scalability is improved due to separation of concerns.
- Provides an audit trail of changes.
- Additional complexity due to managing separate models for reads and writes,
  as well as managing and applying events.
