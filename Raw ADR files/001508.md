# ADR-001: Adoption of Domain-Driven Design

## Status
Accepted

## Date
2025-01-14

## Context
The EdgeRush LootMan codebase had grown organically with a traditional layered architecture organized by technical concerns (controllers, services, repositories). As the system complexity increased with multiple bounded contexts (FLPS calculation, loot distribution, attendance tracking, raid management, applications, and integrations), we needed a better way to organize code that reflects business domains and maintains clear boundaries between different areas of functionality.

The existing structure made it difficult to:
- Understand business logic scattered across multiple service classes
- Maintain clear boundaries between different functional areas
- Ensure consistency in how we model business concepts
- Scale the team as developers needed to understand the entire codebase
- Test business logic in isolation from infrastructure concerns

## Decision
We will adopt Domain-Driven Design (DDD) principles to organize the codebase into bounded contexts with clear layered architecture:

### Bounded Contexts
- **FLPS**: Final Loot Priority Score calculation and modifiers
- **Loot**: Loot distribution, awards, and bans
- **Attendance**: Raid attendance tracking and reporting
- **Raids**: Raid scheduling, signups, and management
- **Applications**: Guild application review and processing
- **Integrations**: External API synchronization
- **Shared**: Cross-cutting concerns (Raider, Guild entities)

### Layered Architecture
Each bounded context follows a consistent four-layer structure:

1. **API Layer** - REST controllers, DTOs, exception handlers
2. **Application Layer** - Use cases that orchestrate domain logic
3. **Domain Layer** - Business logic, entities, value objects, domain services, repository interfaces
4. **Infrastructure Layer** - Repository implementations, external API clients, database entities, mappers

### DDD Patterns
- **Entities**: Objects with identity that persist over time (e.g., Raider, LootAward)
- **Value Objects**: Immutable objects defined by their attributes (e.g., FlpsScore, RaiderId)
- **Aggregates**: Clusters of entities with a root entity that enforces invariants (e.g., Raid with RaidSignups)
- **Domain Services**: Business logic that doesn't naturally fit in entities
- **Repository Pattern**: Abstraction for data access with interfaces in domain layer

## Consequences

### Positive
- **Clear Business Boundaries**: Each bounded context has well-defined responsibilities
- **Improved Testability**: Domain logic can be tested without infrastructure dependencies
- **Better Code Organization**: Developers can work on specific contexts without understanding the entire system
- **Explicit Dependencies**: Use cases make dependencies and data flow clear
- **Maintainability**: Changes to one context have minimal impact on others
- **Scalability**: Team can be organized around bounded contexts
- **Ubiquitous Language**: Code reflects business terminology

### Negative
- **Learning Curve**: Team needs to understand DDD concepts and patterns
- **More Files**: Separation of concerns creates more classes and interfaces
- **Initial Overhead**: Refactoring existing code to DDD structure requires significant effort
- **Potential Over-Engineering**: Simple CRUD operations may feel heavyweight

### Neutral
- **Repository Interfaces**: Domain layer defines interfaces, infrastructure implements them
- **Use Case Pattern**: All business operations go through explicit use case classes
- **Mapper Layer**: Required to convert between domain models and persistence entities

## Implementation Notes
- Migration is being done incrementally, one bounded context at a time
- Existing REST endpoints maintain backward compatibility
- Repository interfaces are defined in domain layer, implementations in infrastructure
- Value objects use Kotlin inline classes where appropriate for performance
- Domain events are prepared for but not yet implemented

## References
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [Implementing Domain-Driven Design by Vaughn Vernon](https://vaughnvernon.com/)
- [DDD Reference by Eric Evans](https://www.domainlanguage.com/ddd/reference/)
