# Initial Conception

## Status
Accepted

## Context
We need a service to handle rooms reservations.
The service will be responsible for storing and displaying the data from and to the database.
The system will also be responsible for managing customers and reservations.

## Decision
We will create a .net core API that will use Entity Framework Core to interact with the database.
The API will be responsible for handling the CRUD operations for the rooms, customers, and reservations.
The API will also be responsible for handling the business logic for the reservations.
We will separate each layer into each own project to have assembly separation on top of namespaces.
We will use the repository pattern to interact with the database.
We will implement cross-cutting concerns like logging and exception handling using middleware.
We will use the mediator pattern to handle the business logic for the reservations.
We will use the CQRS pattern to separate the read and write operations.

## Consequences
The benefits of this decision are:
- We will have a clear separation of concerns.
- We will have a clear separation of the read and write operations.
- We will have a clear separation of the business logic.
- We will have a clear separation of the data access logic.
- We will have a clear separation of the cross-cutting concerns.
- We will have a clear separation of the layers.
- We will have a clear separation of the assemblies.
- We will have a decoupled system.
- We will have a maintainable system.
- We will have a testable system.
- We will have a system that is easy to extend.
- We will have independent features developed in parallel.
- We will have a system that is easy to understand.

## Alternatives Considered
Alternative 1:
We could use a serverless architecture instead of a monolithic architecture. This would involve deploying individual functions to a cloud provider, which would handle the scaling and infrastructure management. This approach can reduce operational overhead and costs, but it may introduce latency and complexity in managing function interactions and state.

## References
- https://docs.microsoft.com/en-us/aspnet/core/web-api/?view=aspnetcore-8.0
- https://docs.microsoft.com/en-us/ef/core/
- https://martinfowler.com/bliki/CQRS.html
- https://adr.github.io/
