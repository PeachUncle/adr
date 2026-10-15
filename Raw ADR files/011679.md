# ADR: Decision on Using CQS
**Date**: January 11, 2025  
**Status**: Accepted

## Context
In the development of the Language Learning platform, we aim to maintain a clean and maintainable codebase. The project involves complex business logic and data manipulation, which necessitates a clear separation of concerns. To achieve this, we considered various architectural patterns and ultimately decided to adopt the Command Query Separation (CQS) pattern.

## Decision
We have decided to implement the CQS pattern in the Language Learning platform. This pattern will be used to separate the responsibilities of commands (which change the state of the system) and queries (which read the state of the system).

### Rationale
1. **Separation of Concerns**: CQS helps in clearly separating the code that modifies the state from the code that reads the state. This makes the codebase easier to understand and maintain.
2. **Simplified Testing**: By separating commands and queries, we can write more focused and simpler unit tests. Commands can be tested for their side effects, while queries can be tested for their return values.
3. **Scalability**: CQS allows us to scale the read and write operations independently. For example, we can optimize queries for performance without affecting the command operations.
4. **Readability and Maintainability**: The clear distinction between commands and queries improves the readability of the code. Developers can easily identify the purpose of each class and method, making the codebase more maintainable.
5. **Alignment with CQRS**: Adopting CQS is a step towards implementing the Command Query Responsibility Segregation (CQRS) pattern, which can further enhance the scalability and performance of the system.

## Implementation
1. **Commands**: Commands are used to change the state of the system. Each command is represented by a class that implements the `ICommand` interface. Command handlers are responsible for executing the commands and are registered in the dependency injection container.
   - **Example**: `CreateUserProfileCommand` and `CreateUserProfileCommandHandler`.
2. **Queries**: Queries are used to read the state of the system. Each query is represented by a class that implements the `IQuery` interface. Query handlers are responsible for executing the queries and are registered in the dependency injection container.
   - **Example**: `GetUserProfileQuery` and `GetUserProfileQueryHandler`.
3. **Command and Query Dispatchers**: We use command and query dispatchers to handle the execution of commands and queries. These dispatchers are responsible for locating the appropriate handler and invoking it.
   - **Example**: `CommandDispatcher` and `QueryDispatcher`.

## Consequences
1. **Positive Consequences**:
   - Improved code readability and maintainability.
   - Simplified unit testing for commands and queries.
   - Enhanced scalability and performance optimization opportunities.
   - Clear separation of concerns, leading to a more organized codebase.
2. **Negative Consequences**:
   - Increased complexity in the initial setup and learning curve for new developers.
   - Potential for increased boilerplate code due to the separation of commands and queries.

## Alternatives Considered
1. **Monolithic Approach**: We considered a monolithic approach where commands and queries are not separated. However, this approach would lead to a tightly coupled codebase, making it difficult to maintain and scale.
2. **CQRS**: We considered implementing the full CQRS pattern. While CQRS offers additional benefits, it also introduces more complexity. We decided to start with CQS as a stepping stone towards CQRS.

## Related Decisions
- ADR: Adoption of Clean Architecture

## References
- [Command Query Separation (CQS) Pattern](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- [Command Query Responsibility Segregation (CQRS) Pattern](https://martinfowler.com/bliki/CQRS.html)

## Status
This decision is final and has been implemented in the Language Learning platform.

---
