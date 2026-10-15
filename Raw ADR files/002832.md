# 4. Project architecture

Date: 2023-12-01

## Status

2023-12-01 accepted

## Context

There is a need to decide on project architecture. In this project is expected to have a considerable amount of business logic in some of its modules, so a new architecture should allow for easy unit testing of that logic.

## Decision

Project will be developed using a modular monolith approach. Every module will have its own database models and other modules will not be allowed to use it directly. At the top level, we'll have an `api-gateway` directory, `contexts` directory, and `core` directory. Controllers from the API layer should contain as little logic as possible, mostly delegating the work to the specific service using message bus.

A given service will be developed using a "Hexagonal architecture", also called "Ports & adapters" or "Clean architecture". Every module will contain `application`, `infrastructure` and `domain` directories. The application directory should contain all "incoming" adapter implementation code (e.g. query handlers). The infrastructure directory should contain all "outgoing" adapter implementation code (e.g. repositories, external services communication). The domain directory should contain all ports definitions and all business logic (e.g aggregates, domain services). This layer must not import any files from other layers, only the other way around.

At a given context layer, we'll group related features in a single directory (e.g. `user-management`). Inside that, we'll have our command and query handlers. In simplest cases, a handler can handle an entire request by itself by making requests to the database directly. However, if any business rules are involved, this code should be moved to the domain layer and unit tested there, while a handler should only coordinate the process by calling functions on repositories, aggregates, or domain services.

## Distinction Between `libs` and `core` Directories

In our project architecture, we make a clear distinction between the `libs` and `core` directories to ensure modularity and maintainability. Here's how they are defined:

### `libs` Directory

The `libs` directory is intended for external libraries or shared utilities that can be used across different projects or services (if needed). This includes:

- Common error handling
- External libraries
- Database error codes and mapping functionalities
- Shared DTOs and value objects
- Utitity functions

These are functionalities or utilities that are not specific to the business logic of our application but are essential for the operation of various parts of the system.

### `core` Directory

The `core` directory, on the other hand, is designed to contain shared functionality that is crucial for the application contexts within our project. This includes:

- Shared domain logic
- Infrastructure code that is common across different modules
- Integration patterns and adapters for external services
- Dtos
- Domain events
- Framework specifics (guards, interceptors, exception filters, decorators, etc)
- Applicatoin enums
- Value objects

The `core` directory serves as the heart of our application, ensuring that common functionalities needed by different parts of the application are centrally managed and easily accessible.

### Recommendations

While the current structure serves well in distinguishing external libraries/utilities from core functionalities, it's recommended to:

1. **Document Usage Guidelines**: Clearly document the intended use cases for both directories. This will help developers understand where to place new code or look for existing functionalities.

2. **Review and Refactor**: Periodically review the contents of both directories to ensure that they remain aligned with their intended purposes. If a functionality initially developed in `core` becomes generic enough to be used in other projects, consider moving it to `libs`.

3. **Namespace Clarity**: Ensure that namespaces and module names clearly reflect their location and purpose. This aids in discoverability and avoids confusion.

By adhering to these guidelines, we can maintain a clear separation of concerns between `libs` and `core`, enhancing the modularity and maintainability of our project.

## Consequences

- It will be easy to unit test domain logic.
- Services will be loosely coupled without the need of deploying them separately.
- Developers will have to learn new architecture patterns.
- It will be more difficult to implement some cross-service functionality than with a regular monolith.
- We will need to develop some infrastructure code and integration patterns between services.
