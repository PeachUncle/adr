# ADR-002: Separation of Domain Logic vs CLI Code

## Status
Accepted

## Date
2025-12-04

## Context
The Todo Console App must follow clean architecture principles to separate domain logic from UI concerns, as required by the project constitution. This separation is critical for maintainability, testability, and future extensibility. The application needs to clearly delineate between business logic (task operations) and presentation logic (CLI interaction).

## Decision
We will implement a clean architecture pattern with a clear separation between:
- **Models** (src/models/): Contain core domain entities with validation rules
- **Services** (src/services/): Implement business logic for task operations
- **CLI** (src/cli/): Handle user input/output and command parsing

The TodoService will be the central component managing all business operations without any knowledge of the CLI interface. The CLI layer will only handle user interaction and delegate operations to the service layer.

## Alternatives Considered
1. **Monolithic approach**: All functionality in a single component - would violate clean architecture principles and reduce maintainability
2. **MVC pattern**: More complex than needed for a simple console application
3. **Layered architecture with 2 tiers only**: Would not provide sufficient separation of concerns

## Consequences

### Positive
- Clear separation of concerns enhances maintainability
- Improved testability as business logic can be tested independently of UI
- Better adherence to project constitution's clean architecture requirement
- Enables easier future extensions (e.g., adding a web interface would only require a new presentation layer)
- Follows established software engineering best practices

### Negative
- Slightly more complex initial setup
- More files and directories to navigate
- Requires more careful design of interfaces between layers
- Additional abstraction may be overhead for such a simple application

## References
- plan.md: "Architecture Overview" and "Component Breakdown" sections
- constitution.md: "Clean Architecture" principle
- plan.md: "Project Structure" section