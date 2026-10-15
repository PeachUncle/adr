# ADR-001: Clean Architecture Pattern

## Status
**Accepted**

## Context
Nucleus needs to integrate with multiple external workflow platforms (n8n, Make, Power Automate) while maintaining a clean separation between business logic and external concerns. The system must be testable, maintainable, and allow for future platform integrations without major refactoring.

Forces at play:
- Need for platform-agnostic business logic
- Requirement for comprehensive testing
- Future extensibility for new platforms
- Clear separation of concerns
- Dependency management complexity

## Decision
We will implement Clean Architecture with four distinct layers:

1. **Domain Layer** (`Nucleus.Domain`): Core business entities, interfaces, and domain logic
2. **Application Layer** (`Nucleus.Application`): Use cases, orchestration, and business workflows
3. **Infrastructure Layer** (`Nucleus.Infrastructure`): External concerns, data access, and integrations
4. **Presentation Layer** (`Nucleus.Presentation`): API controllers and external interfaces

Dependencies flow inward: Presentation → Application → Domain, with Infrastructure implementing Domain/Application interfaces.

## Consequences

### Positive
- **Testability**: Business logic can be tested in isolation
- **Maintainability**: Clear separation makes code easier to understand and modify
- **Flexibility**: Easy to swap implementations (e.g., different databases, LLM providers)
- **Platform Independence**: Core logic is independent of external platforms
- **Scalability**: New features can be added without affecting existing code

### Negative
- **Complexity**: More layers and abstractions to manage
- **Learning Curve**: Team needs to understand Clean Architecture principles
- **Boilerplate**: More interfaces and abstractions required
- **Performance**: Additional abstraction layers may add minimal overhead

### Neutral
- **Structure**: Enforces consistent project organization
- **Documentation**: Architecture decisions are more explicit

## Rationale
Clean Architecture was chosen over alternatives like:
- **Monolithic MVC**: Would tightly couple business logic to framework concerns
- **Microservices**: Overkill for current scale, adds unnecessary complexity
- **Layered Architecture**: Less strict dependency rules, harder to maintain

The decision balances maintainability and testability with the complexity overhead. The inward dependency flow ensures that business logic remains pure and testable, while external concerns are properly abstracted.

## Related Decisions
- [ADR-007: CQRS Pattern Implementation](ADR-007-cqrs-pattern.md)
- [ADR-008: Entity Framework Core](ADR-008-entity-framework.md)

## References
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Architecture Overview](../architecture.md) 